import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/service_provider.dart';
import '../../providers/customer_provider.dart';
import '../../providers/design_provider.dart';
import '../../utils/constants.dart';

/// 创建服务记录页
class ServiceCreateScreen extends StatefulWidget {
  const ServiceCreateScreen({Key? key}) : super(key: key);

  @override
  State<ServiceCreateScreen> createState() => _ServiceCreateScreenState();
}

class _ServiceCreateScreenState extends State<ServiceCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _notesController = TextEditingController();
  final _durationController = TextEditingController();

  int? _selectedCustomerId;
  int? _selectedDesignId;
  DateTime _serviceDate = DateTime.now();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CustomerProvider>().loadCustomers();
      context.read<DesignProvider>().loadDesigns();
    });
  }

  @override
  void dispose() {
    _notesController.dispose();
    _durationController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _serviceDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      locale: const Locale('en', 'US'),
    );
    if (picked != null) {
      setState(() {
        _serviceDate = picked;
      });
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedCustomerId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a customer')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    final provider = context.read<ServiceRecordProvider>();
    final record = await provider.createRecord(
      customerId: _selectedCustomerId!,
      designPlanId: _selectedDesignId,
      serviceDate: DateFormat('yyyy-MM-dd').format(_serviceDate),
      serviceDuration: _durationController.text.isNotEmpty
          ? int.tryParse(_durationController.text)
          : null,
      notes: _notesController.text.trim().isNotEmpty
          ? _notesController.text.trim()
          : null,
    );

    if (mounted) {
      setState(() => _isSubmitting = false);
      if (record != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text(Constants.createSuccess)),
        );
        context.go('/services/${record.id}');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.servicesRoute),
        ),
        title: const Text('Create Service Record'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 客户选择
              Consumer<CustomerProvider>(
                builder: (context, customerProvider, _) {
                  return DropdownButtonFormField<int>(
                    value: _selectedCustomerId,
                    decoration: const InputDecoration(
                      labelText: 'Customer *',
                      hintText: 'Select a customer',
                      helperText: 'Required, select a customer',
                      prefixIcon: Icon(Icons.person_outline),
                    ),
                    items: customerProvider.customers
                        .map((c) => DropdownMenuItem<int>(
                              value: c.id,
                              child: Text(c.name),
                            ))
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedCustomerId = value;
                      });
                    },
                    validator: (value) {
                      if (value == null) return 'Please select a customer';
                      return null;
                    },
                  );
                },
              ),
              const SizedBox(height: 16),

              // 设计方案选择
              Consumer<DesignProvider>(
                builder: (context, designProvider, _) {
                  return DropdownButtonFormField<int>(
                    value: _selectedDesignId,
                    decoration: const InputDecoration(
                      labelText: 'Design Plan',
                      hintText: 'Link a design plan (optional)',
                      prefixIcon: Icon(Icons.brush_outlined),
                    ),
                    items: [
                      const DropdownMenuItem<int>(
                        value: null,
                        child: Text('No design plan'),
                      ),
                      ...designProvider.designs.map(
                        (d) => DropdownMenuItem<int>(
                          value: d.id,
                          child: Text(
                            d.title ?? 'Design #${d.id}',
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedDesignId = value;
                      });
                    },
                  );
                },
              ),
              const SizedBox(height: 16),

              // 服务日期
              InkWell(
                onTap: _pickDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Service Date',
                    prefixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Text(
                    DateFormat('MMM dd, yyyy').format(_serviceDate),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // 预估时长
              TextFormField(
                controller: _durationController,
                decoration: const InputDecoration(
                  labelText: 'Est. Duration (min)',
                  hintText: 'Enter estimated duration (optional)',
                  helperText: 'Optional, must be a positive integer',
                  prefixIcon: Icon(Icons.timer_outlined),
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value != null && value.isNotEmpty) {
                    final num = int.tryParse(value);
                    if (num == null || num <= 0) {
                      return 'Please enter a valid duration';
                    }
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // 备注
              TextFormField(
                controller: _notesController,
                decoration: const InputDecoration(
                  labelText: 'Notes',
                  hintText: 'Enter notes (optional)',
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
                      : const Text('Create Record'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
