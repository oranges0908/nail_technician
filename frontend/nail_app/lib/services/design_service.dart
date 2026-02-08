import '../models/design_plan.dart';
import '../config/api_config.dart';
import 'api_service.dart';

/// 设计方案服务
class DesignService {
  final ApiService _apiService = ApiService();

  /// AI生成设计方案
  Future<DesignPlan> generateDesign({
    required String prompt,
    List<String>? referenceImages,
    String designTarget = '10nails',
    List<String>? styleKeywords,
    int? customerId,
    String? title,
    String? notes,
  }) async {
    final data = <String, dynamic>{
      'prompt': prompt,
      'design_target': designTarget,
    };
    if (referenceImages != null && referenceImages.isNotEmpty) {
      data['reference_images'] = referenceImages;
    }
    if (styleKeywords != null && styleKeywords.isNotEmpty) {
      data['style_keywords'] = styleKeywords;
    }
    if (customerId != null) data['customer_id'] = customerId;
    if (title != null && title.isNotEmpty) data['title'] = title;
    if (notes != null && notes.isNotEmpty) data['notes'] = notes;

    final response = await _apiService.post(
      ApiConfig.designGenerateEndpoint,
      data: data,
    );
    return DesignPlan.fromJson(response.data);
  }

  /// 优化设计方案
  Future<DesignPlan> refineDesign(int designId, String instruction) async {
    final response = await _apiService.post(
      ApiConfig.designRefineEndpoint(designId),
      data: {'refinement_instruction': instruction},
    );
    return DesignPlan.fromJson(response.data);
  }

  /// 获取设计方案列表
  Future<DesignPlanListResponse> getDesigns({
    int skip = 0,
    int limit = 20,
    int? customerId,
    String? search,
    int? isArchived,
  }) async {
    final queryParams = <String, dynamic>{
      'skip': skip,
      'limit': limit,
    };
    if (customerId != null) queryParams['customer_id'] = customerId;
    if (search != null && search.isNotEmpty) queryParams['search'] = search;
    if (isArchived != null) queryParams['is_archived'] = isArchived;

    final response = await _apiService.get(
      ApiConfig.designsEndpoint,
      queryParameters: queryParams,
    );
    return DesignPlanListResponse.fromJson(response.data);
  }

  /// 获取设计方案详情
  Future<DesignPlan> getDesign(int id) async {
    final response = await _apiService.get(
      ApiConfig.designDetailEndpoint(id),
    );
    return DesignPlan.fromJson(response.data);
  }

  /// 获取设计方案版本历史
  Future<List<DesignPlan>> getDesignVersions(int id) async {
    final response = await _apiService.get(
      '${ApiConfig.designDetailEndpoint(id)}/versions',
    );
    return (response.data as List)
        .map((e) => DesignPlan.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// 更新设计方案
  Future<DesignPlan> updateDesign(int id, {String? title, String? notes}) async {
    final data = <String, dynamic>{};
    if (title != null) data['title'] = title;
    if (notes != null) data['notes'] = notes;

    final response = await _apiService.put(
      ApiConfig.designDetailEndpoint(id),
      data: data,
    );
    return DesignPlan.fromJson(response.data);
  }

  /// 归档设计方案
  Future<void> archiveDesign(int id) async {
    await _apiService.put(
      '${ApiConfig.designDetailEndpoint(id)}/archive',
    );
  }

  /// 删除设计方案
  Future<void> deleteDesign(int id) async {
    await _apiService.delete(
      ApiConfig.designDetailEndpoint(id),
    );
  }
}
