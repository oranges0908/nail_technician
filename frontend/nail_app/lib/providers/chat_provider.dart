import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import '../models/conversation.dart';
import '../services/chat_service.dart';

enum ChatStatus { idle, loading, sending, uploading, error }

/// ChatProvider — 管理 AI 对话助理的前端状态
///
/// 职责：
/// - 持有本地消息列表（含乐观更新）
/// - 管理会话 ID 和当前步骤
/// - 暴露 UI 元数据（快捷回复、UI 提示）
class ChatProvider extends ChangeNotifier {
  final ChatApiService _api = ChatApiService();

  // ── 状态 ────────────────────────────────────────────────────────────────

  int? _sessionId;
  List<ChatMessage> _messages = [];
  ChatStatus _status = ChatStatus.idle;
  String? _error;
  String _currentStep = 'greeting';
  Map<String, dynamic> _context = {};
  UiMetadata _currentUiMetadata = UiMetadata.empty();

  // ── Getters ──────────────────────────────────────────────────────────────

  int? get sessionId => _sessionId;
  List<ChatMessage> get messages => List.unmodifiable(_messages);
  ChatStatus get status => _status;
  String? get error => _error;
  String get currentStep => _currentStep;
  Map<String, dynamic> get context => Map.unmodifiable(_context);

  bool get isSending => _status == ChatStatus.sending;
  bool get isUploading => _status == ChatStatus.uploading;
  bool get isLoading => _status == ChatStatus.loading;
  bool get isSessionActive => _sessionId != null;

  List<String> get quickReplies => _currentUiMetadata.quickReplies;
  String get uiHint => _currentUiMetadata.uiHint;
  Map<String, dynamic>? get uiData => _currentUiMetadata.uiData;
  bool get needsImageUpload => _currentUiMetadata.needsImageUpload;

  // ── 会话管理 ─────────────────────────────────────────────────────────────

  /// 创建新会话，加入开场消息
  Future<void> startSession() async {
    _setStatus(ChatStatus.loading);
    _messages = [];
    _sessionId = null;
    _context = {};
    _currentStep = 'greeting';
    _currentUiMetadata = UiMetadata.empty();

    try {
      final resp = await _api.startSession();
      _sessionId = resp.sessionId;
      _currentStep = resp.currentStep;
      _context = Map.from(resp.context);

      final openingMsg = resp.openingMessage;
      _currentUiMetadata = openingMsg.uiMetadata;

      _messages.add(ChatMessage(
        role: 'assistant',
        content: openingMsg.content,
        uiMetadata: openingMsg.uiMetadata,
        timestamp: DateTime.now(),
      ));

      _setStatus(ChatStatus.idle);
    } catch (e) {
      _setError('创建会话失败: $e');
    }
  }

  /// 重置并重新创建会话
  Future<void> newSession() async {
    _sessionId = null;
    _messages = [];
    await startSession();
  }

  // ── 消息发送 ─────────────────────────────────────────────────────────────

  /// 发送文本消息（乐观更新）
  Future<void> sendMessage(
    String content, {
    List<String> imagePaths = const [],
  }) async {
    if (_sessionId == null) return;
    if (isSending || isUploading) return;

    // 乐观插入用户消息
    final userMsg = ChatMessage(
      role: 'user',
      content: content,
      imagePaths: imagePaths.isNotEmpty ? imagePaths : null,
      timestamp: DateTime.now(),
    );
    _messages.add(userMsg);

    // 插入 loading 占位符
    final loadingMsg = ChatMessage(
      role: 'assistant',
      content: '',
      isLoading: true,
      timestamp: DateTime.now(),
    );
    _messages.add(loadingMsg);

    _setStatus(ChatStatus.sending);

    try {
      final resp = await _api.sendMessage(
        _sessionId!,
        content,
        imagePaths: imagePaths,
      );
      _applyAssistantReply(resp.message);
      _setStatus(ChatStatus.idle);
    } catch (e) {
      // 回滚 loading 占位符
      _messages.removeLast();
      _setError('发送失败: $e');
    }
  }

  /// 上传图片（multipart）
  Future<void> uploadImage(
    Uint8List bytes,
    String filename, {
    String purpose = 'inspiration',
  }) async {
    if (_sessionId == null) return;
    if (isSending || isUploading) return;

    // 乐观插入用户图片消息（本地字节预览）
    _messages.add(ChatMessage(
      role: 'user',
      content: '',
      imageBytes: bytes,
      timestamp: DateTime.now(),
    ));

    // 插入 loading 占位符
    final loadingMsg = ChatMessage(
      role: 'assistant',
      content: '',
      isLoading: true,
      timestamp: DateTime.now(),
    );
    _messages.add(loadingMsg);

    _setStatus(ChatStatus.uploading);

    try {
      final resp = await _api.uploadImage(
        _sessionId!,
        bytes,
        filename,
        purpose: purpose,
      );
      _applyAssistantReply(resp.message);
      _setStatus(ChatStatus.idle);
    } catch (e) {
      // 回滚 loading 占位符和用户图片消息
      _messages.removeWhere((m) => m.isLoading || m.imageBytes != null);
      _setError('上传失败: $e');
    }
  }

  void clearError() {
    _error = null;
    if (_status == ChatStatus.error) {
      _status = ChatStatus.idle;
    }
    notifyListeners();
  }

  // ── 私有 ─────────────────────────────────────────────────────────────────

  void _applyAssistantReply(AssistantMessage reply) {
    // 移除 loading 占位符
    _messages.removeWhere((m) => m.isLoading);

    // 插入真实助理消息
    _messages.add(ChatMessage(
      role: 'assistant',
      content: reply.content,
      uiMetadata: reply.uiMetadata,
      timestamp: DateTime.now(),
    ));

    // 更新步骤和上下文
    _currentStep = reply.currentStep;
    _context = Map.from(reply.context);
    _currentUiMetadata = reply.uiMetadata;
  }

  void _setStatus(ChatStatus s) {
    _status = s;
    if (s != ChatStatus.error) _error = null;
    notifyListeners();
  }

  void _setError(String msg) {
    _error = msg;
    _status = ChatStatus.error;
    notifyListeners();
  }
}
