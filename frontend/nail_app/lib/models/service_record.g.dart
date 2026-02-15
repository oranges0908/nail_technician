// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'service_record.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ServiceRecord _$ServiceRecordFromJson(Map<String, dynamic> json) =>
    ServiceRecord(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      customerId: json['customer_id'] as int,
      designPlanId: json['design_plan_id'] as int?,
      serviceDate: json['service_date'] as String,
      serviceDuration: json['service_duration'] as int?,
      actualImagePath: json['actual_image_path'] as String?,
      designImagePath: json['design_image_path'] as String?,
      materialsUsed: json['materials_used'] as String?,
      artistReview: json['artist_review'] as String?,
      customerFeedback: json['customer_feedback'] as String?,
      customerSatisfaction: json['customer_satisfaction'] as int?,
      notes: json['notes'] as String?,
      status: json['status'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      completedAt: json['completed_at'] == null
          ? null
          : DateTime.parse(json['completed_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$ServiceRecordToJson(ServiceRecord instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'customer_id': instance.customerId,
      'design_plan_id': instance.designPlanId,
      'service_date': instance.serviceDate,
      'service_duration': instance.serviceDuration,
      'actual_image_path': instance.actualImagePath,
      'design_image_path': instance.designImagePath,
      'materials_used': instance.materialsUsed,
      'artist_review': instance.artistReview,
      'customer_feedback': instance.customerFeedback,
      'customer_satisfaction': instance.customerSatisfaction,
      'notes': instance.notes,
      'status': instance.status,
      'created_at': instance.createdAt.toIso8601String(),
      'completed_at': instance.completedAt?.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };

ServiceRecordListResponse _$ServiceRecordListResponseFromJson(
        Map<String, dynamic> json) =>
    ServiceRecordListResponse(
      items: (json['items'] as List<dynamic>)
          .map((e) => ServiceRecord.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$ServiceRecordListResponseToJson(
        ServiceRecordListResponse instance) =>
    <String, dynamic>{
      'items': instance.items,
    };
