import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../config/app_config.dart';
import '../../providers/auth_provider.dart';
import '../../utils/constants.dart';

/// 主页
/// 登录后的主界面，展示功能导航和用户信息
class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(AppConfig.appName),
        automaticallyImplyLeading: false,
        actions: [
          // 用户菜单
          PopupMenuButton<String>(
            icon: const Icon(Icons.account_circle),
            onSelected: (value) async {
              if (value == 'logout') {
                final confirmed = await _showLogoutDialog(context);
                if (confirmed) {
                  await context.read<AuthProvider>().logout();
                  context.go(Constants.loginRoute);
                }
              }
            },
            itemBuilder: (context) {
              final user = context.read<AuthProvider>().user;
              return [
                PopupMenuItem<String>(
                  enabled: false,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        user?.username ?? 'User',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: ThemeConfig.textPrimaryLight,
                        ),
                      ),
                      Text(
                        user?.email ?? '',
                        style: const TextStyle(
                          fontSize: 12,
                          color: ThemeConfig.textSecondaryLight,
                        ),
                      ),
                    ],
                  ),
                ),
                const PopupMenuDivider(),
                PopupMenuItem<String>(
                  value: 'logout',
                  child: Row(
                    children: [
                      const Icon(Icons.logout, size: 20, color: ThemeConfig.errorColor),
                      const SizedBox(width: 8),
                      const Text('Sign Out'),
                    ],
                  ),
                ),
              ];
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 欢迎信息
            Consumer<AuthProvider>(
              builder: (context, auth, _) {
                return Text(
                  'Hello, ${auth.user?.username ?? 'Artist'}',
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                );
              },
            ),
            const SizedBox(height: 4),
            Text(
              AppConfig.appDescription,
              style: TextStyle(
                fontSize: 14,
                color: ThemeConfig.textSecondaryLight,
              ),
            ),
            const SizedBox(height: 24),

            // 功能导航卡片
            Expanded(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 840),
                  child: GridView(
                    gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                      maxCrossAxisExtent: 200,
                      mainAxisSpacing: 16,
                      crossAxisSpacing: 16,
                      childAspectRatio: 1.0,
                    ),
                    children: [
                  _buildFeatureCard(
                    context,
                    icon: Icons.people_outline,
                    title: 'Customers',
                    subtitle: 'Manage profiles',
                    color: ThemeConfig.primaryColor,
                    onTap: () {
                      context.go(Constants.customersRoute);
                    },
                  ),
                  _buildFeatureCard(
                    context,
                    icon: Icons.photo_library_outlined,
                    title: 'Inspirations',
                    subtitle: 'Browse references',
                    color: ThemeConfig.accentColor,
                    onTap: () {
                      context.go(Constants.inspirationsRoute);
                    },
                  ),
                  _buildFeatureCard(
                    context,
                    icon: Icons.brush_outlined,
                    title: 'AI Design',
                    subtitle: 'Generate designs',
                    color: ThemeConfig.infoColor,
                    onTap: () {
                      context.go(Constants.designsRoute);
                    },
                  ),
                  _buildFeatureCard(
                    context,
                    icon: Icons.assignment_outlined,
                    title: 'Services',
                    subtitle: 'View service history',
                    color: ThemeConfig.successColor,
                    onTap: () {
                      context.go(Constants.servicesRoute);
                    },
                  ),
                  _buildFeatureCard(
                    context,
                    icon: Icons.radar_outlined,
                    title: 'Ability Center',
                    subtitle: 'Skill growth analysis',
                    color: ThemeConfig.warningColor,
                    onTap: () {
                      context.go(Constants.abilitiesRoute);
                    },
                  ),
                  _buildFeatureCard(
                    context,
                    icon: Icons.chat_bubble_outline,
                    title: 'AI Assistant',
                    subtitle: 'Chat-driven workflow',
                    color: ThemeConfig.primaryColor,
                    onTap: () {
                      context.push('/chat');
                    },
                  ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建功能导航卡片
  Widget _buildFeatureCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, size: 32, color: color),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 12,
                  color: ThemeConfig.textSecondaryLight,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 显示退出确认对话框
  Future<bool> _showLogoutDialog(BuildContext context) async {
    return await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text(Constants.logoutConfirmTitle),
            content: const Text(Constants.logoutConfirmMessage),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: const Text(Constants.cancelButton),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(true),
                style: TextButton.styleFrom(
                  foregroundColor: ThemeConfig.errorColor,
                ),
                child: const Text(Constants.logoutButton),
              ),
            ],
          ),
        ) ??
        false;
  }
}
