/// Application configuration class
/// Defines app-level constants and settings
class AppConfig {
  // App info
  static const String appName = 'Nail';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'Nail Artist Ability Growth System';

  // Local storage keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userIdKey = 'user_id';
  static const String userEmailKey = 'user_email';
  static const String usernameKey = 'username';
  static const String themeKey = 'theme_mode';

  // Pagination settings
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // File upload settings
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

  // Customer satisfaction options (1-5 stars)
  static const int minSatisfaction = 1;
  static const int maxSatisfaction = 5;

  // Difficulty levels
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

  // Environment settings
  static const bool isProduction = bool.fromEnvironment(
    'dart.vm.product',
    defaultValue: false,
  );

  static const bool enableLogging = !isProduction;
}
