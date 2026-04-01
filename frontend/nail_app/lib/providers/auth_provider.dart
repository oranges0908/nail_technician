import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

/// Authentication state management
/// Manages user login state, user info, loading state, and error messages
class AuthProvider extends ChangeNotifier {
  final AuthService _authService;

  AuthProvider({AuthService? authService})
      : _authService = authService ?? AuthService();

  User? _user;
  bool _isLoggedIn = false;
  bool _isLoading = false;
  String? _error;
  bool _initialized = false;

  // ==================== Getters ====================

  User? get user => _user;
  bool get isLoggedIn => _isLoggedIn;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get initialized => _initialized;

  // ==================== Initialization ====================

  /// Check local storage for login state and restore session
  Future<void> initialize() async {
    if (_initialized) return;

    _isLoading = true;
    notifyListeners();

    try {
      final loggedIn = await _authService.isLoggedIn();
      if (loggedIn) {
        // Attempt to fetch user info to verify token is still valid
        final user = await _authService.getCurrentUser();
        if (user != null) {
          _user = user;
          _isLoggedIn = true;
        } else {
          // Token invalid — clear local data
          await _authService.logout();
          _isLoggedIn = false;
        }
      }
    } catch (e) {
      _isLoggedIn = false;
    } finally {
      _isLoading = false;
      _initialized = true;
      notifyListeners();
    }
  }

  // ==================== Login ====================

  /// User login
  ///
  /// Parameters:
  /// - emailOrUsername: email address or username
  /// - password: password
  Future<bool> login({
    required String emailOrUsername,
    required String password,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.login(
        emailOrUsername: emailOrUsername,
        password: password,
      );

      // Fetch user info
      final user = await _authService.getCurrentUser();
      if (user != null) {
        _user = user;
        _isLoggedIn = true;
        await _authService.saveUserInfo(user);
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _error = _parseError(e);
      notifyListeners();
      return false;
    }
  }

  // ==================== Register ====================

  /// User registration
  ///
  /// Parameters:
  /// - email: email address
  /// - username: username
  /// - password: password
  /// - inviteCode: invitation code
  Future<bool> register({
    required String email,
    required String username,
    required String password,
    required String inviteCode,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.register(
        email: email,
        username: username,
        password: password,
        inviteCode: inviteCode,
      );

      // Auto-login after successful registration
      return await login(
        emailOrUsername: email,
        password: password,
      );
    } catch (e) {
      _isLoading = false;
      _error = _parseError(e);
      notifyListeners();
      return false;
    }
  }

  // ==================== Logout ====================

  /// User logout
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _authService.logout();
    } catch (e) {
      // Ignore logout API errors
    } finally {
      _user = null;
      _isLoggedIn = false;
      _isLoading = false;
      _error = null;
      notifyListeners();
    }
  }

  // ==================== Helper Methods ====================

  /// Clear error message
  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// Parse error message
  String _parseError(dynamic error) {
    if (error.toString().contains('401')) {
      return 'Incorrect username or password';
    } else if (error.toString().contains('409') ||
        error.toString().contains('already')) {
      return 'This email or username is already registered';
    } else if (error.toString().contains('invite code error') ||
        (error.toString().contains('400') &&
            error.toString().contains('invite'))) {
      return 'Invalid invitation code, please verify and retry';
    } else if (error.toString().contains('422')) {
      return 'Invalid input format';
    } else if (error.toString().contains('SocketException') ||
        error.toString().contains('Connection')) {
      return 'Network connection failed, please check your network settings';
    } else if (error.toString().contains('timeout')) {
      return 'Request timed out, please retry';
    }
    return 'Operation failed, please retry';
  }
}
