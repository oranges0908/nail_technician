import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/main.dart';
import 'package:nail_app/providers/auth_provider.dart';

void main() {
  testWidgets('App starts with splash screen', (WidgetTester tester) async {
    final authProvider = AuthProvider();
    await tester.pumpWidget(MyApp(authProvider: authProvider));

    // 验证启动页显示应用名称
    expect(find.text('Nail'), findsOneWidget);
    expect(find.text('美甲师能力成长系统'), findsOneWidget);
  });
}
