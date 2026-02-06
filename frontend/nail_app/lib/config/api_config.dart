/// API 配置类
/// 定义所有 API 端点和请求配置
class ApiConfig {
  // 基础 URL（根据环境切换）
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  // 超时配置
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);

  // ==================== 认证相关 ====================
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String refreshTokenEndpoint = '/auth/refresh';
  static const String logoutEndpoint = '/auth/logout';

  // ==================== 用户相关 ====================
  static const String usersEndpoint = '/users';
  static const String userProfileEndpoint = '/users/me';
  static String userDetailEndpoint(int userId) => '/users/$userId';

  // ==================== 客户相关 ====================
  static const String customersEndpoint = '/customers';
  static String customerDetailEndpoint(int customerId) =>
      '/customers/$customerId';
  static String customerProfileEndpoint(int customerId) =>
      '/customers/$customerId/profile';

  // ==================== 灵感图库相关 ====================
  static const String inspirationsEndpoint = '/inspirations';
  static String inspirationDetailEndpoint(int inspirationId) =>
      '/inspirations/$inspirationId';

  // ==================== 设计方案相关 ====================
  static const String designsEndpoint = '/designs';
  static const String designGenerateEndpoint = '/designs/generate';
  static String designDetailEndpoint(int designId) => '/designs/$designId';
  static String designRefineEndpoint(int designId) =>
      '/designs/$designId/refine';

  // ==================== 服务记录相关 ====================
  static const String servicesEndpoint = '/services';
  static String serviceDetailEndpoint(int serviceId) => '/services/$serviceId';
  static String serviceCompleteEndpoint(int serviceId) =>
      '/services/$serviceId/complete';
  static String serviceComparisonEndpoint(int serviceId) =>
      '/services/$serviceId/comparison';
  static String serviceAnalyzeEndpoint(int serviceId) =>
      '/services/$serviceId/analyze';

  // ==================== 能力分析相关 ====================
  static const String abilitiesEndpoint = '/abilities';
  static const String abilityDimensionsEndpoint = '/abilities/dimensions';
  static const String abilityDimensionsInitEndpoint =
      '/abilities/dimensions/init';
  static const String abilityStatsEndpoint = '/abilities/stats';
  static const String abilitySummaryEndpoint = '/abilities/summary';
  static String abilityTrendEndpoint(String dimensionName) =>
      '/abilities/trend/$dimensionName';

  // ==================== 文件上传相关 ====================
  static const String uploadNailsEndpoint = '/uploads/nails';
  static const String uploadInspirationsEndpoint = '/uploads/inspirations';
  static const String uploadDesignsEndpoint = '/uploads/designs';
  static const String uploadActualsEndpoint = '/uploads/actuals';

  // ==================== 健康检查 ====================
  static const String healthEndpoint = '/health';

  // ==================== 静态文件基础路径 ====================
  static String getStaticFileUrl(String path) {
    // 去除 /api/v1 前缀用于静态文件访问
    final baseStaticUrl = baseUrl.replaceAll('/api/v1', '');
    return '$baseStaticUrl/$path';
  }
}
