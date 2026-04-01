import 'package:flutter/foundation.dart';
import '../models/inspiration_image.dart';
import '../services/inspiration_service.dart';
import '../config/app_config.dart';

/// Inspiration gallery state management
class InspirationProvider extends ChangeNotifier {
  final InspirationService _service;

  InspirationProvider({InspirationService? service})
      : _service = service ?? InspirationService();

  List<InspirationImage> _inspirations = [];
  InspirationImage? _selectedInspiration;
  bool _isLoading = false;
  String? _error;
  int _total = 0;
  bool _hasMore = true;
  String _searchQuery = '';
  String? _selectedCategory;

  // Getters
  List<InspirationImage> get inspirations => _inspirations;
  InspirationImage? get selectedInspiration => _selectedInspiration;
  bool get isLoading => _isLoading;
  String? get error => _error;
  int get total => _total;
  bool get hasMore => _hasMore;
  String get searchQuery => _searchQuery;
  String? get selectedCategory => _selectedCategory;

  /// Load inspiration image list
  Future<void> loadInspirations({String? search, String? category}) async {
    _isLoading = true;
    _error = null;
    if (search != null) _searchQuery = search;
    if (category != null) _selectedCategory = category.isEmpty ? null : category;
    notifyListeners();

    try {
      final response = await _service.getInspirations(
        skip: 0,
        limit: AppConfig.defaultPageSize,
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        category: _selectedCategory,
      );
      _inspirations = response.inspirations;
      _total = response.total;
      _hasMore = _inspirations.length < _total;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Load more
  Future<void> loadMore() async {
    if (_isLoading || !_hasMore) return;

    _isLoading = true;
    notifyListeners();

    try {
      final response = await _service.getInspirations(
        skip: _inspirations.length,
        limit: AppConfig.defaultPageSize,
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        category: _selectedCategory,
      );
      _inspirations.addAll(response.inspirations);
      _total = response.total;
      _hasMore = _inspirations.length < _total;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Search
  Future<void> search(String query) async {
    _searchQuery = query;
    await loadInspirations();
  }

  /// Filter by category
  Future<void> filterByCategory(String? category) async {
    _selectedCategory = category;
    await loadInspirations();
  }

  /// Delete an inspiration image
  Future<bool> deleteInspiration(int id) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _service.deleteInspiration(id);
      _inspirations.removeWhere((i) => i.id == id);
      _total--;
      if (_selectedInspiration?.id == id) {
        _selectedInspiration = null;
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

  void clearError() {
    _error = null;
    notifyListeners();
  }

  String _parseError(dynamic error) {
    final msg = error.toString();
    if (msg.contains('404')) {
      return 'Inspiration image not found';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return 'Network connection failed, please check your network settings';
    } else if (msg.contains('timeout')) {
      return 'Request timed out, please retry';
    }
    return 'Operation failed, please retry';
  }
}
