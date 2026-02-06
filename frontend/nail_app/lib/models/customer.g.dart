// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'customer.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Customer _$CustomerFromJson(Map<String, dynamic> json) => Customer(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      name: json['name'] as String,
      phone: json['phone'] as String,
      email: json['email'] as String?,
      avatarPath: json['avatar_path'] as String?,
      notes: json['notes'] as String?,
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      profile: json['profile'] == null
          ? null
          : CustomerProfile.fromJson(json['profile'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$CustomerToJson(Customer instance) => <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'name': instance.name,
      'phone': instance.phone,
      'email': instance.email,
      'avatar_path': instance.avatarPath,
      'notes': instance.notes,
      'is_active': instance.isActive,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
      'profile': instance.profile,
    };

CustomerListResponse _$CustomerListResponseFromJson(
        Map<String, dynamic> json) =>
    CustomerListResponse(
      total: json['total'] as int,
      customers: (json['customers'] as List<dynamic>)
          .map((e) => Customer.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$CustomerListResponseToJson(
        CustomerListResponse instance) =>
    <String, dynamic>{
      'total': instance.total,
      'customers': instance.customers,
    };
