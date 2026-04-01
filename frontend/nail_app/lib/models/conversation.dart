import 'dart:typed_data';
import 'package:json_annotation/json_annotation.dart';

part 'conversation.g.dart';

/// UI rendering metadata (determined by backend LLM)
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

/// Assistant message returned from the server
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

/// Local frontend chat message object (unified list of user and assistant messages)
class ChatMessage {
  final String role; // "user" | "assistant"
  final String content;
  final UiMetadata? uiMetadata;
  final List<String>? imagePaths; // Server-side image paths (for Image.network)
  final Uint8List? imageBytes;   // Local image bytes (preview before upload, for Image.memory)
  final bool isLoading; // Sending placeholder
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

/// Conversation session object (server-side)
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

/// Create session response
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

/// Send message response
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

/// Session list response
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
