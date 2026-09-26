// lib/screens/chat_screen.dart
import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/chat_service.dart';
import '../services/chat_storage_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _msgCtrl = TextEditingController();
  final _chatService = ChatService();
  final _storage = ChatStorageService();
  final _scrollCtrl = ScrollController();

  List<Conversation> _conversations = [];
  Conversation? _current;
  bool _isSending = false;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadConversations();
  }

  @override
  void dispose() {
    _msgCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadConversations() async {
    final list = await _storage.loadConversations();
    if (!mounted) return;
    setState(() {
      _conversations = list;
      if (list.isNotEmpty) {
        _current = list.first;
      } else {
        _newConversation();
      }
      _isLoading = false;
    });
  }

  void _newConversation() {
    final conv = Conversation(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: 'Nouvelle conversation',
      messages: [],
    );
    setState(() {
      _conversations.insert(0, conv);
      _current = conv;
    });
    _save();
  }

  Future<void> _save() async {
    await _storage.saveConversations(_conversations);
  }

  void _openConversation(Conversation conv) {
    setState(() => _current = conv);
    Navigator.pop(context);
    _scrollToBottom();
  }

  void _deleteConversation(Conversation conv) {
    setState(() {
      _conversations.removeWhere((c) => c.id == conv.id);
      if (_current?.id == conv.id) {
        _current = _conversations.isNotEmpty ? _conversations.first : null;
        if (_current == null) _newConversation();
      }
    });
    _save();
  }

  void _togglePin(Conversation conv) {
    setState(() {
      conv.pinned = !conv.pinned;
      _conversations.sort((a, b) {
        if (a.pinned && !b.pinned) return -1;
        if (!a.pinned && b.pinned) return 1;
        return b.updatedAt.compareTo(a.updatedAt);
      });
    });
    _save();
  }

  Future<void> _send() async {
    final text = _msgCtrl.text.trim();
    if (text.isEmpty || _isSending || _current == null) return;

    setState(() {
      _current!.messages.add(ChatMessage(role: 'user', content: text));
      _isSending = true;
      if (_current!.title == 'Nouvelle conversation') {
        _current!.title =
            text.length > 30 ? '${text.substring(0, 30)}...' : text;
      }
      _current!.updatedAt = DateTime.now();
    });
    _msgCtrl.clear();
    _scrollToBottom();

    try {
      final response = await _chatService.sendMessage(
        text,
        history: _current!.messages,
      );
      if (!mounted) return;
      setState(() {
        _current!.messages
            .add(ChatMessage(role: 'assistant', content: response));
        _current!.updatedAt = DateTime.now();
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _current!.messages.add(ChatMessage(
            role: 'assistant', content: '⚠️ Erreur : $e'));
      });
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
        _save();
        _scrollToBottom();
      }
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 200), () {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _openDrawer() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E1E2E),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.6,
          minChildSize: 0.3,
          maxChildSize: 0.9,
          builder: (_, scrollCtrl) {
            return Column(
              children: [
                const SizedBox(height: 8),
                Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      const Text('Conversations',
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold)),
                      const Spacer(),
                      TextButton.icon(
                        onPressed: () {
                          Navigator.pop(ctx);
                          _newConversation();
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('Nouvelle'),
                      ),
                    ],
                  ),
                ),
                const Divider(),
                Expanded(
                  child: _conversations.isEmpty
                      ? const Center(child: Text('Aucune conversation'))
                      : ListView.builder(
                          controller: scrollCtrl,
                          itemCount: _conversations.length,
                          itemBuilder: (_, i) {
                            final conv = _conversations[i];
                            final isActive = conv.id == _current?.id;
                            return ListTile(
                              selected: isActive,
                              leading: Icon(
                                conv.pinned
                                    ? Icons.push_pin
                                    : Icons.chat_bubble_outline,
                                color:
                                    conv.pinned ? Colors.amber : Colors.grey,
                              ),
                              title: Text(
                                conv.title,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              subtitle: Text(
                                '${conv.messages.length} messages',
                                style: const TextStyle(fontSize: 12),
                              ),
                              trailing: PopupMenuButton<String>(
                                icon: const Icon(Icons.more_vert),
                                onSelected: (v) {
                                  if (v == 'pin') _togglePin(conv);
                                  if (v == 'delete') {
                                    _deleteConversation(conv);
                                    Navigator.pop(ctx);
                                  }
                                },
                                itemBuilder: (_) => [
                                  PopupMenuItem(
                                    value: 'pin',
                                    child: Row(
                                      children: [
                                        Icon(
                                          conv.pinned
                                              ? Icons.push_pin_outlined
                                              : Icons.push_pin,
                                          size: 18,
                                        ),
                                        const SizedBox(width: 8),
                                        Text(conv.pinned
                                            ? 'Désépingler'
                                            : 'Épingler'),
                                      ],
                                    ),
                                  ),
                                  const PopupMenuItem(
                                    value: 'delete',
                                    child: Row(
                                      children: [
                                        Icon(Icons.delete,
                                            size: 18, color: Colors.red),
                                        SizedBox(width: 8),
                                        Text('Supprimer',
                                            style:
                                                TextStyle(color: Colors.red)),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              onTap: () => _openConversation(conv),
                            );
                          },
                        ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final messages = _current?.messages ?? [];

    return Scaffold(
      appBar: AppBar(
        title: Text(
          _current?.title ?? 'Assistant IA',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_comment_outlined),
            tooltip: 'Nouvelle conversation',
            onPressed: _newConversation,
          ),
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'Historique',
            onPressed: _openDrawer,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: messages.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.smart_toy, size: 80, color: Colors.purple),
                        SizedBox(height: 16),
                        Text('Bonjour ! 👋',
                            style: TextStyle(
                                fontSize: 24, fontWeight: FontWeight.bold)),
                        SizedBox(height: 8),
                        Text('Posez-moi une question sur les métiers,',
                            style: TextStyle(color: Colors.grey)),
                        Text('compétences, salaires, CV, entretiens...',
                            style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  )
                : ListView.builder(
                    controller: _scrollCtrl,
                    padding: const EdgeInsets.all(12),
                    itemCount: messages.length,
                    itemBuilder: (_, i) => _buildBubble(messages[i]),
                  ),
          ),
          if (_isSending)
            const Padding(
              padding: EdgeInsets.all(8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2)),
                  SizedBox(width: 12),
                  Text('L\'IA réfléchit...'),
                ],
              ),
            ),
          SafeArea(
            top: false,
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                border: Border(top: BorderSide(color: Colors.grey.shade800)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _msgCtrl,
                      decoration: InputDecoration(
                        hintText: 'Posez votre question...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                      ),
                      onSubmitted: (_) => _send(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    radius: 24,
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: _isSending ? null : _send,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBubble(ChatMessage msg) {
    final isUser = msg.role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.78),
        decoration: BoxDecoration(
          color: isUser ? const Color(0xFF7C5CFF) : Colors.grey.shade800,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: Text(
          msg.content,
          style: const TextStyle(color: Colors.white, fontSize: 15),
        ),
      ),
    );
  }
}