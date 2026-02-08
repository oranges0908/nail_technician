import '../models/inspiration_image.dart';
import '../config/api_config.dart';
import 'api_service.dart';

/// 灵感图库服务
class InspirationService {
  final ApiService _apiService = ApiService();

  /// 获取灵感图列表
  Future<InspirationImageListResponse> getInspirations({
    int skip = 0,
    int limit = 20,
    String? category,
    List<String>? tags,
    String? search,
  }) async {
    final queryParams = <String, dynamic>{
      'skip': skip,
      'limit': limit,
    };
    if (category != null && category.isNotEmpty) {
      queryParams['category'] = category;
    }
    if (tags != null && tags.isNotEmpty) {
      queryParams['tags'] = tags;
    }
    if (search != null && search.isNotEmpty) {
      queryParams['search'] = search;
    }

    final response = await _apiService.get(
      ApiConfig.inspirationsEndpoint,
      queryParameters: queryParams,
    );
    return InspirationImageListResponse.fromJson(response.data);
  }

  /// 获取灵感图详情
  Future<InspirationImage> getInspiration(int id) async {
    final response = await _apiService.get(
      ApiConfig.inspirationDetailEndpoint(id),
    );
    return InspirationImage.fromJson(response.data);
  }

  /// 创建灵感图
  Future<InspirationImage> createInspiration({
    required String imagePath,
    String? title,
    String? description,
    List<String>? tags,
    String? category,
    String? sourceUrl,
    String? sourcePlatform,
  }) async {
    final data = <String, dynamic>{
      'image_path': imagePath,
    };
    if (title != null && title.isNotEmpty) data['title'] = title;
    if (description != null && description.isNotEmpty) {
      data['description'] = description;
    }
    if (tags != null && tags.isNotEmpty) data['tags'] = tags;
    if (category != null && category.isNotEmpty) data['category'] = category;
    if (sourceUrl != null && sourceUrl.isNotEmpty) {
      data['source_url'] = sourceUrl;
    }
    if (sourcePlatform != null && sourcePlatform.isNotEmpty) {
      data['source_platform'] = sourcePlatform;
    }

    final response = await _apiService.post(
      ApiConfig.inspirationsEndpoint,
      data: data,
    );
    return InspirationImage.fromJson(response.data);
  }

  /// 删除灵感图
  Future<void> deleteInspiration(int id) async {
    await _apiService.delete(
      ApiConfig.inspirationDetailEndpoint(id),
    );
  }

  /// 标记使用灵感图
  Future<void> useInspiration(int id) async {
    await _apiService.post(
      '${ApiConfig.inspirationDetailEndpoint(id)}/use',
    );
  }
}
