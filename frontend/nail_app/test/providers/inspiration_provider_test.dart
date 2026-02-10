import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/inspiration_image.dart';
import 'package:nail_app/providers/inspiration_provider.dart';
import 'package:nail_app/services/inspiration_service.dart';

class FakeInspirationService extends InspirationService {
  InspirationImageListResponse? listResponse;
  Exception? error;

  @override
  Future<InspirationImageListResponse> getInspirations({
    int skip = 0,
    int limit = 20,
    String? category,
    List<String>? tags,
    String? search,
  }) async {
    if (error != null) throw error!;
    return listResponse!;
  }

  @override
  Future<void> deleteInspiration(int id) async {
    if (error != null) throw error!;
  }
}

void main() {
  late FakeInspirationService fakeService;
  late InspirationProvider provider;

  final now = DateTime.now();

  InspirationImage makeInspiration(int id) => InspirationImage(
        id: id,
        userId: 1,
        imagePath: '/inspirations/$id.jpg',
        title: '灵感图$id',
        category: '法式',
        usageCount: 0,
        createdAt: now,
        updatedAt: now,
      );

  setUp(() {
    fakeService = FakeInspirationService();
    provider = InspirationProvider(service: fakeService);
  });

  group('InspirationProvider', () {
    test('initial state', () {
      expect(provider.inspirations, isEmpty);
      expect(provider.isLoading, false);
      expect(provider.error, isNull);
    });

    test('loadInspirations success', () async {
      fakeService.listResponse = InspirationImageListResponse(
        total: 2,
        inspirations: [makeInspiration(1), makeInspiration(2)],
      );

      await provider.loadInspirations();

      expect(provider.inspirations.length, 2);
      expect(provider.total, 2);
      expect(provider.isLoading, false);
    });

    test('deleteInspiration removes from list', () async {
      fakeService.listResponse = InspirationImageListResponse(
        total: 2,
        inspirations: [makeInspiration(1), makeInspiration(2)],
      );
      await provider.loadInspirations();

      fakeService.error = null;
      final result = await provider.deleteInspiration(1);

      expect(result, true);
      expect(provider.inspirations.length, 1);
      expect(provider.inspirations[0].id, 2);
    });

    test('loadInspirations error sets error', () async {
      fakeService.error = Exception('Connection failed');

      await provider.loadInspirations();

      expect(provider.error, contains('网络'));
      expect(provider.isLoading, false);
    });

    test('clearError clears error', () async {
      fakeService.error = Exception('timeout');
      await provider.loadInspirations();
      expect(provider.error, isNotNull);

      provider.clearError();
      expect(provider.error, isNull);
    });
  });
}
