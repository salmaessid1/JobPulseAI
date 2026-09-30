// lib/screens/notifications_screen.dart
import 'package:flutter/material.dart';
import '../services/notification_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E2E) : Colors.white;
    final notifications = NotificationService.notifications;

    return Scaffold(
      backgroundColor:
          isDark ? const Color(0xFF0A0A15) : Colors.grey.shade100,
      appBar: AppBar(
        title: const Text('🔔 Notifications'),
        actions: [
          if (notifications.isNotEmpty)
            PopupMenuButton<String>(
              icon: const Icon(Icons.more_vert),
              onSelected: (v) async {
                if (v == 'read_all') {
                  await NotificationService.markAllAsRead();
                  setState(() {});
                } else if (v == 'clear') {
                  final confirm = await showDialog<bool>(
                    context: context,
                    builder: (_) => AlertDialog(
                      backgroundColor: cardColor,
                      title: const Text('Tout effacer ?'),
                      content: const Text(
                          'Toutes les notifications seront supprimées.'),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context, false),
                          child: const Text('Annuler'),
                        ),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red),
                          onPressed: () => Navigator.pop(context, true),
                          child: const Text('Effacer'),
                        ),
                      ],
                    ),
                  );
                  if (confirm == true) {
                    await NotificationService.clearAll();
                    setState(() {});
                  }
                }
              },
              itemBuilder: (_) => const [
                PopupMenuItem(
                  value: 'read_all',
                  child: Row(
                    children: [
                      Icon(Icons.done_all, size: 18),
                      SizedBox(width: 8),
                      Text('Tout marquer comme lu'),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: 'clear',
                  child: Row(
                    children: [
                      Icon(Icons.delete_sweep, size: 18, color: Colors.red),
                      SizedBox(width: 8),
                      Text('Tout effacer',
                          style: TextStyle(color: Colors.red)),
                    ],
                  ),
                ),
              ],
            ),
        ],
      ),
      body: notifications.isEmpty
          ? _emptyState()
          : ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: notifications.length,
              itemBuilder: (_, i) {
                final n = notifications[i];
                return _buildItem(n, cardColor, isDark);
              },
            ),
    );
  }

  Widget _emptyState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.notifications_none,
              size: 80, color: Colors.grey.shade600),
          const SizedBox(height: 16),
          const Text('Aucune notification',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(
            'Vous serez notifié des nouvelles offres,\nanalyses et recommandations.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildItem(AppNotification n, Color cardColor, bool isDark) {
    final iconData = _iconForType(n.type);
    final iconColor = _colorForType(n.type);
    final isHigh = n.priority == 'high';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: n.read ? cardColor.withValues(alpha: 0.6) : cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: n.read
              ? Colors.grey.withValues(alpha: 0.2)
              : const Color(0xFF7C5CFF).withValues(alpha: 0.5),
          width: n.read ? 1 : 1.5,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ICÔNE TYPE
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(iconData, color: iconColor, size: 22),
          ),
          const SizedBox(width: 12),

          // CONTENU
          Expanded(
            child: GestureDetector(
              onTap: () async {
                if (!n.read) {
                  await NotificationService.markAsRead(n.id);
                  if (mounted) setState(() {});
                }
                if (mounted) _showDetail(context, n);
              },
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      if (isHigh)
                        const Padding(
                          padding: EdgeInsets.only(right: 4),
                          child: Icon(Icons.priority_high,
                              size: 14, color: Colors.red),
                        ),
                      Expanded(
                        child: Text(
                          n.title,
                          style: TextStyle(
                            fontWeight:
                                n.read ? FontWeight.w500 : FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      if (!n.read)
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Color(0xFF7C5CFF),
                            shape: BoxShape.circle,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    n.body,
                    style: TextStyle(
                      fontSize: 13,
                      color: isDark
                          ? Colors.grey.shade400
                          : Colors.grey.shade700,
                      height: 1.4,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _timeAgo(n.date),
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),

          // BOUTON SUPPRESSION
          IconButton(
            icon: const Icon(Icons.delete_outline, size: 20),
            color: Colors.red,
            tooltip: 'Supprimer',
            onPressed: () async {
              await NotificationService.remove(n.id);
              if (mounted) setState(() {});
            },
          ),
        ],
      ),
    );
  }

  IconData _iconForType(String type) {
    switch (type) {
      case 'job':
        return Icons.work_outline;
      case 'analysis':
        return Icons.description_outlined;
      case 'recommendation':
        return Icons.stars_outlined;
      default:
        return Icons.info_outline;
    }
  }

  Color _colorForType(String type) {
    switch (type) {
      case 'job':
        return Colors.blue;
      case 'analysis':
        return Colors.purple;
      case 'recommendation':
        return Colors.amber;
      default:
        return Colors.green;
    }
  }

  String _timeAgo(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inSeconds < 60) return 'À l\'instant';
    if (diff.inMinutes < 60) return 'Il y a ${diff.inMinutes} min';
    if (diff.inHours < 24) return 'Il y a ${diff.inHours} h';
    if (diff.inDays < 7) return 'Il y a ${diff.inDays} j';
    return '${date.day}/${date.month}/${date.year}';
  }

  void _showDetail(BuildContext context, AppNotification n) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(n.title),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(n.body),
            const SizedBox(height: 12),
            Text(_timeAgo(n.date),
                style: const TextStyle(fontSize: 11, color: Colors.grey)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Fermer'),
          ),
        ],
      ),
    );
  }
}