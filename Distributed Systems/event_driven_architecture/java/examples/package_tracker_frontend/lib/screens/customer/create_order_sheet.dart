import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../cubits/order_cubit.dart';
import '../../widgets/app_form_field.dart';
import '../../widgets/section_header.dart';
import '../../widgets/sheet_handle.dart';

class CreateOrderSheet extends StatefulWidget {
  final int userId;

  const CreateOrderSheet({super.key, required this.userId});

  @override
  State<CreateOrderSheet> createState() => _CreateOrderSheetState();
}

class _CreateOrderSheetState extends State<CreateOrderSheet> {
  final _formKey = GlobalKey<FormState>();
  final _itemCtrl = TextEditingController();
  final _amountCtrl = TextEditingController();
  final _streetCtrl = TextEditingController();
  final _cityCtrl = TextEditingController();
  final _stateCtrl = TextEditingController();
  final _zipCtrl = TextEditingController();
  final _items = <String>[];

  @override
  void dispose() {
    _itemCtrl.dispose();
    _amountCtrl.dispose();
    _streetCtrl.dispose();
    _cityCtrl.dispose();
    _stateCtrl.dispose();
    _zipCtrl.dispose();
    super.dispose();
  }

  void _addItem() {
    final text = _itemCtrl.text.trim();
    if (text.isEmpty) return;
    setState(() {
      _items.add(text);
      _itemCtrl.clear();
    });
  }

  void _removeItem(int index) {
    setState(() => _items.removeAt(index));
  }

  String _generateUUID() {
    final random = Random();
    const hex = '0123456789abcdef';
    return List.generate(36, (i) {
      if (i == 8 || i == 13 || i == 18 || i == 23) return '-';
      if (i == 14) return '4';
      return hex[random.nextInt(16)];
    }).join();
  }

  Future<void> _createOrder() async {
    if (_items.isEmpty || !_formKey.currentState!.validate()) return;

    final body = <String, dynamic>{
      'orderId': _generateUUID(),
      'user': {'id': widget.userId},
      'status': 'CREATED',

      'totalAmount': double.tryParse(_amountCtrl.text.trim()) ?? 0.0,
      'shippingAddress': {
        'street': _streetCtrl.text.trim(),
        'city': _cityCtrl.text.trim(),
        'state': _stateCtrl.text.trim(),
        'zip': _zipCtrl.text.trim(),
      },
    };
    await context.read<OrderCubit>().createOrder(body, widget.userId);
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Padding(
      padding: EdgeInsets.only(bottom: bottomInset),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SheetHandle(),
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    Text(
                      'New Order',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 20),
                    const SectionHeader(title: 'Order Items'),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _itemCtrl,
                            decoration: InputDecoration(
                              labelText: 'Add item',
                              hintText: 'e.g. Wireless Mouse',
                              prefixIcon: const Icon(
                                Icons.shopping_bag_outlined,
                              ),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              filled: true,
                              fillColor:
                                  theme.colorScheme.surfaceContainerLowest,
                            ),
                            textCapitalization: TextCapitalization.sentences,
                            onSubmitted: (_) => _addItem(),
                          ),
                        ),
                        const SizedBox(width: 8),
                        FilledButton(
                          onPressed: _addItem,
                          style: FilledButton.styleFrom(
                            minimumSize: const Size(48, 56),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: const Icon(Icons.add),
                        ),
                      ],
                    ),
                    if (_items.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerLowest,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: theme.colorScheme.outlineVariant.withValues(
                              alpha: 0.3,
                            ),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Items (${_items.length})',
                              style: theme.textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 8),
                            ...List.generate(
                              _items.length,
                              (i) => Padding(
                                padding: const EdgeInsets.only(bottom: 6),
                                child: Row(
                                  children: [
                                    Icon(
                                      Icons.check_circle,
                                      size: 18,
                                      color: theme.colorScheme.primary,
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(child: Text(_items[i])),
                                    GestureDetector(
                                      onTap: () => _removeItem(i),
                                      child: Icon(
                                        Icons.close,
                                        size: 18,
                                        color: theme.colorScheme.error,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 20),
                    const SectionHeader(title: 'Payment'),
                    const SizedBox(height: 12),
                    AppFormField(
                      controller: _amountCtrl,
                      label: 'Total Amount',
                      prefixIcon: Icons.currency_rupee,
                      prefixText: '\$ ',
                      hintText: '0.00',
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                      validator: (v) {
                        if (v == null || v.trim().isEmpty) return 'Required';
                        if (double.tryParse(v.trim()) == null) {
                          return 'Enter a valid amount';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 20),
                    const SectionHeader(title: 'Shipping Address'),
                    const SizedBox(height: 12),
                    AppFormField(
                      controller: _streetCtrl,
                      label: 'Street',
                      hintText: 'e.g. 221B Baker Street',
                      prefixIcon: Icons.home_outlined,
                      validator: (v) =>
                          v == null || v.trim().isEmpty ? 'Required' : null,
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: AppFormField(
                            controller: _cityCtrl,
                            label: 'City',
                            prefixIcon: Icons.location_city,
                            validator: (v) => v == null || v.trim().isEmpty
                                ? 'Required'
                                : null,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: AppFormField(
                            controller: _stateCtrl,
                            label: 'State',
                            validator: (v) => v == null || v.trim().isEmpty
                                ? 'Required'
                                : null,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    AppFormField(
                      controller: _zipCtrl,
                      label: 'Zip Code',
                      prefixIcon: Icons.markunread_mailbox,
                      validator: (v) =>
                          v == null || v.trim().isEmpty ? 'Required' : null,
                    ),
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: FilledButton.icon(
                        onPressed: _items.isEmpty
                            ? null
                            : () {
                                _createOrder();
                              },
                        icon: const Icon(Icons.shopping_cart_checkout),
                        label: const Text(
                          'Place Order',
                          style: TextStyle(fontSize: 16),
                        ),
                        style: FilledButton.styleFrom(
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
