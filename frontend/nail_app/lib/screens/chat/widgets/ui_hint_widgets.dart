import 'package:flutter/material.dart';
import '../../../config/api_config.dart';
import '../../../config/theme_config.dart';
import '../../../models/conversation.dart';

/// 根据 uiHint 渲染不同的内嵌卡片
class UiHintWidget extends StatelessWidget {
  final UiMetadata uiMetadata;

  const UiHintWidget({Key? key, required this.uiMetadata}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    switch (uiMetadata.uiHint) {
      case 'show_customer_card':
        return CustomerCard(data: uiMetadata.uiData ?? {});
      case 'show_design_preview':
        return DesignPreviewCard(data: uiMetadata.uiData ?? {});
      case 'show_upload_button':
        return const ImageUploadButton();
      case 'show_analysis_result':
        return AnalysisResultCard(data: uiMetadata.uiData ?? {});
      case 'show_final_summary':
        return FinalSummaryCard(data: uiMetadata.uiData ?? {});
      default:
        return const SizedBox.shrink();
    }
  }
}

/// 客户信息卡片
class CustomerCard extends StatelessWidget {
  final Map<String, dynamic> data;

  const CustomerCard({Key? key, required this.data}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: ThemeConfig.primaryLightColor,
                  child: Text(
                    (data['name'] as String? ?? '?').isNotEmpty
                        ? (data['name'] as String).substring(0, 1)
                        : '?',
                    style: const TextStyle(
                      color: ThemeConfig.primaryColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      data['name'] as String? ?? '未知客户',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                    ),
                    if (data['phone'] != null)
                      Text(
                        data['phone'] as String,
                        style: const TextStyle(
                          color: ThemeConfig.textSecondaryLight,
                          fontSize: 13,
                        ),
                      ),
                  ],
                ),
              ],
            ),
            if (data['notes'] != null && (data['notes'] as String).isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  data['notes'] as String,
                  style: const TextStyle(
                    color: ThemeConfig.textSecondaryLight,
                    fontSize: 13,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// 设计图预览卡片
class DesignPreviewCard extends StatelessWidget {
  final Map<String, dynamic> data;

  const DesignPreviewCard({Key? key, required this.data}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final imageUrl = data['image_url'] as String?;
    final designId = data['design_id'];
    final tags = data['style_keywords'] as List<dynamic>?;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 设计图
          if (imageUrl != null)
            AspectRatio(
              aspectRatio: 1.3,
              child: Image.network(
                ApiConfig.getStaticFileUrl(imageUrl),
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  color: Colors.grey[200],
                  child: const Center(
                    child: Icon(Icons.broken_image, color: Colors.grey,
                        size: 48),
                  ),
                ),
              ),
            )
          else
            Container(
              height: 120,
              color: Colors.grey[100],
              child: const Center(child: CircularProgressIndicator()),
            ),

          // 信息行
          Padding(
            padding: const EdgeInsets.all(10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (designId != null)
                  Text(
                    '设计方案 #$designId',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                if (tags != null && tags.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Wrap(
                      spacing: 4,
                      runSpacing: 4,
                      children: tags
                          .map((t) => Chip(
                                label: Text(t.toString()),
                                labelStyle: const TextStyle(fontSize: 11),
                                padding: EdgeInsets.zero,
                                materialTapTargetSize:
                                    MaterialTapTargetSize.shrinkWrap,
                              ))
                          .toList(),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// 图片上传提示按钮（配合 needs_image_upload）
class ImageUploadButton extends StatelessWidget {
  const ImageUploadButton({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: ThemeConfig.primaryLightColor.withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: ThemeConfig.primaryColor.withOpacity(0.4)),
      ),
      child: Row(
        children: [
          Icon(Icons.add_photo_alternate_outlined,
              color: ThemeConfig.primaryColor, size: 28),
          const SizedBox(width: 10),
          const Expanded(
            child: Text(
              '点击下方相机图标上传图片',
              style: TextStyle(
                color: ThemeConfig.primaryColor,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// AI 分析结果卡片（相似度 + 6维评分）
class AnalysisResultCard extends StatelessWidget {
  final Map<String, dynamic> data;

  const AnalysisResultCard({Key? key, required this.data}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final similarity = data['similarity_score'] as num?;
    final scores = data['scores'] as Map<String, dynamic>? ?? {};

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题
            Row(
              children: const [
                Icon(Icons.analytics_outlined,
                    color: ThemeConfig.infoColor, size: 20),
                SizedBox(width: 6),
                Text(
                  'AI 对比分析结果',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // 相似度进度条
            if (similarity != null) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('整体相似度',
                      style: TextStyle(fontSize: 13,
                          color: ThemeConfig.textSecondaryLight)),
                  Text(
                    '${similarity.toStringAsFixed(0)} 分',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: ThemeConfig.infoColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              LinearProgressIndicator(
                value: (similarity / 100).clamp(0.0, 1.0),
                backgroundColor: Colors.grey[200],
                valueColor: const AlwaysStoppedAnimation<Color>(
                    ThemeConfig.infoColor),
                minHeight: 8,
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 14),
            ],

            // 6维评分列表
            if (scores.isNotEmpty) ...[
              const Text(
                '维度评分',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 8),
              ...scores.entries.map((e) {
                final score = (e.value as num).toDouble();
                return Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 72,
                        child: Text(
                          e.key,
                          style: const TextStyle(fontSize: 12),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: LinearProgressIndicator(
                          value: (score / 100).clamp(0.0, 1.0),
                          backgroundColor: Colors.grey[200],
                          valueColor: AlwaysStoppedAnimation<Color>(
                            _scoreColor(score),
                          ),
                          minHeight: 6,
                          borderRadius: BorderRadius.circular(3),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        score.toStringAsFixed(0),
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }

  Color _scoreColor(double score) {
    if (score >= 80) return ThemeConfig.successColor;
    if (score >= 60) return ThemeConfig.warningColor;
    return ThemeConfig.errorColor;
  }
}

/// 成长复盘总结卡片
class FinalSummaryCard extends StatelessWidget {
  final Map<String, dynamic> data;

  const FinalSummaryCard({Key? key, required this.data}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final strengths = data['strengths'] as List<dynamic>? ?? [];
    final improvements = data['improvements'] as List<dynamic>? ?? [];

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(Icons.emoji_events_outlined,
                    color: ThemeConfig.warningColor, size: 20),
                SizedBox(width: 6),
                Text(
                  '本次成长复盘',
                  style: TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 14),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (strengths.isNotEmpty) ...[
              const Text('✨ 亮点',
                  style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: ThemeConfig.successColor,
                      fontSize: 13)),
              const SizedBox(height: 6),
              ...strengths.map((s) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('• ',
                            style: TextStyle(
                                color: ThemeConfig.successColor)),
                        Expanded(child: Text(s.toString(),
                            style: const TextStyle(fontSize: 13))),
                      ],
                    ),
                  )),
              const SizedBox(height: 10),
            ],
            if (improvements.isNotEmpty) ...[
              const Text('📈 待提升',
                  style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: ThemeConfig.warningColor,
                      fontSize: 13)),
              const SizedBox(height: 6),
              ...improvements.map((s) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('• ',
                            style: TextStyle(
                                color: ThemeConfig.warningColor)),
                        Expanded(child: Text(s.toString(),
                            style: const TextStyle(fontSize: 13))),
                      ],
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
}
