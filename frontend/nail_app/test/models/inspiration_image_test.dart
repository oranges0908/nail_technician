import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/inspiration_image.dart';

void main() {
  group('InspirationImage', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');
    final json = {
      'id': 1,
      'user_id': 10,
      'image_path': '/inspirations/1.jpg',
      'title': '法式美甲灵感',
      'description': '优雅法式风格',
      'tags': ['法式', '优雅'],
      'category': '法式',
      'source_url': 'https://example.com/1.jpg',
      'source_platform': 'Pinterest',
      'usage_count': 3,
      'last_used_at': now.toIso8601String(),
      'created_at': now.toIso8601String(),
      'updated_at': now.toIso8601String(),
    };

    test('fromJson creates correct InspirationImage', () {
      final img = InspirationImage.fromJson(json);
      expect(img.id, 1);
      expect(img.imagePath, '/inspirations/1.jpg');
      expect(img.title, '法式美甲灵感');
      expect(img.tags, ['法式', '优雅']);
      expect(img.category, '法式');
      expect(img.usageCount, 3);
      expect(img.sourcePlatform, 'Pinterest');
    });

    test('toJson roundtrip', () {
      final img1 = InspirationImage.fromJson(json);
      final img2 = InspirationImage.fromJson(img1.toJson());
      expect(img2.id, img1.id);
      expect(img2.imagePath, img1.imagePath);
      expect(img2.tags, img1.tags);
    });

    test('nullable fields default correctly', () {
      final minimal = {
        'id': 2,
        'user_id': 10,
        'image_path': '/inspirations/2.jpg',
        'usage_count': 0,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };
      final img = InspirationImage.fromJson(minimal);
      expect(img.title, isNull);
      expect(img.tags, isNull);
      expect(img.category, isNull);
      expect(img.lastUsedAt, isNull);
      expect(img.usageCount, 0);
    });

    test('toString contains key info', () {
      final img = InspirationImage.fromJson(json);
      expect(img.toString(), contains('法式美甲灵感'));
    });
  });

  group('InspirationImageListResponse', () {
    final now = DateTime.parse('2025-01-15T10:30:00.000');

    test('fromJson parses list', () {
      final json = {
        'total': 1,
        'inspirations': [
          {
            'id': 1,
            'user_id': 10,
            'image_path': '/inspirations/1.jpg',
            'usage_count': 0,
            'created_at': now.toIso8601String(),
            'updated_at': now.toIso8601String(),
          },
        ],
      };
      final response = InspirationImageListResponse.fromJson(json);
      expect(response.total, 1);
      expect(response.inspirations.length, 1);
    });
  });
}
