// lib/services/notification_service.dart
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppNotification {
  final String id;
  final String title;
  final String body;
  final String type; // 'job', 'analysis', 'recommendation', 'system'
  final String priority; // 'high', 'normal', 'low'
  final DateTime date;
  bool read;

  AppNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    required this.date,
    this.priority = 'normal',
    this.read = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'body': body,
        'type': type,
        'priority': priority,
        'date': date.toIso8601String(),
        'read': read,
      };

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      body: json['body'] ?? '',
      type: json['type'] ?? 'system',
      priority: json['priority'] ?? 'normal',
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
      read: json['read'] ?? false,
    );
  }
}

class NotificationService {
  static final ValueNotifier<int> unreadCount = ValueNotifier(0);
  static final List<AppNotification> _notifications = [];
  static const String _key = 'notifications';
  static const String _keyEnabled = 'notifications_enabled';

  /// État : les notifications sont-elles activées ?
  static bool _enabled = true;

  static bool get enabled => _enabled;

  static List<AppNotification> get notifications =>
      List.unmodifiable(_notifications);

  static int get unread => _notifications.where((n) => !n.read).length;

  /// Charge les notifications depuis SharedPreferences
  static Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _enabled = prefs.getBool(_keyEnabled) ?? true;
    final data = prefs.getString(_key);
    if (data != null) {
      final List<dynamic> list = jsonDecode(data);
      _notifications.clear();
      _notifications.addAll(
        list.map((e) => AppNotification.fromJson(e)),
      );
    }
    _updateUnreadCount();
  }

static Future<void> setEnabled(bool enabled) async {
  _enabled = enabled;
  final prefs = await SharedPreferences.getInstance();
  await prefs.setBool(_keyEnabled, enabled);
  debugPrint('🔔 Notifications : ${enabled ? "activées" : "désactivées"}');
}

  static Future<void> _save() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _key,
      jsonEncode(_notifications.map((n) => n.toJson()).toList()),
    );
  }

  /// Ajoute une notification (avec son et priorité)
  /// Types de notifications considérés comme importants
static const Set<String> _importantTypes = {
  'job',            // Nouvelle offre
  'recommendation', // Recommandations prêtes
  'analysis',       // CV analysé
  'alert',          // Alerte importante
};

/// Ajoute une notification (uniquement si importante)
static Future<void> add({
  required String title,
  required String body,
  String type = 'system',
  String priority = 'normal',
  bool playSound = true,
}) async {
  // ✅ PREMIÈRE VÉRIFICATION : si désactivé, on arrête
  if (!_enabled) {
    debugPrint('🔕 Notifications désactivées - ignorée : $title');
    return;
  }

  // ✅ Filtre sur les types importants
  if (!_importantTypes.contains(type)) {
    return;
  }

  if (priority == 'low') return;

  _notifications.insert(
    0,
    AppNotification(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      body: body,
      type: type,
      priority: priority,
      date: DateTime.now(),
    ),
  );

  // Sonnerie (uniquement pour les notifications de priorité haute)
  if (playSound && priority == 'high') {
    try {
      await SystemSound.play(SystemSoundType.alert);
      await HapticFeedback.heavyImpact();
    } catch (_) {}
  } else if (playSound && priority == 'normal') {
    try {
      await HapticFeedback.mediumImpact();
    } catch (_) {}
  }

  await _save();
  _updateUnreadCount();
}

  static Future<void> markAsRead(String id) async {
    final idx = _notifications.indexWhere((n) => n.id == id);
    if (idx >= 0) {
      _notifications[idx].read = true;
      await _save();
      _updateUnreadCount();
    }
  }

  static Future<void> markAllAsRead() async {
    for (final n in _notifications) {
      n.read = true;
    }
    await _save();
    _updateUnreadCount();
  }

  static Future<void> remove(String id) async {
    _notifications.removeWhere((n) => n.id == id);
    await _save();
    _updateUnreadCount();
  }

  static Future<void> clearAll() async {
    _notifications.clear();
    await _save();
    _updateUnreadCount();
  }

  static void _updateUnreadCount() {
    unreadCount.value = unread;
  }
}