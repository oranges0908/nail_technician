import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

/// 认证状态管理
/// 管理用户登录状态、用户信息、加载状态和错误信息
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

  // ==================== 初始化 ====================

  /// 检查本地存储的登录状态，恢复会话
  Future<void> initialize() async {
    if (_initialized) return;

    _isLoading = true;
    notifyListeners();

    try {
      final loggedIn = await _authService.isLoggedIn();
      if (loggedIn) {
        // 尝试获取用户信息验证 token 是否有效
        final user = await _authService.getCurrentUser();
        if (user != null) {
          _user = user;
          _isLoggedIn = true;
        } else {
          // Token 无效，清除本地数据
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

  // ==================== 登录 ====================

  /// 用户登录
  ///
  /// 参数:
  /// - emailOrUsername: 邮箱或用户名
  /// - password: 密码
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

      // 获取用户信息
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

  // ==================== 注册 ====================

  /// 用户注册
  ///
  /// 参数:
  /// - email: 邮箱
  /// - username: 用户名
  /// - password: 密码
  Future<bool> register({
    required String email,
    required String username,
    required String password,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.register(
        email: email,
        username: username,
        password: password,
      );

      // 注册成功后自动登录
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

  // ==================== 登出 ====================

  /// 用户登出
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _authService.logout();
    } catch (e) {
      // 忽略登出 API 错误
    } finally {
      _user = null;
      _isLoggedIn = false;
      _isLoading = false;
      _error = null;
      notifyListeners();
    }
  }

  // ==================== 辅助方法 ====================

  /// 清除错误信息
  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// 解析错误信息
  String _parseError(dynamic error) {
    if (error.toString().contains('401')) {
      return '用户名或密码错误';
    } else if (error.toString().contains('409') ||
        error.toString().contains('already')) {
      return '该邮箱或用户名已被注册';
    } else if (error.toString().contains('422')) {
      return '输入信息格式不正确';
    } else if (error.toString().contains('SocketException') ||
        error.toString().contains('Connection')) {
      return '网络连接失败，请检查网络设置';
    } else if (error.toString().contains('timeout')) {
      return '请求超时，请重试';
    }
    return '操作失败，请重试';
  }
}
