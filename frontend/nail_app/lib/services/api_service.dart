import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';
import '../config/app_config.dart';

/// API 服务类
/// 封装所有 HTTP 请求，包括请求拦截、错误处理等
class ApiService {
  late Dio _dio;
  static final ApiService _instance = ApiService._internal();
  bool _isRefreshing = false;

  factory ApiService() {
    return _instance;
  }

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectTimeout.inMilliseconds,
      receiveTimeout: ApiConfig.receiveTimeout.inMilliseconds,
      sendTimeout: ApiConfig.sendTimeout.inMilliseconds,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // 添加请求拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: _onRequest,
      onResponse: _onResponse,
      onError: _onError,
    ));

    // 添加日志拦截器（开发环境）
    if (AppConfig.enableLogging) {
      _dio.interceptors.add(LogInterceptor(
        request: true,
        requestHeader: true,
        requestBody: true,
        responseHeader: false,
        responseBody: true,
        error: true,
      ));
    }
  }

  /// 获取 Dio 实例
  Dio get dio => _dio;

  /// 请求拦截器
  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // 从本地存储获取 token
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(AppConfig.accessTokenKey);

    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }

    return handler.next(options);
  }

  /// 响应拦截器
  void _onResponse(
    Response response,
    ResponseInterceptorHandler handler,
  ) {
    // 可以在这里统一处理响应数据格式
    return handler.next(response);
  }

  /// 错误拦截器
  Future<void> _onError(
    DioError error,
    ErrorInterceptorHandler handler,
  ) async {
    // 处理 401 未授权错误（避免递归刷新）
    if (error.response?.statusCode == 401 && !_isRefreshing) {
      _isRefreshing = true;
      try {
        final refreshed = await _refreshToken();
        if (refreshed) {
          // FormData 的 stream 已被消耗，无法在拦截器内重试
          // 文件上传的重试由 upload() 方法处理
          if (error.requestOptions.data is FormData) {
            return handler.next(error);
          }

          // Token 刷新成功，重试原请求
          final options = error.requestOptions;
          final prefs = await SharedPreferences.getInstance();
          final newToken = prefs.getString(AppConfig.accessTokenKey);
          options.headers['Authorization'] = 'Bearer $newToken';

          try {
            final response = await _dio.fetch(options);
            return handler.resolve(response);
          } catch (e) {
            // 重试失败，继续抛出错误
          }
        } else {
          // Token 刷新失败，清除本地数据
          await _clearAuthData();
        }
      } finally {
        _isRefreshing = false;
      }
    }

    // 其他错误继续抛出
    return handler.next(error);
  }

  /// 刷新 Token（使用独立 Dio 实例避免拦截器递归）
  Future<bool> _refreshToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString(AppConfig.refreshTokenKey);

      if (refreshToken == null || refreshToken.isEmpty) {
        return false;
      }

      // 使用独立的 Dio 实例，避免触发拦截器导致递归
      final refreshDio = Dio(BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: ApiConfig.connectTimeout.inMilliseconds,
        receiveTimeout: ApiConfig.receiveTimeout.inMilliseconds,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ));

      final response = await refreshDio.post(
        ApiConfig.refreshTokenEndpoint,
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data;
        await prefs.setString(
          AppConfig.accessTokenKey,
          data['access_token'],
        );
        if (data['refresh_token'] != null) {
          await prefs.setString(
            AppConfig.refreshTokenKey,
            data['refresh_token'],
          );
        }
        return true;
      }

      return false;
    } catch (e) {
      return false;
    }
  }

  /// 清除认证数据
  Future<void> _clearAuthData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConfig.accessTokenKey);
    await prefs.remove(AppConfig.refreshTokenKey);
    await prefs.remove(AppConfig.userIdKey);
    await prefs.remove(AppConfig.userEmailKey);
    await prefs.remove(AppConfig.usernameKey);
  }

  // ==================== HTTP 方法封装 ====================

  /// GET 请求
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.get(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// POST 请求
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.post(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// PUT 请求
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.put(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// DELETE 请求
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.delete(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// 文件上传
  /// 如果 token 过期会自动刷新并重试
  Future<Response> upload(
    String path,
    String filePath, {
    String fileKey = 'file',
    Map<String, dynamic>? data,
    ProgressCallback? onSendProgress,
  }) async {
    Future<FormData> buildFormData() async {
      return FormData.fromMap({
        fileKey: await MultipartFile.fromFile(filePath),
        if (data != null) ...data,
      });
    }

    try {
      final formData = await buildFormData();
      return await _dio.post(
        path,
        data: formData,
        onSendProgress: onSendProgress,
      );
    } on DioError catch (e) {
      // 文件上传遇到 401 时，需要重新构建 FormData（stream 已被消耗）
      if (e.response?.statusCode == 401) {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString(AppConfig.accessTokenKey);
        if (token != null && token.isNotEmpty) {
          // token 已被拦截器刷新，用新 FormData 重试
          final newFormData = await buildFormData();
          return await _dio.post(
            path,
            data: newFormData,
            onSendProgress: onSendProgress,
          );
        }
      }
      rethrow;
    }
  }

  /// 文件上传（基于字节数据，兼容 Web 平台）
  Future<Response> uploadBytes(
    String path,
    Uint8List bytes,
    String filename, {
    String fileKey = 'file',
    Map<String, dynamic>? data,
    ProgressCallback? onSendProgress,
  }) async {
    Future<FormData> buildFormData() async {
      return FormData.fromMap({
        fileKey: MultipartFile.fromBytes(
          bytes,
          filename: filename,
          contentType: _getMediaType(filename),
        ),
        if (data != null) ...data,
      });
    }

    try {
      final formData = await buildFormData();
      return await _dio.post(
        path,
        data: formData,
        onSendProgress: onSendProgress,
      );
    } on DioError catch (e) {
      if (e.response?.statusCode == 401) {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString(AppConfig.accessTokenKey);
        if (token != null && token.isNotEmpty) {
          final newFormData = await buildFormData();
          return await _dio.post(
            path,
            data: newFormData,
            onSendProgress: onSendProgress,
          );
        }
      }
      rethrow;
    }
  }

  /// 根据文件名获取 MIME 类型
  static MediaType _getMediaType(String filename) {
    final ext = filename.split('.').last.toLowerCase();
    switch (ext) {
      case 'jpg':
      case 'jpeg':
        return MediaType('image', 'jpeg');
      case 'png':
        return MediaType('image', 'png');
      case 'webp':
        return MediaType('image', 'webp');
      default:
        return MediaType('image', 'jpeg');
    }
  }

  /// 文件下载
  Future<Response> download(
    String urlPath,
    String savePath, {
    ProgressCallback? onReceiveProgress,
  }) async {
    return await _dio.download(
      urlPath,
      savePath,
      onReceiveProgress: onReceiveProgress,
    );
  }
}
