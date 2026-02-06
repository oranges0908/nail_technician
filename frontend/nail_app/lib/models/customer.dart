import 'package:json_annotation/json_annotation.dart';
import 'customer_profile.dart';

part 'customer.g.dart';

/// 客户数据模型
@JsonSerializable()
class Customer {
  final int id;

  @JsonKey(name: 'user_id')
  final int userId;

  final String name;
  final String phone;
  final String? email;

  @JsonKey(name: 'avatar_path')
  final String? avatarPath;

  final String? notes;

  @JsonKey(name: 'is_active')
  final dynamic isActive;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  final CustomerProfile? profile;

  Customer({
    required this.id,
    required this.userId,
    required this.name,
    required this.phone,
    this.email,
    this.avatarPath,
    this.notes,
    this.isActive = true,
    required this.createdAt,
    required this.updatedAt,
    this.profile,
  });

  /// Backend returns is_active as 1/0 or true/false
  bool get active {
    if (isActive is bool) return isActive;
    if (isActive is int) return isActive == 1;
    return true;
  }

  factory Customer.fromJson(Map<String, dynamic> json) =>
      _$CustomerFromJson(json);
  Map<String, dynamic> toJson() => _$CustomerToJson(this);

  @override
  String toString() {
    return 'Customer(id: $id, name: $name, phone: $phone)';
  }
}

/// 客户列表响应
@JsonSerializable()
class CustomerListResponse {
  final int total;
  final List<Customer> customers;

  CustomerListResponse({
    required this.total,
    required this.customers,
  });

  factory CustomerListResponse.fromJson(Map<String, dynamic> json) =>
      _$CustomerListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$CustomerListResponseToJson(this);
}
