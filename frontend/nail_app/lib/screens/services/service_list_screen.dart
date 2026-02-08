import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../config/app_config.dart';
import '../../providers/service_provider.dart';
import '../../models/service_record.dart';
import '../../utils/constants.dart';

/// 服务记录列表页
class ServiceListScreen extends StatefulWidget {
  const ServiceListScreen({Key? key}) : super(key: key);

  @override
  State<ServiceListScreen> createState() => _ServiceListScreenState();
}

class _ServiceListScreenState extends State<ServiceListScreen> {
  final _scrollController = ScrollController();
  String? _statusFilter;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ServiceRecordProvider>().loadRecords();
    });
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      context.read<ServiceRecordProvider>().loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('服务记录'),
      ),
      body: Column(
        children: [
          // 状态筛选
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: Row(
              children: [
                _buildFilterChip('全部', null),
                const SizedBox(width: 8),
                _buildFilterChip('待完成', 'pending'),
                const SizedBox(width: 8),
                _buildFilterChip('已完成', 'completed'),
              ],
            ),
          ),

          // 列表
          Expanded(
            child: Consumer<ServiceRecordProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading && provider.records.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (provider.error != null && provider.records.isEmpty) {
                  return _buildErrorView(provider);
                }

                if (provider.records.isEmpty) {
                  return _buildEmptyView();
                }

                return RefreshIndicator(
                  onRefresh: () =>
                      provider.loadRecords(status: _statusFilter),
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount:
                        provider.records.length + (provider.hasMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == provider.records.length) {
                        return const Padding(
                          padding: EdgeInsets.all(16),
                          child: Center(child: CircularProgressIndicator()),
                        );
                      }
                      return _buildRecordCard(provider.records[index]);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.go('/services/new'),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildFilterChip(String label, String? status) {
    final isSelected = _statusFilter == status;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        setState(() {
          _statusFilter = status;
        });
        context
            .read<ServiceRecordProvider>()
            .loadRecords(status: status ?? '');
      },
      selectedColor: ThemeConfig.primaryLightColor,
    );
  }

  Widget _buildRecordCard(ServiceRecord record) {
    final statusLabel =
        AppConfig.serviceStatusLabels[record.status] ?? record.status;
    final statusColor =
        record.isCompleted ? ThemeConfig.successColor : ThemeConfig.warningColor;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: () => context.go('/services/${record.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // 状态标签
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      statusLabel,
                      style: TextStyle(
                        fontSize: 12,
                        color: statusColor,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    record.serviceDate,
                    style: TextStyle(
                      fontSize: 13,
                      color: ThemeConfig.textSecondaryLight,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.person_outline,
                      size: 16, color: ThemeConfig.textHintLight),
                  const SizedBox(width: 4),
                  Text(
                    '客户 #${record.customerId}',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  if (record.designPlanId != null) ...[
                    const SizedBox(width: 12),
                    Icon(Icons.brush_outlined,
                        size: 16, color: ThemeConfig.textHintLight),
                    const SizedBox(width: 4),
                    Text(
                      '设计 #${record.designPlanId}',
                      style: TextStyle(
                        fontSize: 13,
                        color: ThemeConfig.textSecondaryLight,
                      ),
                    ),
                  ],
                ],
              ),
              if (record.serviceDuration != null ||
                  record.customerSatisfaction != null) ...[
                const SizedBox(height: 6),
                Row(
                  children: [
                    if (record.serviceDuration != null) ...[
                      Icon(Icons.timer_outlined,
                          size: 14, color: ThemeConfig.textHintLight),
                      const SizedBox(width: 4),
                      Text(
                        '${record.serviceDuration} 分钟',
                        style: TextStyle(
                          fontSize: 12,
                          color: ThemeConfig.textSecondaryLight,
                        ),
                      ),
                    ],
                    if (record.customerSatisfaction != null) ...[
                      const SizedBox(width: 16),
                      ...List.generate(
                        5,
                        (i) => Icon(
                          i < record.customerSatisfaction!
                              ? Icons.star
                              : Icons.star_border,
                          size: 14,
                          color: ThemeConfig.warningColor,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.assignment_outlined,
              size: 64, color: ThemeConfig.textSecondaryLight),
          const SizedBox(height: 16),
          Text(
            '暂无服务记录',
            style: TextStyle(
                fontSize: 16, color: ThemeConfig.textSecondaryLight),
          ),
          const SizedBox(height: 8),
          Text(
            '点击右下角按钮创建服务记录',
            style:
                TextStyle(fontSize: 14, color: ThemeConfig.textHintLight),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView(ServiceRecordProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline,
              size: 64, color: ThemeConfig.errorColor),
          const SizedBox(height: 16),
          Text(provider.error ?? Constants.unknownError),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => provider.loadRecords(),
            child: const Text(Constants.retryButton),
          ),
        ],
      ),
    );
  }
}
