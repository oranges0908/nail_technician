// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'comparison_result.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ComparisonResult _$ComparisonResultFromJson(Map<String, dynamic> json) =>
    ComparisonResult(
      id: json['id'] as int,
      serviceRecordId: json['service_record_id'] as int,
      similarityScore: json['similarity_score'] as int,
      differences: json['differences'] as Map<String, dynamic>,
      suggestions: json['suggestions'] as List<dynamic>,
      contextualInsights: json['contextual_insights'] as Map<String, dynamic>?,
      analyzedAt: DateTime.parse(json['analyzed_at'] as String),
    );

Map<String, dynamic> _$ComparisonResultToJson(ComparisonResult instance) =>
    <String, dynamic>{
      'id': instance.id,
      'service_record_id': instance.serviceRecordId,
      'similarity_score': instance.similarityScore,
      'differences': instance.differences,
      'suggestions': instance.suggestions,
      'contextual_insights': instance.contextualInsights,
      'analyzed_at': instance.analyzedAt.toIso8601String(),
    };
