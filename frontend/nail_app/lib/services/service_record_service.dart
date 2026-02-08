import '../models/service_record.dart';
import '../models/comparison_result.dart';
import '../config/api_config.dart';
import 'api_service.dart';

/// 服务记录服务
class ServiceRecordService {
  final ApiService _apiService = ApiService();

  /// 获取服务记录列表
  Future<List<ServiceRecord>> getServiceRecords({
    int? customerId,
    String? status,
    int skip = 0,
    int limit = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'skip': skip,
      'limit': limit,
    };
    if (customerId != null) queryParams['customer_id'] = customerId;
    if (status != null && status.isNotEmpty) queryParams['status'] = status;

    final response = await _apiService.get(
      ApiConfig.servicesEndpoint,
      queryParameters: queryParams,
    );
    return (response.data as List)
        .map((e) => ServiceRecord.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// 获取服务记录详情
  Future<ServiceRecord> getServiceRecord(int id) async {
    final response = await _apiService.get(
      ApiConfig.serviceDetailEndpoint(id),
    );
    return ServiceRecord.fromJson(response.data);
  }

  /// 创建服务记录
  Future<ServiceRecord> createServiceRecord({
    required int customerId,
    int? designPlanId,
    required String serviceDate,
    int? serviceDuration,
    String? materialsUsed,
    String? notes,
  }) async {
    final data = <String, dynamic>{
      'customer_id': customerId,
      'service_date': serviceDate,
    };
    if (designPlanId != null) data['design_plan_id'] = designPlanId;
    if (serviceDuration != null) data['service_duration'] = serviceDuration;
    if (materialsUsed != null && materialsUsed.isNotEmpty) {
      data['materials_used'] = materialsUsed;
    }
    if (notes != null && notes.isNotEmpty) data['notes'] = notes;

    final response = await _apiService.post(
      ApiConfig.servicesEndpoint,
      data: data,
    );
    return ServiceRecord.fromJson(response.data);
  }

  /// 更新服务记录
  Future<ServiceRecord> updateServiceRecord(
    int id,
    Map<String, dynamic> data,
  ) async {
    final response = await _apiService.put(
      ApiConfig.serviceDetailEndpoint(id),
      data: data,
    );
    return ServiceRecord.fromJson(response.data);
  }

  /// 完成服务记录
  Future<ServiceRecord> completeService(
    int id, {
    required String actualImagePath,
    required int serviceDuration,
    String? materialsUsed,
    String? artistReview,
    String? customerFeedback,
    int? customerSatisfaction,
    String? notes,
  }) async {
    final data = <String, dynamic>{
      'actual_image_path': actualImagePath,
      'service_duration': serviceDuration,
    };
    if (materialsUsed != null && materialsUsed.isNotEmpty) {
      data['materials_used'] = materialsUsed;
    }
    if (artistReview != null && artistReview.isNotEmpty) {
      data['artist_review'] = artistReview;
    }
    if (customerFeedback != null && customerFeedback.isNotEmpty) {
      data['customer_feedback'] = customerFeedback;
    }
    if (customerSatisfaction != null) {
      data['customer_satisfaction'] = customerSatisfaction;
    }
    if (notes != null && notes.isNotEmpty) data['notes'] = notes;

    final response = await _apiService.put(
      ApiConfig.serviceCompleteEndpoint(id),
      data: data,
    );
    return ServiceRecord.fromJson(response.data);
  }

  /// 获取对比分析结果
  Future<ComparisonResult> getComparison(int serviceId) async {
    final response = await _apiService.get(
      ApiConfig.serviceComparisonEndpoint(serviceId),
    );
    return ComparisonResult.fromJson(response.data);
  }

  /// 触发AI分析
  Future<ComparisonResult> triggerAnalysis(int serviceId) async {
    final response = await _apiService.post(
      ApiConfig.serviceAnalyzeEndpoint(serviceId),
    );
    return ComparisonResult.fromJson(response.data);
  }

  /// 删除服务记录
  Future<void> deleteServiceRecord(int id) async {
    await _apiService.delete(
      ApiConfig.serviceDetailEndpoint(id),
    );
  }
}
