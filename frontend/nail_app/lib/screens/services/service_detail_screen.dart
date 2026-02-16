import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/theme_config.dart';
import '../../config/api_config.dart';
import '../../config/app_config.dart';
import '../../providers/service_provider.dart';
import '../../models/service_record.dart';
import '../../models/comparison_result.dart';
import '../../utils/constants.dart';

/// 服务记录详情页
class ServiceDetailScreen extends StatefulWidget {
  final int serviceId;

  const ServiceDetailScreen({Key? key, required this.serviceId})
      : super(key: key);

  @override
  State<ServiceDetailScreen> createState() => _ServiceDetailScreenState();
}

class _ServiceDetailScreenState extends State<ServiceDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<ServiceRecordProvider>();
      provider.getRecordDetail(widget.serviceId);
      provider.getComparison(widget.serviceId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.servicesRoute),
        ),
        title: const Text('服务详情'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: _confirmDelete,
          ),
        ],
      ),
      body: Consumer<ServiceRecordProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading && provider.selectedRecord == null) {
            return const Center(child: CircularProgressIndicator());
          }

          final record = provider.selectedRecord;
          if (record == null) {
            return Center(
              child: Text(provider.error ?? '服务记录不存在'),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 状态卡片
                _buildStatusCard(record),
                const SizedBox(height: 16),

                // 基本信息卡片
                _buildInfoCard(record),
                const SizedBox(height: 16),

                // 设计图 vs 实际图
                if (record.designImagePath != null || record.actualImagePath != null)
                  _buildComparisonImages(record),

                // 复盘信息
                if (record.isCompleted) ...[
                  const SizedBox(height: 16),
                  _buildReviewCard(record),
                ],

                // AI分析结果
                if (provider.comparison != null) ...[
                  const SizedBox(height: 16),
                  _buildAnalysisCard(provider.comparison!),
                ] else if (record.isCompleted &&
                    record.designPlanId != null) ...[
                  const SizedBox(height: 16),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          if (provider.isAnalyzing) ...[
                            const CircularProgressIndicator(),
                            const SizedBox(height: 12),
                            const Text('AI 分析中...'),
                          ] else ...[
                            const Text('暂无 AI 分析结果'),
                            const SizedBox(height: 8),
                            ElevatedButton.icon(
                              onPressed: () =>
                                  provider.triggerAnalysis(widget.serviceId),
                              icon: const Icon(Icons.analytics),
                              label: const Text('触发 AI 分析'),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ],

                const SizedBox(height: 24),

                // 完成服务按钮
                if (record.isPending)
                  SizedBox(
                    height: Constants.largeButtonHeight,
                    child: ElevatedButton.icon(
                      onPressed: () =>
                          context.go('/services/${record.id}/complete'),
                      icon: const Icon(Icons.check_circle_outline),
                      label: const Text('完成服务'),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildStatusCard(ServiceRecord record) {
    final statusLabel =
        AppConfig.serviceStatusLabels[record.status] ?? record.status;
    final statusColor =
        record.isCompleted ? ThemeConfig.successColor : ThemeConfig.warningColor;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    record.isCompleted
                        ? Icons.check_circle
                        : Icons.pending_actions,
                    size: 16,
                    color: statusColor,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    statusLabel,
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
            const Spacer(),
            Text(
              record.serviceDate,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard(ServiceRecord record) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '基本信息',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _infoRow('客户', '客户 #${record.customerId}'),
            if (record.designPlanId != null)
              _infoRow('设计方案', '设计 #${record.designPlanId}'),
            if (record.serviceDuration != null)
              _infoRow('服务时长', '${record.serviceDuration} 分钟'),
            if (record.notes != null) _infoRow('备注', record.notes!),
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(
                color: ThemeConfig.textSecondaryLight,
                fontSize: 14,
              ),
            ),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(fontSize: 14)),
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonImages(ServiceRecord record) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '设计 vs 实际',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                // 设计图
                Expanded(
                  child: Column(
                    children: [
                      const Text('设计图',
                          style: TextStyle(fontSize: 12, color: ThemeConfig.textSecondaryLight)),
                      const SizedBox(height: 4),
                      Container(
                        height: 150,
                        decoration: BoxDecoration(
                          color: ThemeConfig.dividerLight.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: record.designImagePath != null
                            ? ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: CachedNetworkImage(
                                  imageUrl: ApiConfig.getStaticFileUrl(
                                      record.designImagePath!),
                                  fit: BoxFit.cover,
                                  width: double.infinity,
                                  height: 150,
                                  errorWidget: (_, __, ___) => const Icon(
                                      Icons.broken_image),
                                ),
                              )
                            : const Center(child: Text('无设计图')),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                // 实际图
                Expanded(
                  child: Column(
                    children: [
                      const Text('实际效果',
                          style: TextStyle(fontSize: 12, color: ThemeConfig.textSecondaryLight)),
                      const SizedBox(height: 4),
                      Container(
                        height: 150,
                        decoration: BoxDecoration(
                          color: ThemeConfig.dividerLight.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: record.actualImagePath != null
                            ? ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: CachedNetworkImage(
                                  imageUrl: ApiConfig.getStaticFileUrl(
                                      record.actualImagePath!),
                                  fit: BoxFit.cover,
                                  width: double.infinity,
                                  height: 150,
                                  errorWidget: (_, __, ___) => const Icon(
                                      Icons.broken_image),
                                ),
                              )
                            : const Center(child: Text('待上传')),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReviewCard(ServiceRecord record) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '服务复盘',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            if (record.customerSatisfaction != null) ...[
              Row(
                children: [
                  const Text('客户满意度  '),
                  ...List.generate(
                    5,
                    (i) => Icon(
                      i < record.customerSatisfaction!
                          ? Icons.star
                          : Icons.star_border,
                      size: 20,
                      color: ThemeConfig.warningColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
            ],
            if (record.materialsUsed != null)
              _infoRow('使用材料', record.materialsUsed!),
            if (record.artistReview != null)
              _infoRow('美甲师复盘', record.artistReview!),
            if (record.customerFeedback != null)
              _infoRow('客户反馈', record.customerFeedback!),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisCard(ComparisonResult comparison) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'AI 分析结果',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                // 相似度得分
                SizedBox(
                  width: 50,
                  height: 50,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      CircularProgressIndicator(
                        value: comparison.similarityScore / 100,
                        backgroundColor: ThemeConfig.dividerLight,
                        color: _getScoreColor(comparison.similarityScore),
                        strokeWidth: 4,
                      ),
                      Text(
                        '${comparison.similarityScore}',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: _getScoreColor(comparison.similarityScore),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // 差异
            if (comparison.differences.isNotEmpty) ...[
              const Text(
                '差异分析',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 4),
              ...comparison.differences.entries.map(
                (e) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('  \u2022 ',
                          style: TextStyle(color: ThemeConfig.warningColor)),
                      Expanded(
                        child: Text(
                          '${e.key}: ${e.value}',
                          style: const TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),
            ],

            // 建议
            if (comparison.suggestions.isNotEmpty) ...[
              const Text(
                '改进建议',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 4),
              ...comparison.suggestions.map(
                (s) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('  \u2022 ',
                          style: TextStyle(color: ThemeConfig.infoColor)),
                      Expanded(
                        child: Text(
                          s.toString(),
                          style: const TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 80) return ThemeConfig.successColor;
    if (score >= 60) return ThemeConfig.warningColor;
    return ThemeConfig.errorColor;
  }

  void _confirmDelete() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(Constants.deleteConfirmTitle),
        content: const Text('确定要删除此服务记录吗？关联的分析结果也将被删除。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(Constants.cancelButton),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final success = await context
                  .read<ServiceRecordProvider>()
                  .deleteRecord(widget.serviceId);
              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text(Constants.deleteSuccess)),
                );
                context.go(Constants.servicesRoute);
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
