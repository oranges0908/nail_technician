import 'package:flutter/material.dart';
import '../../../config/theme_config.dart';
import '../../../providers/chat_provider.dart';
import 'package:provider/provider.dart';

/// 快捷回复行（水平滚动的 ActionChip）
class QuickRepliesRow extends StatelessWidget {
  final List<String> quickReplies;

  const QuickRepliesRow({
    Key? key,
    required this.quickReplies,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (quickReplies.isEmpty) return const SizedBox.shrink();

    return Container(
      height: 44,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: quickReplies.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final reply = quickReplies[index];
          return ActionChip(
            label: Text(reply),
            labelStyle: const TextStyle(
              color: ThemeConfig.primaryColor,
              fontSize: 13,
            ),
            backgroundColor: ThemeConfig.primaryLightColor.withOpacity(0.3),
            side: BorderSide(
              color: ThemeConfig.primaryColor.withOpacity(0.4),
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            onPressed: () {
              context.read<ChatProvider>().sendMessage(reply);
            },
          );
        },
      ),
    );
  }
}
