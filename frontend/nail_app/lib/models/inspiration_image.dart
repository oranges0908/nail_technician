import 'package:json_annotation/json_annotation.dart';

part 'inspiration_image.g.dart';

/// 灵感图数据模型
@JsonSerializable()
class InspirationImage {
  final int id;

  @JsonKey(name: 'user_id')
  final int userId;

  @JsonKey(name: 'image_path')
  final String imagePath;

  final String? title;
  final String? description;
  final List<String>? tags;
  final String? category;

  @JsonKey(name: 'source_url')
  final String? sourceUrl;

  @JsonKey(name: 'source_platform')
  final String? sourcePlatform;

  @JsonKey(name: 'usage_count')
  final int usageCount;

  @JsonKey(name: 'last_used_at')
  final DateTime? lastUsedAt;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  InspirationImage({
    required this.id,
    required this.userId,
    required this.imagePath,
    this.title,
    this.description,
    this.tags,
    this.category,
    this.sourceUrl,
    this.sourcePlatform,
    this.usageCount = 0,
    this.lastUsedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory InspirationImage.fromJson(Map<String, dynamic> json) =>
      _$InspirationImageFromJson(json);
  Map<String, dynamic> toJson() => _$InspirationImageToJson(this);

  @override
  String toString() {
    return 'InspirationImage(id: $id, title: $title, category: $category)';
  }
}

/// 灵感图列表响应
@JsonSerializable()
class InspirationImageListResponse {
  final int total;
  final List<InspirationImage> inspirations;

  InspirationImageListResponse({
    required this.total,
    required this.inspirations,
  });

  factory InspirationImageListResponse.fromJson(Map<String, dynamic> json) =>
      _$InspirationImageListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$InspirationImageListResponseToJson(this);
}
