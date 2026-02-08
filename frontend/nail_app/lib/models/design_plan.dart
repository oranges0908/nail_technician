import 'package:json_annotation/json_annotation.dart';

part 'design_plan.g.dart';

/// 设计方案数据模型
@JsonSerializable()
class DesignPlan {
  final int id;

  @JsonKey(name: 'user_id')
  final int userId;

  @JsonKey(name: 'customer_id')
  final int? customerId;

  final String? title;
  final String? notes;

  @JsonKey(name: 'ai_prompt')
  final String aiPrompt;

  @JsonKey(name: 'generated_image_path')
  final String generatedImagePath;

  @JsonKey(name: 'model_version')
  final String? modelVersion;

  @JsonKey(name: 'design_target')
  final String? designTarget;

  @JsonKey(name: 'style_keywords')
  final List<String>? styleKeywords;

  @JsonKey(name: 'reference_images')
  final List<String>? referenceImages;

  @JsonKey(name: 'parent_design_id')
  final int? parentDesignId;

  final int version;

  @JsonKey(name: 'refinement_instruction')
  final String? refinementInstruction;

  @JsonKey(name: 'estimated_duration')
  final int? estimatedDuration;

  @JsonKey(name: 'estimated_materials')
  final List<String>? estimatedMaterials;

  @JsonKey(name: 'difficulty_level')
  final String? difficultyLevel;

  @JsonKey(name: 'is_archived')
  final dynamic isArchived;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  DesignPlan({
    required this.id,
    required this.userId,
    this.customerId,
    this.title,
    this.notes,
    required this.aiPrompt,
    required this.generatedImagePath,
    this.modelVersion,
    this.designTarget,
    this.styleKeywords,
    this.referenceImages,
    this.parentDesignId,
    this.version = 1,
    this.refinementInstruction,
    this.estimatedDuration,
    this.estimatedMaterials,
    this.difficultyLevel,
    this.isArchived = 0,
    required this.createdAt,
    required this.updatedAt,
  });

  bool get archived {
    if (isArchived is bool) return isArchived;
    if (isArchived is int) return isArchived == 1;
    return false;
  }

  factory DesignPlan.fromJson(Map<String, dynamic> json) =>
      _$DesignPlanFromJson(json);
  Map<String, dynamic> toJson() => _$DesignPlanToJson(this);

  @override
  String toString() {
    return 'DesignPlan(id: $id, title: $title, version: $version)';
  }
}

/// 设计方案列表响应
@JsonSerializable()
class DesignPlanListResponse {
  final int total;
  final List<DesignPlan> designs;

  DesignPlanListResponse({
    required this.total,
    required this.designs,
  });

  factory DesignPlanListResponse.fromJson(Map<String, dynamic> json) =>
      _$DesignPlanListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$DesignPlanListResponseToJson(this);
}
