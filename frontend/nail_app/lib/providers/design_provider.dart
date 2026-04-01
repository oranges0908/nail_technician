import 'package:flutter/foundation.dart';
import '../models/design_plan.dart';
import '../services/design_service.dart';
import '../config/app_config.dart';

/// Design plan state management
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

  /// Load design plan list
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

  /// Load more
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

  /// AI-generate a design plan
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

  /// Refine a design plan
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

  /// Get design plan detail
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

  /// Get version history
  Future<void> getVersions(int id) async {
    try {
      _designVersions = await _service.getDesignVersions(id);
      notifyListeners();
    } catch (e) {
      _designVersions = [];
    }
  }

  /// Update design plan title
  Future<bool> updateDesignTitle(int id, String title) async {
    try {
      final updated = await _service.updateDesign(id, title: title);
      final index = _designs.indexWhere((d) => d.id == id);
      if (index != -1) {
        _designs[index] = updated;
      }
      if (_selectedDesign?.id == id) {
        _selectedDesign = updated;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _error = _parseError(e);
      notifyListeners();
      return false;
    }
  }

  /// Archive a design plan
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

  /// Delete a design plan
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
      return 'Design plan not found';
    } else if (msg.contains('SocketException') || msg.contains('Connection')) {
      return 'Network connection failed, please check your network settings';
    } else if (msg.contains('timeout')) {
      return 'Request timed out, please retry';
    } else if (msg.contains('500')) {
      return 'AI generation failed, please try again later';
    }
    return 'Operation failed, please retry';
  }
}
