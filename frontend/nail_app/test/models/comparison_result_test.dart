import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/comparison_result.dart' as model;

void main() {
  group('ComparisonResult', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');
    final json = {
      'id': 1,
      'service_record_id': 5,
      'similarity_score': 85,
      'differences': {
        'color_accuracy': '颜色准确度90%',
        'shape_accuracy': '形状准确度80%',
      },
      'suggestions': ['渐变过渡可更自然', '注意甲面平整度'],
      'contextual_insights': {
        'overall': '整体完成度较高',
        'improvement_area': '细节处理',
      },
      'analyzed_at': now.toIso8601String(),
    };

    test('fromJson creates correct ComparisonResult', () {
      final result = model.ComparisonResult.fromJson(json);
      expect(result.id, 1);
      expect(result.serviceRecordId, 5);
      expect(result.similarityScore, 85);
      expect(result.differences['color_accuracy'], '颜色准确度90%');
      expect(result.suggestions.length, 2);
      expect(result.contextualInsights, isNotNull);
    });

    test('toJson roundtrip', () {
      final r1 = model.ComparisonResult.fromJson(json);
      final r2 = model.ComparisonResult.fromJson(r1.toJson());
      expect(r2.similarityScore, r1.similarityScore);
      expect(r2.differences, r1.differences);
    });

    test('nullable contextualInsights', () {
      final j = Map<String, dynamic>.from(json);
      j['contextual_insights'] = null;
      final result = model.ComparisonResult.fromJson(j);
      expect(result.contextualInsights, isNull);
    });

    test('toString contains key info', () {
      final result = model.ComparisonResult.fromJson(json);
      expect(result.toString(), contains('85'));
    });
  });
}
