import 'package:flutter_test/flutter_test.dart';
import 'package:package_tracker/app.dart';

void main() {
  testWidgets('App renders with navigation', (WidgetTester tester) async {
    await tester.pumpWidget(const PackageTrackerApp());

    expect(find.text('Customer'), findsWidgets);
    expect(find.text('Seller'), findsWidgets);
    expect(find.text('Delivery'), findsWidgets);
  });
}
