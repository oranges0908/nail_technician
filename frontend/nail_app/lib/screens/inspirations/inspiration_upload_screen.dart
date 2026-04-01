import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/inspiration_provider.dart';
import '../../services/upload_service.dart';
import '../../services/inspiration_service.dart';
import '../../utils/constants.dart';

/// 灵感图上传页
class InspirationUploadScreen extends StatefulWidget {
  const InspirationUploadScreen({Key? key}) : super(key: key);

  @override
  State<InspirationUploadScreen> createState() =>
      _InspirationUploadScreenState();
}

class _InspirationUploadScreenState extends State<InspirationUploadScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _tagController = TextEditingController();
  final _imagePicker = ImagePicker();
  final _uploadService = UploadService();
  final _inspirationService = InspirationService();

  XFile? _selectedImage;
  Uint8List? _selectedImageBytes;
  String? _selectedCategory;
  List<String> _tags = [];
  bool _isUploading = false;
  double _uploadProgress = 0;

  static const _categories = ['French', 'Gradient', 'Extensions', 'Art', 'Solid', 'Floral', 'Geometric', 'Other'];

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    _tagController.dispose();
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
      final bytes = await picked.readAsBytes();
      setState(() {
        _selectedImage = picked;
        _selectedImageBytes = bytes;
      });
    }
  }

  void _addTag() {
    final tag = _tagController.text.trim();
    if (tag.isNotEmpty && !_tags.contains(tag)) {
      setState(() {
        _tags.add(tag);
        _tagController.clear();
      });
    }
  }

  void _removeTag(String tag) {
    setState(() {
      _tags.remove(tag);
    });
  }

  Future<void> _submit() async {
    if (_selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an image first')),
      );
      return;
    }

    setState(() {
      _isUploading = true;
      _uploadProgress = 0;
    });

    try {
      // 1. 上传图片
      final uploadResult = await _uploadService.uploadImageBytes(
        _selectedImageBytes!,
        _selectedImage!.name,
        'inspirations',
        onProgress: (sent, total) {
          setState(() {
            _uploadProgress = sent / total;
          });
        },
      );

      // 2. 创建灵感图记录
      await _inspirationService.createInspiration(
        imagePath: uploadResult.fileUrl,
        title: _titleController.text.trim().isNotEmpty
            ? _titleController.text.trim()
            : null,
        description: _descriptionController.text.trim().isNotEmpty
            ? _descriptionController.text.trim()
            : null,
        tags: _tags.isNotEmpty ? _tags : null,
        category: _selectedCategory,
      );

      if (mounted) {
        // 刷新列表
        context.read<InspirationProvider>().loadInspirations();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text(Constants.uploadSuccess)),
        );
        context.go(Constants.inspirationsRoute);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Upload failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isUploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Constants.inspirationsRoute),
        ),
        title: const Text('Upload Inspiration'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 图片选择区域
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
                      style: BorderStyle.solid,
                    ),
                  ),
                  child: _selectedImageBytes != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: Image.memory(
                            _selectedImageBytes!,
                            fit: BoxFit.cover,
                            width: double.infinity,
                          ),
                        )
                      : Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.add_photo_alternate_outlined,
                              size: 48,
                              color: ThemeConfig.textHintLight,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Tap to select image',
                              style: TextStyle(
                                color: ThemeConfig.textHintLight,
                              ),
                            ),
                          ],
                        ),
                ),
              ),

              if (_isUploading) ...[
                const SizedBox(height: 12),
                LinearProgressIndicator(value: _uploadProgress),
                const SizedBox(height: 4),
                Text(
                  'Uploading ${(_uploadProgress * 100).toInt()}%',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    color: ThemeConfig.textSecondaryLight,
                  ),
                ),
              ],

              const SizedBox(height: 16),

              // 标题
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: 'Title',
                  hintText: 'Give it a name (optional)',
                  prefixIcon: Icon(Icons.title),
                ),
              ),
              const SizedBox(height: 16),

              // 描述
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  hintText: 'Describe this inspiration (optional)',
                  prefixIcon: Icon(Icons.description_outlined),
                  alignLabelWithHint: true,
                ),
                maxLines: 3,
                keyboardType: TextInputType.multiline,
                textInputAction: TextInputAction.newline,
              ),
              const SizedBox(height: 16),

              // 分类
              DropdownButtonFormField<String>(
                value: _selectedCategory,
                decoration: const InputDecoration(
                  labelText: 'Category',
                  prefixIcon: Icon(Icons.category_outlined),
                ),
                items: _categories
                    .map((cat) => DropdownMenuItem(
                          value: cat,
                          child: Text(cat),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedCategory = value;
                  });
                },
              ),
              const SizedBox(height: 16),

              // 标签输入
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _tagController,
                      decoration: const InputDecoration(
                        labelText: 'Tags',
                        hintText: 'Enter a tag and tap add',
                        prefixIcon: Icon(Icons.tag),
                      ),
                      onFieldSubmitted: (_) => _addTag(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: _addTag,
                    icon: const Icon(Icons.add_circle),
                    color: ThemeConfig.primaryColor,
                  ),
                ],
              ),
              if (_tags.isNotEmpty) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: _tags
                      .map((tag) => Chip(
                            label: Text(tag, style: const TextStyle(fontSize: 12)),
                            onDeleted: () => _removeTag(tag),
                            materialTapTargetSize:
                                MaterialTapTargetSize.shrinkWrap,
                            visualDensity: VisualDensity.compact,
                          ))
                      .toList(),
                ),
              ],

              const SizedBox(height: 32),

              // 提交按钮
              SizedBox(
                height: Constants.largeButtonHeight,
                child: ElevatedButton(
                  onPressed: _isUploading ? null : _submit,
                  child: _isUploading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Text('Upload'),
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
              title: const Text('Take Photo'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Choose from Gallery'),
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
