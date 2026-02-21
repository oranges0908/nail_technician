import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../../../config/api_config.dart';
import '../../../config/theme_config.dart';
import '../../../models/conversation.dart';
import 'ui_hint_widgets.dart';

/// 用户消息气泡（右对齐，主题色背景）
class UserBubble extends StatelessWidget {
  final ChatMessage message;

  const UserBubble({Key? key, required this.message}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                // 本地图片预览（上传前）
                if (message.imageBytes != null)
                  _buildLocalImagePreview(),
                // 服务器图片缩略图（如有）
                if (message.imagePaths != null &&
                    message.imagePaths!.isNotEmpty)
                  _buildImagePreviews(context),
                // 文字气泡
                if (message.content.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(top: 4),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: ThemeConfig.primaryColor,
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(18),
                        topRight: Radius.circular(18),
                        bottomLeft: Radius.circular(18),
                        bottomRight: Radius.circular(4),
                      ),
                    ),
                    child: Text(
                      message.content,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            radius: 16,
            backgroundColor: ThemeConfig.primaryLightColor,
            child: const Icon(Icons.person, size: 18,
                color: ThemeConfig.primaryColor),
          ),
        ],
      ),
    );
  }

  Widget _buildLocalImagePreview() {
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: Image.memory(
        message.imageBytes!,
        width: 160,
        height: 160,
        fit: BoxFit.cover,
      ),
    );
  }

  Widget _buildImagePreviews(BuildContext context) {
    return Wrap(
      spacing: 4,
      runSpacing: 4,
      alignment: WrapAlignment.end,
      children: message.imagePaths!.map((path) {
        final url = ApiConfig.getStaticFileUrl(path);
        return ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.network(
            url,
            width: 100,
            height: 100,
            fit: BoxFit.cover,
            errorBuilder: (_, __, ___) => Container(
              width: 100,
              height: 100,
              color: Colors.grey[200],
              child: const Icon(Icons.broken_image, color: Colors.grey),
            ),
          ),
        );
      }).toList(),
    );
  }
}

/// 助理消息气泡（左对齐，带头像）
class AssistantBubble extends StatelessWidget {
  final ChatMessage message;

  const AssistantBubble({Key? key, required this.message}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 头像
          Container(
            width: 32,
            height: 32,
            margin: const EdgeInsets.only(top: 4),
            decoration: BoxDecoration(
              color: ThemeConfig.primaryColor,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.auto_awesome, size: 18,
                color: Colors.white),
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 文字气泡
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: ThemeConfig.dividerLight),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(4),
                      topRight: Radius.circular(18),
                      bottomLeft: Radius.circular(18),
                      bottomRight: Radius.circular(18),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.04),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Text(
                    message.content,
                    style: const TextStyle(
                      color: ThemeConfig.textPrimaryLight,
                      fontSize: 15,
                      height: 1.5,
                    ),
                  ),
                ),
                // UI Hint 子 Widget（设计预览、客户卡片等）
                if (message.uiMetadata != null &&
                    message.uiMetadata!.uiHint != 'none')
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: UiHintWidget(uiMetadata: message.uiMetadata!),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// 打字中动画（三个跳动点）
class TypingIndicator extends StatefulWidget {
  const TypingIndicator({Key? key}) : super(key: key);

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(
      3,
      (i) => AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 400),
      )..repeat(reverse: true),
    );
    for (int i = 0; i < 3; i++) {
      Future.delayed(Duration(milliseconds: i * 130), () {
        if (mounted) _controllers[i].repeat(reverse: true);
      });
    }
    _animations = _controllers
        .map((c) => Tween<double>(begin: 0, end: -6).animate(
              CurvedAnimation(parent: c, curve: Curves.easeInOut),
            ))
        .toList();
  }

  @override
  void dispose() {
    for (final c in _controllers) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: const BoxDecoration(
              color: ThemeConfig.primaryColor,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.auto_awesome, size: 18,
                color: Colors.white),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: ThemeConfig.dividerLight),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                return AnimatedBuilder(
                  animation: _animations[i],
                  builder: (_, __) => Transform.translate(
                    offset: Offset(0, _animations[i].value),
                    child: Container(
                      width: 8,
                      height: 8,
                      margin: const EdgeInsets.symmetric(horizontal: 2),
                      decoration: const BoxDecoration(
                        color: ThemeConfig.primaryColor,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}
