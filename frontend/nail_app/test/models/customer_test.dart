import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/customer.dart';
import 'package:nail_app/models/customer_profile.dart';

void main() {
  group('Customer', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');
    final json = {
      'id': 1,
      'user_id': 10,
      'name': '张三',
      'phone': '13800138000',
      'email': 'zhangsan@example.com',
      'avatar_path': null,
      'notes': 'VIP客户',
      'is_active': true,
      'created_at': now.toIso8601String(),
      'updated_at': now.toIso8601String(),
      'profile': null,
    };

    test('fromJson creates correct Customer', () {
      final customer = Customer.fromJson(json);
      expect(customer.id, 1);
      expect(customer.userId, 10);
      expect(customer.name, '张三');
      expect(customer.phone, '13800138000');
      expect(customer.email, 'zhangsan@example.com');
      expect(customer.notes, 'VIP客户');
      expect(customer.profile, isNull);
    });

    test('toJson produces correct map', () {
      final customer = Customer.fromJson(json);
      final result = customer.toJson();
      expect(result['user_id'], 10);
      expect(result['name'], '张三');
      expect(result['phone'], '13800138000');
    });

    test('active getter with bool true', () {
      final customer = Customer.fromJson(json);
      expect(customer.active, true);
    });

    test('active getter with bool false', () {
      final j = Map<String, dynamic>.from(json);
      j['is_active'] = false;
      final customer = Customer.fromJson(j);
      expect(customer.active, false);
    });

    test('active getter with int 1', () {
      final j = Map<String, dynamic>.from(json);
      j['is_active'] = 1;
      final customer = Customer.fromJson(j);
      expect(customer.active, true);
    });

    test('active getter with int 0', () {
      final j = Map<String, dynamic>.from(json);
      j['is_active'] = 0;
      final customer = Customer.fromJson(j);
      expect(customer.active, false);
    });

    test('nullable fields can be null', () {
      final minimal = {
        'id': 2,
        'user_id': 10,
        'name': '李四',
        'phone': '13900139000',
        'is_active': true,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };
      final customer = Customer.fromJson(minimal);
      expect(customer.email, isNull);
      expect(customer.avatarPath, isNull);
      expect(customer.notes, isNull);
      expect(customer.profile, isNull);
    });

    test('with nested profile', () {
      final j = Map<String, dynamic>.from(json);
      j['profile'] = {
        'id': 1,
        'customer_id': 1,
        'nail_shape': '方形',
        'nail_length': '中长',
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };
      final customer = Customer.fromJson(j);
      expect(customer.profile, isNotNull);
      expect(customer.profile!.nailShape, '方形');
    });
  });

  group('CustomerProfile', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');

    test('fromJson with all fields', () {
      final json = {
        'id': 1,
        'customer_id': 1,
        'nail_shape': '方形',
        'nail_length': '中长',
        'nail_condition': '健康',
        'nail_photos': ['/photos/1.jpg'],
        'color_preferences': ['粉色', '红色'],
        'color_dislikes': ['黑色'],
        'style_preferences': ['简约'],
        'pattern_preferences': '花卉',
        'allergies': '无',
        'prohibitions': null,
        'occasion_preferences': {'daily': '简约'},
        'maintenance_preference': '两周一次',
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };
      final profile = CustomerProfile.fromJson(json);
      expect(profile.nailShape, '方形');
      expect(profile.colorPreferences, ['粉色', '红色']);
      expect(profile.occasionPreferences, {'daily': '简约'});
      expect(profile.maintenancePreference, '两周一次');
    });

    test('fromJson with minimal fields', () {
      final json = {
        'id': 2,
        'customer_id': 2,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };
      final profile = CustomerProfile.fromJson(json);
      expect(profile.nailShape, isNull);
      expect(profile.colorPreferences, isNull);
    });
  });

  group('CustomerListResponse', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');

    test('fromJson parses list', () {
      final json = {
        'total': 2,
        'customers': [
          {
            'id': 1,
            'user_id': 10,
            'name': '张三',
            'phone': '13800138000',
            'is_active': true,
            'created_at': now.toIso8601String(),
            'updated_at': now.toIso8601String(),
          },
          {
            'id': 2,
            'user_id': 10,
            'name': '李四',
            'phone': '13900139000',
            'is_active': true,
            'created_at': now.toIso8601String(),
            'updated_at': now.toIso8601String(),
          },
        ],
      };
      final response = CustomerListResponse.fromJson(json);
      expect(response.total, 2);
      expect(response.customers.length, 2);
      expect(response.customers[0].name, '张三');
    });
  });
}
