import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/user.dart';

void main() {
  group('User', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');
    final json = {
      'id': 1,
      'email': 'test@example.com',
      'username': 'testuser',
      'is_active': true,
      'is_superuser': false,
      'created_at': now.toIso8601String(),
      'updated_at': null,
    };

    test('fromJson creates correct User', () {
      final user = User.fromJson(json);
      expect(user.id, 1);
      expect(user.email, 'test@example.com');
      expect(user.username, 'testuser');
      expect(user.isActive, true);
      expect(user.isSuperuser, false);
      expect(user.createdAt, now);
      expect(user.updatedAt, isNull);
    });

    test('toJson produces correct map', () {
      final user = User.fromJson(json);
      final result = user.toJson();
      expect(result['id'], 1);
      expect(result['email'], 'test@example.com');
      expect(result['is_active'], true);
      expect(result['is_superuser'], false);
    });

    test('fromJson with updatedAt', () {
      final jsonWithUpdate = Map<String, dynamic>.from(json);
      jsonWithUpdate['updated_at'] = '2025-02-01T12:00:00.000';
      final user = User.fromJson(jsonWithUpdate);
      expect(user.updatedAt, isNotNull);
      expect(user.updatedAt!.month, 2);
    });

    test('roundtrip fromJson -> toJson -> fromJson', () {
      final user1 = User.fromJson(json);
      final user2 = User.fromJson(user1.toJson());
      expect(user2.id, user1.id);
      expect(user2.email, user1.email);
      expect(user2.username, user1.username);
      expect(user2.isActive, user1.isActive);
    });

    test('copyWith creates modified copy', () {
      final user = User.fromJson(json);
      final modified = user.copyWith(username: 'newname', isActive: false);
      expect(modified.username, 'newname');
      expect(modified.isActive, false);
      expect(modified.email, user.email);
      expect(modified.id, user.id);
    });

    test('copyWith with no changes preserves values', () {
      final user = User.fromJson(json);
      final copy = user.copyWith();
      expect(copy.id, user.id);
      expect(copy.email, user.email);
    });

    test('toString contains key info', () {
      final user = User.fromJson(json);
      expect(user.toString(), contains('testuser'));
      expect(user.toString(), contains('test@example.com'));
    });
  });
}
