import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/user.dart';
import 'package:nail_app/models/token.dart';
import 'package:nail_app/providers/auth_provider.dart';
import 'package:nail_app/services/auth_service.dart';

/// Fake AuthService for testing
class FakeAuthService extends AuthService {
  bool loginCalled = false;
  bool registerCalled = false;
  bool logoutCalled = false;
  bool saveUserInfoCalled = false;
  int loginCallCount = 0;

  User? userToReturn;
  Token? tokenToReturn;
  bool isLoggedInResult = false;
  Exception? loginError;
  Exception? registerError;

  @override
  Future<Token> login({
    required String emailOrUsername,
    required String password,
  }) async {
    loginCalled = true;
    loginCallCount++;
    if (loginError != null) throw loginError!;
    return tokenToReturn!;
  }

  @override
  Future<User> register({
    required String email,
    required String username,
    required String password,
  }) async {
    registerCalled = true;
    if (registerError != null) throw registerError!;
    return userToReturn!;
  }

  @override
  Future<User?> getCurrentUser() async => userToReturn;

  @override
  Future<bool> isLoggedIn() async => isLoggedInResult;

  @override
  Future<void> logout() async {
    logoutCalled = true;
  }

  @override
  Future<void> saveUserInfo(User user) async {
    saveUserInfoCalled = true;
  }
}

void main() {
  late FakeAuthService fakeService;
  late AuthProvider provider;

  final testUser = User(
    id: 1,
    email: 'test@example.com',
    username: 'testuser',
    isActive: true,
    isSuperuser: false,
    createdAt: DateTime.now(),
  );

  final testToken = Token(
    accessToken: 'test_access_token_12345',
    tokenType: 'bearer',
  );

  setUp(() {
    fakeService = FakeAuthService();
    fakeService.userToReturn = testUser;
    fakeService.tokenToReturn = testToken;
    provider = AuthProvider(authService: fakeService);
  });

  group('AuthProvider', () {
    test('initial state', () {
      expect(provider.isLoggedIn, false);
      expect(provider.isLoading, false);
      expect(provider.user, isNull);
      expect(provider.error, isNull);
      expect(provider.initialized, false);
    });

    test('login success sets user and isLoggedIn', () async {
      final result = await provider.login(
        emailOrUsername: 'test@example.com',
        password: 'password123',
      );

      expect(result, true);
      expect(provider.isLoggedIn, true);
      expect(provider.user, testUser);
      expect(provider.isLoading, false);
      expect(provider.error, isNull);
      expect(fakeService.loginCalled, true);
      expect(fakeService.saveUserInfoCalled, true);
    });

    test('login failure sets error', () async {
      fakeService.loginError = Exception('401 Unauthorized');

      final result = await provider.login(
        emailOrUsername: 'wrong@example.com',
        password: 'wrong',
      );

      expect(result, false);
      expect(provider.isLoggedIn, false);
      expect(provider.error, isNotNull);
      expect(provider.error, contains('密码错误'));
    });

    test('logout clears state', () async {
      // First login
      await provider.login(
        emailOrUsername: 'test@example.com',
        password: 'password123',
      );
      expect(provider.isLoggedIn, true);

      // Then logout
      await provider.logout();

      expect(provider.isLoggedIn, false);
      expect(provider.user, isNull);
      expect(provider.error, isNull);
      expect(fakeService.logoutCalled, true);
    });

    test('clearError clears error', () async {
      fakeService.loginError = Exception('401');
      await provider.login(emailOrUsername: 'test', password: 'test');
      expect(provider.error, isNotNull);

      provider.clearError();
      expect(provider.error, isNull);
    });

    test('register success calls login', () async {
      final result = await provider.register(
        email: 'new@example.com',
        username: 'newuser',
        password: 'password123',
      );

      expect(result, true);
      expect(provider.isLoggedIn, true);
      expect(fakeService.registerCalled, true);
      expect(fakeService.loginCalled, true);
    });

    test('register failure sets error', () async {
      fakeService.registerError = Exception('409 already exists');

      final result = await provider.register(
        email: 'existing@example.com',
        username: 'existing',
        password: 'password123',
      );

      expect(result, false);
      expect(provider.error, contains('已被注册'));
    });
  });
}
