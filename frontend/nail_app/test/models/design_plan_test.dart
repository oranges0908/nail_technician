import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/design_plan.dart';

void main() {
  group('DesignPlan', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');
    final json = {
      'id': 1,
      'user_id': 10,
      'customer_id': 5,
      'title': '粉色渐变美甲',
      'notes': '测试备注',
      'ai_prompt': '粉色渐变法式美甲',
      'generated_image_path': '/designs/1.png',
      'model_version': 'dall-e-3',
      'design_target': 'full_hand',
      'style_keywords': ['渐变', '法式'],
      'reference_images': ['/ref/1.jpg'],
      'parent_design_id': null,
      'version': 1,
      'refinement_instruction': null,
      'estimated_duration': 90,
      'estimated_materials': ['甲油胶', '亮片'],
      'difficulty_level': '中等',
      'is_archived': 0,
      'created_at': now.toIso8601String(),
      'updated_at': now.toIso8601String(),
    };

    test('fromJson creates correct DesignPlan', () {
      final plan = DesignPlan.fromJson(json);
      expect(plan.id, 1);
      expect(plan.userId, 10);
      expect(plan.customerId, 5);
      expect(plan.title, '粉色渐变美甲');
      expect(plan.aiPrompt, '粉色渐变法式美甲');
      expect(plan.generatedImagePath, '/designs/1.png');
      expect(plan.styleKeywords, ['渐变', '法式']);
      expect(plan.estimatedDuration, 90);
      expect(plan.version, 1);
    });

    test('toJson roundtrip', () {
      final plan1 = DesignPlan.fromJson(json);
      final plan2 = DesignPlan.fromJson(plan1.toJson());
      expect(plan2.id, plan1.id);
      expect(plan2.aiPrompt, plan1.aiPrompt);
      expect(plan2.styleKeywords, plan1.styleKeywords);
    });

    test('archived getter with int 0', () {
      final plan = DesignPlan.fromJson(json);
      expect(plan.archived, false);
    });

    test('archived getter with int 1', () {
      final j = Map<String, dynamic>.from(json);
      j['is_archived'] = 1;
      final plan = DesignPlan.fromJson(j);
      expect(plan.archived, true);
    });

    test('archived getter with bool', () {
      final j = Map<String, dynamic>.from(json);
      j['is_archived'] = true;
      final plan = DesignPlan.fromJson(j);
      expect(plan.archived, true);
    });

    test('self-referential parentDesignId', () {
      final j = Map<String, dynamic>.from(json);
      j['parent_design_id'] = 1;
      j['version'] = 2;
      j['refinement_instruction'] = '增加更多亮片';
      final plan = DesignPlan.fromJson(j);
      expect(plan.parentDesignId, 1);
      expect(plan.version, 2);
      expect(plan.refinementInstruction, '增加更多亮片');
    });

    test('nullable fields default correctly', () {
      final minimal = {
        'id': 2,
        'user_id': 10,
        'ai_prompt': 'test',
        'generated_image_path': '/test.png',
        'version': 1,
        'is_archived': 0,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };
      final plan = DesignPlan.fromJson(minimal);
      expect(plan.customerId, isNull);
      expect(plan.title, isNull);
      expect(plan.parentDesignId, isNull);
      expect(plan.estimatedMaterials, isNull);
    });
  });

  group('DesignPlanListResponse', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');

    test('fromJson parses list', () {
      final json = {
        'total': 1,
        'designs': [
          {
            'id': 1,
            'user_id': 10,
            'ai_prompt': 'test',
            'generated_image_path': '/test.png',
            'version': 1,
            'is_archived': 0,
            'created_at': now.toIso8601String(),
            'updated_at': now.toIso8601String(),
          },
        ],
      };
      final response = DesignPlanListResponse.fromJson(json);
      expect(response.total, 1);
      expect(response.designs.length, 1);
    });
  });
}
