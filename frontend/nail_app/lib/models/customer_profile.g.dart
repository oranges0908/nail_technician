// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'customer_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CustomerProfile _$CustomerProfileFromJson(Map<String, dynamic> json) =>
    CustomerProfile(
      id: json['id'] as int,
      customerId: json['customer_id'] as int,
      nailShape: json['nail_shape'] as String?,
      nailLength: json['nail_length'] as String?,
      nailCondition: json['nail_condition'] as String?,
      nailPhotos: (json['nail_photos'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      colorPreferences: (json['color_preferences'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      colorDislikes: (json['color_dislikes'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      stylePreferences: (json['style_preferences'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      patternPreferences: json['pattern_preferences'] as String?,
      allergies: json['allergies'] as String?,
      prohibitions: json['prohibitions'] as String?,
      occasionPreferences:
          json['occasion_preferences'] as Map<String, dynamic>?,
      maintenancePreference: json['maintenance_preference'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$CustomerProfileToJson(CustomerProfile instance) =>
    <String, dynamic>{
      'id': instance.id,
      'customer_id': instance.customerId,
      'nail_shape': instance.nailShape,
      'nail_length': instance.nailLength,
      'nail_condition': instance.nailCondition,
      'nail_photos': instance.nailPhotos,
      'color_preferences': instance.colorPreferences,
      'color_dislikes': instance.colorDislikes,
      'style_preferences': instance.stylePreferences,
      'pattern_preferences': instance.patternPreferences,
      'allergies': instance.allergies,
      'prohibitions': instance.prohibitions,
      'occasion_preferences': instance.occasionPreferences,
      'maintenance_preference': instance.maintenancePreference,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };
