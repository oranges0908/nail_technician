import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../config/app_config.dart';
import '../../providers/auth_provider.dart';

/// 启动页
/// 显示应用 Logo 和加载动画，同时初始化认证状态
class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initialize();
  }

  /// 初始化应用
  /// 检查登录状态，完成后路由守卫自动导航
  Future<void> _initialize() async {
    // 显示 splash 最少 1.5 秒
    await Future.wait([
      context.read<AuthProvider>().initialize(),
      Future.delayed(const Duration(milliseconds: 1500)),
    ]);
    // 初始化完成后，GoRouter 的 redirect 会自动处理导航
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ThemeConfig.primaryColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo 图标
            const Icon(
              Icons.auto_fix_high,
              size: 120,
              color: Colors.white,
            ),
            const SizedBox(height: 24),

            // 应用名称
            const Text(
              AppConfig.appName,
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 8),

            // 应用描述
            Text(
              AppConfig.appDescription,
              style: TextStyle(
                fontSize: 16,
                color: Colors.white.withOpacity(0.9),
              ),
            ),
            const SizedBox(height: 48),

            // 加载动画
            const SpinKitWave(
              color: Colors.white,
              size: 40,
            ),
            const SizedBox(height: 16),

            // 加载文字
            Text(
              '正在加载...',
              style: TextStyle(
                fontSize: 14,
                color: Colors.white.withOpacity(0.8),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
