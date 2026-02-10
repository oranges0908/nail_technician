import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:nail_app/screens/services/service_list_screen.dart';
import 'package:nail_app/providers/service_provider.dart';
import 'package:nail_app/services/service_record_service.dart';
import 'package:nail_app/models/service_record.dart';
import 'package:nail_app/models/comparison_result.dart' as model;

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

  Widget buildWidget() {
    return ChangeNotifierProvider<ServiceRecordProvider>.value(
      value: provider,
      child: const MaterialApp(home: ServiceListScreen()),
    );
  }

  group('ServiceListScreen', () {
    testWidgets('renders app bar title', (tester) async {
      fakeService.recordsToReturn = [];

      await tester.pumpWidget(buildWidget());

      expect(find.text('服务记录'), findsOneWidget);
    });

    testWidgets('shows filter chips', (tester) async {
      fakeService.recordsToReturn = [];

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('全部'), findsOneWidget);
      expect(find.text('待完成'), findsOneWidget);
      expect(find.text('已完成'), findsOneWidget);
    });

    testWidgets('shows records after load', (tester) async {
      fakeService.recordsToReturn = [
        makeRecord(1, status: 'pending'),
        makeRecord(2, status: 'completed'),
      ];

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('待开始'), findsOneWidget);
      expect(find.text('已完成'), findsWidgets); // filter chip + status label
      expect(find.text('2025-01-15'), findsNWidgets(2));
      expect(find.text('客户 #5'), findsNWidgets(2));
    });

    testWidgets('shows empty view when no records', (tester) async {
      fakeService.recordsToReturn = [];

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('暂无服务记录'), findsOneWidget);
      expect(find.text('点击右下角按钮创建服务记录'), findsOneWidget);
      expect(find.byIcon(Icons.assignment_outlined), findsOneWidget);
    });

    testWidgets('shows error view with retry', (tester) async {
      fakeService.error = Exception('Connection failed');

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('重试'), findsOneWidget);
      expect(find.byIcon(Icons.error_outline), findsOneWidget);
    });

    testWidgets('has floating action button', (tester) async {
      fakeService.recordsToReturn = [];

      await tester.pumpWidget(buildWidget());

      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);
    });
  });
}
