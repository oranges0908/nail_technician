// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conversation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UiMetadata _$UiMetadataFromJson(Map<String, dynamic> json) => UiMetadata(
      quickReplies: (json['quick_replies'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      uiHint: json['ui_hint'] as String? ?? 'none',
      uiData: (json['ui_data'] as Map<String, dynamic>?),
      needsImageUpload: json['needs_image_upload'] as bool? ?? false,
    );

Map<String, dynamic> _$UiMetadataToJson(UiMetadata instance) =>
    <String, dynamic>{
      'quick_replies': instance.quickReplies,
      'ui_hint': instance.uiHint,
      'ui_data': instance.uiData,
      'needs_image_upload': instance.needsImageUpload,
    };

AssistantMessage _$AssistantMessageFromJson(Map<String, dynamic> json) =>
    AssistantMessage(
      content: json['content'] as String,
      uiMetadata: UiMetadata.fromJson(
          json['ui_metadata'] as Map<String, dynamic>),
      stepComplete: json['step_complete'] as bool? ?? false,
      currentStep: json['current_step'] as String? ?? 'greeting',
      context: (json['context'] as Map<String, dynamic>?) ?? const {},
    );

Map<String, dynamic> _$AssistantMessageToJson(AssistantMessage instance) =>
    <String, dynamic>{
      'content': instance.content,
      'ui_metadata': instance.uiMetadata.toJson(),
      'step_complete': instance.stepComplete,
      'current_step': instance.currentStep,
      'context': instance.context,
    };

ConversationSession _$ConversationSessionFromJson(Map<String, dynamic> json) =>
    ConversationSession(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      status: json['status'] as String,
      currentStep: json['current_step'] as String,
      context: (json['context'] as Map<String, dynamic>?) ?? const {},
      stepSummaries: (json['step_summaries'] as List<dynamic>?)
              ?.map((e) => (e as Map<String, dynamic>))
              .toList() ??
          const [],
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$ConversationSessionToJson(
        ConversationSession instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'status': instance.status,
      'current_step': instance.currentStep,
      'context': instance.context,
      'step_summaries': instance.stepSummaries,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };

StartSessionResponse _$StartSessionResponseFromJson(
        Map<String, dynamic> json) =>
    StartSessionResponse(
      sessionId: json['session_id'] as int,
      status: json['status'] as String,
      currentStep: json['current_step'] as String,
      context: (json['context'] as Map<String, dynamic>?) ?? const {},
      openingMessage: AssistantMessage.fromJson(
          json['opening_message'] as Map<String, dynamic>),
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$StartSessionResponseToJson(
        StartSessionResponse instance) =>
    <String, dynamic>{
      'session_id': instance.sessionId,
      'status': instance.status,
      'current_step': instance.currentStep,
      'context': instance.context,
      'opening_message': instance.openingMessage.toJson(),
      'created_at': instance.createdAt.toIso8601String(),
    };

SendMessageResponse _$SendMessageResponseFromJson(
        Map<String, dynamic> json) =>
    SendMessageResponse(
      message:
          AssistantMessage.fromJson(json['message'] as Map<String, dynamic>),
      sessionId: json['session_id'] as int,
    );

Map<String, dynamic> _$SendMessageResponseToJson(
        SendMessageResponse instance) =>
    <String, dynamic>{
      'message': instance.message.toJson(),
      'session_id': instance.sessionId,
    };

SessionListResponse _$SessionListResponseFromJson(
        Map<String, dynamic> json) =>
    SessionListResponse(
      total: json['total'] as int,
      sessions: (json['sessions'] as List<dynamic>)
          .map((e) =>
              ConversationSession.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$SessionListResponseToJson(
        SessionListResponse instance) =>
    <String, dynamic>{
      'total': instance.total,
      'sessions': instance.sessions.map((e) => e.toJson()).toList(),
    };
