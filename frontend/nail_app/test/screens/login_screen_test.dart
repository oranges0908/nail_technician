import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:nail_app/screens/auth/login_screen.dart';
import 'package:nail_app/providers/auth_provider.dart';
import 'package:nail_app/services/auth_service.dart';
import 'package:nail_app/models/user.dart';
import 'package:nail_app/models/token.dart';
import 'package:nail_app/utils/constants.dart';

class FakeAuthService extends AuthService {
  User? userToReturn;
  Token? tokenToReturn;
  bool isLoggedInResult = false;
  Exception? loginError;

  @override
  Future<Token> login({
    required String emailOrUsername,
    required String password,
  }) async {
    if (loginError != null) throw loginError!;
    return tokenToReturn!;
  }

  @override
  Future<User?> getCurrentUser() async => userToReturn;

  @override
  Future<bool> isLoggedIn() async => isLoggedInResult;

  @override
  Future<void> logout() async {}

  @override
  Future<void> saveUserInfo(User user) async {}

  @override
  Future<User> register({
    required String email,
    required String username,
    required String password,
  }) async {
    throw UnimplementedError();
  }
}

void main() {
  late FakeAuthService fakeService;
  late AuthProvider authProvider;

  setUp(() {
    fakeService = FakeAuthService();
    authProvider = AuthProvider(authService: fakeService);
  });

  Widget buildWidget() {
    return ChangeNotifierProvider<AuthProvider>.value(
      value: authProvider,
      child: const MaterialApp(home: LoginScreen()),
    );
  }

  group('LoginScreen', () {
    testWidgets('renders app title and form fields', (tester) async {
      await tester.pumpWidget(buildWidget());

      expect(find.text('Nail'), findsOneWidget);
      expect(find.text('美甲师能力成长系统'), findsOneWidget);
      expect(find.text('邮箱或用户名'), findsWidgets);
      expect(find.text('密码'), findsWidgets);
      expect(find.text('登录'), findsOneWidget);
      expect(find.text('还没有账号？'), findsOneWidget);
      expect(find.text('立即注册'), findsOneWidget);
    });

    testWidgets('shows validation errors on empty submit', (tester) async {
      await tester.pumpWidget(buildWidget());

      await tester.tap(find.text('登录'));
      await tester.pump();

      expect(find.text(Constants.emptyEmailError), findsOneWidget);
      // Password error text matches hint text, so finds 2 (hint + error)
      expect(find.text(Constants.emptyPasswordError), findsWidgets);
    });

    testWidgets('shows short password error', (tester) async {
      await tester.pumpWidget(buildWidget());

      final fields = find.byType(TextFormField);
      await tester.enterText(fields.at(0), 'test@test.com');
      await tester.enterText(fields.at(1), '123');

      await tester.tap(find.text('登录'));
      await tester.pump();

      expect(find.text(Constants.shortPasswordError), findsOneWidget);
    });

    testWidgets('shows error banner when login fails', (tester) async {
      fakeService.loginError = Exception('401 Unauthorized');

      await tester.pumpWidget(buildWidget());

      final fields = find.byType(TextFormField);
      await tester.enterText(fields.at(0), 'test@test.com');
      await tester.enterText(fields.at(1), 'password123');

      await tester.tap(find.text('登录'));
      await tester.pumpAndSettle();

      expect(find.text('用户名或密码错误'), findsOneWidget);
      expect(find.byIcon(Icons.error_outline), findsOneWidget);
    });

    testWidgets('remember me checkbox toggles', (tester) async {
      await tester.pumpWidget(buildWidget());

      final checkbox = find.byType(Checkbox);
      expect(checkbox, findsOneWidget);

      // Initially unchecked
      expect(
        tester.widget<Checkbox>(checkbox).value,
        false,
      );

      // Tap the checkbox directly (not the text label)
      await tester.tap(checkbox);
      await tester.pump();

      expect(
        tester.widget<Checkbox>(checkbox).value,
        true,
      );
    });
  });
}
