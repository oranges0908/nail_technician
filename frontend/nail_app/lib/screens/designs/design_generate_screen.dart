import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/api_config.dart';
import '../../config/theme_config.dart';
import '../../config/app_config.dart';
import '../../models/inspiration_image.dart';
import '../../providers/design_provider.dart';
import '../../providers/customer_provider.dart';
import '../../providers/inspiration_provider.dart';
import '../../utils/constants.dart';

/// AI设计生成页
class DesignGenerateScreen extends StatefulWidget {
  const DesignGenerateScreen({Key? key}) : super(key: key);

  @override
  State<DesignGenerateScreen> createState() => _DesignGenerateScreenState();
}

class _DesignGenerateScreenState extends State<DesignGenerateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _promptController = TextEditingController();
  final _titleController = TextEditingController();
  final _keywordController = TextEditingController();

  int? _selectedCustomerId;
  String _designTarget = '10nails';
  List<String> _styleKeywords = [];
  List<InspirationImage> _selectedInspirations = [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CustomerProvider>().loadCustomers();
      context.read<InspirationProvider>().loadInspirations();
    });
  }

  @override
  void dispose() {
    _promptController.dispose();
    _titleController.dispose();
    _keywordController.dispose();
    super.dispose();
  }

  void _addKeyword() {
    final keyword = _keywordController.text.trim();
    if (keyword.isNotEmpty && !_styleKeywords.contains(keyword)) {
      setState(() {
        _styleKeywords.add(keyword);
        _keywordController.clear();
      });
    }
  }

  void _removeKeyword(String keyword) {
    setState(() {
      _styleKeywords.remove(keyword);
    });
  }

  Future<void> _generate() async {
    if (!_formKey.currentState!.validate()) return;

    final provider = context.read<DesignProvider>();
    final design = await provider.generateDesign(
      prompt: _promptController.text.trim(),
      designTarget: _designTarget,
      styleKeywords: _styleKeywords.isNotEmpty ? _styleKeywords : null,
      referenceImages: _selectedInspirations.isNotEmpty
          ? _selectedInspirations.map((i) => i.imagePath).toList()
          : null,
      customerId: _selectedCustomerId,
      title: _titleController.text.trim().isNotEmpty
          ? _titleController.text.trim()
          : null,
    );

    if (design != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('设计生成成功！')),
      );
      context.go('/designs/${design.id}');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.designsRoute),
        ),
        title: const Text('AI 设计生成'),
      ),
      body: Consumer<DesignProvider>(
        builder: (context, designProvider, _) {
          return Stack(
            children: [
              SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // 错误提示
                      if (designProvider.error != null)
                        Container(
                          padding: const EdgeInsets.all(12),
                          margin: const EdgeInsets.only(bottom: 16),
                          decoration: BoxDecoration(
                            color: ThemeConfig.errorColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.error_outline,
                                  color: ThemeConfig.errorColor, size: 20),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  designProvider.error!,
                                  style: const TextStyle(
                                      color: ThemeConfig.errorColor),
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.close, size: 18),
                                onPressed: designProvider.clearError,
                                padding: EdgeInsets.zero,
                                constraints: const BoxConstraints(),
                              ),
                            ],
                          ),
                        ),

                      // 设计描述（主输入）
                      TextFormField(
                        controller: _promptController,
                        decoration: const InputDecoration(
                          labelText: '设计描述 *',
                          hintText: '描述你想要的美甲设计，例如：\n春日粉色樱花主题，渐变底色配手绘樱花花瓣，点缀金色亮片',
                          helperText: '必填，描述越详细生成效果越好',
                          prefixIcon: Icon(Icons.auto_awesome),
                          alignLabelWithHint: true,
                        ),
                        maxLines: 5,
                        keyboardType: TextInputType.multiline,
                        textInputAction: TextInputAction.newline,
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return '请输入设计描述';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      // 标题
                      TextFormField(
                        controller: _titleController,
                        decoration: const InputDecoration(
                          labelText: '方案标题',
                          hintText: '给设计方案起个名字（选填）',
                          prefixIcon: Icon(Icons.title),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // 客户选择
                      Consumer<CustomerProvider>(
                        builder: (context, customerProvider, _) {
                          return DropdownButtonFormField<int>(
                            value: _selectedCustomerId,
                            decoration: const InputDecoration(
                              labelText: '关联客户',
                              hintText: '选择客户（选填）',
                              prefixIcon: Icon(Icons.person_outline),
                            ),
                            items: [
                              const DropdownMenuItem<int>(
                                value: null,
                                child: Text('不关联客户'),
                              ),
                              ...customerProvider.customers.map(
                                (c) => DropdownMenuItem<int>(
                                  value: c.id,
                                  child: Text(c.name),
                                ),
                              ),
                            ],
                            onChanged: (value) {
                              setState(() {
                                _selectedCustomerId = value;
                              });
                            },
                          );
                        },
                      ),
                      const SizedBox(height: 16),

                      // 灵感参考图选择
                      Consumer<InspirationProvider>(
                        builder: (context, inspProvider, _) {
                          final inspirations = inspProvider.inspirations;
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.photo_library, size: 20, color: ThemeConfig.primaryColor),
                                  const SizedBox(width: 8),
                                  const Text(
                                    '参考灵感图',
                                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                                  ),
                                  const Spacer(),
                                  if (_selectedInspirations.isNotEmpty)
                                    Text(
                                      '已选 ${_selectedInspirations.length} 张',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: ThemeConfig.primaryColor,
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              if (inspirations.isEmpty)
                                Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    border: Border.all(color: ThemeConfig.dividerLight),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Center(
                                    child: Text(
                                      '暂无灵感图，可在灵感图库中上传',
                                      style: TextStyle(color: ThemeConfig.textSecondaryLight, fontSize: 13),
                                    ),
                                  ),
                                )
                              else
                                SizedBox(
                                  height: 100,
                                  child: ListView.separated(
                                    scrollDirection: Axis.horizontal,
                                    itemCount: inspirations.length,
                                    separatorBuilder: (_, __) => const SizedBox(width: 8),
                                    itemBuilder: (context, index) {
                                      final insp = inspirations[index];
                                      final selected = _selectedInspirations.any((s) => s.id == insp.id);
                                      return GestureDetector(
                                        onTap: () {
                                          setState(() {
                                            if (selected) {
                                              _selectedInspirations.removeWhere((s) => s.id == insp.id);
                                            } else {
                                              _selectedInspirations.add(insp);
                                            }
                                          });
                                        },
                                        child: Container(
                                          width: 100,
                                          decoration: BoxDecoration(
                                            borderRadius: BorderRadius.circular(8),
                                            border: Border.all(
                                              color: selected ? ThemeConfig.primaryColor : ThemeConfig.dividerLight,
                                              width: selected ? 2.5 : 1,
                                            ),
                                          ),
                                          child: ClipRRect(
                                            borderRadius: BorderRadius.circular(6),
                                            child: Stack(
                                              fit: StackFit.expand,
                                              children: [
                                                CachedNetworkImage(
                                                  imageUrl: ApiConfig.getStaticFileUrl(insp.imagePath),
                                                  fit: BoxFit.cover,
                                                  placeholder: (_, __) => const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                                                  errorWidget: (_, __, ___) => const Icon(Icons.broken_image),
                                                ),
                                                if (selected)
                                                  Container(
                                                    color: ThemeConfig.primaryColor.withOpacity(0.3),
                                                    child: const Center(
                                                      child: Icon(Icons.check_circle, color: Colors.white, size: 28),
                                                    ),
                                                  ),
                                              ],
                                            ),
                                          ),
                                        ),
                                      );
                                    },
                                  ),
                                ),
                            ],
                          );
                        },
                      ),
                      const SizedBox(height: 16),

                      // 设计目标
                      const Text(
                        '设计目标',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        children: AppConfig.designTargets.map((target) {
                          final label =
                              AppConfig.designTargetLabels[target] ?? target;
                          return ChoiceChip(
                            label: Text(label),
                            selected: _designTarget == target,
                            onSelected: (_) {
                              setState(() {
                                _designTarget = target;
                              });
                            },
                            selectedColor: ThemeConfig.primaryLightColor,
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 16),

                      // 风格关键词
                      Row(
                        children: [
                          Expanded(
                            child: TextFormField(
                              controller: _keywordController,
                              decoration: const InputDecoration(
                                labelText: '风格关键词',
                                hintText: '如：优雅、清新、复古',
                                prefixIcon: Icon(Icons.style),
                              ),
                              onFieldSubmitted: (_) => _addKeyword(),
                            ),
                          ),
                          const SizedBox(width: 8),
                          IconButton(
                            onPressed: _addKeyword,
                            icon: const Icon(Icons.add_circle),
                            color: ThemeConfig.primaryColor,
                          ),
                        ],
                      ),
                      if (_styleKeywords.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: _styleKeywords
                              .map((kw) => Chip(
                                    label: Text(kw,
                                        style: const TextStyle(fontSize: 12)),
                                    onDeleted: () => _removeKeyword(kw),
                                    materialTapTargetSize:
                                        MaterialTapTargetSize.shrinkWrap,
                                    visualDensity: VisualDensity.compact,
                                  ))
                              .toList(),
                        ),
                      ],

                      const SizedBox(height: 32),

                      // 生成按钮
                      SizedBox(
                        height: Constants.largeButtonHeight,
                        child: ElevatedButton.icon(
                          onPressed:
                              designProvider.isGenerating ? null : _generate,
                          icon: const Icon(Icons.auto_awesome),
                          label: Text(designProvider.isGenerating
                              ? 'AI 生成中...'
                              : '生成设计'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // 生成中遮罩
              if (designProvider.isGenerating)
                Container(
                  color: Colors.black.withOpacity(0.3),
                  child: Center(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const CircularProgressIndicator(),
                            const SizedBox(height: 16),
                            const Text(
                              'AI 正在生成设计...',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '这可能需要 10-30 秒',
                              style: TextStyle(
                                color: ThemeConfig.textSecondaryLight,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}
