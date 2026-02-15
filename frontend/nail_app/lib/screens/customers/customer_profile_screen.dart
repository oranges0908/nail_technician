import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/customer_provider.dart';
import '../../utils/constants.dart';

/// 客户档案编辑页面
class CustomerProfileScreen extends StatefulWidget {
  final int customerId;

  const CustomerProfileScreen({Key? key, required this.customerId})
      : super(key: key);

  @override
  State<CustomerProfileScreen> createState() => _CustomerProfileScreenState();
}

class _CustomerProfileScreenState extends State<CustomerProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isSubmitting = false;

  // 甲型
  String? _nailShape;
  String? _nailLength;
  final _nailConditionController = TextEditingController();

  // 颜色偏好
  final _colorPrefController = TextEditingController();
  List<String> _colorPreferences = [];
  final _colorDislikeController = TextEditingController();
  List<String> _colorDislikes = [];

  // 风格偏好
  List<String> _stylePreferences = [];
  final _patternPrefController = TextEditingController();

  // 禁忌
  final _allergiesController = TextEditingController();
  final _prohibitionsController = TextEditingController();

  // 维护偏好
  String? _maintenancePreference;

  static const _nailShapes = ['椭圆形', '方形', '圆形', '杏仁形', '尖形'];
  static const _nailLengths = ['短', '中等', '长'];
  static const _styleOptions = ['简约', '华丽', '可爱', '性感', '清新', '复古', '潮流'];
  static const _maintenanceOptions = ['持久性', '易维护', '快速'];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadProfile();
    });
  }

  Future<void> _loadProfile() async {
    final provider = context.read<CustomerProvider>();
    await provider.getCustomerDetail(widget.customerId);
    final profile = provider.selectedCustomer?.profile;
    if (profile != null) {
      setState(() {
        _nailShape = profile.nailShape;
        _nailLength = profile.nailLength;
        _nailConditionController.text = profile.nailCondition ?? '';
        _colorPreferences = List<String>.from(profile.colorPreferences ?? []);
        _colorDislikes = List<String>.from(profile.colorDislikes ?? []);
        _stylePreferences = List<String>.from(profile.stylePreferences ?? []);
        _patternPrefController.text = profile.patternPreferences ?? '';
        _allergiesController.text = profile.allergies ?? '';
        _prohibitionsController.text = profile.prohibitions ?? '';
        _maintenancePreference = profile.maintenancePreference;
      });
    }
  }

  @override
  void dispose() {
    _nailConditionController.dispose();
    _colorPrefController.dispose();
    _colorDislikeController.dispose();
    _patternPrefController.dispose();
    _allergiesController.dispose();
    _prohibitionsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/customers/${widget.customerId}'),
        ),
        title: const Text('客户档案'),
      ),
      body: Consumer<CustomerProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading && provider.selectedCustomer == null) {
            return const Center(child: CircularProgressIndicator());
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 甲型信息
                  _buildSectionHeader('甲型信息', Icons.spa_outlined),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    value: _nailShape,
                    decoration: const InputDecoration(labelText: '甲形'),
                    items: _nailShapes
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (v) => setState(() => _nailShape = v),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _nailLength,
                    decoration: const InputDecoration(labelText: '甲长'),
                    items: _nailLengths
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (v) => setState(() => _nailLength = v),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _nailConditionController,
                    decoration: const InputDecoration(
                      labelText: '甲况描述',
                      hintText: '如：指甲质地良好，无明显问题',
                    ),
                    maxLines: 2,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                  ),
                  const SizedBox(height: 24),

                  // 颜色偏好
                  _buildSectionHeader('颜色偏好', Icons.palette_outlined),
                  const SizedBox(height: 8),
                  _buildTagInput(
                    controller: _colorPrefController,
                    tags: _colorPreferences,
                    label: '喜欢的颜色',
                    hint: '输入颜色后按回车添加',
                    onAdd: (tag) => setState(() => _colorPreferences.add(tag)),
                    onRemove: (tag) => setState(() => _colorPreferences.remove(tag)),
                  ),
                  const SizedBox(height: 12),
                  _buildTagInput(
                    controller: _colorDislikeController,
                    tags: _colorDislikes,
                    label: '不喜欢的颜色',
                    hint: '输入颜色后按回车添加',
                    onAdd: (tag) => setState(() => _colorDislikes.add(tag)),
                    onRemove: (tag) => setState(() => _colorDislikes.remove(tag)),
                    chipColor: ThemeConfig.errorColor.withOpacity(0.1),
                  ),
                  const SizedBox(height: 24),

                  // 风格偏好
                  _buildSectionHeader('风格偏好', Icons.style_outlined),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _styleOptions.map((style) {
                      final selected = _stylePreferences.contains(style);
                      return FilterChip(
                        label: Text(style),
                        selected: selected,
                        selectedColor: ThemeConfig.accentColor.withOpacity(0.2),
                        onSelected: (val) {
                          setState(() {
                            if (val) {
                              _stylePreferences.add(style);
                            } else {
                              _stylePreferences.remove(style);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _patternPrefController,
                    decoration: const InputDecoration(
                      labelText: '图案偏好',
                      hintText: '如：喜欢珍珠、碎钻装饰',
                    ),
                    maxLines: 2,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                  ),
                  const SizedBox(height: 24),

                  // 过敏与禁忌
                  _buildSectionHeader('过敏与禁忌', Icons.warning_amber_outlined),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _allergiesController,
                    decoration: const InputDecoration(
                      labelText: '过敏信息',
                      hintText: '如：对某些胶水过敏',
                    ),
                    maxLines: 2,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _prohibitionsController,
                    decoration: const InputDecoration(
                      labelText: '禁忌事项',
                      hintText: '如：不接受过长指甲',
                    ),
                    maxLines: 2,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                  ),
                  const SizedBox(height: 24),

                  // 维护偏好
                  _buildSectionHeader('维护偏好', Icons.build_outlined),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    value: _maintenancePreference,
                    decoration: const InputDecoration(labelText: '维护偏好'),
                    items: _maintenanceOptions
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (v) => setState(() => _maintenancePreference = v),
                  ),
                  const SizedBox(height: 32),

                  // 保存按钮
                  SizedBox(
                    height: Constants.largeButtonHeight,
                    child: ElevatedButton(
                      onPressed: _isSubmitting ? null : _submit,
                      child: _isSubmitting
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Text(Constants.saveButton),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: ThemeConfig.primaryColor),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildTagInput({
    required TextEditingController controller,
    required List<String> tags,
    required String label,
    required String hint,
    required Function(String) onAdd,
    required Function(String) onRemove,
    Color? chipColor,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: controller,
          decoration: InputDecoration(
            labelText: label,
            hintText: hint,
            suffixIcon: IconButton(
              icon: const Icon(Icons.add),
              onPressed: () {
                final text = controller.text.trim();
                if (text.isNotEmpty && !tags.contains(text)) {
                  onAdd(text);
                  controller.clear();
                }
              },
            ),
          ),
          onSubmitted: (value) {
            final text = value.trim();
            if (text.isNotEmpty && !tags.contains(text)) {
              onAdd(text);
              controller.clear();
            }
          },
        ),
        if (tags.isNotEmpty) ...[
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: tags
                .map((tag) => Chip(
                      label: Text(tag, style: const TextStyle(fontSize: 12)),
                      backgroundColor: chipColor,
                      deleteIcon: const Icon(Icons.close, size: 16),
                      onDeleted: () => onRemove(tag),
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ))
                .toList(),
          ),
        ],
      ],
    );
  }

  Future<void> _submit() async {
    setState(() => _isSubmitting = true);

    final profileData = <String, dynamic>{};

    if (_nailShape != null) profileData['nail_shape'] = _nailShape;
    if (_nailLength != null) profileData['nail_length'] = _nailLength;
    if (_nailConditionController.text.isNotEmpty) {
      profileData['nail_condition'] = _nailConditionController.text.trim();
    }
    if (_colorPreferences.isNotEmpty) {
      profileData['color_preferences'] = _colorPreferences;
    }
    if (_colorDislikes.isNotEmpty) {
      profileData['color_dislikes'] = _colorDislikes;
    }
    if (_stylePreferences.isNotEmpty) {
      profileData['style_preferences'] = _stylePreferences;
    }
    if (_patternPrefController.text.isNotEmpty) {
      profileData['pattern_preferences'] = _patternPrefController.text.trim();
    }
    if (_allergiesController.text.isNotEmpty) {
      profileData['allergies'] = _allergiesController.text.trim();
    }
    if (_prohibitionsController.text.isNotEmpty) {
      profileData['prohibitions'] = _prohibitionsController.text.trim();
    }
    if (_maintenancePreference != null) {
      profileData['maintenance_preference'] = _maintenancePreference;
    }

    final provider = context.read<CustomerProvider>();
    final result = await provider.updateProfile(widget.customerId, profileData);

    if (result != null) {
      context.go('/customers/${widget.customerId}');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text(Constants.updateSuccess)),
      );
    } else if (provider.error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(provider.error!)),
      );
    }

    if (mounted) {
      setState(() => _isSubmitting = false);
    }
  }
}
