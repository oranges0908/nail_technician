// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'design_plan.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DesignPlan _$DesignPlanFromJson(Map<String, dynamic> json) => DesignPlan(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      customerId: json['customer_id'] as int?,
      title: json['title'] as String?,
      notes: json['notes'] as String?,
      aiPrompt: json['ai_prompt'] as String,
      generatedImagePath: json['generated_image_path'] as String,
      modelVersion: json['model_version'] as String?,
      designTarget: json['design_target'] as String?,
      styleKeywords: (json['style_keywords'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      referenceImages: (json['reference_images'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      parentDesignId: json['parent_design_id'] as int?,
      version: json['version'] as int? ?? 1,
      refinementInstruction: json['refinement_instruction'] as String?,
      estimatedDuration: json['estimated_duration'] as int?,
      estimatedMaterials: (json['estimated_materials'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      difficultyLevel: json['difficulty_level'] as String?,
      isArchived: json['is_archived'] ?? 0,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$DesignPlanToJson(DesignPlan instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'customer_id': instance.customerId,
      'title': instance.title,
      'notes': instance.notes,
      'ai_prompt': instance.aiPrompt,
      'generated_image_path': instance.generatedImagePath,
      'model_version': instance.modelVersion,
      'design_target': instance.designTarget,
      'style_keywords': instance.styleKeywords,
      'reference_images': instance.referenceImages,
      'parent_design_id': instance.parentDesignId,
      'version': instance.version,
      'refinement_instruction': instance.refinementInstruction,
      'estimated_duration': instance.estimatedDuration,
      'estimated_materials': instance.estimatedMaterials,
      'difficulty_level': instance.difficultyLevel,
      'is_archived': instance.isArchived,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };

DesignPlanListResponse _$DesignPlanListResponseFromJson(
        Map<String, dynamic> json) =>
    DesignPlanListResponse(
      total: json['total'] as int,
      designs: (json['designs'] as List<dynamic>)
          .map((e) => DesignPlan.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$DesignPlanListResponseToJson(
        DesignPlanListResponse instance) =>
    <String, dynamic>{
      'total': instance.total,
      'designs': instance.designs,
    };
