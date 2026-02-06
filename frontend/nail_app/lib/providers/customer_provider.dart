import 'package:flutter/foundation.dart';
import '../models/customer.dart';
import '../models/customer_profile.dart';
import '../services/customer_service.dart';
import '../config/app_config.dart';

/// 客户管理状态
class CustomerProvider extends ChangeNotifier {
  final CustomerService _service = CustomerService();

  List<Customer> _customers = [];
  Customer? _selectedCustomer;
  bool _isLoading = false;
  String? _error;
  int _total = 0;
  String _searchQuery = '';
  bool _hasMore = true;

  // Getters
  List<Customer> get customers => _customers;
  Customer? get selectedCustomer => _selectedCustomer;
  bool get isLoading => _isLoading;
  String? get error => _error;
  int get total => _total;
  String get searchQuery => _searchQuery;
  bool get hasMore => _hasMore;

  /// 加载客户列表（首次/刷新）
  Future<void> loadCustomers({String? search}) async {
    _isLoading = true;
    _error = null;
    if (search != null) _searchQuery = search;
    notifyListeners();

    try {
      final response = await _service.getCustomers(
        skip: 0,
        limit: AppConfig.defaultPageSize,
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        isActive: true,
      );
      _customers = response.customers;
      _total = response.total;
      _hasMore = _customers.length < _total;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 加载更多（分页）
  Future<void> loadMore() async {
    if (_isLoading || !_hasMore) return;

    _isLoading = true;
    notifyListeners();

    try {
      final response = await _service.getCustomers(
        skip: _customers.length,
        limit: AppConfig.defaultPageSize,
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        isActive: true,
      );
      _customers.addAll(response.customers);
      _total = response.total;
      _hasMore = _customers.length < _total;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 获取客户详情
  Future<void> getCustomerDetail(int customerId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _selectedCustomer = await _service.getCustomer(customerId);
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 创建客户
  Future<Customer?> createCustomer({
    required String name,
    required String phone,
    String? email,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final customer = await _service.createCustomer(
        name: name,
        phone: phone,
        email: email,
        notes: notes,
      );
      _customers.insert(0, customer);
      _total++;
      _isLoading = false;
      notifyListeners();
      return customer;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  /// 更新客户
  Future<Customer?> updateCustomer(int customerId, {
    String? name,
    String? phone,
    String? email,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final updated = await _service.updateCustomer(
        customerId,
        name: name,
        phone: phone,
        email: email,
        notes: notes,
      );
      final index = _customers.indexWhere((c) => c.id == customerId);
      if (index >= 0) {
        _customers[index] = updated;
      }
      if (_selectedCustomer?.id == customerId) {
        _selectedCustomer = updated;
      }
      _isLoading = false;
      notifyListeners();
      return updated;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  /// 删除客户
  Future<bool> deleteCustomer(int customerId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _service.deleteCustomer(customerId);
      _customers.removeWhere((c) => c.id == customerId);
      _total--;
      if (_selectedCustomer?.id == customerId) {
        _selectedCustomer = null;
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 更新客户档案
  Future<CustomerProfile?> updateProfile(
    int customerId,
    Map<String, dynamic> profileData,
  ) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final profile = await _service.updateProfile(customerId, profileData);
      // Refresh detail if viewing this customer
      if (_selectedCustomer?.id == customerId) {
        await getCustomerDetail(customerId);
      }
      _isLoading = false;
      notifyListeners();
      return profile;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  void clearSelectedCustomer() {
    _selectedCustomer = null;
  }

  String _parseError(dynamic error) {
    final msg = error.toString();
    if (msg.contains('409')) {
      return '该手机号已被使用';
    } else if (msg.contains('404')) {
      return '客户不存在';
    } else if (msg.contains('422')) {
      return '输入信息格式不正确';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return '网络连接失败，请检查网络设置';
    } else if (msg.contains('timeout')) {
      return '请求超时，请重试';
    }
    return '操作失败，请重试';
  }
}
