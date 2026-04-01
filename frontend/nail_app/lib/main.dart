import 'package:flutter/foundation.dart';
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
import 'providers/chat_provider.dart';
import 'routes/app_router.dart';

void main() async {
  // Ensure Flutter binding is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Set status bar style and screen orientation (native platforms only, has no effect on Web)
  if (!kIsWeb) {
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
      ),
    );

    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
  }

  // Create AuthProvider and register it with the router
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
        ChangeNotifierProvider(create: (_) => ChatProvider()),
      ],
      child: MaterialApp.router(
        // App title
        title: AppConfig.appName,

        // Theme settings
        theme: ThemeConfig.lightTheme,
        darkTheme: ThemeConfig.darkTheme,
        themeMode: ThemeMode.light,

        // Router settings
        routerConfig: AppRouter.router,

        // Debug banner (disabled in production)
        debugShowCheckedModeBanner: !AppConfig.isProduction,

        // Localization settings
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

        // Performance optimization
        builder: (context, child) {
          return MediaQuery(
            // Disable system font scaling
            data: MediaQuery.of(context).copyWith(textScaler: TextScaler.noScaling),
            child: child!,
          );
        },
      ),
    );
  }
}
