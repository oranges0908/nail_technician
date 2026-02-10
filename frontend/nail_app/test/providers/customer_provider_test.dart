import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/customer.dart';
import 'package:nail_app/models/customer_profile.dart';
import 'package:nail_app/providers/customer_provider.dart';
import 'package:nail_app/services/customer_service.dart';

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

  group('CustomerProvider', () {
    test('initial state', () {
      expect(provider.customers, isEmpty);
      expect(provider.isLoading, false);
      expect(provider.error, isNull);
      expect(provider.total, 0);
    });

    test('loadCustomers success populates list', () async {
      final customers = [makeCustomer(1, '张三'), makeCustomer(2, '李四')];
      fakeService.listResponse = CustomerListResponse(
        total: 2,
        customers: customers,
      );

      await provider.loadCustomers();

      expect(provider.customers.length, 2);
      expect(provider.total, 2);
      expect(provider.isLoading, false);
      expect(provider.error, isNull);
    });

    test('loadCustomers error sets error message', () async {
      fakeService.error = Exception('SocketException');

      await provider.loadCustomers();

      expect(provider.error, contains('网络'));
      expect(provider.isLoading, false);
    });

    test('createCustomer adds to list', () async {
      final newCustomer = makeCustomer(3, '王五');
      fakeService.customerToReturn = newCustomer;

      final result = await provider.createCustomer(
        name: '王五',
        phone: '13700137000',
      );

      expect(result, isNotNull);
      expect(result!.name, '王五');
      expect(provider.customers.length, 1);
      expect(provider.total, 1);
    });

    test('deleteCustomer removes from list', () async {
      final customers = [makeCustomer(1, '张三'), makeCustomer(2, '李四')];
      fakeService.listResponse = CustomerListResponse(
        total: 2,
        customers: customers,
      );
      await provider.loadCustomers();
      expect(provider.customers.length, 2);

      fakeService.error = null;
      final result = await provider.deleteCustomer(1);

      expect(result, true);
      expect(provider.customers.length, 1);
      expect(provider.customers[0].name, '李四');
    });

    test('updateCustomer updates list item', () async {
      fakeService.listResponse = CustomerListResponse(
        total: 1,
        customers: [makeCustomer(1, '张三')],
      );
      await provider.loadCustomers();

      fakeService.customerToReturn = makeCustomer(1, '张三改名');
      fakeService.error = null;
      final result = await provider.updateCustomer(1, name: '张三改名');

      expect(result, isNotNull);
      expect(provider.customers[0].name, '张三改名');
    });

    test('clearError clears error', () async {
      fakeService.error = Exception('timeout');
      await provider.loadCustomers();
      expect(provider.error, isNotNull);

      provider.clearError();
      expect(provider.error, isNull);
    });
  });
}
