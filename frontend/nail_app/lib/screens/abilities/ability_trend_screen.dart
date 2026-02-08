import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../config/theme_config.dart';
import '../../providers/ability_provider.dart';

/// 能力趋势详情页
/// 展示某个维度的历史评分趋势图
class AbilityTrendScreen extends StatefulWidget {
  final String dimensionName;

  const AbilityTrendScreen({
    Key? key,
    required this.dimensionName,
  }) : super(key: key);

  @override
  State<AbilityTrendScreen> createState() => _AbilityTrendScreenState();
}

class _AbilityTrendScreenState extends State<AbilityTrendScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AbilityProvider>().loadTrend(widget.dimensionName);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.dimensionName),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<AbilityProvider>().loadTrend(widget.dimensionName);
            },
          ),
        ],
      ),
      body: Consumer<AbilityProvider>(
        builder: (context, provider, _) {
          if (provider.isTrendLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.trendDataPoints.isEmpty) {
            return _buildEmptyView();
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 趋势概要
                _buildSummaryCard(provider),
                const SizedBox(height: 20),

                // 趋势图
                _buildTrendChartCard(provider),
                const SizedBox(height: 20),

                // 历史记录列表
                _buildHistoryList(provider),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSummaryCard(AbilityProvider provider) {
    final points = provider.trendDataPoints;
    final latestScore = (points.last['score'] as num?)?.toDouble() ?? 0;
    final firstScore = (points.first['score'] as num?)?.toDouble() ?? 0;
    final change = latestScore - firstScore;
    final avgScore = points.fold<double>(
          0,
          (sum, p) => sum + ((p['score'] as num?)?.toDouble() ?? 0),
        ) /
        points.length;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${widget.dimensionName}趋势',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _buildStatItem(
                  '最新评分',
                  latestScore.toStringAsFixed(0),
                  _getScoreColor(latestScore),
                ),
                _buildStatItem(
                  '平均评分',
                  avgScore.toStringAsFixed(1),
                  ThemeConfig.infoColor,
                ),
                _buildStatItem(
                  '变化趋势',
                  '${change >= 0 ? "+" : ""}${change.toStringAsFixed(0)}',
                  change >= 0 ? ThemeConfig.successColor : ThemeConfig.errorColor,
                ),
                _buildStatItem(
                  '评分次数',
                  '${points.length}',
                  ThemeConfig.textSecondaryLight,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Expanded(
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: ThemeConfig.textSecondaryLight,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrendChartCard(AbilityProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '评分趋势',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: CustomPaint(
                size: Size.infinite,
                painter: TrendChartPainter(
                  dataPoints: provider.trendDataPoints,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryList(AbilityProvider provider) {
    final points = provider.trendDataPoints.reversed.toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '历史记录',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        ...points.map((point) {
          final score = (point['score'] as num?)?.toDouble() ?? 0;
          final date = point['date'] as String? ?? '';
          final displayDate = date.length >= 10 ? date.substring(0, 10) : date;

          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: _getScoreColor(score).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Center(
                  child: Text(
                    score.toStringAsFixed(0),
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _getScoreColor(score),
                    ),
                  ),
                ),
              ),
              title: Text('评分: ${score.toStringAsFixed(0)}'),
              subtitle: Text(
                displayDate,
                style: TextStyle(
                  fontSize: 12,
                  color: ThemeConfig.textSecondaryLight,
                ),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.show_chart,
              size: 80,
              color: ThemeConfig.textHintLight,
            ),
            const SizedBox(height: 16),
            Text(
              '暂无"${widget.dimensionName}"的评分记录',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '完成服务并进行 AI 分析后\n将自动生成该维度的评分',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: ThemeConfig.textSecondaryLight,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return ThemeConfig.successColor;
    if (score >= 60) return ThemeConfig.infoColor;
    if (score >= 40) return ThemeConfig.warningColor;
    return ThemeConfig.errorColor;
  }
}

/// 趋势折线图绘制器
class TrendChartPainter extends CustomPainter {
  final List<Map<String, dynamic>> dataPoints;

  TrendChartPainter({required this.dataPoints});

  @override
  void paint(Canvas canvas, Size size) {
    if (dataPoints.isEmpty) return;

    const paddingLeft = 40.0;
    const paddingRight = 16.0;
    const paddingTop = 16.0;
    const paddingBottom = 30.0;

    final chartWidth = size.width - paddingLeft - paddingRight;
    final chartHeight = size.height - paddingTop - paddingBottom;

    // 绘制Y轴刻度和网格线
    final gridPaint = Paint()
      ..color = Colors.grey.withOpacity(0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    final labelStyle = TextStyle(
      color: Colors.grey[500],
      fontSize: 10,
    );

    for (int i = 0; i <= 5; i++) {
      final y = paddingTop + chartHeight * (1 - i / 5);
      final value = (i * 20).toString();

      canvas.drawLine(
        Offset(paddingLeft, y),
        Offset(size.width - paddingRight, y),
        gridPaint,
      );

      final textSpan = TextSpan(text: value, style: labelStyle);
      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(paddingLeft - textPainter.width - 4, y - textPainter.height / 2),
      );
    }

    // 绘制数据线
    final scores = dataPoints
        .map((p) => (p['score'] as num?)?.toDouble() ?? 0)
        .toList();

    if (scores.length == 1) {
      // 单个点
      final x = paddingLeft + chartWidth / 2;
      final y = paddingTop + chartHeight * (1 - scores[0] / 100);
      final dotPaint = Paint()
        ..color = ThemeConfig.primaryColor
        ..style = PaintingStyle.fill;
      canvas.drawCircle(Offset(x, y), 5, dotPaint);
      return;
    }

    final stepX = chartWidth / (scores.length - 1);

    // 绘制填充区域
    final fillPath = Path();
    fillPath.moveTo(paddingLeft, paddingTop + chartHeight);
    for (int i = 0; i < scores.length; i++) {
      final x = paddingLeft + stepX * i;
      final y = paddingTop + chartHeight * (1 - scores[i] / 100);
      fillPath.lineTo(x, y);
    }
    fillPath.lineTo(paddingLeft + stepX * (scores.length - 1), paddingTop + chartHeight);
    fillPath.close();

    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          ThemeConfig.primaryColor.withOpacity(0.3),
          ThemeConfig.primaryColor.withOpacity(0.05),
        ],
      ).createShader(Rect.fromLTWH(0, paddingTop, size.width, chartHeight));
    canvas.drawPath(fillPath, fillPaint);

    // 绘制线条
    final linePath = Path();
    for (int i = 0; i < scores.length; i++) {
      final x = paddingLeft + stepX * i;
      final y = paddingTop + chartHeight * (1 - scores[i] / 100);
      if (i == 0) {
        linePath.moveTo(x, y);
      } else {
        linePath.lineTo(x, y);
      }
    }

    final linePaint = Paint()
      ..color = ThemeConfig.primaryColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    canvas.drawPath(linePath, linePaint);

    // 绘制数据点
    final dotPaint = Paint()
      ..color = ThemeConfig.primaryColor
      ..style = PaintingStyle.fill;
    final dotBorderPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    for (int i = 0; i < scores.length; i++) {
      final x = paddingLeft + stepX * i;
      final y = paddingTop + chartHeight * (1 - scores[i] / 100);
      canvas.drawCircle(Offset(x, y), 5, dotBorderPaint);
      canvas.drawCircle(Offset(x, y), 3.5, dotPaint);
    }
  }

  @override
  bool shouldRepaint(covariant TrendChartPainter oldDelegate) {
    return oldDelegate.dataPoints != dataPoints;
  }
}
