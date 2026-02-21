import 'dart:typed_data';
import 'package:json_annotation/json_annotation.dart';

part 'conversation.g.dart';

/// UI 渲染元数据（由后端 LLM 决策）
@JsonSerializable()
class UiMetadata {
  @JsonKey(name: 'quick_replies')
  final List<String> quickReplies;

  @JsonKey(name: 'ui_hint')
  final String uiHint;

  @JsonKey(name: 'ui_data')
  final Map<String, dynamic>? uiData;

  @JsonKey(name: 'needs_image_upload')
  final bool needsImageUpload;

  const UiMetadata({
    this.quickReplies = const [],
    this.uiHint = 'none',
    this.uiData,
    this.needsImageUpload = false,
  });

  factory UiMetadata.fromJson(Map<String, dynamic> json) =>
      _$UiMetadataFromJson(json);
  Map<String, dynamic> toJson() => _$UiMetadataToJson(this);

  static UiMetadata empty() => const UiMetadata();
}

/// 服务端返回的助理消息
@JsonSerializable()
class AssistantMessage {
  final String content;

  @JsonKey(name: 'ui_metadata')
  final UiMetadata uiMetadata;

  @JsonKey(name: 'step_complete')
  final bool stepComplete;

  @JsonKey(name: 'current_step')
  final String currentStep;

  final Map<String, dynamic> context;

  const AssistantMessage({
    required this.content,
    required this.uiMetadata,
    this.stepComplete = false,
    this.currentStep = 'greeting',
    this.context = const {},
  });

  factory AssistantMessage.fromJson(Map<String, dynamic> json) =>
      _$AssistantMessageFromJson(json);
  Map<String, dynamic> toJson() => _$AssistantMessageToJson(this);
}

/// 前端本地消息对象（用户消息 + 助理消息统一列表）
class ChatMessage {
  final String role; // "user" | "assistant"
  final String content;
  final UiMetadata? uiMetadata;
  final List<String>? imagePaths; // 服务器端图片路径（用于 Image.network）
  final Uint8List? imageBytes;   // 本地图片字节（上传前预览，用于 Image.memory）
  final bool isLoading; // 发送中占位符
  final DateTime timestamp;

  const ChatMessage({
    required this.role,
    required this.content,
    this.uiMetadata,
    this.imagePaths,
    this.imageBytes,
    this.isLoading = false,
    required this.timestamp,
  });

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';

  ChatMessage copyWith({
    String? role,
    String? content,
    UiMetadata? uiMetadata,
    List<String>? imagePaths,
    Uint8List? imageBytes,
    bool? isLoading,
    DateTime? timestamp,
  }) {
    return ChatMessage(
      role: role ?? this.role,
      content: content ?? this.content,
      uiMetadata: uiMetadata ?? this.uiMetadata,
      imagePaths: imagePaths ?? this.imagePaths,
      imageBytes: imageBytes ?? this.imageBytes,
      isLoading: isLoading ?? this.isLoading,
      timestamp: timestamp ?? this.timestamp,
    );
  }
}

/// 会话对象（服务端）
@JsonSerializable()
class ConversationSession {
  final int id;

  @JsonKey(name: 'user_id')
  final int userId;

  final String status;

  @JsonKey(name: 'current_step')
  final String currentStep;

  final Map<String, dynamic> context;

  @JsonKey(name: 'step_summaries')
  final List<Map<String, dynamic>> stepSummaries;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  const ConversationSession({
    required this.id,
    required this.userId,
    required this.status,
    required this.currentStep,
    required this.context,
    required this.stepSummaries,
    required this.createdAt,
    required this.updatedAt,
  });

  bool get isActive => status == 'active';

  factory ConversationSession.fromJson(Map<String, dynamic> json) =>
      _$ConversationSessionFromJson(json);
  Map<String, dynamic> toJson() => _$ConversationSessionToJson(this);
}

/// 创建会话响应
@JsonSerializable()
class StartSessionResponse {
  @JsonKey(name: 'session_id')
  final int sessionId;

  final String status;

  @JsonKey(name: 'current_step')
  final String currentStep;

  final Map<String, dynamic> context;

  @JsonKey(name: 'opening_message')
  final AssistantMessage openingMessage;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  const StartSessionResponse({
    required this.sessionId,
    required this.status,
    required this.currentStep,
    required this.context,
    required this.openingMessage,
    required this.createdAt,
  });

  factory StartSessionResponse.fromJson(Map<String, dynamic> json) =>
      _$StartSessionResponseFromJson(json);
  Map<String, dynamic> toJson() => _$StartSessionResponseToJson(this);
}

/// 发送消息响应
@JsonSerializable()
class SendMessageResponse {
  final AssistantMessage message;

  @JsonKey(name: 'session_id')
  final int sessionId;

  const SendMessageResponse({
    required this.message,
    required this.sessionId,
  });

  factory SendMessageResponse.fromJson(Map<String, dynamic> json) =>
      _$SendMessageResponseFromJson(json);
  Map<String, dynamic> toJson() => _$SendMessageResponseToJson(this);
}

/// 会话列表响应
@JsonSerializable()
class SessionListResponse {
  final int total;
  final List<ConversationSession> sessions;

  const SessionListResponse({
    required this.total,
    required this.sessions,
  });

  factory SessionListResponse.fromJson(Map<String, dynamic> json) =>
      _$SessionListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$SessionListResponseToJson(this);
}
