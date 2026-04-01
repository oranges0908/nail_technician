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
  static const String inspirationsUploadRoute = '/inspirations/upload';
  static const String designsRoute = '/designs';
  static const String designGenerateRoute = '/designs/generate';
  static const String designDetailRoute = '/designs/:id';
  static const String servicesRoute = '/services';
  static const String serviceNewRoute = '/services/new';
  static const String serviceDetailRoute = '/services/:id';
  static const String serviceCompleteRoute = '/services/:id/complete';
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

  // ==================== Error Messages ====================
  static const String networkError = 'Network connection failed, please check your network settings';
  static const String serverError = 'Server error, please try again later';
  static const String unauthorizedError = 'Unauthorized, please log in again';
  static const String notFoundError = 'The requested resource does not exist';
  static const String timeoutError = 'Request timed out, please retry';
  static const String unknownError = 'Unknown error';

  // ==================== Validation Messages ====================
  static const String emptyEmailError = 'Please enter your email';
  static const String invalidEmailError = 'Invalid email format';
  static const String emptyPasswordError = 'Please enter your password';
  static const String shortPasswordError = 'Password must be at least 6 characters';
  static const String emptyUsernameError = 'Please enter your username';
  static const String emptyNameError = 'Please enter a name';
  static const String emptyPhoneError = 'Please enter a phone number';
  static const String invalidPhoneError = 'Invalid phone number format';

  // ==================== Success Messages ====================
  static const String loginSuccess = 'Login successful';
  static const String registerSuccess = 'Registration successful';
  static const String logoutSuccess = 'Logged out successfully';
  static const String createSuccess = 'Created successfully';
  static const String updateSuccess = 'Updated successfully';
  static const String deleteSuccess = 'Deleted successfully';
  static const String uploadSuccess = 'Uploaded successfully';

  // ==================== Confirmation Messages ====================
  static const String deleteConfirmTitle = 'Confirm Delete';
  static const String deleteConfirmMessage = 'Are you sure you want to delete? This action cannot be undone.';
  static const String logoutConfirmTitle = 'Confirm Logout';
  static const String logoutConfirmMessage = 'Are you sure you want to log out?';
  static const String cancelConfirmTitle = 'Confirm Cancel';
  static const String cancelConfirmMessage = 'Are you sure you want to cancel? Unsaved changes will be lost.';

  // ==================== Button Labels ====================
  static const String confirmButton = 'Confirm';
  static const String cancelButton = 'Cancel';
  static const String saveButton = 'Save';
  static const String deleteButton = 'Delete';
  static const String editButton = 'Edit';
  static const String submitButton = 'Submit';
  static const String retryButton = 'Retry';
  static const String backButton = 'Back';
  static const String nextButton = 'Next';
  static const String finishButton = 'Done';
  static const String skipButton = 'Skip';
  static const String loginButton = 'Login';
  static const String registerButton = 'Register';
  static const String logoutButton = 'Logout';

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
