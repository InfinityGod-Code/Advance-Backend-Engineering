import 'package:flutter/material.dart';
import '../../models/user.dart';
import '../../data/mock_data.dart';
import 'widgets/user_card.dart';
import 'create_user_sheet.dart';
import 'user_orders_screen.dart';

class CustomerScreen extends StatelessWidget {
  const CustomerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: MockDataStore(),
      builder: (context, _) {
        final store = MockDataStore();
        return _CustomerBody(store: store);
      },
    );
  }
}

class _CustomerBody extends StatefulWidget {
  final MockDataStore store;

  const _CustomerBody({required this.store});

  @override
  State<_CustomerBody> createState() => _CustomerBodyState();
}

class _CustomerBodyState extends State<_CustomerBody> {
  final _searchCtrl = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  List<User> get _filteredUsers {
    final users = widget.store.users;
    if (_searchQuery.isEmpty) return users;
    final q = _searchQuery.toLowerCase();
    return users
        .where(
          (u) =>
              u.name.toLowerCase().contains(q) ||
              u.email.toLowerCase().contains(q),
        )
        .toList();
  }

  void _openCreateUser() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => const CreateUserSheet(),
    );
  }

  void _openUserOrders(User user) {
    Navigator.of(
      context,
    ).push(MaterialPageRoute(builder: (_) => UserOrdersScreen(user: user)));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final users = _filteredUsers;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 160,
            pinned: true,
            stretch: true,
            backgroundColor: Colors.transparent,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      const Color(0xFF2D1B64),
                      const Color(0xFF1C3879),
                      theme.colorScheme.primary.withValues(alpha: 0.8),
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 50, 24, 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.people_alt_outlined,
                              color: Colors.white,
                              size: 28,
                            ),
                            const SizedBox(width: 10),
                            Text(
                              'Customers',
                              style: theme.textTheme.headlineSmall?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const Spacer(),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 12,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                '${widget.store.users.length} total',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w500,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: TextField(
                controller: _searchCtrl,
                onChanged: (v) => setState(() => _searchQuery = v),
                decoration: InputDecoration(
                  hintText: 'Search customers...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchCtrl.clear();
                            setState(() => _searchQuery = '');
                          },
                        )
                      : null,
                  filled: true,
                  fillColor: theme.colorScheme.surfaceContainerHighest
                      .withValues(alpha: 0.5),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                ),
              ),
            ),
          ),
          if (users.isEmpty)
            SliverFillRemaining(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.people_outline,
                      size: 64,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _searchQuery.isNotEmpty
                          ? 'No customers match "$_searchQuery"'
                          : 'No customers yet',
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    if (_searchQuery.isEmpty) ...[
                      const SizedBox(height: 8),
                      FilledButton.tonalIcon(
                        onPressed: _openCreateUser,
                        icon: const Icon(Icons.person_add),
                        label: const Text('Add your first customer'),
                      ),
                    ],
                  ],
                ),
              ),
            )
          else
            SliverList(
              delegate: SliverChildBuilderDelegate((context, index) {
                final user = users[index];
                return UserCard(user: user, onTap: () => _openUserOrders(user));
              }, childCount: users.length),
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openCreateUser,
        icon: const Icon(Icons.person_add),
        label: const Text('Add'),
      ),
    );
  }
}
