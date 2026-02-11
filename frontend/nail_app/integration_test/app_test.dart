import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:provider/provider.dart';
import 'package:nail_app/providers/auth_provider.dart';
import 'package:nail_app/providers/customer_provider.dart';
import 'package:nail_app/providers/inspiration_provider.dart';
import 'package:nail_app/providers/design_provider.dart';
import 'package:nail_app/providers/service_provider.dart';
import 'package:nail_app/providers/ability_provider.dart';
import 'package:nail_app/screens/splash/splash_screen.dart';
import 'package:nail_app/screens/auth/login_screen.dart';
import 'package:nail_app/config/theme_config.dart';

/// 集成冒烟测试
/// 验证应用启动和关键页面渲染
///
/// 运行方式（需后端启动或 mock 网络层）：
///   flutter test integration_test/
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  Widget buildApp() {
    final authProvider = AuthProvider();
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authProvider),
        ChangeNotifierProvider(create: (_) => CustomerProvider()),
        ChangeNotifierProvider(create: (_) => InspirationProvider()),
        ChangeNotifierProvider(create: (_) => DesignProvider()),
        ChangeNotifierProvider(create: (_) => ServiceRecordProvider()),
        ChangeNotifierProvider(create: (_) => AbilityProvider()),
      ],
      child: MaterialApp(
        theme: ThemeConfig.lightTheme,
        home: const SplashScreen(),
      ),
    );
  }

  group('App Smoke Tests', () {
    testWidgets('app launches and shows splash screen', (tester) async {
      await tester.pumpWidget(buildApp());

      // 验证 Splash 页面元素
      expect(find.text('Nail'), findsOneWidget);
      expect(find.text('美甲师能力成长系统'), findsOneWidget);
      expect(find.text('正在加载...'), findsOneWidget);
      expect(find.byIcon(Icons.auto_fix_high), findsOneWidget);
    });

    testWidgets('login screen renders correctly', (tester) async {
      final authProvider = AuthProvider();
      await tester.pumpWidget(
        ChangeNotifierProvider<AuthProvider>.value(
          value: authProvider,
          child: const MaterialApp(home: LoginScreen()),
        ),
      );

      // 验证登录页元素
      expect(find.text('Nail'), findsOneWidget);
      expect(find.text('邮箱或用户名'), findsWidgets);
      expect(find.text('密码'), findsWidgets);
      expect(find.text('登录'), findsOneWidget);
      expect(find.text('还没有账号？'), findsOneWidget);
      expect(find.text('立即注册'), findsOneWidget);
    });

    testWidgets('login form validates empty fields', (tester) async {
      final authProvider = AuthProvider();
      await tester.pumpWidget(
        ChangeNotifierProvider<AuthProvider>.value(
          value: authProvider,
          child: const MaterialApp(home: LoginScreen()),
        ),
      );

      // 点击登录按钮不填内容
      await tester.tap(find.text('登录'));
      await tester.pump();

      // 应显示验证错误
      expect(find.text('请输入邮箱或用户名'), findsOneWidget);
    });
  });
}
