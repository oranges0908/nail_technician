# Flutter 项目结构详解

## 创建项目后的目录结构

使用 `flutter create nail_app` 后，建议按以下方式组织代码:

## lib/ 目录结构

```
lib/
├── config/
│   ├── api_config.dart         # API 配置
│   ├── app_config.dart         # 应用配置
│   └── theme_config.dart       # 主题配置
│
├── models/
│   ├── user.dart               # 用户模型
│   ├── user.g.dart             # 自动生成的序列化代码
│   └── response_wrapper.dart   # API 响应包装
│
├── providers/
│   ├── auth_provider.dart      # 认证状态管理
│   ├── user_provider.dart      # 用户状态管理
│   └── theme_provider.dart     # 主题状态管理
│
├── services/
│   ├── api_service.dart        # API 基础服务
│   ├── auth_service.dart       # 认证服务
│   ├── user_service.dart       # 用户服务
│   └── storage_service.dart    # 本地存储服务
│
├── screens/
│   ├── splash/
│   │   └── splash_screen.dart
│   ├── auth/
│   │   ├── login_screen.dart
│   │   └── register_screen.dart
│   ├── home/
│   │   └── home_screen.dart
│   └── profile/
│       └── profile_screen.dart
│
├── widgets/
│   ├── common/
│   │   ├── custom_button.dart
│   │   ├── custom_text_field.dart
│   │   └── loading_widget.dart
│   └── auth/
│       └── auth_form.dart
│
├── utils/
│   ├── constants.dart          # 常量定义
│   ├── validators.dart         # 表单验证
│   ├── helpers.dart            # 辅助函数
│   └── extensions.dart         # 扩展方法
│
├── routes/
│   └── app_router.dart         # 路由配置
│
└── main.dart                   # 应用入口
```

## 核心文件示例

### main.dart

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme_config.dart';
import 'providers/auth_provider.dart';
import 'routes/app_router.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Nail App',
      theme: ThemeConfig.lightTheme,
      darkTheme: ThemeConfig.darkTheme,
      routerConfig: AppRouter.router,
    );
  }
}
```

### config/api_config.dart

```dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // API 端点
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String usersEndpoint = '/users';
}
```

### models/user.dart

```dart
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final int id;
  final String email;
  final String username;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  User({
    required this.id,
    required this.email,
    required this.username,
    required this.isActive,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

### services/api_service.dart

```dart
import 'package:dio/dio.dart';
import '../config/api_config.dart';

class ApiService {
  late Dio _dio;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // 添加 token
        final token = ''; // 从存储中获取
        if (token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        // 错误处理
        return handler.next(error);
      },
    ));
  }

  Dio get dio => _dio;
}
```

## 使用说明

1. 首先运行 `flutter create nail_app` 创建项目
2. 按照上述结构创建目录和文件
3. 复制 `pubspec_template.yaml` 内容到 `pubspec.yaml`
4. 运行 `flutter pub get` 安装依赖
5. 运行 `flutter pub run build_runner build` 生成序列化代码
6. 开始开发

## 注意事项

- 使用 JSON 序列化需要运行代码生成命令
- Provider 使用需要在 main.dart 中正确配置
- API 服务需要根据实际后端接口调整
- 路由配置使用 go_router 包
