import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/theme_config.dart';
import '../../config/api_config.dart';
import '../../config/app_config.dart';
import '../../providers/design_provider.dart';
import '../../models/design_plan.dart';
import '../../utils/constants.dart';
import 'package:intl/intl.dart';

/// 设计方案列表页
class DesignListScreen extends StatefulWidget {
  const DesignListScreen({Key? key}) : super(key: key);

  @override
  State<DesignListScreen> createState() => _DesignListScreenState();
}

class _DesignListScreenState extends State<DesignListScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DesignProvider>().loadDesigns();
    });
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      context.read<DesignProvider>().loadMore(
            search: _searchController.text.isNotEmpty
                ? _searchController.text
                : null,
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.homeRoute),
        ),
        title: const Text('设计方案'),
      ),
      body: Column(
        children: [
          // 搜索栏
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: '搜索设计方案...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          context.read<DesignProvider>().loadDesigns();
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(Constants.largeRadius),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              onChanged: (query) {
                context
                    .read<DesignProvider>()
                    .loadDesigns(search: query.isNotEmpty ? query : null);
              },
            ),
          ),

          // 列表
          Expanded(
            child: Consumer<DesignProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading && provider.designs.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (provider.error != null && provider.designs.isEmpty) {
                  return _buildErrorView(provider);
                }

                if (provider.designs.isEmpty) {
                  return _buildEmptyView();
                }

                return RefreshIndicator(
                  onRefresh: () => provider.loadDesigns(),
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount:
                        provider.designs.length + (provider.hasMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == provider.designs.length) {
                        return const Padding(
                          padding: EdgeInsets.all(16),
                          child: Center(child: CircularProgressIndicator()),
                        );
                      }
                      return _buildDesignCard(provider.designs[index]);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.go('/designs/generate'),
        icon: const Icon(Icons.auto_awesome),
        label: const Text('AI 生成'),
      ),
    );
  }

  Widget _buildDesignCard(DesignPlan design) {
    final dateStr = DateFormat('yyyy-MM-dd').format(design.createdAt);
    final targetLabel =
        AppConfig.designTargetLabels[design.designTarget] ?? design.designTarget;
    final difficultyLabel =
        AppConfig.difficultyLabels[design.difficultyLevel] ??
            design.difficultyLevel;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => context.go('/designs/${design.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // 缩略图
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: CachedNetworkImage(
                  imageUrl: ApiConfig.getStaticFileUrl(
                      design.generatedImagePath),
                  width: 80,
                  height: 80,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => Container(
                    width: 80,
                    height: 80,
                    color: ThemeConfig.dividerLight,
                    child: const Center(
                        child: CircularProgressIndicator(strokeWidth: 2)),
                  ),
                  errorWidget: (context, url, error) => Container(
                    width: 80,
                    height: 80,
                    color: ThemeConfig.dividerLight,
                    child: const Icon(Icons.broken_image),
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // 信息
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            design.title ?? '设计方案 #${design.id}',
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 15,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        SizedBox(
                          width: 28,
                          height: 28,
                          child: IconButton(
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                            icon: Icon(Icons.edit_outlined, size: 16,
                                color: ThemeConfig.textSecondaryLight),
                            onPressed: () => _showRenameDialog(design),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      dateStr,
                      style: TextStyle(
                        fontSize: 12,
                        color: ThemeConfig.textSecondaryLight,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        if (targetLabel != null) _buildTag(targetLabel),
                        if (difficultyLabel != null) ...[
                          const SizedBox(width: 6),
                          _buildTag(difficultyLabel),
                        ],
                        if (design.version > 1) ...[
                          const SizedBox(width: 6),
                          _buildTag('v${design.version}',
                              color: ThemeConfig.infoColor),
                        ],
                      ],
                    ),
                  ],
                ),
              ),

              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTag(String text, {Color? color}) {
    final c = color ?? ThemeConfig.primaryColor;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: c.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(fontSize: 10, color: c),
      ),
    );
  }

  void _showRenameDialog(DesignPlan design) {
    final controller = TextEditingController(
      text: design.title ?? '设计方案 #${design.id}',
    );
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('重命名'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: '输入新名称'),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(Constants.cancelButton),
          ),
          TextButton(
            onPressed: () async {
              final title = controller.text.trim();
              if (title.isEmpty) return;
              Navigator.pop(context);
              await context
                  .read<DesignProvider>()
                  .updateDesignTitle(design.id, title);
            },
            child: const Text(Constants.confirmButton),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.brush_outlined,
              size: 64, color: ThemeConfig.textSecondaryLight),
          const SizedBox(height: 16),
          Text(
            '暂无设计方案',
            style: TextStyle(
                fontSize: 16, color: ThemeConfig.textSecondaryLight),
          ),
          const SizedBox(height: 8),
          Text(
            '点击右下角按钮生成 AI 设计',
            style:
                TextStyle(fontSize: 14, color: ThemeConfig.textHintLight),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView(DesignProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline,
              size: 64, color: ThemeConfig.errorColor),
          const SizedBox(height: 16),
          Text(provider.error ?? Constants.unknownError),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => provider.loadDesigns(),
            child: const Text(Constants.retryButton),
          ),
        ],
      ),
    );
  }
}
