import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import '../models/conversation.dart';
import '../services/chat_service.dart';

enum ChatStatus { idle, loading, sending, uploading, error }

/// ChatProvider — manages the frontend state of the AI chat assistant
///
/// Responsibilities:
/// - Hold local message list (with optimistic updates)
/// - Manage session ID and current step
/// - Expose UI metadata (quick replies, UI hints)
class ChatProvider extends ChangeNotifier {
  final ChatApiService _api = ChatApiService();

  // ── State ────────────────────────────────────────────────────────────────

  int? _sessionId;
  List<ChatMessage> _messages = [];
  ChatStatus _status = ChatStatus.idle;
  String? _error;
  String _currentStep = 'collect';
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

  // ── Session Management ───────────────────────────────────────────────────

  /// Create a new session and add the opening message
  Future<void> startSession() async {
    _setStatus(ChatStatus.loading);
    _messages = [];
    _sessionId = null;
    _context = {};
    _currentStep = 'collect';
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
      _setError('Failed to create session: $e');
    }
  }

  /// Reset and create a new session
  Future<void> newSession() async {
    _sessionId = null;
    _messages = [];
    await startSession();
  }

  // ── Message Sending ──────────────────────────────────────────────────────

  /// Send a text message (optimistic update)
  Future<void> sendMessage(
    String content, {
    List<String> imagePaths = const [],
  }) async {
    if (_sessionId == null) return;
    if (isSending || isUploading) return;

    // Optimistically insert user message
    final userMsg = ChatMessage(
      role: 'user',
      content: content,
      imagePaths: imagePaths.isNotEmpty ? imagePaths : null,
      timestamp: DateTime.now(),
    );
    _messages.add(userMsg);

    // Insert loading placeholder
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
      // Roll back loading placeholder
      _messages.removeLast();
      _setError('Failed to send message: $e');
    }
  }

  /// Upload an image (multipart)
  Future<void> uploadImage(
    Uint8List bytes,
    String filename, {
    String purpose = 'inspiration',
  }) async {
    if (_sessionId == null) return;
    if (isSending || isUploading) return;

    // Optimistically insert user image message (local bytes preview)
    _messages.add(ChatMessage(
      role: 'user',
      content: '',
      imageBytes: bytes,
      timestamp: DateTime.now(),
    ));

    // Insert loading placeholder
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
      // Roll back loading placeholder and user image message
      _messages.removeWhere((m) => m.isLoading || m.imageBytes != null);
      _setError('Upload failed: $e');
    }
  }

  void clearError() {
    _error = null;
    if (_status == ChatStatus.error) {
      _status = ChatStatus.idle;
    }
    notifyListeners();
  }

  // ── Private ──────────────────────────────────────────────────────────────

  void _applyAssistantReply(AssistantMessage reply) {
    // Remove loading placeholder
    _messages.removeWhere((m) => m.isLoading);

    // Insert real assistant message
    _messages.add(ChatMessage(
      role: 'assistant',
      content: reply.content,
      uiMetadata: reply.uiMetadata,
      timestamp: DateTime.now(),
    ));

    // Update step and context
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
