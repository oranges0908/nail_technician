/// 常量定义类
/// 定义应用中使用的各种常量
class Constants {
  // ==================== 路由名称 ====================
  static const String splashRoute = '/';
  static const String loginRoute = '/login';
  static const String registerRoute = '/register';
  static const String homeRoute = '/home';
  static const String profileRoute = '/profile';
  static const String customersRoute = '/customers';
  static const String customerDetailRoute = '/customers/:id';
  static const String inspirationsRoute = '/inspirations';
  static const String designsRoute = '/designs';
  static const String servicesRoute = '/services';
  static const String serviceDetailRoute = '/services/:id';
  static const String abilitiesRoute = '/abilities';

  // ==================== 动画时长 ====================
  static const Duration shortAnimationDuration = Duration(milliseconds: 200);
  static const Duration mediumAnimationDuration = Duration(milliseconds: 300);
  static const Duration longAnimationDuration = Duration(milliseconds: 500);

  // ==================== 间距 ====================
  static const double tinySpacing = 4.0;
  static const double smallSpacing = 8.0;
  static const double mediumSpacing = 16.0;
  static const double largeSpacing = 24.0;
  static const double extraLargeSpacing = 32.0;

  // ==================== 圆角 ====================
  static const double smallRadius = 4.0;
  static const double mediumRadius = 8.0;
  static const double largeRadius = 12.0;
  static const double extraLargeRadius = 16.0;
  static const double circularRadius = 999.0;

  // ==================== 阴影 ====================
  static const double smallElevation = 2.0;
  static const double mediumElevation = 4.0;
  static const double largeElevation = 8.0;

  // ==================== 图标大小 ====================
  static const double smallIconSize = 16.0;
  static const double mediumIconSize = 24.0;
  static const double largeIconSize = 32.0;
  static const double extraLargeIconSize = 48.0;

  // ==================== 按钮高度 ====================
  static const double smallButtonHeight = 32.0;
  static const double mediumButtonHeight = 44.0;
  static const double largeButtonHeight = 56.0;

  // ==================== 默认图片 ====================
  static const String defaultAvatar = 'assets/images/default_avatar.png';
  static const String defaultNailImage = 'assets/images/default_nail.png';
  static const String logoImage = 'assets/images/logo.png';

  // ==================== 错误消息 ====================
  static const String networkError = '网络连接失败，请检查网络设置';
  static const String serverError = '服务器错误，请稍后重试';
  static const String unauthorizedError = '未授权，请重新登录';
  static const String notFoundError = '请求的资源不存在';
  static const String timeoutError = '请求超时，请重试';
  static const String unknownError = '未知错误';

  // ==================== 验证消息 ====================
  static const String emptyEmailError = '请输入邮箱';
  static const String invalidEmailError = '邮箱格式不正确';
  static const String emptyPasswordError = '请输入密码';
  static const String shortPasswordError = '密码至少6位';
  static const String emptyUsernameError = '请输入用户名';
  static const String emptyNameError = '请输入姓名';
  static const String emptyPhoneError = '请输入手机号';
  static const String invalidPhoneError = '手机号格式不正确';

  // ==================== 成功消息 ====================
  static const String loginSuccess = '登录成功';
  static const String registerSuccess = '注册成功';
  static const String logoutSuccess = '退出登录成功';
  static const String createSuccess = '创建成功';
  static const String updateSuccess = '更新成功';
  static const String deleteSuccess = '删除成功';
  static const String uploadSuccess = '上传成功';

  // ==================== 确认消息 ====================
  static const String deleteConfirmTitle = '确认删除';
  static const String deleteConfirmMessage = '确定要删除吗？此操作不可撤销。';
  static const String logoutConfirmTitle = '确认退出';
  static const String logoutConfirmMessage = '确定要退出登录吗？';
  static const String cancelConfirmTitle = '确认取消';
  static const String cancelConfirmMessage = '确定要取消吗？未保存的更改将丢失。';

  // ==================== 按钮文字 ====================
  static const String confirmButton = '确定';
  static const String cancelButton = '取消';
  static const String saveButton = '保存';
  static const String deleteButton = '删除';
  static const String editButton = '编辑';
  static const String submitButton = '提交';
  static const String retryButton = '重试';
  static const String backButton = '返回';
  static const String nextButton = '下一步';
  static const String finishButton = '完成';
  static const String skipButton = '跳过';
  static const String loginButton = '登录';
  static const String registerButton = '注册';
  static const String logoutButton = '退出登录';

  // ==================== 正则表达式 ====================
  static final RegExp emailRegex = RegExp(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
  );
  static final RegExp phoneRegex = RegExp(
    r'^1[3-9]\d{9}$',
  );
  static final RegExp usernameRegex = RegExp(
    r'^[a-zA-Z0-9_]{3,20}$',
  );
}
