import 'package:json_annotation/json_annotation.dart';

part 'comparison_result.g.dart';

/// AI对比分析结果数据模型
@JsonSerializable()
class ComparisonResult {
  final int id;

  @JsonKey(name: 'service_record_id')
  final int serviceRecordId;

  @JsonKey(name: 'similarity_score')
  final int similarityScore;

  final Map<String, dynamic> differences;
  final List<dynamic> suggestions;

  @JsonKey(name: 'contextual_insights')
  final Map<String, dynamic>? contextualInsights;

  @JsonKey(name: 'analyzed_at')
  final DateTime analyzedAt;

  ComparisonResult({
    required this.id,
    required this.serviceRecordId,
    required this.similarityScore,
    required this.differences,
    required this.suggestions,
    this.contextualInsights,
    required this.analyzedAt,
  });

  factory ComparisonResult.fromJson(Map<String, dynamic> json) =>
      _$ComparisonResultFromJson(json);
  Map<String, dynamic> toJson() => _$ComparisonResultToJson(this);

  @override
  String toString() {
    return 'ComparisonResult(id: $id, similarityScore: $similarityScore)';
  }
}
