import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/providers/ability_provider.dart';
import 'package:nail_app/services/ability_service.dart';

class FakeAbilityService extends AbilityService {
  Map<String, dynamic>? statsToReturn;
  Map<String, dynamic>? summaryToReturn;
  Map<String, dynamic>? trendToReturn;
  Map<String, dynamic>? dimensionsToReturn;
  Exception? error;
  Exception? trendError;

  @override
  Future<Map<String, dynamic>> getAbilityStats() async {
    if (error != null) throw error!;
    return statsToReturn!;
  }

  @override
  Future<Map<String, dynamic>> getAbilitySummary() async {
    if (error != null) throw error!;
    return summaryToReturn!;
  }

  @override
  Future<Map<String, dynamic>> getAbilityTrend(
    String dimensionName, {
    int limit = 20,
  }) async {
    if (trendError != null) throw trendError!;
    return trendToReturn!;
  }

  @override
  Future<Map<String, dynamic>> initializeDimensions() async {
    if (error != null) throw error!;
    return dimensionsToReturn ?? {};
  }
}

void main() {
  late FakeAbilityService fakeService;
  late AbilityProvider provider;

  setUp(() {
    fakeService = FakeAbilityService();
    provider = AbilityProvider(service: fakeService);
  });

  group('AbilityProvider', () {
    test('initial state', () {
      expect(provider.dimensions, isEmpty);
      expect(provider.scores, isEmpty);
      expect(provider.isLoading, false);
      expect(provider.error, isNull);
      expect(provider.hasData, false);
    });

    test('loadAbilityOverview success', () async {
      fakeService.statsToReturn = {
        'dimensions': ['颜色搭配', '图案精度', '细节处理'],
        'scores': [80.0, 75.0, 90.0],
        'avg_score': 81.7,
        'total_records': 5,
      };
      fakeService.summaryToReturn = {
        'strengths': [
          {'dimension': '细节处理', 'score': 90.0}
        ],
        'improvements': [
          {'dimension': '图案精度', 'score': 75.0}
        ],
        'total_services': 10,
      };

      await provider.loadAbilityOverview();

      expect(provider.dimensions.length, 3);
      expect(provider.scores.length, 3);
      expect(provider.avgScore, closeTo(81.7, 0.1));
      expect(provider.totalRecords, 5);
      expect(provider.strengths.length, 1);
      expect(provider.improvements.length, 1);
      expect(provider.totalServices, 10);
      expect(provider.hasData, true);
      expect(provider.isLoading, false);
    });

    test('loadTrend success', () async {
      fakeService.trendToReturn = {
        'data_points': [
          {'date': '2025-01-01', 'score': 70.0},
          {'date': '2025-01-15', 'score': 80.0},
        ],
      };

      await provider.loadTrend('颜色搭配');

      expect(provider.trendDimensionName, '颜色搭配');
      expect(provider.trendDataPoints.length, 2);
      expect(provider.isTrendLoading, false);
    });

    test('loadAbilityOverview error sets error', () async {
      fakeService.error = Exception('Connection failed');

      await provider.loadAbilityOverview();

      expect(provider.error, isNotNull);
      expect(provider.isLoading, false);
    });

    test('clearError clears error', () async {
      fakeService.error = Exception('timeout');
      await provider.loadAbilityOverview();
      expect(provider.error, isNotNull);

      provider.clearError();
      expect(provider.error, isNull);
    });
  });
}
