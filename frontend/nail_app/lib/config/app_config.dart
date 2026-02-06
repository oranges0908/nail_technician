/// 应用配置类
/// 定义应用级别的常量和配置
class AppConfig {
  // 应用信息
  static const String appName = 'Nail';
  static const String appVersion = '1.0.0';
  static const String appDescription = '美甲师能力成长系统';

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

  // 能力维度名称（与后端一致）
  static const List<String> abilityDimensions = [
    '颜色搭配',
    '图案精度',
    '细节处理',
    '整体构图',
    '技法运用',
    '创意表达',
  ];

  // 能力维度英文名（与后端一致）
  static const Map<String, String> abilityDimensionEnNames = {
    '颜色搭配': 'color_matching',
    '图案精度': 'pattern_precision',
    '细节处理': 'detail_work',
    '整体构图': 'composition',
    '技法运用': 'technique_application',
    '创意表达': 'creative_expression',
  };

  // 设计目标选项
  static const List<String> designTargets = [
    'single', // 单个指甲
    '5nails', // 一只手
    '10nails', // 双手
  ];

  static const Map<String, String> designTargetLabels = {
    'single': '单个指甲',
    '5nails': '一只手（5个）',
    '10nails': '双手（10个）',
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
    'easy': '简单',
    'medium': '中等',
    'hard': '困难',
    'expert': '专家',
  };

  // 服务记录状态
  static const List<String> serviceStatuses = [
    'pending',
    'in_progress',
    'completed',
    'cancelled',
  ];

  static const Map<String, String> serviceStatusLabels = {
    'pending': '待开始',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消',
  };

  // 环境配置
  static const bool isProduction = bool.fromEnvironment(
    'dart.vm.product',
    defaultValue: false,
  );

  static const bool enableLogging = !isProduction;
}
