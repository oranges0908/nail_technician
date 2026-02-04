# Flutter 前端

## 创建 Flutter 项目

```bash
cd frontend
flutter create nail_app
cd nail_app
```

## 项目结构

```
nail_app/
├── lib/
│   ├── config/          # 配置文件
│   │   ├── api_config.dart
│   │   └── app_config.dart
│   ├── models/          # 数据模型
│   │   └── user.dart
│   ├── providers/       # 状态管理 (Provider/Riverpod)
│   │   └── auth_provider.dart
│   ├── services/        # API 服务
│   │   ├── api_service.dart
│   │   └── auth_service.dart
│   ├── screens/         # 页面
│   │   ├── home/
│   │   ├── auth/
│   │   └── profile/
│   ├── widgets/         # 通用组件
│   │   └── common/
│   ├── utils/           # 工具类
│   │   ├── constants.dart
│   │   └── helpers.dart
│   └── main.dart        # 应用入口
├── test/                # 测试文件
├── android/             # Android 配置
├── ios/                 # iOS 配置
└── pubspec.yaml         # 依赖配置
```

## 必要依赖

在 `pubspec.yaml` 中添加:

```yaml
dependencies:
  flutter:
    sdk: flutter

  # HTTP 请求
  dio: ^5.4.0

  # 状态管理
  provider: ^6.1.1
  # 或者使用 riverpod:
  # flutter_riverpod: ^2.4.9

  # 本地存储
  shared_preferences: ^2.2.2

  # JSON 序列化
  json_annotation: ^4.8.1

  # 路由导航
  go_router: ^13.0.0

  # UI 组件
  flutter_screenutil: ^5.9.0

  # 图片加载
  cached_network_image: ^3.3.1

  # 加载指示器
  flutter_spinkit: ^5.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

  # JSON 代码生成
  build_runner: ^2.4.8
  json_serializable: ^6.7.1
```

## 快速开始

### 1. 安装依赖

```bash
flutter pub get
```

### 2. 运行代码生成

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### 3. 运行应用

```bash
# iOS
flutter run -d ios

# Android
flutter run -d android

# Web
flutter run -d chrome
```

## 配置说明

### API 配置

创建 `lib/config/api_config.dart`:

```dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  static const Duration timeout = Duration(seconds: 30);
}
```

### 环境配置

开发环境和生产环境使用不同的 API 地址。

## 构建发布版本

### Android

```bash
flutter build apk --release
# 或
flutter build appbundle --release
```

### iOS

```bash
flutter build ios --release
```

## 测试

```bash
# 运行所有测试
flutter test

# 运行特定测试
flutter test test/models/user_test.dart

# 生成测试覆盖率
flutter test --coverage
```
