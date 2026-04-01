/// 应用配置类
/// 定义应用级别的常量和配置
class AppConfig {
  // 应用信息
  static const String appName = 'Nail';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'Nail Artist Ability Growth System';

  // 本地存储 Key
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userIdKey = 'user_id';
  static const String userEmailKey = 'user_email';
  static const String usernameKey = 'username';
  static const String themeKey = 'theme_mode';

  // 分页配置
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // 文件上传配置
  static const int maxImageSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedImageExtensions = [
    'jpg',
    'jpeg',
    'png',
    'webp'
  ];

  // Ability dimension names (must match backend)
  static const List<String> abilityDimensions = [
    'color_matching',
    'pattern_precision',
    'detail_work',
    'composition',
    'technique_application',
    'creative_expression',
  ];

  // Ability dimension display labels
  static const Map<String, String> abilityDimensionLabels = {
    'color_matching': 'Color Matching',
    'pattern_precision': 'Pattern Precision',
    'detail_work': 'Detail Work',
    'composition': 'Composition',
    'technique_application': 'Technique Application',
    'creative_expression': 'Creative Expression',
  };

  // Design target options
  static const List<String> designTargets = [
    'single', // single nail
    '5nails', // one hand
    '10nails', // both hands
  ];

  static const Map<String, String> designTargetLabels = {
    'single': 'Single Nail',
    '5nails': 'One Hand (5 nails)',
    '10nails': 'Both Hands (10 nails)',
  };

  // 客户满意度选项（1-5 星）
  static const int minSatisfaction = 1;
  static const int maxSatisfaction = 5;

  // 难度级别
  static const List<String> difficultyLevels = [
    'easy',
    'medium',
    'hard',
    'expert',
  ];

  static const Map<String, String> difficultyLabels = {
    'easy': 'Easy',
    'medium': 'Medium',
    'hard': 'Hard',
    'expert': 'Expert',
  };

  // Service record statuses
  static const List<String> serviceStatuses = [
    'pending',
    'in_progress',
    'completed',
    'cancelled',
  ];

  static const Map<String, String> serviceStatusLabels = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
  };

  // 环境配置
  static const bool isProduction = bool.fromEnvironment(
    'dart.vm.product',
    defaultValue: false,
  );

  static const bool enableLogging = !isProduction;
}
