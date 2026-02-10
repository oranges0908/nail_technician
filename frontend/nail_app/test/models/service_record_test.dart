import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/service_record.dart';

void main() {
  group('ServiceRecord', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');
    final json = {
      'id': 1,
      'user_id': 10,
      'customer_id': 5,
      'design_plan_id': 3,
      'service_date': '2025-01-15',
      'service_duration': 90,
      'actual_image_path': '/actuals/1.jpg',
      'materials_used': '甲油胶,亮片',
      'artist_review': '整体完成度高',
      'customer_feedback': '非常满意',
      'customer_satisfaction': 5,
      'notes': '测试',
      'status': 'completed',
      'created_at': now.toIso8601String(),
      'completed_at': now.toIso8601String(),
      'updated_at': now.toIso8601String(),
    };

    test('fromJson creates correct ServiceRecord', () {
      final record = ServiceRecord.fromJson(json);
      expect(record.id, 1);
      expect(record.userId, 10);
      expect(record.customerId, 5);
      expect(record.designPlanId, 3);
      expect(record.serviceDate, '2025-01-15');
      expect(record.serviceDuration, 90);
      expect(record.customerSatisfaction, 5);
      expect(record.status, 'completed');
    });

    test('toJson roundtrip', () {
      final r1 = ServiceRecord.fromJson(json);
      final r2 = ServiceRecord.fromJson(r1.toJson());
      expect(r2.id, r1.id);
      expect(r2.status, r1.status);
      expect(r2.serviceDate, r1.serviceDate);
    });

    test('isCompleted returns true for completed status', () {
      final record = ServiceRecord.fromJson(json);
      expect(record.isCompleted, true);
      expect(record.isPending, false);
    });

    test('isPending returns true for pending status', () {
      final j = Map<String, dynamic>.from(json);
      j['status'] = 'pending';
      final record = ServiceRecord.fromJson(j);
      expect(record.isPending, true);
      expect(record.isCompleted, false);
    });

    test('nullable fields', () {
      final minimal = {
        'id': 2,
        'user_id': 10,
        'customer_id': 5,
        'service_date': '2025-01-15',
        'status': 'pending',
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };
      final record = ServiceRecord.fromJson(minimal);
      expect(record.designPlanId, isNull);
      expect(record.serviceDuration, isNull);
      expect(record.actualImagePath, isNull);
      expect(record.completedAt, isNull);
    });

    test('toString contains key info', () {
      final record = ServiceRecord.fromJson(json);
      expect(record.toString(), contains('completed'));
    });
  });

  group('ServiceRecordListResponse', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');

    test('fromJson parses list', () {
      final jsonList = [
        {
          'id': 1,
          'user_id': 10,
          'customer_id': 5,
          'service_date': '2025-01-15',
          'status': 'pending',
          'created_at': now.toIso8601String(),
          'updated_at': now.toIso8601String(),
        },
      ];
      final response = ServiceRecordListResponse.fromJson(jsonList);
      expect(response.items.length, 1);
      expect(response.items[0].id, 1);
    });
  });
}
