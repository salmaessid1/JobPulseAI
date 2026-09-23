import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';

class ChatService {
  static const String baseUrl = 'https://jobpulseai-ux5q.onrender.com';

  Future<String> sendMessage(String question, {List<ChatMessage>? history}) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/chatbot/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'question': question,
        'profile': null,
        'history': history?.map((m) => m.toJson()).toList() ?? [],
      }),
    ).timeout(const Duration(seconds: 60));

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      return data['response'] ?? 'Erreur';
    } else {
      throw Exception('Erreur du chatbot');
    }
  }
}