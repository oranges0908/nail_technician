import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'config/theme_config.dart';
import 'config/app_config.dart';
import 'providers/auth_provider.dart';
import 'providers/customer_provider.dart';
import 'providers/inspiration_provider.dart';
import 'providers/design_provider.dart';
import 'providers/service_provider.dart';
import 'providers/ability_provider.dart';
import 'routes/app_router.dart';

void main() async {
  // 确保 Flutter 绑定已初始化
  WidgetsFlutterBinding.ensureInitialized();

  // 设置状态栏样式
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
    ),
  );

  // 设置屏幕方向（仅竖屏）
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // 创建 AuthProvider 并注册到路由
  final authProvider = AuthProvider();
  AppRouter.setAuthProvider(authProvider);

  runApp(MyApp(authProvider: authProvider));
}

class MyApp extends StatelessWidget {
  final AuthProvider authProvider;

  const MyApp({Key? key, required this.authProvider}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authProvider),
        ChangeNotifierProvider(create: (_) => CustomerProvider()),
        ChangeNotifierProvider(create: (_) => InspirationProvider()),
        ChangeNotifierProvider(create: (_) => DesignProvider()),
        ChangeNotifierProvider(create: (_) => ServiceRecordProvider()),
        ChangeNotifierProvider(create: (_) => AbilityProvider()),
      ],
      child: MaterialApp.router(
        // 应用标题
        title: AppConfig.appName,

        // 主题配置
        theme: ThemeConfig.lightTheme,
        darkTheme: ThemeConfig.darkTheme,
        themeMode: ThemeMode.light,

        // 路由配置
        routeInformationProvider: AppRouter.router.routeInformationProvider,
        routeInformationParser: AppRouter.router.routeInformationParser,
        routerDelegate: AppRouter.router.routerDelegate,

        // 调试横幅（生产环境关闭）
        debugShowCheckedModeBanner: !AppConfig.isProduction,

        // 本地化配置
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('zh', 'CN'),
          Locale('en', 'US'),
        ],
        locale: const Locale('zh', 'CN'),

        // 性能优化
        builder: (context, child) {
          return MediaQuery(
            // 禁用系统字体缩放
            data: MediaQuery.of(context).copyWith(textScaleFactor: 1.0),
            child: child!,
          );
        },
      ),
    );
  }
}
