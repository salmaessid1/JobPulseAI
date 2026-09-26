// lib/services/chat_storage_service.dart
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class ChatStorageService {
  static const String _key = 'conversations';

  Future<List<Conversation>> loadConversations() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_key);
    if (data == null) return [];
    final list = jsonDecode(data) as List<dynamic>;
    return list.map((e) => Conversation.fromJson(e)).toList();
  }

  Future<void> saveConversations(List<Conversation> conversations) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _key,
      jsonEncode(conversations.map((c) => c.toJson()).toList()),
    );
  }
}