import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/service_record.dart';
import 'package:nail_app/models/comparison_result.dart' as model;
import 'package:nail_app/providers/service_provider.dart';
import 'package:nail_app/services/service_record_service.dart';

class FakeServiceRecordService extends ServiceRecordService {
  List<ServiceRecord>? recordsToReturn;
  ServiceRecord? recordToReturn;
  model.ComparisonResult? comparisonToReturn;
  Exception? error;

  @override
  Future<List<ServiceRecord>> getServiceRecords({
    int? customerId,
    String? status,
    int skip = 0,
    int limit = 20,
  }) async {
    if (error != null) throw error!;
    return recordsToReturn ?? [];
  }

  @override
  Future<ServiceRecord> getServiceRecord(int id) async {
    if (error != null) throw error!;
    return recordToReturn!;
  }

  @override
  Future<ServiceRecord> createServiceRecord({
    required int customerId,
    int? designPlanId,
    required String serviceDate,
    int? serviceDuration,
    String? materialsUsed,
    String? notes,
  }) async {
    if (error != null) throw error!;
    return recordToReturn!;
  }

  @override
  Future<ServiceRecord> completeService(
    int id, {
    required String actualImagePath,
    required int serviceDuration,
    String? materialsUsed,
    String? artistReview,
    String? customerFeedback,
    int? customerSatisfaction,
    String? notes,
  }) async {
    if (error != null) throw error!;
    return recordToReturn!;
  }

  @override
  Future<void> deleteServiceRecord(int id) async {
    if (error != null) throw error!;
  }

  @override
  Future<model.ComparisonResult> getComparison(int serviceId) async {
    if (error != null) throw error!;
    return comparisonToReturn!;
  }

  @override
  Future<model.ComparisonResult> triggerAnalysis(int serviceId) async {
    if (error != null) throw error!;
    return comparisonToReturn!;
  }
}

void main() {
  late FakeServiceRecordService fakeService;
  late ServiceRecordProvider provider;

  final now = DateTime.now();

  ServiceRecord makeRecord(int id, {String status = 'pending'}) =>
      ServiceRecord(
        id: id,
        userId: 1,
        customerId: 5,
        serviceDate: '2025-01-15',
        status: status,
        createdAt: now,
        updatedAt: now,
      );

  setUp(() {
    fakeService = FakeServiceRecordService();
    provider = ServiceRecordProvider(service: fakeService);
  });

  group('ServiceRecordProvider', () {
    test('initial state', () {
      expect(provider.records, isEmpty);
      expect(provider.isLoading, false);
      expect(provider.isAnalyzing, false);
      expect(provider.error, isNull);
      expect(provider.comparison, isNull);
    });

    test('loadRecords success', () async {
      fakeService.recordsToReturn = [makeRecord(1), makeRecord(2)];

      await provider.loadRecords();

      expect(provider.records.length, 2);
      expect(provider.isLoading, false);
    });

    test('createRecord adds to list', () async {
      fakeService.recordToReturn = makeRecord(1);

      final result = await provider.createRecord(
        customerId: 5,
        serviceDate: '2025-01-15',
      );

      expect(result, isNotNull);
      expect(provider.records.length, 1);
      expect(provider.total, 1);
    });

    test('completeService updates record in list', () async {
      fakeService.recordsToReturn = [makeRecord(1)];
      await provider.loadRecords();

      final completed = makeRecord(1, status: 'completed');
      fakeService.recordToReturn = completed;
      fakeService.error = null;

      final result = await provider.completeService(
        1,
        actualImagePath: '/actuals/1.jpg',
        serviceDuration: 90,
      );

      expect(result, isNotNull);
      expect(result!.status, 'completed');
      expect(provider.records[0].status, 'completed');
      expect(provider.selectedRecord, completed);
    });

    test('deleteRecord removes from list', () async {
      fakeService.recordsToReturn = [makeRecord(1), makeRecord(2)];
      await provider.loadRecords();

      fakeService.error = null;
      final result = await provider.deleteRecord(1);

      expect(result, true);
      expect(provider.records.length, 1);
      expect(provider.records[0].id, 2);
    });

    test('triggerAnalysis sets comparison', () async {
      final comparison = model.ComparisonResult(
        id: 1,
        serviceRecordId: 1,
        similarityScore: 85,
        differences: {'color': '准确'},
        suggestions: ['更自然的过渡'],
        analyzedAt: now,
      );
      fakeService.comparisonToReturn = comparison;

      final result = await provider.triggerAnalysis(1);

      expect(result, isNotNull);
      expect(result!.similarityScore, 85);
      expect(provider.comparison, isNotNull);
      expect(provider.isAnalyzing, false);
    });
  });
}
