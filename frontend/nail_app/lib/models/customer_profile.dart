import 'package:json_annotation/json_annotation.dart';

part 'customer_profile.g.dart';

/// 客户详细档案模型
@JsonSerializable()
class CustomerProfile {
  final int id;

  @JsonKey(name: 'customer_id')
  final int customerId;

  @JsonKey(name: 'nail_shape')
  final String? nailShape;

  @JsonKey(name: 'nail_length')
  final String? nailLength;

  @JsonKey(name: 'nail_condition')
  final String? nailCondition;

  @JsonKey(name: 'nail_photos')
  final List<String>? nailPhotos;

  @JsonKey(name: 'color_preferences')
  final List<String>? colorPreferences;

  @JsonKey(name: 'color_dislikes')
  final List<String>? colorDislikes;

  @JsonKey(name: 'style_preferences')
  final List<String>? stylePreferences;

  @JsonKey(name: 'pattern_preferences')
  final String? patternPreferences;

  final String? allergies;
  final String? prohibitions;

  @JsonKey(name: 'occasion_preferences')
  final Map<String, dynamic>? occasionPreferences;

  @JsonKey(name: 'maintenance_preference')
  final String? maintenancePreference;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  CustomerProfile({
    required this.id,
    required this.customerId,
    this.nailShape,
    this.nailLength,
    this.nailCondition,
    this.nailPhotos,
    this.colorPreferences,
    this.colorDislikes,
    this.stylePreferences,
    this.patternPreferences,
    this.allergies,
    this.prohibitions,
    this.occasionPreferences,
    this.maintenancePreference,
    required this.createdAt,
    required this.updatedAt,
  });

  factory CustomerProfile.fromJson(Map<String, dynamic> json) =>
      _$CustomerProfileFromJson(json);
  Map<String, dynamic> toJson() => _$CustomerProfileToJson(this);
}
