/// API configuration class
/// Defines all API endpoints and request settings
class ApiConfig {
  // Base URL (switch based on environment)
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8002/api/v1',
  );

  // Timeout settings
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);

  // ==================== Auth ====================
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String refreshTokenEndpoint = '/auth/refresh';
  static const String logoutEndpoint = '/auth/logout';

  // ==================== Users ====================
  static const String usersEndpoint = '/users';
  static const String userProfileEndpoint = '/users/me';
  static String userDetailEndpoint(int userId) => '/users/$userId';

  // ==================== Customers ====================
  static const String customersEndpoint = '/customers';
  static String customerDetailEndpoint(int customerId) =>
      '/customers/$customerId';
  static String customerProfileEndpoint(int customerId) =>
      '/customers/$customerId/profile';

  // ==================== Inspiration Gallery ====================
  static const String inspirationsEndpoint = '/inspirations';
  static String inspirationDetailEndpoint(int inspirationId) =>
      '/inspirations/$inspirationId';

  // ==================== Design Plans ====================
  static const String designsEndpoint = '/designs';
  static const String designGenerateEndpoint = '/designs/generate';
  static String designDetailEndpoint(int designId) => '/designs/$designId';
  static String designRefineEndpoint(int designId) =>
      '/designs/$designId/refine';

  // ==================== Service Records ====================
  static const String servicesEndpoint = '/services';
  static String serviceDetailEndpoint(int serviceId) => '/services/$serviceId';
  static String serviceCompleteEndpoint(int serviceId) =>
      '/services/$serviceId/complete';
  static String serviceComparisonEndpoint(int serviceId) =>
      '/services/$serviceId/comparison';
  static String serviceAnalyzeEndpoint(int serviceId) =>
      '/services/$serviceId/analyze';

  // ==================== Ability Analysis ====================
  static const String abilitiesEndpoint = '/abilities';
  static const String abilityDimensionsEndpoint = '/abilities/dimensions';
  static const String abilityDimensionsInitEndpoint =
      '/abilities/dimensions/init';
  static const String abilityStatsEndpoint = '/abilities/stats';
  static const String abilitySummaryEndpoint = '/abilities/summary';
  static String abilityTrendEndpoint(String dimensionName) =>
      '/abilities/trend/$dimensionName';

  // ==================== File Uploads ====================
  static const String uploadNailsEndpoint = '/uploads/nails';
  static const String uploadInspirationsEndpoint = '/uploads/inspirations';
  static const String uploadDesignsEndpoint = '/uploads/designs';
  static const String uploadActualsEndpoint = '/uploads/actuals';

  // ==================== AI Chat Assistant ====================
  static const String conversationsEndpoint = '/conversations';
  static String conversationDetailEndpoint(int id) => '/conversations/$id';
  static String conversationMessagesEndpoint(int id) =>
      '/conversations/$id/messages';
  static String conversationImagesEndpoint(int id) =>
      '/conversations/$id/images';

  // ==================== Health Check ====================
  static const String healthEndpoint = '/health';

  // ==================== Static Files Base Path ====================
  static String getStaticFileUrl(String path) {
    // Remove /api/v1 prefix for static file access
    final baseStaticUrl = baseUrl.replaceAll('/api/v1', '');
    // Remove leading slash from path to avoid double slashes
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return '$baseStaticUrl/$cleanPath';
  }
}
