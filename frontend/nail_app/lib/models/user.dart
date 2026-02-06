import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

/// 用户数据模型
/// 与后端 UserResponse Schema 对应
@JsonSerializable()
class User {
  final int id;
  final String email;
  final String username;

  @JsonKey(name: 'is_active')
  final bool isActive;

  @JsonKey(name: 'is_superuser')
  final bool isSuperuser;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  User({
    required this.id,
    required this.email,
    required this.username,
    required this.isActive,
    required this.isSuperuser,
    required this.createdAt,
    this.updatedAt,
  });

  /// 从 JSON 创建 User 对象
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  /// 将 User 对象转换为 JSON
  Map<String, dynamic> toJson() => _$UserToJson(this);

  /// 复制对象并修改部分字段
  User copyWith({
    int? id,
    String? email,
    String? username,
    bool? isActive,
    bool? isSuperuser,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      username: username ?? this.username,
      isActive: isActive ?? this.isActive,
      isSuperuser: isSuperuser ?? this.isSuperuser,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'User(id: $id, email: $email, username: $username, isActive: $isActive)';
  }
}
