import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

/// User data model
/// Corresponds to the backend UserResponse Schema
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

  /// Create a User object from JSON
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  /// Convert User object to JSON
  Map<String, dynamic> toJson() => _$UserToJson(this);

  /// Copy the object with some fields modified
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
