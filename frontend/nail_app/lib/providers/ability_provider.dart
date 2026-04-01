import 'package:flutter/foundation.dart';
import '../services/ability_service.dart';

/// Ability analysis state management
class AbilityProvider extends ChangeNotifier {
  final AbilityService _service;

  AbilityProvider({AbilityService? service})
      : _service = service ?? AbilityService();

  // Radar chart data
  List<String> _dimensions = [];
  List<double> _scores = [];
  double _avgScore = 0.0;
  int _totalRecords = 0;

  // Ability summary
  List<Map<String, dynamic>> _strengths = [];
  List<Map<String, dynamic>> _improvements = [];
  int _totalServices = 0;

  // Trend data
  String? _trendDimensionName;
  List<Map<String, dynamic>> _trendDataPoints = [];

  // Status
  bool _isLoading = false;
  bool _isTrendLoading = false;
  String? _error;

  // Getters
  List<String> get dimensions => _dimensions;
  List<double> get scores => _scores;
  double get avgScore => _avgScore;
  int get totalRecords => _totalRecords;
  List<Map<String, dynamic>> get strengths => _strengths;
  List<Map<String, dynamic>> get improvements => _improvements;
  int get totalServices => _totalServices;
  String? get trendDimensionName => _trendDimensionName;
  List<Map<String, dynamic>> get trendDataPoints => _trendDataPoints;
  bool get isLoading => _isLoading;
  bool get isTrendLoading => _isTrendLoading;
  String? get error => _error;
  bool get hasData => _dimensions.isNotEmpty && _totalRecords > 0;

  /// Load ability overview (radar chart + summary)
  Future<void> loadAbilityOverview() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Load stats and summary in parallel
      final results = await Future.wait([
        _service.getAbilityStats(),
        _service.getAbilitySummary(),
      ]);

      final stats = results[0];
      _dimensions = List<String>.from(stats['dimensions'] ?? []);
      _scores = (stats['scores'] as List?)
              ?.map((s) => (s as num).toDouble())
              .toList() ??
          [];
      _avgScore = (stats['avg_score'] as num?)?.toDouble() ?? 0.0;
      _totalRecords = stats['total_records'] as int? ?? 0;

      final summary = results[1];
      _strengths = List<Map<String, dynamic>>.from(
        (summary['strengths'] as List?)?.map((e) => Map<String, dynamic>.from(e)) ?? [],
      );
      _improvements = List<Map<String, dynamic>>.from(
        (summary['improvements'] as List?)?.map((e) => Map<String, dynamic>.from(e)) ?? [],
      );
      _totalServices = summary['total_services'] as int? ?? 0;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Load trend data for a specific dimension
  Future<void> loadTrend(String dimensionName, {int limit = 20}) async {
    _isTrendLoading = true;
    _trendDimensionName = dimensionName;
    _trendDataPoints = [];
    notifyListeners();

    try {
      final data = await _service.getAbilityTrend(dimensionName, limit: limit);
      _trendDataPoints = List<Map<String, dynamic>>.from(
        (data['data_points'] as List?)?.map((e) => Map<String, dynamic>.from(e)) ?? [],
      );
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isTrendLoading = false;
      notifyListeners();
    }
  }

  /// Initialize ability dimensions
  Future<bool> initializeDimensions() async {
    try {
      await _service.initializeDimensions();
      await loadAbilityOverview();
      return true;
    } catch (e) {
      _error = _parseError(e);
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
      return 'No score records found';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return 'Network connection failed, please check your network settings';
    } else if (msg.contains('timeout')) {
      return 'Request timed out, please retry';
    }
    return 'Failed to load, please retry';
  }
}
