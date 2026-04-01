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
import '../screens/chat/chat_screen.dart';
import '../utils/constants.dart';

/// Application router configuration
/// Uses go_router for navigation, including authentication guards
class AppRouter {
  /// Must be set in main() so the route guard can access AuthProvider
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
      // Splash screen
      GoRoute(
        path: Constants.splashRoute,
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),

      // Login screen
      GoRoute(
        path: Constants.loginRoute,
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),

      // Register screen
      GoRoute(
        path: Constants.registerRoute,
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),

      // Home screen
      GoRoute(
        path: Constants.homeRoute,
        name: 'home',
        builder: (context, state) => const HomeScreen(),
      ),

      // Customer management
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

      // Inspiration gallery
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

      // Design plans
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

      // Service records
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

      // AI chat assistant
      GoRoute(
        path: '/chat',
        name: 'chat',
        builder: (context, state) => const ChatScreen(),
      ),
      GoRoute(
        path: '/chat/:sessionId',
        name: 'chat-session',
        builder: (context, state) {
          final sessionId = int.tryParse(
              state.pathParameters['sessionId'] ?? '');
          return ChatScreen(sessionId: sessionId);
        },
      ),

      // Ability center
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

    // Route guard
    redirect: (context, state) {
      final authProvider = _authProvider;
      if (authProvider == null) return null;

      // Stay on splash while initialization is not complete
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

      // After splash initialization, redirect based on login state
      if (isSplash) {
        return isLoggedIn ? Constants.homeRoute : Constants.loginRoute;
      }

      // Not logged in and not on an auth page — redirect to login
      if (!isLoggedIn && !isAuthRoute) {
        return Constants.loginRoute;
      }

      // Logged in and on an auth page — redirect to home
      if (isLoggedIn && isAuthRoute) {
        return Constants.homeRoute;
      }

      return null;
    },

    // Error page
    errorBuilder: (context, state) {
      return const SplashScreen();
    },
  );
}
