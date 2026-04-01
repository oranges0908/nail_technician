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

/// 设计方案详情页
class DesignDetailScreen extends StatefulWidget {
  final int designId;

  const DesignDetailScreen({Key? key, required this.designId})
      : super(key: key);

  @override
  State<DesignDetailScreen> createState() => _DesignDetailScreenState();
}

class _DesignDetailScreenState extends State<DesignDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<DesignProvider>();
      provider.getDesignDetail(widget.designId);
      provider.getVersions(widget.designId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.designsRoute),
        ),
        title: const Text('Design Details'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) async {
              if (value == 'archive') {
                _confirmArchive();
              } else if (value == 'delete') {
                _confirmDelete();
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'archive',
                child: Row(
                  children: const [
                    Icon(Icons.archive_outlined, size: 20),
                    SizedBox(width: 8),
                    Text('Archive'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: const [
                    Icon(Icons.delete_outline,
                        size: 20, color: ThemeConfig.errorColor),
                    SizedBox(width: 8),
                    Text('Delete',
                        style: TextStyle(color: ThemeConfig.errorColor)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Consumer<DesignProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading && provider.selectedDesign == null) {
            return const Center(child: CircularProgressIndicator());
          }

          final design = provider.selectedDesign;
          if (design == null) {
            return Center(
              child: Text(provider.error ?? 'Design not found'),
            );
          }

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 设计图
                CachedNetworkImage(
                  imageUrl: ApiConfig.getStaticFileUrl(
                      design.generatedImagePath),
                  fit: BoxFit.contain,
                  height: 350,
                  placeholder: (context, url) => Container(
                    height: 350,
                    color: ThemeConfig.dividerLight,
                    child: const Center(child: CircularProgressIndicator()),
                  ),
                  errorWidget: (context, url, error) => Container(
                    height: 350,
                    color: ThemeConfig.dividerLight,
                    child: const Icon(Icons.broken_image, size: 64),
                  ),
                ),

                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 标题和版本
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              design.title ?? 'Design #${design.id}',
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          IconButton(
                            icon: Icon(Icons.edit_outlined, size: 20,
                                color: ThemeConfig.textSecondaryLight),
                            onPressed: () => _showRenameDialog(design),
                            tooltip: 'Rename',
                          ),
                          if (design.version > 1)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: ThemeConfig.infoColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                'v${design.version}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: ThemeConfig.infoColor,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        DateFormat('MMM dd, yyyy HH:mm')
                            .format(design.createdAt),
                        style: TextStyle(
                          color: ThemeConfig.textSecondaryLight,
                        ),
                      ),

                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 12),

                      // 设计参数
                      _buildInfoSection('Design Description', design.aiPrompt),

                      if (design.designTarget != null)
                        _buildInfoRow(
                            'Design Target',
                            AppConfig.designTargetLabels[
                                    design.designTarget] ??
                                design.designTarget!),

                      if (design.difficultyLevel != null)
                        _buildInfoRow(
                            'Difficulty',
                            AppConfig.difficultyLabels[
                                    design.difficultyLevel] ??
                                design.difficultyLevel!),

                      if (design.estimatedDuration != null)
                        _buildInfoRow(
                            'Est. Duration', '${design.estimatedDuration} min'),

                      if (design.estimatedMaterials != null &&
                          design.estimatedMaterials!.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        const Text(
                          'Est. Materials',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: design.estimatedMaterials!
                              .map((m) => Chip(
                                    label: Text(m,
                                        style: const TextStyle(fontSize: 12)),
                                    materialTapTargetSize:
                                        MaterialTapTargetSize.shrinkWrap,
                                    visualDensity: VisualDensity.compact,
                                  ))
                              .toList(),
                        ),
                      ],

                      if (design.styleKeywords != null &&
                          design.styleKeywords!.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        const Text(
                          'Style Keywords',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: design.styleKeywords!
                              .map((kw) => Chip(
                                    label: Text(kw,
                                        style: const TextStyle(fontSize: 12)),
                                    materialTapTargetSize:
                                        MaterialTapTargetSize.shrinkWrap,
                                    visualDensity: VisualDensity.compact,
                                    backgroundColor:
                                        ThemeConfig.accentColor.withOpacity(0.1),
                                  ))
                              .toList(),
                        ),
                      ],

                      if (design.refinementInstruction != null) ...[
                        const SizedBox(height: 12),
                        _buildInfoSection(
                            'Refinement Instruction', design.refinementInstruction!),
                      ],

                      if (design.notes != null) ...[
                        const SizedBox(height: 12),
                        _buildInfoSection('Notes', design.notes!),
                      ],

                      // 版本历史
                      if (provider.designVersions.length > 1) ...[
                        const SizedBox(height: 16),
                        const Divider(),
                        const SizedBox(height: 12),
                        const Text(
                          'Version History',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        ...provider.designVersions.map(
                          (v) => _buildVersionItem(v, v.id == design.id),
                        ),
                      ],

                      const SizedBox(height: 24),

                      // 优化按钮
                      SizedBox(
                        width: double.infinity,
                        height: Constants.largeButtonHeight,
                        child: OutlinedButton.icon(
                          onPressed: provider.isGenerating
                              ? null
                              : () => _showRefineDialog(design.id),
                          icon: const Icon(Icons.auto_fix_high),
                          label: const Text('Refine Design'),
                        ),
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

  Widget _buildInfoSection(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: ThemeConfig.textSecondaryLight,
          ),
        ),
        const SizedBox(height: 8),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Text(
            '$label：',
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
          Text(
            value,
            style: TextStyle(color: ThemeConfig.textSecondaryLight),
          ),
        ],
      ),
    );
  }

  Widget _buildVersionItem(DesignPlan version, bool isCurrent) {
    return ListTile(
      dense: true,
      leading: CircleAvatar(
        radius: 14,
        backgroundColor: isCurrent
            ? ThemeConfig.primaryColor
            : ThemeConfig.dividerLight,
        child: Text(
          'v${version.version}',
          style: TextStyle(
            fontSize: 10,
            color: isCurrent ? Colors.white : ThemeConfig.textSecondaryLight,
          ),
        ),
      ),
      title: Text(
        version.refinementInstruction ?? 'Initial version',
        style: TextStyle(
          fontSize: 13,
          fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
        ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: Text(
        DateFormat('MM/dd HH:mm').format(version.createdAt),
        style: const TextStyle(fontSize: 11),
      ),
      onTap: isCurrent
          ? null
          : () => context.go('/designs/${version.id}'),
    );
  }

  void _showRenameDialog(DesignPlan design) {
    final controller = TextEditingController(
      text: design.title ?? 'Design #${design.id}',
    );
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Rename'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: 'Enter a new name'),
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

  void _showRefineDialog(int designId) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        title: const Text('Refine Design'),
        content: SizedBox(
          width: MediaQuery.of(context).size.width * 0.8,
          child: TextField(
            controller: controller,
            decoration: const InputDecoration(
              hintText: 'Describe your desired changes, e.g.:\nAdd more glitter, make the gradient smoother',
              alignLabelWithHint: true,
            ),
            maxLines: 4,
            keyboardType: TextInputType.multiline,
            textInputAction: TextInputAction.newline,
            autofocus: true,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(Constants.cancelButton),
          ),
          TextButton(
            onPressed: () async {
              final instruction = controller.text.trim();
              if (instruction.isEmpty) return;
              Navigator.pop(context);

              final provider = context.read<DesignProvider>();
              final refined =
                  await provider.refineDesign(designId, instruction);
              if (refined != null && mounted) {
                context.go('/designs/${refined.id}');
              }
            },
            child: const Text('Generate'),
          ),
        ],
      ),
    );
  }

  void _confirmArchive() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Archive Design'),
        content: const Text('Archived designs won\'t appear in the list but can still be found via search.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(Constants.cancelButton),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final success = await context
                  .read<DesignProvider>()
                  .archiveDesign(widget.designId);
              if (success && mounted) {
                context.go(Constants.designsRoute);
              }
            },
            child: const Text(Constants.confirmButton),
          ),
        ],
      ),
    );
  }

  void _confirmDelete() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(Constants.deleteConfirmTitle),
        content: const Text('Are you sure you want to delete this design? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(Constants.cancelButton),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final success = await context
                  .read<DesignProvider>()
                  .deleteDesign(widget.designId);
              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text(Constants.deleteSuccess)),
                );
                context.go(Constants.designsRoute);
              }
            },
            style: TextButton.styleFrom(foregroundColor: ThemeConfig.errorColor),
            child: const Text(Constants.deleteButton),
          ),
        ],
      ),
    );
  }
}
