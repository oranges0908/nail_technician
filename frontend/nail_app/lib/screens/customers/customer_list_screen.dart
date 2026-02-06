import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/customer_provider.dart';
import '../../models/customer.dart';
import '../../utils/constants.dart';

/// 客户列表页面
class CustomerListScreen extends StatefulWidget {
  const CustomerListScreen({Key? key}) : super(key: key);

  @override
  State<CustomerListScreen> createState() => _CustomerListScreenState();
}

class _CustomerListScreenState extends State<CustomerListScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CustomerProvider>().loadCustomers();
    });
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      context.read<CustomerProvider>().loadMore();
    }
  }

  void _onSearch(String query) {
    context.read<CustomerProvider>().loadCustomers(search: query);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('客户管理'),
      ),
      body: Column(
        children: [
          // 搜索栏
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: '搜索客户姓名或手机号',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _onSearch('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(Constants.largeRadius),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              onChanged: _onSearch,
            ),
          ),

          // 客户列表
          Expanded(
            child: Consumer<CustomerProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading && provider.customers.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (provider.error != null && provider.customers.isEmpty) {
                  return _buildErrorView(provider);
                }

                if (provider.customers.isEmpty) {
                  return _buildEmptyView();
                }

                return RefreshIndicator(
                  onRefresh: () => provider.loadCustomers(
                    search: provider.searchQuery,
                  ),
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: provider.customers.length +
                        (provider.hasMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == provider.customers.length) {
                        return const Padding(
                          padding: EdgeInsets.all(16),
                          child: Center(child: CircularProgressIndicator()),
                        );
                      }
                      return _buildCustomerCard(provider.customers[index]);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.go('/customers/new'),
        child: const Icon(Icons.person_add),
      ),
    );
  }

  Widget _buildCustomerCard(Customer customer) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: ThemeConfig.primaryColor.withOpacity(0.1),
          child: Text(
            customer.name.isNotEmpty ? customer.name[0] : '?',
            style: const TextStyle(
              color: ThemeConfig.primaryColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          customer.name,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(customer.phone),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => context.go('/customers/${customer.id}'),
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.people_outline,
            size: 64,
            color: ThemeConfig.textSecondaryLight,
          ),
          const SizedBox(height: 16),
          Text(
            _searchController.text.isNotEmpty ? '未找到匹配的客户' : '暂无客户',
            style: TextStyle(
              fontSize: 16,
              color: ThemeConfig.textSecondaryLight,
            ),
          ),
          if (_searchController.text.isEmpty) ...[
            const SizedBox(height: 8),
            Text(
              '点击右下角按钮添加客户',
              style: TextStyle(
                fontSize: 14,
                color: ThemeConfig.textHintLight,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildErrorView(CustomerProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: ThemeConfig.errorColor),
          const SizedBox(height: 16),
          Text(provider.error ?? Constants.unknownError),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => provider.loadCustomers(),
            child: const Text(Constants.retryButton),
          ),
        ],
      ),
    );
  }
}
