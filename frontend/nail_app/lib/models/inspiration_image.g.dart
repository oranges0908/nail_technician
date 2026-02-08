// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'inspiration_image.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

InspirationImage _$InspirationImageFromJson(Map<String, dynamic> json) =>
    InspirationImage(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      imagePath: json['image_path'] as String,
      title: json['title'] as String?,
      description: json['description'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      category: json['category'] as String?,
      sourceUrl: json['source_url'] as String?,
      sourcePlatform: json['source_platform'] as String?,
      usageCount: json['usage_count'] as int? ?? 0,
      lastUsedAt: json['last_used_at'] == null
          ? null
          : DateTime.parse(json['last_used_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$InspirationImageToJson(InspirationImage instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'image_path': instance.imagePath,
      'title': instance.title,
      'description': instance.description,
      'tags': instance.tags,
      'category': instance.category,
      'source_url': instance.sourceUrl,
      'source_platform': instance.sourcePlatform,
      'usage_count': instance.usageCount,
      'last_used_at': instance.lastUsedAt?.toIso8601String(),
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };

InspirationImageListResponse _$InspirationImageListResponseFromJson(
        Map<String, dynamic> json) =>
    InspirationImageListResponse(
      total: json['total'] as int,
      inspirations: (json['inspirations'] as List<dynamic>)
          .map((e) => InspirationImage.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$InspirationImageListResponseToJson(
        InspirationImageListResponse instance) =>
    <String, dynamic>{
      'total': instance.total,
      'inspirations': instance.inspirations,
    };
