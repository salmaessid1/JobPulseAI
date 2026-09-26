class User {
  final int userId;
  final String email;
  final String fullName;
  final String token;

  User({
    required this.userId,
    required this.email,
    required this.fullName,
    required this.token,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['user_id'] ?? 0,
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      token: json['token'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'email': email,
    'full_name': fullName,
    'token': token,
  };
}

class ChatMessage {
  final String role;
  final String content;
  final DateTime timestamp;

  ChatMessage({
    required this.role,
    required this.content,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() => {
    'role': role,
    'content': content,
    'timestamp': timestamp.toIso8601String(),
  };

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      role: json['role'] ?? 'user',
      content: json['content'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}
// lib/models/user_model.dart (AJOUTER cette classe à la fin du fichier existant)
class Conversation {
  final String id;
  String title;
  List<ChatMessage> messages;
  bool pinned;
  DateTime updatedAt;

  Conversation({
    required this.id,
    required this.title,
    required this.messages,
    this.pinned = false,
    DateTime? updatedAt,
  }) : updatedAt = updatedAt ?? DateTime.now();

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'messages': messages.map((m) => m.toJson()).toList(),
    'pinned': pinned,
    'updated_at': updatedAt.toIso8601String(),
  };

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] ?? '',
      title: json['title'] ?? 'Nouvelle conversation',
      messages: (json['messages'] as List<dynamic>? ?? [])
          .map((e) => ChatMessage.fromJson(e))
          .toList(),
      pinned: json['pinned'] ?? false,
      updatedAt: DateTime.tryParse(json['updated_at'] ?? '') ?? DateTime.now(),
    );
  }
}