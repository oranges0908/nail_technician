import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../screens/splash/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/customers/customer_list_screen.dart';
import '../screens/customers/customer_detail_screen.dart';
import '../screens/customers/customer_form_screen.dart';
import '../screens/customers/customer_profile_screen.dart';
import '../screens/inspirations/inspiration_list_screen.dart';
import '../screens/inspirations/inspiration_upload_screen.dart';
import '../screens/designs/design_list_screen.dart';
import '../screens/designs/design_generate_screen.dart';
import '../screens/designs/design_detail_screen.dart';
import '../screens/services/service_list_screen.dart';
import '../screens/services/service_create_screen.dart';
import '../screens/services/service_detail_screen.dart';
import '../screens/services/service_complete_screen.dart';
import '../screens/abilities/ability_center_screen.dart';
import '../screens/abilities/ability_trend_screen.dart';
import '../utils/constants.dart';

/// 应用路由配置
/// 使用 go_router 进行路由管理，包含认证守卫
class AppRouter {
  /// 需要在 main 中设置，用于路由守卫获取 AuthProvider
  static AuthProvider? _authProvider;

  static void setAuthProvider(AuthProvider provider) {
    _authProvider = provider;
    _router = _createRouter();
  }

  static GoRouter get router => _router;
  static late GoRouter _router;

  static GoRouter _createRouter() => GoRouter(
    initialLocation: Constants.splashRoute,
    refreshListenable: _authProvider,
    routes: [
      // 启动页
      GoRoute(
        path: Constants.splashRoute,
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),

      // 登录页
      GoRoute(
        path: Constants.loginRoute,
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),

      // 注册页
      GoRoute(
        path: Constants.registerRoute,
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),

      // 主页
      GoRoute(
        path: Constants.homeRoute,
        name: 'home',
        builder: (context, state) => const HomeScreen(),
      ),

      // 客户管理
      GoRoute(
        path: Constants.customersRoute,
        name: 'customers',
        builder: (context, state) => const CustomerListScreen(),
      ),
      GoRoute(
        path: '/customers/new',
        name: 'customer-new',
        builder: (context, state) => const CustomerFormScreen(),
      ),
      GoRoute(
        path: '/customers/:id',
        name: 'customer-detail',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return CustomerDetailScreen(customerId: id);
        },
      ),
      GoRoute(
        path: '/customers/:id/edit',
        name: 'customer-edit',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return CustomerFormScreen(customerId: id);
        },
      ),
      GoRoute(
        path: '/customers/:id/profile',
        name: 'customer-profile',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return CustomerProfileScreen(customerId: id);
        },
      ),

      // 灵感图库
      GoRoute(
        path: Constants.inspirationsRoute,
        name: 'inspirations',
        builder: (context, state) => const InspirationListScreen(),
      ),
      GoRoute(
        path: Constants.inspirationsUploadRoute,
        name: 'inspiration-upload',
        builder: (context, state) => const InspirationUploadScreen(),
      ),

      // 设计方案
      GoRoute(
        path: Constants.designsRoute,
        name: 'designs',
        builder: (context, state) => const DesignListScreen(),
      ),
      GoRoute(
        path: Constants.designGenerateRoute,
        name: 'design-generate',
        builder: (context, state) => const DesignGenerateScreen(),
      ),
      GoRoute(
        path: '/designs/:id',
        name: 'design-detail',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return DesignDetailScreen(designId: id);
        },
      ),

      // 服务记录
      GoRoute(
        path: Constants.servicesRoute,
        name: 'services',
        builder: (context, state) => const ServiceListScreen(),
      ),
      GoRoute(
        path: Constants.serviceNewRoute,
        name: 'service-new',
        builder: (context, state) => const ServiceCreateScreen(),
      ),
      GoRoute(
        path: '/services/:id',
        name: 'service-detail',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return ServiceDetailScreen(serviceId: id);
        },
      ),
      GoRoute(
        path: '/services/:id/complete',
        name: 'service-complete',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return ServiceCompleteScreen(serviceId: id);
        },
      ),

      // 能力中心
      GoRoute(
        path: Constants.abilitiesRoute,
        name: 'abilities',
        builder: (context, state) => const AbilityCenterScreen(),
      ),
      GoRoute(
        path: '/abilities/trend/:dimensionName',
        name: 'ability-trend',
        builder: (context, state) {
          final dimensionName = state.pathParameters['dimensionName']!;
          return AbilityTrendScreen(dimensionName: dimensionName);
        },
      ),
    ],

    // 路由守卫
    redirect: (context, state) {
      final authProvider = _authProvider;
      if (authProvider == null) return null;

      // 初始化未完成时，停留在 splash
      if (!authProvider.initialized) {
        if (state.matchedLocation != Constants.splashRoute) {
          return Constants.splashRoute;
        }
        return null;
      }

      final isLoggedIn = authProvider.isLoggedIn;
      final isAuthRoute = state.matchedLocation == Constants.loginRoute ||
          state.matchedLocation == Constants.registerRoute;
      final isSplash = state.matchedLocation == Constants.splashRoute;

      // splash 页面初始化完成后，根据登录状态跳转
      if (isSplash) {
        return isLoggedIn ? Constants.homeRoute : Constants.loginRoute;
      }

      // 未登录且不在认证页面，跳转到登录页
      if (!isLoggedIn && !isAuthRoute) {
        return Constants.loginRoute;
      }

      // 已登录且在认证页面，跳转到主页
      if (isLoggedIn && isAuthRoute) {
        return Constants.homeRoute;
      }

      return null;
    },

    // 错误页面
    errorBuilder: (context, state) {
      return const SplashScreen();
    },
  );
}
