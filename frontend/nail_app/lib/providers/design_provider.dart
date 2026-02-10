import 'package:flutter/foundation.dart';
import '../models/design_plan.dart';
import '../services/design_service.dart';
import '../config/app_config.dart';

/// 设计方案状态管理
class DesignProvider extends ChangeNotifier {
  final DesignService _service;

  DesignProvider({DesignService? service})
      : _service = service ?? DesignService();

  List<DesignPlan> _designs = [];
  DesignPlan? _selectedDesign;
  List<DesignPlan> _designVersions = [];
  bool _isLoading = false;
  bool _isGenerating = false;
  String? _error;
  int _total = 0;
  bool _hasMore = true;

  // Getters
  List<DesignPlan> get designs => _designs;
  DesignPlan? get selectedDesign => _selectedDesign;
  List<DesignPlan> get designVersions => _designVersions;
  bool get isLoading => _isLoading;
  bool get isGenerating => _isGenerating;
  String? get error => _error;
  int get total => _total;
  bool get hasMore => _hasMore;

  /// 加载设计方案列表
  Future<void> loadDesigns({int? customerId, String? search}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _service.getDesigns(
        skip: 0,
        limit: AppConfig.defaultPageSize,
        customerId: customerId,
        search: search,
        isArchived: 0,
      );
      _designs = response.designs;
      _total = response.total;
      _hasMore = _designs.length < _total;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 加载更多
  Future<void> loadMore({int? customerId, String? search}) async {
    if (_isLoading || !_hasMore) return;

    _isLoading = true;
    notifyListeners();

    try {
      final response = await _service.getDesigns(
        skip: _designs.length,
        limit: AppConfig.defaultPageSize,
        customerId: customerId,
        search: search,
        isArchived: 0,
      );
      _designs.addAll(response.designs);
      _total = response.total;
      _hasMore = _designs.length < _total;
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// AI生成设计方案
  Future<DesignPlan?> generateDesign({
    required String prompt,
    List<String>? referenceImages,
    String designTarget = '10nails',
    List<String>? styleKeywords,
    int? customerId,
    String? title,
    String? notes,
  }) async {
    _isGenerating = true;
    _error = null;
    notifyListeners();

    try {
      final design = await _service.generateDesign(
        prompt: prompt,
        referenceImages: referenceImages,
        designTarget: designTarget,
        styleKeywords: styleKeywords,
        customerId: customerId,
        title: title,
        notes: notes,
      );
      _designs.insert(0, design);
      _total++;
      _selectedDesign = design;
      _isGenerating = false;
      notifyListeners();
      return design;
    } catch (e) {
      _error = _parseError(e);
      _isGenerating = false;
      notifyListeners();
      return null;
    }
  }

  /// 优化设计方案
  Future<DesignPlan?> refineDesign(int designId, String instruction) async {
    _isGenerating = true;
    _error = null;
    notifyListeners();

    try {
      final design = await _service.refineDesign(designId, instruction);
      _designs.insert(0, design);
      _total++;
      _selectedDesign = design;
      _isGenerating = false;
      notifyListeners();
      return design;
    } catch (e) {
      _error = _parseError(e);
      _isGenerating = false;
      notifyListeners();
      return null;
    }
  }

  /// 获取设计方案详情
  Future<void> getDesignDetail(int id) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _selectedDesign = await _service.getDesign(id);
    } catch (e) {
      _error = _parseError(e);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 获取版本历史
  Future<void> getVersions(int id) async {
    try {
      _designVersions = await _service.getDesignVersions(id);
      notifyListeners();
    } catch (e) {
      _designVersions = [];
    }
  }

  /// 归档设计方案
  Future<bool> archiveDesign(int id) async {
    try {
      await _service.archiveDesign(id);
      _designs.removeWhere((d) => d.id == id);
      _total--;
      if (_selectedDesign?.id == id) _selectedDesign = null;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _parseError(e);
      notifyListeners();
      return false;
    }
  }

  /// 删除设计方案
  Future<bool> deleteDesign(int id) async {
    try {
      await _service.deleteDesign(id);
      _designs.removeWhere((d) => d.id == id);
      _total--;
      if (_selectedDesign?.id == id) _selectedDesign = null;
      notifyListeners();
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

  void clearSelectedDesign() {
    _selectedDesign = null;
    _designVersions = [];
  }

  String _parseError(dynamic error) {
    final msg = error.toString();
    if (msg.contains('404')) {
      return '设计方案不存在';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return '网络连接失败，请检查网络设置';
    } else if (msg.contains('timeout')) {
      return '请求超时，请重试';
    } else if (msg.contains('500')) {
      return 'AI生成失败，请稍后重试';
    }
    return '操作失败，请重试';
  }
}
