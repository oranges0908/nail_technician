import 'dart:io';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/service_provider.dart';
import '../../services/upload_service.dart';
import '../../utils/constants.dart';

/// 完成服务记录页
class ServiceCompleteScreen extends StatefulWidget {
  final int serviceId;

  const ServiceCompleteScreen({Key? key, required this.serviceId})
      : super(key: key);

  @override
  State<ServiceCompleteScreen> createState() => _ServiceCompleteScreenState();
}

class _ServiceCompleteScreenState extends State<ServiceCompleteScreen> {
  final _formKey = GlobalKey<FormState>();
  final _durationController = TextEditingController();
  final _materialsController = TextEditingController();
  final _reviewController = TextEditingController();
  final _feedbackController = TextEditingController();
  final _imagePicker = ImagePicker();
  final _uploadService = UploadService();

  File? _actualImage;
  int _satisfaction = 5;
  bool _isSubmitting = false;
  double _uploadProgress = 0;

  @override
  void dispose() {
    _durationController.dispose();
    _materialsController.dispose();
    _reviewController.dispose();
    _feedbackController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final picked = await _imagePicker.pickImage(
      source: source,
      maxWidth: 1920,
      maxHeight: 1920,
      imageQuality: 85,
    );
    if (picked != null) {
      setState(() {
        _actualImage = File(picked.path);
      });
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_actualImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请上传实际完成图')),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
      _uploadProgress = 0;
    });

    try {
      // 1. 上传实际图
      final uploadResult = await _uploadService.uploadImage(
        _actualImage!.path,
        'actuals',
        onProgress: (sent, total) {
          setState(() {
            _uploadProgress = sent / total * 0.5; // 50% for upload
          });
        },
      );

      setState(() {
        _uploadProgress = 0.5;
      });

      // 2. 完成服务记录（会自动触发AI分析）
      final provider = context.read<ServiceRecordProvider>();
      final record = await provider.completeService(
        widget.serviceId,
        actualImagePath: uploadResult.fileUrl,
        serviceDuration: int.parse(_durationController.text),
        materialsUsed: _materialsController.text.trim().isNotEmpty
            ? _materialsController.text.trim()
            : null,
        artistReview: _reviewController.text.trim().isNotEmpty
            ? _reviewController.text.trim()
            : null,
        customerFeedback: _feedbackController.text.trim().isNotEmpty
            ? _feedbackController.text.trim()
            : null,
        customerSatisfaction: _satisfaction,
      );

      setState(() {
        _uploadProgress = 1.0;
      });

      if (record != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('服务完成！AI 正在分析...')),
        );
        // 尝试获取分析结果
        await provider.getComparison(widget.serviceId);
        if (mounted) {
          context.go('/services/${widget.serviceId}');
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('操作失败: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('完成服务'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 实际图上传
              const Text(
                '实际完成图 *',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              GestureDetector(
                onTap: () => _showImageSourceDialog(),
                child: Container(
                  height: 200,
                  decoration: BoxDecoration(
                    color: ThemeConfig.dividerLight.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: ThemeConfig.dividerLight,
                      width: 2,
                    ),
                  ),
                  child: _actualImage != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: Image.file(
                            _actualImage!,
                            fit: BoxFit.cover,
                            width: double.infinity,
                          ),
                        )
                      : Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.camera_alt_outlined,
                                size: 48, color: ThemeConfig.textHintLight),
                            const SizedBox(height: 8),
                            Text('点击拍照或选择图片',
                                style: TextStyle(
                                    color: ThemeConfig.textHintLight)),
                          ],
                        ),
                ),
              ),

              if (_isSubmitting) ...[
                const SizedBox(height: 12),
                LinearProgressIndicator(value: _uploadProgress),
                const SizedBox(height: 4),
                Text(
                  _uploadProgress < 0.5
                      ? '上传图片中...'
                      : _uploadProgress < 1.0
                          ? '提交中...'
                          : '完成！',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    color: ThemeConfig.textSecondaryLight,
                  ),
                ),
              ],

              const SizedBox(height: 16),

              // 实际时长
              TextFormField(
                controller: _durationController,
                decoration: const InputDecoration(
                  labelText: '实际服务时长（分钟）*',
                  hintText: '输入实际服务时长',
                  prefixIcon: Icon(Icons.timer),
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return '请输入服务时长';
                  }
                  final num = int.tryParse(value);
                  if (num == null || num <= 0) {
                    return '请输入有效的时长';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // 使用材料
              TextFormField(
                controller: _materialsController,
                decoration: const InputDecoration(
                  labelText: '使用材料',
                  hintText: '记录实际使用的材料（选填）',
                  prefixIcon: Icon(Icons.inventory_outlined),
                  alignLabelWithHint: true,
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 16),

              // 美甲师复盘
              TextFormField(
                controller: _reviewController,
                decoration: const InputDecoration(
                  labelText: '美甲师复盘',
                  hintText: '记录你的复盘心得（选填）',
                  prefixIcon: Icon(Icons.rate_review_outlined),
                  alignLabelWithHint: true,
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),

              // 客户反馈
              TextFormField(
                controller: _feedbackController,
                decoration: const InputDecoration(
                  labelText: '客户反馈',
                  hintText: '记录客户的评价（选填）',
                  prefixIcon: Icon(Icons.feedback_outlined),
                  alignLabelWithHint: true,
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 16),

              // 满意度评分
              const Text(
                '客户满意度',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  5,
                  (i) => IconButton(
                    onPressed: () {
                      setState(() {
                        _satisfaction = i + 1;
                      });
                    },
                    icon: Icon(
                      i < _satisfaction ? Icons.star : Icons.star_border,
                      size: 36,
                      color: ThemeConfig.warningColor,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // 提交按钮
              SizedBox(
                height: Constants.largeButtonHeight,
                child: ElevatedButton.icon(
                  onPressed: _isSubmitting ? null : _submit,
                  icon: _isSubmitting
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.check),
                  label: Text(_isSubmitting ? '提交中...' : '完成服务'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('拍照'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('从相册选择'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }
}
