import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/customer_provider.dart';
import '../../utils/constants.dart';

/// 客户创建/编辑页面
class CustomerFormScreen extends StatefulWidget {
  final int? customerId;

  const CustomerFormScreen({Key? key, this.customerId}) : super(key: key);

  @override
  State<CustomerFormScreen> createState() => _CustomerFormScreenState();
}

class _CustomerFormScreenState extends State<CustomerFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _notesController = TextEditingController();
  bool _isSubmitting = false;

  bool get isEdit => widget.customerId != null;

  @override
  void initState() {
    super.initState();
    if (isEdit) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _loadCustomerData();
      });
    }
  }

  Future<void> _loadCustomerData() async {
    final provider = context.read<CustomerProvider>();
    await provider.getCustomerDetail(widget.customerId!);
    final customer = provider.selectedCustomer;
    if (customer != null) {
      _nameController.text = customer.name;
      _phoneController.text = customer.phone;
      _emailController.text = customer.email ?? '';
      _notesController.text = customer.notes ?? '';
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => isEdit
              ? context.go('/customers/${widget.customerId}')
              : context.go(Constants.customersRoute),
        ),
        title: Text(isEdit ? '编辑客户' : '添加客户'),
      ),
      body: Consumer<CustomerProvider>(
        builder: (context, provider, _) {
          if (isEdit && provider.isLoading && provider.selectedCustomer == null) {
            return const Center(child: CircularProgressIndicator());
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 错误提示
                  if (provider.error != null)
                    Container(
                      padding: const EdgeInsets.all(12),
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: ThemeConfig.errorColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline,
                              color: ThemeConfig.errorColor, size: 20),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              provider.error!,
                              style: const TextStyle(color: ThemeConfig.errorColor),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, size: 18),
                            onPressed: provider.clearError,
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                          ),
                        ],
                      ),
                    ),

                  // 姓名
                  TextFormField(
                    controller: _nameController,
                    decoration: const InputDecoration(
                      labelText: '姓名 *',
                      hintText: '请输入客户姓名',
                      helperText: '必填，最多100个字符',
                      prefixIcon: Icon(Icons.person_outline),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return Constants.emptyNameError;
                      }
                      if (value.trim().length > 100) {
                        return '姓名不能超过100个字符';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // 手机号
                  TextFormField(
                    controller: _phoneController,
                    decoration: const InputDecoration(
                      labelText: '手机号 *',
                      hintText: '请输入手机号',
                      helperText: '必填，11位国内手机号',
                      prefixIcon: Icon(Icons.phone_outlined),
                    ),
                    keyboardType: TextInputType.phone,
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return Constants.emptyPhoneError;
                      }
                      if (!Constants.phoneRegex.hasMatch(value.trim())) {
                        return Constants.invalidPhoneError;
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // 邮箱
                  TextFormField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: '邮箱',
                      hintText: '请输入邮箱（选填）',
                      helperText: '选填，如填写需为有效邮箱格式',
                      prefixIcon: Icon(Icons.email_outlined),
                    ),
                    keyboardType: TextInputType.emailAddress,
                    validator: (value) {
                      if (value != null &&
                          value.isNotEmpty &&
                          !Constants.emailRegex.hasMatch(value.trim())) {
                        return Constants.invalidEmailError;
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // 备注
                  TextFormField(
                    controller: _notesController,
                    decoration: const InputDecoration(
                      labelText: '备注',
                      hintText: '请输入备注信息（选填）',
                      prefixIcon: Icon(Icons.notes_outlined),
                      alignLabelWithHint: true,
                    ),
                    maxLines: 3,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                  ),
                  const SizedBox(height: 32),

                  // 提交按钮
                  SizedBox(
                    height: Constants.largeButtonHeight,
                    child: ElevatedButton(
                      onPressed: _isSubmitting ? null : _submit,
                      child: _isSubmitting
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : Text(isEdit ? Constants.saveButton : '添加客户'),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    final provider = context.read<CustomerProvider>();

    if (isEdit) {
      final result = await provider.updateCustomer(
        widget.customerId!,
        name: _nameController.text.trim(),
        phone: _phoneController.text.trim(),
        email: _emailController.text.trim(),
        notes: _notesController.text.trim(),
      );
      if (result != null) {
        context.go('/customers/${widget.customerId}');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text(Constants.updateSuccess)),
        );
      }
    } else {
      final result = await provider.createCustomer(
        name: _nameController.text.trim(),
        phone: _phoneController.text.trim(),
        email: _emailController.text.trim().isNotEmpty
            ? _emailController.text.trim()
            : null,
        notes: _notesController.text.trim().isNotEmpty
            ? _notesController.text.trim()
            : null,
      );
      if (result != null) {
        context.go('/customers/${result.id}');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text(Constants.createSuccess)),
        );
      }
    }

    if (mounted) {
      setState(() => _isSubmitting = false);
    }
  }
}
