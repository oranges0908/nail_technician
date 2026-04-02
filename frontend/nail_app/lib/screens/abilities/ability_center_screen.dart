import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;

import '../../config/app_config.dart';
import '../../config/theme_config.dart';
import '../../providers/ability_provider.dart';
import '../../utils/constants.dart';

/// Ability center main screen
/// Displays radar chart, ability summary, and per-dimension entries
class AbilityCenterScreen extends StatefulWidget {
  const AbilityCenterScreen({Key? key}) : super(key: key);

  @override
  State<AbilityCenterScreen> createState() => _AbilityCenterScreenState();
}

class _AbilityCenterScreenState extends State<AbilityCenterScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AbilityProvider>().loadAbilityOverview();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ability Center'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.homeRoute),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<AbilityProvider>().loadAbilityOverview();
            },
          ),
        ],
      ),
      body: Consumer<AbilityProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null) {
            return _buildErrorView(context, provider);
          }

          if (!provider.hasData) {
            return _buildEmptyView(context, provider);
          }

          return RefreshIndicator(
            onRefresh: () => provider.loadAbilityOverview(),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Overall score card
                  _buildOverallScoreCard(provider),
                  const SizedBox(height: 20),

                  // Radar chart
                  _buildRadarChartCard(provider),
                  const SizedBox(height: 20),

                  // Strengths
                  if (provider.strengths.isNotEmpty) ...[
                    _buildSectionTitle('Strengths', Icons.star, ThemeConfig.successColor),
                    const SizedBox(height: 8),
                    ...provider.strengths.map((s) => _buildDimensionTile(
                      s['dimension'] as String? ?? '',
                      (s['score'] as num?)?.toDouble() ?? 0,
                      ThemeConfig.successColor,
                    )),
                    const SizedBox(height: 16),
                  ],

                  // Areas to improve
                  if (provider.improvements.isNotEmpty) ...[
                    _buildSectionTitle('Areas to Improve', Icons.trending_up, ThemeConfig.warningColor),
                    const SizedBox(height: 8),
                    ...provider.improvements.map((s) => _buildDimensionTile(
                      s['dimension'] as String? ?? '',
                      (s['score'] as num?)?.toDouble() ?? 0,
                      ThemeConfig.warningColor,
                    )),
                    const SizedBox(height: 16),
                  ],

                  // All dimensions list
                  _buildSectionTitle('All Dimensions', Icons.list_alt, ThemeConfig.primaryColor),
                  const SizedBox(height: 8),
                  _buildAllDimensionsList(provider),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildOverallScoreCard(AbilityProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            // Overall score ring
            SizedBox(
              width: 80,
              height: 80,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(
                    value: provider.avgScore / 100,
                    strokeWidth: 8,
                    backgroundColor: ThemeConfig.dividerLight,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _getScoreColor(provider.avgScore),
                    ),
                  ),
                  Text(
                    provider.avgScore.toStringAsFixed(0),
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: _getScoreColor(provider.avgScore),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Overall Ability Score',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${provider.totalServices} services completed',
                    style: TextStyle(
                      fontSize: 14,
                      color: ThemeConfig.textSecondaryLight,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${provider.totalRecords} score records total',
                    style: TextStyle(
                      fontSize: 14,
                      color: ThemeConfig.textSecondaryLight,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRadarChartCard(AbilityProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ability Radar Chart',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            AspectRatio(
              aspectRatio: 1,
              child: CustomPaint(
                painter: RadarChartPainter(
                  dimensions: provider.dimensions
                      .map((d) => AppConfig.abilityDimensionLabels[d] ?? d)
                      .toList(),
                  scores: provider.scores,
                  maxScore: 100,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, size: 20, color: color),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildDimensionTile(String dimension, double score, Color accentColor) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(AppConfig.abilityDimensionLabels[dimension] ?? dimension),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              score.toStringAsFixed(0),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: _getScoreColor(score),
              ),
            ),
            const SizedBox(width: 4),
            const Icon(Icons.chevron_right, color: ThemeConfig.textHintLight),
          ],
        ),
        onTap: () {
          context.push('/abilities/trend/$dimension');
        },
      ),
    );
  }

  Widget _buildAllDimensionsList(AbilityProvider provider) {
    return Column(
      children: List.generate(provider.dimensions.length, (i) {
        final dimension = provider.dimensions[i];
        final score = provider.scores[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: _getScoreColor(score).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  '${i + 1}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: _getScoreColor(score),
                  ),
                ),
              ),
            ),
            title: Text(AppConfig.abilityDimensionLabels[dimension] ?? dimension),
            subtitle: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: score / 100,
                backgroundColor: ThemeConfig.dividerLight,
                valueColor: AlwaysStoppedAnimation<Color>(
                  _getScoreColor(score),
                ),
                minHeight: 6,
              ),
            ),
            trailing: Text(
              score.toStringAsFixed(0),
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: _getScoreColor(score),
              ),
            ),
            onTap: () {
              context.push('/abilities/trend/$dimension');
            },
          ),
        );
      }),
    );
  }

  Widget _buildEmptyView(BuildContext context, AbilityProvider provider) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.radar_outlined,
              size: 80,
              color: ThemeConfig.textHintLight,
            ),
            const SizedBox(height: 16),
            const Text(
              'No ability data yet',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Complete a service and run AI analysis\nto automatically generate ability scores',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: ThemeConfig.textSecondaryLight,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => provider.initializeDimensions(),
              icon: const Icon(Icons.play_arrow),
              label: const Text('Initialize Ability Dimensions'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView(BuildContext context, AbilityProvider provider) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: ThemeConfig.errorColor,
            ),
            const SizedBox(height: 16),
            Text(
              provider.error!,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                provider.clearError();
                provider.loadAbilityOverview();
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
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

/// Radar chart painter
class RadarChartPainter extends CustomPainter {
  final List<String> dimensions;
  final List<double> scores;
  final double maxScore;

  RadarChartPainter({
    required this.dimensions,
    required this.scores,
    required this.maxScore,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 40;
    final sides = dimensions.length;

    if (sides < 3) return;

    final angleStep = 2 * math.pi / sides;
    // Start from top (-π/2)
    const startAngle = -math.pi / 2;

    // Draw background grid (5 levels)
    final gridPaint = Paint()
      ..color = Colors.grey.withOpacity(0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    for (int level = 1; level <= 5; level++) {
      final levelRadius = radius * level / 5;
      final path = Path();
      for (int i = 0; i <= sides; i++) {
        final angle = startAngle + angleStep * (i % sides);
        final x = center.dx + levelRadius * math.cos(angle);
        final y = center.dy + levelRadius * math.sin(angle);
        if (i == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      path.close();
      canvas.drawPath(path, gridPaint);
    }

    // Draw lines from center to each vertex
    final linePaint = Paint()
      ..color = Colors.grey.withOpacity(0.15)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    for (int i = 0; i < sides; i++) {
      final angle = startAngle + angleStep * i;
      final x = center.dx + radius * math.cos(angle);
      final y = center.dy + radius * math.sin(angle);
      canvas.drawLine(center, Offset(x, y), linePaint);
    }

    // Draw data polygon
    if (scores.isNotEmpty) {
      final dataPath = Path();
      final dataFillPaint = Paint()
        ..color = ThemeConfig.primaryColor.withOpacity(0.2)
        ..style = PaintingStyle.fill;

      final dataStrokePaint = Paint()
        ..color = ThemeConfig.primaryColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;

      for (int i = 0; i <= sides; i++) {
        final idx = i % sides;
        final score = idx < scores.length ? scores[idx] : 0.0;
        final ratio = score / maxScore;
        final angle = startAngle + angleStep * idx;
        final x = center.dx + radius * ratio * math.cos(angle);
        final y = center.dy + radius * ratio * math.sin(angle);
        if (i == 0) {
          dataPath.moveTo(x, y);
        } else {
          dataPath.lineTo(x, y);
        }
      }
      dataPath.close();
      canvas.drawPath(dataPath, dataFillPaint);
      canvas.drawPath(dataPath, dataStrokePaint);

      // Draw data points
      final dotPaint = Paint()
        ..color = ThemeConfig.primaryColor
        ..style = PaintingStyle.fill;

      for (int i = 0; i < sides; i++) {
        final score = i < scores.length ? scores[i] : 0.0;
        final ratio = score / maxScore;
        final angle = startAngle + angleStep * i;
        final x = center.dx + radius * ratio * math.cos(angle);
        final y = center.dy + radius * ratio * math.sin(angle);
        canvas.drawCircle(Offset(x, y), 4, dotPaint);
      }
    }

    // Draw dimension labels
    final textStyle = TextStyle(
      color: Colors.grey[700],
      fontSize: 12,
      fontWeight: FontWeight.w500,
    );

    for (int i = 0; i < sides; i++) {
      final angle = startAngle + angleStep * i;
      final labelRadius = radius + 24;
      final x = center.dx + labelRadius * math.cos(angle);
      final y = center.dy + labelRadius * math.sin(angle);

      final textSpan = TextSpan(text: dimensions[i], style: textStyle);
      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();

      // Adjust label position based on angle
      double dx = x - textPainter.width / 2;
      double dy = y - textPainter.height / 2;

      textPainter.paint(canvas, Offset(dx, dy));
    }
  }

  @override
  bool shouldRepaint(covariant RadarChartPainter oldDelegate) {
    return oldDelegate.scores != scores || oldDelegate.dimensions != dimensions;
  }
}
