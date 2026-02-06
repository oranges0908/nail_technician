import '../models/customer.dart';
import '../models/customer_profile.dart';
import '../config/api_config.dart';
import 'api_service.dart';

/// 客户管理 API 服务
class CustomerService {
  final ApiService _apiService = ApiService();

  /// 获取客户列表
  Future<CustomerListResponse> getCustomers({
    int skip = 0,
    int limit = 20,
    String? search,
    bool? isActive,
  }) async {
    final queryParams = <String, dynamic>{
      'skip': skip,
      'limit': limit,
    };
    if (search != null && search.isNotEmpty) {
      queryParams['search'] = search;
    }
    if (isActive != null) {
      queryParams['is_active'] = isActive;
    }

    final response = await _apiService.get(
      ApiConfig.customersEndpoint,
      queryParameters: queryParams,
    );
    return CustomerListResponse.fromJson(response.data);
  }

  /// 获取客户详情（含档案）
  Future<Customer> getCustomer(int customerId) async {
    final response = await _apiService.get(
      ApiConfig.customerDetailEndpoint(customerId),
    );
    return Customer.fromJson(response.data);
  }

  /// 创建客户
  Future<Customer> createCustomer({
    required String name,
    required String phone,
    String? email,
    String? notes,
  }) async {
    final data = <String, dynamic>{
      'name': name,
      'phone': phone,
    };
    if (email != null && email.isNotEmpty) data['email'] = email;
    if (notes != null && notes.isNotEmpty) data['notes'] = notes;

    final response = await _apiService.post(
      ApiConfig.customersEndpoint,
      data: data,
    );
    return Customer.fromJson(response.data);
  }

  /// 更新客户
  Future<Customer> updateCustomer(int customerId, {
    String? name,
    String? phone,
    String? email,
    String? notes,
    bool? isActive,
  }) async {
    final data = <String, dynamic>{};
    if (name != null) data['name'] = name;
    if (phone != null) data['phone'] = phone;
    if (email != null) data['email'] = email;
    if (notes != null) data['notes'] = notes;
    if (isActive != null) data['is_active'] = isActive;

    final response = await _apiService.put(
      ApiConfig.customerDetailEndpoint(customerId),
      data: data,
    );
    return Customer.fromJson(response.data);
  }

  /// 删除客户（软删除）
  Future<void> deleteCustomer(int customerId) async {
    await _apiService.delete(
      ApiConfig.customerDetailEndpoint(customerId),
    );
  }

  /// 获取客户档案
  Future<CustomerProfile> getProfile(int customerId) async {
    final response = await _apiService.get(
      ApiConfig.customerProfileEndpoint(customerId),
    );
    return CustomerProfile.fromJson(response.data);
  }

  /// 创建或更新客户档案
  Future<CustomerProfile> updateProfile(
    int customerId,
    Map<String, dynamic> profileData,
  ) async {
    final response = await _apiService.put(
      ApiConfig.customerProfileEndpoint(customerId),
      data: profileData,
    );
    return CustomerProfile.fromJson(response.data);
  }
}
