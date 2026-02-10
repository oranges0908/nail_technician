import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:nail_app/screens/designs/design_generate_screen.dart';
import 'package:nail_app/providers/design_provider.dart';
import 'package:nail_app/providers/customer_provider.dart';
import 'package:nail_app/services/design_service.dart';
import 'package:nail_app/services/customer_service.dart';
import 'package:nail_app/models/design_plan.dart';
import 'package:nail_app/models/customer.dart';
import 'package:nail_app/models/customer_profile.dart';

class FakeDesignService extends DesignService {
  DesignPlanListResponse? listResponse;
  DesignPlan? designToReturn;
  Exception? error;

  @override
  Future<DesignPlanListResponse> getDesigns({
    int skip = 0,
    int limit = 20,
    int? customerId,
    String? search,
    int? isArchived,
  }) async {
    if (error != null) throw error!;
    return listResponse!;
  }

  @override
  Future<DesignPlan> generateDesign({
    required String prompt,
    List<String>? referenceImages,
    String designTarget = '10nails',
    List<String>? styleKeywords,
    int? customerId,
    String? title,
    String? notes,
  }) async {
    if (error != null) throw error!;
    return designToReturn!;
  }

  @override
  Future<DesignPlan> refineDesign(int designId, String instruction) async {
    if (error != null) throw error!;
    return designToReturn!;
  }

  @override
  Future<DesignPlan> getDesign(int id) async {
    if (error != null) throw error!;
    return designToReturn!;
  }

  @override
  Future<List<DesignPlan>> getDesignVersions(int id) async => [];

  @override
  Future<void> archiveDesign(int id) async {}

  @override
  Future<void> deleteDesign(int id) async {}
}

class FakeCustomerService extends CustomerService {
  CustomerListResponse? listResponse;
  Exception? error;

  @override
  Future<CustomerListResponse> getCustomers({
    int skip = 0,
    int limit = 20,
    String? search,
    bool? isActive,
  }) async {
    if (error != null) throw error!;
    return listResponse!;
  }

  @override
  Future<Customer> getCustomer(int customerId) async =>
      throw UnimplementedError();

  @override
  Future<Customer> createCustomer({
    required String name,
    required String phone,
    String? email,
    String? notes,
  }) async =>
      throw UnimplementedError();

  @override
  Future<Customer> updateCustomer(int customerId, {
    String? name,
    String? phone,
    String? email,
    String? notes,
    bool? isActive,
  }) async =>
      throw UnimplementedError();

  @override
  Future<void> deleteCustomer(int customerId) async {}

  @override
  Future<CustomerProfile> updateProfile(
    int customerId,
    Map<String, dynamic> profileData,
  ) async =>
      throw UnimplementedError();
}

void main() {
  late FakeDesignService fakeDesignService;
  late FakeCustomerService fakeCustomerService;
  late DesignProvider designProvider;
  late CustomerProvider customerProvider;

  final now = DateTime.now();

  setUp(() {
    fakeDesignService = FakeDesignService();
    fakeCustomerService = FakeCustomerService();
    fakeCustomerService.listResponse =
        CustomerListResponse(total: 0, customers: []);
    designProvider = DesignProvider(service: fakeDesignService);
    customerProvider = CustomerProvider(service: fakeCustomerService);
  });

  Widget buildWidget() {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<DesignProvider>.value(value: designProvider),
        ChangeNotifierProvider<CustomerProvider>.value(
            value: customerProvider),
      ],
      child: const MaterialApp(home: DesignGenerateScreen()),
    );
  }

  group('DesignGenerateScreen', () {
    testWidgets('renders app bar and form fields', (tester) async {
      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('AI 设计生成'), findsOneWidget);
      expect(find.text('设计描述 *'), findsOneWidget);
      expect(find.text('方案标题'), findsOneWidget);
      expect(find.text('风格关键词'), findsOneWidget);
      expect(find.text('设计目标'), findsOneWidget);
    });

    testWidgets('shows validation error for empty prompt', (tester) async {
      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      // Tap the generate button without entering prompt
      await tester.tap(find.text('生成设计'));
      await tester.pump();

      expect(find.text('请输入设计描述'), findsOneWidget);
    });

    testWidgets('displays design target chips', (tester) async {
      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('单个指甲'), findsOneWidget);
      expect(find.text('一只手（5个）'), findsOneWidget);
      expect(find.text('双手（10个）'), findsOneWidget);
    });

    testWidgets('has generate button', (tester) async {
      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('生成设计'), findsOneWidget);
      expect(find.byIcon(Icons.auto_awesome), findsWidgets);
    });

    testWidgets('shows error when generation fails', (tester) async {
      fakeDesignService.error = Exception('500 Internal Server Error');

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      // Enter prompt and submit
      final promptField = find.byType(TextFormField).first;
      await tester.enterText(promptField, '粉色渐变');

      await tester.tap(find.text('生成设计'));
      await tester.pumpAndSettle();

      expect(find.text('AI生成失败，请稍后重试'), findsOneWidget);
    });
  });
}
