import 'dart:typed_data';
import 'package:dio/dio.dart';
import '../config/api_config.dart';
import 'api_service.dart';

/// 文件上传响应
class UploadResponse {
  final String filename;
  final String filePath;
  final String fileUrl;
  final int fileSize;
  final String contentType;

  UploadResponse({
    required this.filename,
    required this.filePath,
    required this.fileUrl,
    required this.fileSize,
    required this.contentType,
  });

  factory UploadResponse.fromJson(Map<String, dynamic> json) {
    return UploadResponse(
      filename: json['filename'] as String,
      filePath: json['file_path'] as String,
      fileUrl: json['file_url'] as String,
      fileSize: json['file_size'] as int,
      contentType: json['content_type'] as String,
    );
  }
}

/// 文件上传服务
class UploadService {
  final ApiService _apiService = ApiService();

  /// 上传图片
  /// [filePath] 本地文件路径
  /// [category] 分类: nails, inspirations, designs, actuals
  Future<UploadResponse> uploadImage(
    String filePath,
    String category, {
    ProgressCallback? onProgress,
  }) async {
    String endpoint;
    switch (category) {
      case 'nails':
        endpoint = ApiConfig.uploadNailsEndpoint;
        break;
      case 'inspirations':
        endpoint = ApiConfig.uploadInspirationsEndpoint;
        break;
      case 'designs':
        endpoint = ApiConfig.uploadDesignsEndpoint;
        break;
      case 'actuals':
        endpoint = ApiConfig.uploadActualsEndpoint;
        break;
      default:
        throw ArgumentError('Invalid category: $category');
    }

    final response = await _apiService.upload(
      endpoint,
      filePath,
      onSendProgress: onProgress,
    );
    return UploadResponse.fromJson(response.data);
  }

  /// 上传图片（基于字节数据，兼容 Web 平台）
  /// [bytes] 图片字节数据
  /// [filename] 文件名
  /// [category] 分类: nails, inspirations, designs, actuals
  Future<UploadResponse> uploadImageBytes(
    Uint8List bytes,
    String filename,
    String category, {
    ProgressCallback? onProgress,
  }) async {
    String endpoint;
    switch (category) {
      case 'nails':
        endpoint = ApiConfig.uploadNailsEndpoint;
        break;
      case 'inspirations':
        endpoint = ApiConfig.uploadInspirationsEndpoint;
        break;
      case 'designs':
        endpoint = ApiConfig.uploadDesignsEndpoint;
        break;
      case 'actuals':
        endpoint = ApiConfig.uploadActualsEndpoint;
        break;
      default:
        throw ArgumentError('Invalid category: $category');
    }

    final response = await _apiService.uploadBytes(
      endpoint,
      bytes,
      filename,
      onSendProgress: onProgress,
    );
    return UploadResponse.fromJson(response.data);
  }
}
