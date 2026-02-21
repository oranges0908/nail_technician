import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../models/conversation.dart';
import '../../providers/chat_provider.dart';
import 'widgets/message_bubble.dart';
import 'widgets/quick_replies_row.dart';

/// AI 对话助理主界面
class ChatScreen extends StatefulWidget {
  final int? sessionId;

  const ChatScreen({Key? key, this.sessionId}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    // 在下一帧初始化会话，避免在 build 中调用 setState
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initSession();
    });
  }

  Future<void> _initSession() async {
    final provider = context.read<ChatProvider>();
    if (!provider.isSessionActive) {
      await provider.startSession();
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // ── 操作处理 ──────────────────────────────────────────────────────────────

  Future<void> _sendMessage() async {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;
    _inputController.clear();

    await context.read<ChatProvider>().sendMessage(text);
    _scrollToBottom();
  }

  Future<void> _pickAndUploadImage() async {
    final purpose = _getPurposeByStep(
        context.read<ChatProvider>().currentStep);

    final result = await showModalBottomSheet<String>(
      context: context,
      builder: (_) => _ImageSourceSheet(purpose: purpose),
    );
    if (result == null) return;

    XFile? pickedFile;
    if (result == 'camera') {
      pickedFile = await _imagePicker.pickImage(
          source: ImageSource.camera, imageQuality: 80);
    } else {
      pickedFile = await _imagePicker.pickImage(
          source: ImageSource.gallery, imageQuality: 80);
    }
    if (pickedFile == null) return;

    final bytes = await pickedFile.readAsBytes();
    if (!mounted) return;

    await context.read<ChatProvider>().uploadImage(
          bytes,
          pickedFile.name,
          purpose: purpose,
        );
    _scrollToBottom();
  }

  String _getPurposeByStep(String step) {
    return step == 'complete' ? 'actual' : 'inspiration';
  }

  String _stepLabel(String step) {
    const labels = {
      'greeting': '开始',
      'customer': '客户确认',
      'design': '设计生成',
      'service': '服务记录',
      'complete': '完成服务',
      'analysis': 'AI 分析',
      'review': '成长复盘',
    };
    return labels[step] ?? step;
  }

  // ── Build ────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Consumer<ChatProvider>(
      builder: (context, provider, _) {
        // 自动滚到底部（新消息到来时）
        if (provider.messages.isNotEmpty) {
          _scrollToBottom();
        }

        return Scaffold(
          backgroundColor: const Color(0xFFF5F5F5),
          appBar: _buildAppBar(provider),
          body: Column(
            children: [
              // 消息列表
              Expanded(
                child: _buildMessageList(provider),
              ),

              // 错误提示
              if (provider.error != null)
                _buildErrorBanner(provider),

              // 快捷回复行
              if (provider.quickReplies.isNotEmpty && !provider.isSending)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: QuickRepliesRow(
                      quickReplies: provider.quickReplies),
                ),

              // 输入栏
              _buildInputRow(provider),
            ],
          ),
        );
      },
    );
  }

  AppBar _buildAppBar(ChatProvider provider) {
    return AppBar(
      title: Row(
        children: [
          const Text('AI 助理'),
          const SizedBox(width: 8),
          Chip(
            label: Text(
              _stepLabel(provider.currentStep),
              style: const TextStyle(fontSize: 11, color: Colors.white),
            ),
            backgroundColor: ThemeConfig.primaryColor,
            padding: EdgeInsets.zero,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ],
      ),
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => context.pop(),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.add_comment_outlined),
          tooltip: '新建会话',
          onPressed: () async {
            final confirmed = await showDialog<bool>(
              context: context,
              builder: (_) => AlertDialog(
                title: const Text('新建会话'),
                content: const Text('确定开始新的对话？当前会话将被保留在历史记录中。'),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context, false),
                    child: const Text('取消'),
                  ),
                  TextButton(
                    onPressed: () => Navigator.pop(context, true),
                    child: const Text('确定'),
                  ),
                ],
              ),
            );
            if (confirmed == true && mounted) {
              await provider.newSession();
              _scrollToBottom();
            }
          },
        ),
      ],
    );
  }

  Widget _buildMessageList(ChatProvider provider) {
    if (provider.isLoading && provider.messages.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    final messages = provider.messages;

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(vertical: 12),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final msg = messages[index];

        if (msg.isLoading) {
          return const TypingIndicator();
        }
        if (msg.isUser) {
          return UserBubble(message: msg);
        }
        return AssistantBubble(message: msg);
      },
    );
  }

  Widget _buildErrorBanner(ChatProvider provider) {
    return Container(
      color: ThemeConfig.errorColor.withOpacity(0.1),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          const Icon(Icons.error_outline,
              color: ThemeConfig.errorColor, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              provider.error!,
              style: const TextStyle(
                  color: ThemeConfig.errorColor, fontSize: 13),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: provider.clearError,
            color: ThemeConfig.errorColor,
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
        ],
      ),
    );
  }

  Widget _buildInputRow(ChatProvider provider) {
    final isBusy = provider.isSending || provider.isUploading;

    return Container(
      color: Colors.white,
      padding: EdgeInsets.only(
        left: 8,
        right: 8,
        top: 8,
        bottom: 8 + MediaQuery.of(context).viewInsets.bottom,
      ),
      child: SafeArea(
        top: false,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            // 图片上传按钮
            IconButton(
              icon: Stack(
                alignment: Alignment.topRight,
                children: [
                  const Icon(Icons.photo_camera_outlined),
                  if (provider.needsImageUpload)
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: ThemeConfig.errorColor,
                        shape: BoxShape.circle,
                      ),
                    ),
                ],
              ),
              color: ThemeConfig.primaryColor,
              onPressed: isBusy ? null : _pickAndUploadImage,
              tooltip: '上传图片',
            ),

            // 文本输入框
            Expanded(
              child: TextField(
                controller: _inputController,
                enabled: !isBusy,
                minLines: 1,
                maxLines: 4,
                textCapitalization: TextCapitalization.sentences,
                decoration: InputDecoration(
                  hintText: isBusy ? 'AI 正在处理...' : '输入消息...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(22),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: const Color(0xFFF0F0F0),
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 10),
                ),
                onSubmitted: isBusy ? null : (_) => _sendMessage(),
              ),
            ),

            // 发送按钮
            const SizedBox(width: 4),
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 200),
              child: isBusy
                  ? const Padding(
                      padding: EdgeInsets.all(12),
                      child: SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    )
                  : IconButton(
                      icon: const Icon(Icons.send_rounded),
                      color: ThemeConfig.primaryColor,
                      onPressed: _sendMessage,
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 图片来源选择底部弹窗
class _ImageSourceSheet extends StatelessWidget {
  final String purpose;

  const _ImageSourceSheet({Key? key, required this.purpose}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final label = purpose == 'actual' ? '实拍完成图' : '灵感参考图';

    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              '上传$label',
              style: const TextStyle(
                  fontWeight: FontWeight.bold, fontSize: 16),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.camera_alt_outlined),
            title: const Text('拍照'),
            onTap: () => Navigator.pop(context, 'camera'),
          ),
          ListTile(
            leading: const Icon(Icons.photo_library_outlined),
            title: const Text('从相册选择'),
            onTap: () => Navigator.pop(context, 'gallery'),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}
