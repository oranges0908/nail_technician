import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';
import '../config/api_config.dart';
import '../models/conversation.dart';
import 'api_service.dart';

/// AI 对话助理 API 客户端
class ChatApiService {
  final Dio _dio = ApiService().dio;

  // ── 会话管理 ──────────────────────────────────────────────────────────

  /// 创建新会话
  Future<StartSessionResponse> startSession() async {
    final response = await _dio.post(ApiConfig.conversationsEndpoint);
    return StartSessionResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// 获取会话详情
  Future<ConversationSession> getSession(int sessionId) async {
    final response = await _dio.get(
      ApiConfig.conversationDetailEndpoint(sessionId),
    );
    return ConversationSession.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// 列出历史会话
  Future<SessionListResponse> listSessions({
    int skip = 0,
    int limit = 20,
  }) async {
    final response = await _dio.get(
      ApiConfig.conversationsEndpoint,
      queryParameters: {'skip': skip, 'limit': limit},
    );
    return SessionListResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// 放弃会话
  Future<void> abandonSession(int sessionId) async {
    await _dio.delete(ApiConfig.conversationDetailEndpoint(sessionId));
  }

  // ── 消息交互 ──────────────────────────────────────────────────────────

  /// 发送文本消息，返回助理回复
  Future<SendMessageResponse> sendMessage(
    int sessionId,
    String content, {
    List<String> imagePaths = const [],
  }) async {
    final response = await _dio.post(
      ApiConfig.conversationMessagesEndpoint(sessionId),
      data: {
        'content': content,
        'image_paths': imagePaths,
      },
    );
    return SendMessageResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// 会话内上传图片（multipart），返回助理回复
  Future<SendMessageResponse> uploadImage(
    int sessionId,
    Uint8List bytes,
    String filename, {
    String purpose = 'inspiration',
  }) async {
    final formData = FormData.fromMap({
      'file': MultipartFile.fromBytes(
        bytes,
        filename: filename,
        contentType: MediaType('image', _inferSubtype(filename)),
      ),
      'purpose': purpose,
    });

    final response = await _dio.post(
      ApiConfig.conversationImagesEndpoint(sessionId),
      data: formData,
      queryParameters: {'purpose': purpose},
      options: Options(
        contentType: 'multipart/form-data',
        receiveTimeout: 120000,
      ),
    );
    return SendMessageResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  String _inferSubtype(String filename) {
    final ext = filename.split('.').last.toLowerCase();
    switch (ext) {
      case 'jpg':
      case 'jpeg':
        return 'jpeg';
      case 'png':
        return 'png';
      case 'webp':
        return 'webp';
      default:
        return 'jpeg';
    }
  }
}
