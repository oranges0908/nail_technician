import '../config/api_config.dart';
import 'api_service.dart';

/// 能力分析服务
class AbilityService {
  final ApiService _apiService = ApiService();

  /// 获取能力维度列表
  Future<Map<String, dynamic>> getDimensions({
    bool includeInactive = false,
  }) async {
    final response = await _apiService.get(
      ApiConfig.abilityDimensionsEndpoint,
      queryParameters: {'include_inactive': includeInactive},
    );
    return response.data as Map<String, dynamic>;
  }

  /// 初始化能力维度
  Future<Map<String, dynamic>> initializeDimensions() async {
    final response = await _apiService.post(
      ApiConfig.abilityDimensionsInitEndpoint,
    );
    return response.data as Map<String, dynamic>;
  }

  /// 获取能力统计（雷达图数据）
  Future<Map<String, dynamic>> getAbilityStats() async {
    final response = await _apiService.get(
      ApiConfig.abilityStatsEndpoint,
    );
    return response.data as Map<String, dynamic>;
  }

  /// 获取能力总结（擅长/待提升）
  Future<Map<String, dynamic>> getAbilitySummary() async {
    final response = await _apiService.get(
      ApiConfig.abilitySummaryEndpoint,
    );
    return response.data as Map<String, dynamic>;
  }

  /// 获取能力趋势数据
  Future<Map<String, dynamic>> getAbilityTrend(
    String dimensionName, {
    int limit = 20,
  }) async {
    final response = await _apiService.get(
      ApiConfig.abilityTrendEndpoint(dimensionName),
      queryParameters: {'limit': limit},
    );
    return response.data as Map<String, dynamic>;
  }
}
