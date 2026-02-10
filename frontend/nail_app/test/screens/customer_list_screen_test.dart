import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:nail_app/screens/customers/customer_list_screen.dart';
import 'package:nail_app/providers/customer_provider.dart';
import 'package:nail_app/services/customer_service.dart';
import 'package:nail_app/models/customer.dart';
import 'package:nail_app/models/customer_profile.dart';

class FakeCustomerService extends CustomerService {
  CustomerListResponse? listResponse;
  Customer? customerToReturn;
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
  Future<Customer> getCustomer(int customerId) async {
    if (error != null) throw error!;
    return customerToReturn!;
  }

  @override
  Future<Customer> createCustomer({
    required String name,
    required String phone,
    String? email,
    String? notes,
  }) async {
    if (error != null) throw error!;
    return customerToReturn!;
  }

  @override
  Future<Customer> updateCustomer(int customerId, {
    String? name,
    String? phone,
    String? email,
    String? notes,
    bool? isActive,
  }) async {
    if (error != null) throw error!;
    return customerToReturn!;
  }

  @override
  Future<void> deleteCustomer(int customerId) async {
    if (error != null) throw error!;
  }

  @override
  Future<CustomerProfile> updateProfile(
    int customerId,
    Map<String, dynamic> profileData,
  ) async {
    if (error != null) throw error!;
    return CustomerProfile(
      id: 1,
      customerId: customerId,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }
}

void main() {
  late FakeCustomerService fakeService;
  late CustomerProvider provider;

  final now = DateTime.now();

  Customer makeCustomer(int id, String name) => Customer(
        id: id,
        userId: 1,
        name: name,
        phone: '1380013800$id',
        isActive: true,
        createdAt: now,
        updatedAt: now,
      );

  setUp(() {
    fakeService = FakeCustomerService();
    provider = CustomerProvider(service: fakeService);
  });

  Widget buildWidget() {
    return ChangeNotifierProvider<CustomerProvider>.value(
      value: provider,
      child: const MaterialApp(home: CustomerListScreen()),
    );
  }

  group('CustomerListScreen', () {
    testWidgets('renders app bar title', (tester) async {
      fakeService.listResponse =
          CustomerListResponse(total: 0, customers: []);

      await tester.pumpWidget(buildWidget());

      expect(find.text('客户管理'), findsOneWidget);
    });

    testWidgets('shows customer list after load', (tester) async {
      fakeService.listResponse = CustomerListResponse(
        total: 2,
        customers: [makeCustomer(1, '张三'), makeCustomer(2, '李四')],
      );

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('张三'), findsOneWidget);
      expect(find.text('李四'), findsOneWidget);
      expect(find.text('13800138001'), findsOneWidget);
      expect(find.text('13800138002'), findsOneWidget);
    });

    testWidgets('shows empty view when no customers', (tester) async {
      fakeService.listResponse =
          CustomerListResponse(total: 0, customers: []);

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('暂无客户'), findsOneWidget);
      expect(find.text('点击右下角按钮添加客户'), findsOneWidget);
      expect(find.byIcon(Icons.people_outline), findsOneWidget);
    });

    testWidgets('shows error view with retry button', (tester) async {
      fakeService.error = Exception('SocketException');

      await tester.pumpWidget(buildWidget());
      await tester.pumpAndSettle();

      expect(find.text('重试'), findsOneWidget);
      expect(find.byIcon(Icons.error_outline), findsOneWidget);
    });

    testWidgets('has search field', (tester) async {
      fakeService.listResponse =
          CustomerListResponse(total: 0, customers: []);

      await tester.pumpWidget(buildWidget());

      expect(find.byIcon(Icons.search), findsOneWidget);
      expect(
        find.widgetWithText(TextField, '搜索客户姓名或手机号'),
        findsOneWidget,
      );
    });

    testWidgets('has floating action button', (tester) async {
      fakeService.listResponse =
          CustomerListResponse(total: 0, customers: []);

      await tester.pumpWidget(buildWidget());

      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.byIcon(Icons.person_add), findsOneWidget);
    });
  });
}
