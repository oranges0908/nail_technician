import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/token.dart';
import '../config/api_config.dart';
import '../config/app_config.dart';
import 'api_service.dart';

/// 认证服务类
/// 负责用户注册、登录、登出、Token管理等
class AuthService {
  final ApiService _apiService = ApiService();

  /// 用户注册
  ///
  /// 参数:
  /// - email: 用户邮箱
  /// - username: 用户名
  /// - password: 密码
  /// - inviteCode: 邀请码
  ///
  /// 返回: User 对象
  Future<User> register({
    required String email,
    required String username,
    required String password,
    required String inviteCode,
  }) async {
    try {
      final response = await _apiService.post(
        ApiConfig.registerEndpoint,
        data: {
          'email': email,
          'username': username,
          'password': password,
          'invite_code': inviteCode,
        },
      );

      return User.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }

  /// 用户登录
  ///
  /// 参数:
  /// - emailOrUsername: 邮箱或用户名
  /// - password: 密码
  ///
  /// 返回: Token 对象
  Future<Token> login({
    required String emailOrUsername,
    required String password,
  }) async {
    try {
      // 后端使用 OAuth2PasswordRequestForm，需要 form-data 格式
      final formData = FormData.fromMap({
        'username': emailOrUsername,
        'password': password,
      });

      final response = await _apiService.post(
        ApiConfig.loginEndpoint,
        data: formData,
      );

      final token = Token.fromJson(response.data);

      // 保存 Token 到本地存储
      await _saveTokens(token);

      return token;
    } catch (e) {
      rethrow;
    }
  }

  /// 刷新 Access Token
  ///
  /// 返回: 新的 Token 对象
  Future<Token> refreshToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString(AppConfig.refreshTokenKey);

      if (refreshToken == null || refreshToken.isEmpty) {
        throw Exception('Refresh token not found');
      }

      final response = await _apiService.post(
        ApiConfig.refreshTokenEndpoint,
        data: {
          'refresh_token': refreshToken,
        },
      );

      final token = Token.fromJson(response.data);

      // 保存新的 Token
      await _saveTokens(token);

      return token;
    } catch (e) {
      rethrow;
    }
  }

  /// 用户登出
  ///
  /// 清除本地存储的 Token 和用户信息
  Future<void> logout() async {
    try {
      // 调用后端登出 API（可选，JWT 是无状态的）
      await _apiService.post(ApiConfig.logoutEndpoint);
    } catch (e) {
      // 即使 API 调用失败，也要清除本地数据
    } finally {
      // 清除本地存储
      await _clearLocalData();
    }
  }

  /// 获取当前用户信息
  ///
  /// 返回: User 对象，如果未登录则返回 null
  Future<User?> getCurrentUser() async {
    try {
      final response = await _apiService.get(ApiConfig.userProfileEndpoint);
      return User.fromJson(response.data);
    } catch (e) {
      return null;
    }
  }

  /// 检查是否已登录
  ///
  /// 返回: true 表示已登录，false 表示未登录
  Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(AppConfig.accessTokenKey);
    return token != null && token.isNotEmpty;
  }

  /// 保存 Token 到本地存储
  Future<void> _saveTokens(Token token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConfig.accessTokenKey, token.accessToken);

    if (token.refreshToken != null) {
      await prefs.setString(AppConfig.refreshTokenKey, token.refreshToken!);
    }
  }

  /// 清除本地存储的认证数据
  Future<void> _clearLocalData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConfig.accessTokenKey);
    await prefs.remove(AppConfig.refreshTokenKey);
    await prefs.remove(AppConfig.userIdKey);
    await prefs.remove(AppConfig.userEmailKey);
    await prefs.remove(AppConfig.usernameKey);
  }

  /// 保存用户信息到本地存储
  Future<void> saveUserInfo(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(AppConfig.userIdKey, user.id);
    await prefs.setString(AppConfig.userEmailKey, user.email);
    await prefs.setString(AppConfig.usernameKey, user.username);
  }

  /// 从本地存储获取用户ID
  Future<int?> getUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(AppConfig.userIdKey);
  }

  /// 从本地存储获取用户邮箱
  Future<String?> getUserEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConfig.userEmailKey);
  }

  /// 从本地存储获取用户名
  Future<String?> getUsername() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConfig.usernameKey);
  }
}
