import 'package:flutter/foundation.dart';
import '../services/ability_service.dart';

/// 能力分析状态管理
class AbilityProvider extends ChangeNotifier {
  final AbilityService _service = AbilityService();

  // 雷达图数据
  List<String> _dimensions = [];
  List<double> _scores = [];
  double _avgScore = 0.0;
  int _totalRecords = 0;

  // 能力总结
  List<Map<String, dynamic>> _strengths = [];
  List<Map<String, dynamic>> _improvements = [];
  int _totalServices = 0;

  // 趋势数据
  String? _trendDimensionName;
  List<Map<String, dynamic>> _trendDataPoints = [];

  // 状态
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

  /// 加载能力概览（雷达图 + 总结）
  Future<void> loadAbilityOverview() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // 并行加载统计和总结
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

  /// 加载指定维度的趋势数据
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

  /// 初始化能力维度
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
      return '未找到评分记录';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return '网络连接失败，请检查网络设置';
    } else if (msg.contains('timeout')) {
      return '请求超时，请重试';
    }
    return '加载失败，请重试';
  }
}
