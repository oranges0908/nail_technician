import 'package:flutter/foundation.dart';
import '../models/service_record.dart';
import '../models/comparison_result.dart';
import '../services/service_record_service.dart';
import '../config/app_config.dart';

/// Service record state management
class ServiceRecordProvider extends ChangeNotifier {
  final ServiceRecordService _service;

  ServiceRecordProvider({ServiceRecordService? service})
      : _service = service ?? ServiceRecordService();

  List<ServiceRecord> _records = [];
  ServiceRecord? _selectedRecord;
  ComparisonResult? _comparison;
  bool _isLoading = false;
  bool _isAnalyzing = false;
  String? _error;
  int _total = 0;
  bool _hasMore = true;
  String? _statusFilter;

  // Getters
  List<ServiceRecord> get records => _records;
  ServiceRecord? get selectedRecord => _selectedRecord;
  ComparisonResult? get comparison => _comparison;
  bool get isLoading => _isLoading;
  bool get isAnalyzing => _isAnalyzing;
  String? get error => _error;
  int get total => _total;
  bool get hasMore => _hasMore;
  String? get statusFilter => _statusFilter;

  /// Load service record list
  Future<void> loadRecords({int? customerId, String? status}) async {
    _isLoading = true;
    _error = null;
    if (status != null) _statusFilter = status.isEmpty ? null : status;
    notifyListeners();

    try {
      final records = await _service.getServiceRecords(
        customerId: customerId,
        status: _statusFilter,
        skip: 0,
        limit: AppConfig.defaultPageSize,
      );
      _records = records;
      _total = records.length;
      _hasMore = records.length >= AppConfig.defaultPageSize;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Load more
  Future<void> loadMore({int? customerId}) async {
    if (_isLoading || !_hasMore) return;

    _isLoading = true;
    notifyListeners();

    try {
      final records = await _service.getServiceRecords(
        customerId: customerId,
        status: _statusFilter,
        skip: _records.length,
        limit: AppConfig.defaultPageSize,
      );
      _records.addAll(records);
      _hasMore = records.length >= AppConfig.defaultPageSize;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Create service record
  Future<ServiceRecord?> createRecord({
    required int customerId,
    int? designPlanId,
    required String serviceDate,
    int? serviceDuration,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final record = await _service.createServiceRecord(
        customerId: customerId,
        designPlanId: designPlanId,
        serviceDate: serviceDate,
        serviceDuration: serviceDuration,
        notes: notes,
      );
      _records.insert(0, record);
      _total++;
      _isLoading = false;
      notifyListeners();
      return record;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  /// Complete service
  Future<ServiceRecord?> completeService(
    int id, {
    required String actualImagePath,
    required int serviceDuration,
    String? materialsUsed,
    String? artistReview,
    String? customerFeedback,
    int? customerSatisfaction,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final record = await _service.completeService(
        id,
        actualImagePath: actualImagePath,
        serviceDuration: serviceDuration,
        materialsUsed: materialsUsed,
        artistReview: artistReview,
        customerFeedback: customerFeedback,
        customerSatisfaction: customerSatisfaction,
        notes: notes,
      );
      final index = _records.indexWhere((r) => r.id == id);
      if (index >= 0) _records[index] = record;
      _selectedRecord = record;
      _isLoading = false;
      notifyListeners();
      return record;
    } catch (e) {
      _error = _parseError(e);
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  /// Get service record detail
  Future<void> getRecordDetail(int id) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _selectedRecord = await _service.getServiceRecord(id);
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Get comparison analysis result
  Future<void> getComparison(int serviceId) async {
    _isAnalyzing = true;
    notifyListeners();

    try {
      _comparison = await _service.getComparison(serviceId);
    } catch (e) {
      _comparison = null;
    } finally {
      _isAnalyzing = false;
      notifyListeners();
    }
  }

  /// Trigger AI analysis
  Future<ComparisonResult?> triggerAnalysis(int serviceId) async {
    _isAnalyzing = true;
    _error = null;
    notifyListeners();

    try {
      _comparison = await _service.triggerAnalysis(serviceId);
      _isAnalyzing = false;
      notifyListeners();
      return _comparison;
    } catch (e) {
      _error = _parseError(e);
      _isAnalyzing = false;
      notifyListeners();
      return null;
    }
  }

  /// Delete service record
  Future<bool> deleteRecord(int id) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _service.deleteServiceRecord(id);
      _records.removeWhere((r) => r.id == id);
      _total--;
      if (_selectedRecord?.id == id) {
        _selectedRecord = null;
        _comparison = null;
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

  void clearSelectedRecord() {
    _selectedRecord = null;
    _comparison = null;
  }

  String _parseError(dynamic error) {
    final msg = error.toString();
    if (msg.contains('404')) {
      return 'Service record not found';
    } else if (msg.contains('400')) {
      return 'Invalid request parameters';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return 'Network connection failed, please check your network settings';
    } else if (msg.contains('timeout')) {
      return 'Request timed out, please retry';
    }
    return 'Operation failed, please retry';
  }
}
