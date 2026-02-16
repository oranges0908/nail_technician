import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/customer_provider.dart';
import '../../models/customer.dart';
import '../../models/customer_profile.dart';
import '../../utils/constants.dart';

/// 客户详情页面
class CustomerDetailScreen extends StatefulWidget {
  final int customerId;

  const CustomerDetailScreen({Key? key, required this.customerId})
      : super(key: key);

  @override
  State<CustomerDetailScreen> createState() => _CustomerDetailScreenState();
}

class _CustomerDetailScreenState extends State<CustomerDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CustomerProvider>().getCustomerDetail(widget.customerId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.customersRoute),
        ),
        title: const Text('客户详情'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () => context.go(
              '/customers/${widget.customerId}/edit',
            ),
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'delete') _confirmDelete();
            },
            itemBuilder: (context) => [
              PopupMenuItem<String>(
                value: 'delete',
                child: Row(
                  children: const [
                    Icon(Icons.delete_outline, size: 20, color: ThemeConfig.errorColor),
                    SizedBox(width: 8),
                    Text('删除客户'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Consumer<CustomerProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading && provider.selectedCustomer == null) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null && provider.selectedCustomer == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: ThemeConfig.errorColor),
                  const SizedBox(height: 16),
                  Text(provider.error!),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => provider.getCustomerDetail(widget.customerId),
                    child: const Text(Constants.retryButton),
                  ),
                ],
              ),
            );
          }

          final customer = provider.selectedCustomer;
          if (customer == null) {
            return const Center(child: Text('客户不存在'));
          }

          return RefreshIndicator(
            onRefresh: () => provider.getCustomerDetail(widget.customerId),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildBasicInfo(customer),
                  const SizedBox(height: 16),
                  if (customer.profile != null) ...[
                    _buildProfileSection(customer.profile!),
                  ] else
                    _buildNoProfileHint(),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildBasicInfo(Customer customer) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 32,
                  backgroundColor: ThemeConfig.primaryColor.withOpacity(0.1),
                  child: Text(
                    customer.name.isNotEmpty ? customer.name[0] : '?',
                    style: const TextStyle(
                      fontSize: 28,
                      color: ThemeConfig.primaryColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        customer.name,
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(Icons.phone, size: 16, color: ThemeConfig.textSecondaryLight),
                          const SizedBox(width: 4),
                          Text(
                            customer.phone,
                            style: TextStyle(color: ThemeConfig.textSecondaryLight),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            if (customer.email != null && customer.email!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  const Icon(Icons.email_outlined, size: 16, color: ThemeConfig.textSecondaryLight),
                  const SizedBox(width: 4),
                  Text(
                    customer.email!,
                    style: TextStyle(color: ThemeConfig.textSecondaryLight),
                  ),
                ],
              ),
            ],
            if (customer.notes != null && customer.notes!.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Text(
                '备注',
                style: TextStyle(
                  fontSize: 12,
                  color: ThemeConfig.textHintLight,
                ),
              ),
              const SizedBox(height: 4),
              Text(customer.notes!),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildProfileSection(CustomerProfile profile) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '客户档案',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton.icon(
                  icon: const Icon(Icons.edit, size: 16),
                  label: const Text('编辑'),
                  onPressed: () => context.go(
                    '/customers/${widget.customerId}/profile',
                  ),
                ),
              ],
            ),
            const Divider(),

            // 甲型信息
            if (profile.nailShape != null || profile.nailLength != null) ...[
              _buildSectionTitle('甲型信息'),
              if (profile.nailShape != null)
                _buildInfoRow('甲形', profile.nailShape!),
              if (profile.nailLength != null)
                _buildInfoRow('甲长', profile.nailLength!),
              if (profile.nailCondition != null)
                _buildInfoRow('甲况', profile.nailCondition!),
              const SizedBox(height: 12),
            ],

            // 颜色偏好
            if (profile.colorPreferences != null &&
                profile.colorPreferences!.isNotEmpty) ...[
              _buildSectionTitle('喜欢的颜色'),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: profile.colorPreferences!
                    .map((c) => Chip(
                          label: Text(c, style: const TextStyle(fontSize: 12)),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ))
                    .toList(),
              ),
              const SizedBox(height: 12),
            ],

            if (profile.colorDislikes != null &&
                profile.colorDislikes!.isNotEmpty) ...[
              _buildSectionTitle('不喜欢的颜色'),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: profile.colorDislikes!
                    .map((c) => Chip(
                          label: Text(c, style: const TextStyle(fontSize: 12)),
                          backgroundColor: ThemeConfig.errorColor.withOpacity(0.1),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ))
                    .toList(),
              ),
              const SizedBox(height: 12),
            ],

            // 风格偏好
            if (profile.stylePreferences != null &&
                profile.stylePreferences!.isNotEmpty) ...[
              _buildSectionTitle('风格偏好'),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: profile.stylePreferences!
                    .map((s) => Chip(
                          label: Text(s, style: const TextStyle(fontSize: 12)),
                          backgroundColor: ThemeConfig.accentColor.withOpacity(0.1),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ))
                    .toList(),
              ),
              const SizedBox(height: 12),
            ],

            // 过敏和禁忌
            if (profile.allergies != null && profile.allergies!.isNotEmpty) ...[
              _buildSectionTitle('过敏信息'),
              Text(profile.allergies!),
              const SizedBox(height: 12),
            ],
            if (profile.prohibitions != null &&
                profile.prohibitions!.isNotEmpty) ...[
              _buildSectionTitle('禁忌事项'),
              Text(profile.prohibitions!),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: ThemeConfig.textSecondaryLight,
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 60,
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: ThemeConfig.textSecondaryLight,
              ),
            ),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 14))),
        ],
      ),
    );
  }

  Widget _buildNoProfileHint() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(
              Icons.assignment_outlined,
              size: 48,
              color: ThemeConfig.textHintLight,
            ),
            const SizedBox(height: 12),
            Text(
              '尚未创建客户档案',
              style: TextStyle(color: ThemeConfig.textSecondaryLight),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: () => context.go(
                '/customers/${widget.customerId}/profile',
              ),
              child: const Text('创建档案'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _confirmDelete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(Constants.deleteConfirmTitle),
        content: const Text('确定要删除该客户吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text(Constants.cancelButton),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: ThemeConfig.errorColor),
            child: const Text(Constants.deleteButton),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final provider = context.read<CustomerProvider>();
      final success = await provider.deleteCustomer(widget.customerId);
      if (success) {
        context.go(Constants.customersRoute);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text(Constants.deleteSuccess)),
        );
      } else if (provider.error != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(provider.error!)),
        );
      }
    }
  }
}
