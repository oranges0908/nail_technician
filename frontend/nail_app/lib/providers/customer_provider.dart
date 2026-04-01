import 'package:flutter/foundation.dart';
import '../models/customer.dart';
import '../models/customer_profile.dart';
import '../services/customer_service.dart';
import '../config/app_config.dart';

/// Customer management state
class CustomerProvider extends ChangeNotifier {
  final CustomerService _service;

  CustomerProvider({CustomerService? service})
      : _service = service ?? CustomerService();

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

  /// Load customer list (initial / refresh)
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

  /// Load more (pagination)
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

  /// Get customer detail
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

  /// Create customer
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

  /// Update customer
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

  /// Delete customer
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

  /// Update customer profile
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
      return 'This phone number is already in use';
    } else if (msg.contains('404')) {
      return 'Customer not found';
    } else if (msg.contains('422')) {
      return 'Invalid input format';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return 'Network connection failed, please check your network settings';
    } else if (msg.contains('timeout')) {
      return 'Request timed out, please retry';
    }
    return 'Operation failed, please retry';
  }
}
