import 'package:json_annotation/json_annotation.dart';

part 'service_record.g.dart';

/// 服务记录数据模型
@JsonSerializable()
class ServiceRecord {
  final int id;

  @JsonKey(name: 'user_id')
  final int userId;

  @JsonKey(name: 'customer_id')
  final int customerId;

  @JsonKey(name: 'design_plan_id')
  final int? designPlanId;

  @JsonKey(name: 'service_date')
  final String serviceDate;

  @JsonKey(name: 'service_duration')
  final int? serviceDuration;

  @JsonKey(name: 'actual_image_path')
  final String? actualImagePath;

  @JsonKey(name: 'design_image_path')
  final String? designImagePath;

  @JsonKey(name: 'materials_used')
  final String? materialsUsed;

  @JsonKey(name: 'artist_review')
  final String? artistReview;

  @JsonKey(name: 'customer_feedback')
  final String? customerFeedback;

  @JsonKey(name: 'customer_satisfaction')
  final int? customerSatisfaction;

  final String? notes;
  final String status;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'completed_at')
  final DateTime? completedAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  ServiceRecord({
    required this.id,
    required this.userId,
    required this.customerId,
    this.designPlanId,
    required this.serviceDate,
    this.serviceDuration,
    this.actualImagePath,
    this.designImagePath,
    this.materialsUsed,
    this.artistReview,
    this.customerFeedback,
    this.customerSatisfaction,
    this.notes,
    required this.status,
    required this.createdAt,
    this.completedAt,
    required this.updatedAt,
  });

  bool get isCompleted => status == 'completed';
  bool get isPending => status == 'pending';

  factory ServiceRecord.fromJson(Map<String, dynamic> json) =>
      _$ServiceRecordFromJson(json);
  Map<String, dynamic> toJson() => _$ServiceRecordToJson(this);

  @override
  String toString() {
    return 'ServiceRecord(id: $id, customerId: $customerId, status: $status)';
  }
}

/// 服务记录列表响应
@JsonSerializable()
class ServiceRecordListResponse {
  final List<ServiceRecord> items;

  ServiceRecordListResponse({
    required this.items,
  });

  factory ServiceRecordListResponse.fromJson(List<dynamic> json) {
    return ServiceRecordListResponse(
      items: json.map((e) => ServiceRecord.fromJson(e as Map<String, dynamic>)).toList(),
    );
  }
}
