import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/theme_config.dart';
import '../../config/api_config.dart';
import '../../providers/inspiration_provider.dart';
import '../../models/inspiration_image.dart';
import '../../utils/constants.dart';

/// 灵感图库列表页
class InspirationListScreen extends StatefulWidget {
  const InspirationListScreen({Key? key}) : super(key: key);

  @override
  State<InspirationListScreen> createState() => _InspirationListScreenState();
}

class _InspirationListScreenState extends State<InspirationListScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();

  static const _categories = ['法式', '渐变', '贴片', '彩绘', '纯色', '花卉', '几何', '其他'];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<InspirationProvider>().loadInspirations();
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
      context.read<InspirationProvider>().loadMore();
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
        title: const Text('灵感图库'),
      ),
      body: Column(
        children: [
          // 搜索栏
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: '搜索灵感图...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          context.read<InspirationProvider>().search('');
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
                context.read<InspirationProvider>().search(query);
              },
            ),
          ),

          // 分类筛选
          Consumer<InspirationProvider>(
            builder: (context, provider, _) {
              return SizedBox(
                height: 40,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: FilterChip(
                        label: const Text('全部'),
                        selected: provider.selectedCategory == null,
                        onSelected: (_) => provider.filterByCategory(null),
                        selectedColor: ThemeConfig.primaryLightColor,
                      ),
                    ),
                    ..._categories.map((cat) => Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          child: FilterChip(
                            label: Text(cat),
                            selected: provider.selectedCategory == cat,
                            onSelected: (_) => provider.filterByCategory(cat),
                            selectedColor: ThemeConfig.primaryLightColor,
                          ),
                        )),
                  ],
                ),
              );
            },
          ),

          const SizedBox(height: 8),

          // 图片网格
          Expanded(
            child: Consumer<InspirationProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading && provider.inspirations.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (provider.error != null && provider.inspirations.isEmpty) {
                  return _buildErrorView(provider);
                }

                if (provider.inspirations.isEmpty) {
                  return _buildEmptyView();
                }

                return RefreshIndicator(
                  onRefresh: () => provider.loadInspirations(),
                  child: GridView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(8),
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 8,
                      crossAxisSpacing: 8,
                      childAspectRatio: 0.8,
                    ),
                    itemCount: provider.inspirations.length +
                        (provider.hasMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == provider.inspirations.length) {
                        return const Center(child: CircularProgressIndicator());
                      }
                      return _buildInspirationCard(
                          provider.inspirations[index]);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.go('/inspirations/upload'),
        child: const Icon(Icons.add_photo_alternate),
      ),
    );
  }

  Widget _buildInspirationCard(InspirationImage inspiration) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          _showInspirationDetail(inspiration);
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: CachedNetworkImage(
                imageUrl:
                    ApiConfig.getStaticFileUrl(inspiration.imagePath),
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: ThemeConfig.dividerLight,
                  child: const Center(child: CircularProgressIndicator()),
                ),
                errorWidget: (context, url, error) => Container(
                  color: ThemeConfig.dividerLight,
                  child: const Icon(Icons.broken_image, size: 48),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    inspiration.title ?? '未命名',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      if (inspiration.category != null) ...[
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: ThemeConfig.primaryColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            inspiration.category!,
                            style: const TextStyle(
                              fontSize: 10,
                              color: ThemeConfig.primaryColor,
                            ),
                          ),
                        ),
                        const Spacer(),
                      ],
                      Icon(
                        Icons.favorite,
                        size: 12,
                        color: ThemeConfig.textHintLight,
                      ),
                      const SizedBox(width: 2),
                      Text(
                        '${inspiration.usageCount}',
                        style: const TextStyle(
                          fontSize: 10,
                          color: ThemeConfig.textHintLight,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showInspirationDetail(InspirationImage inspiration) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.95,
        minChildSize: 0.5,
        expand: false,
        builder: (context, scrollController) {
          return SingleChildScrollView(
            controller: scrollController,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 拖动指示器
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: ThemeConfig.dividerLight,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                // 图片
                CachedNetworkImage(
                  imageUrl: ApiConfig.getStaticFileUrl(inspiration.imagePath),
                  fit: BoxFit.contain,
                  height: 300,
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        inspiration.title ?? '未命名',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (inspiration.description != null) ...[
                        const SizedBox(height: 8),
                        Text(
                          inspiration.description!,
                          style: TextStyle(
                            color: ThemeConfig.textSecondaryLight,
                          ),
                        ),
                      ],
                      if (inspiration.tags != null &&
                          inspiration.tags!.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: inspiration.tags!
                              .map((tag) => Chip(
                                    label: Text(tag,
                                        style: const TextStyle(fontSize: 12)),
                                    materialTapTargetSize:
                                        MaterialTapTargetSize.shrinkWrap,
                                    visualDensity: VisualDensity.compact,
                                  ))
                              .toList(),
                        ),
                      ],
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () {
                                Navigator.pop(context);
                                _confirmDelete(inspiration.id);
                              },
                              icon: const Icon(Icons.delete_outline),
                              label: const Text('删除'),
                              style: OutlinedButton.styleFrom(
                                primary: ThemeConfig.errorColor,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _confirmDelete(int id) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(Constants.deleteConfirmTitle),
        content: const Text('确定要删除这张灵感图吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(Constants.cancelButton),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final success = await context
                  .read<InspirationProvider>()
                  .deleteInspiration(id);
              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text(Constants.deleteSuccess)),
                );
              }
            },
            style: TextButton.styleFrom(primary: ThemeConfig.errorColor),
            child: const Text(Constants.deleteButton),
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
          Icon(
            Icons.photo_library_outlined,
            size: 64,
            color: ThemeConfig.textSecondaryLight,
          ),
          const SizedBox(height: 16),
          Text(
            '暂无灵感图',
            style: TextStyle(
              fontSize: 16,
              color: ThemeConfig.textSecondaryLight,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '点击右下角按钮上传灵感图',
            style: TextStyle(
              fontSize: 14,
              color: ThemeConfig.textHintLight,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView(InspirationProvider provider) {
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
            onPressed: () => provider.loadInspirations(),
            child: const Text(Constants.retryButton),
          ),
        ],
      ),
    );
  }
}
