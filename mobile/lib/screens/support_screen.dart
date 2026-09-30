// lib/screens/support_screen.dart
import 'package:flutter/material.dart';

class SupportScreen extends StatefulWidget {
  const SupportScreen({super.key});

  @override
  State<SupportScreen> createState() => _SupportScreenState();
}

class _SupportScreenState extends State<SupportScreen> {
  final _msgCtrl = TextEditingController();
  final _scrollCtrl = ScrollController();
  final List<_SupportMsg> _messages = [];
  bool _typing = false;

  @override
  void initState() {
    super.initState();
    _messages.add(_SupportMsg(
      role: 'agent',
      content: 'Bonjour ! 👋 Je suis Sarah, votre assistante JobPulseAI.\n\n'
          'Comment puis-je vous aider aujourd\'hui ?',
    ));
  }

  @override
  void dispose() {
    _msgCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final text = _msgCtrl.text.trim();
    if (text.isEmpty || _typing) return;

    setState(() {
      _messages.add(_SupportMsg(role: 'user', content: text));
      _typing = true;
    });
    _msgCtrl.clear();
    _scroll();

    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;

    final reply = _autoReply(text);
    setState(() {
      _messages.add(_SupportMsg(role: 'agent', content: reply));
      _typing = false;
    });
    _scroll();
  }

  String _autoReply(String msg) {
    final lower = msg.toLowerCase();

    if (lower.contains('mot de passe') || lower.contains('password')) {
      return '🔐 Pour modifier votre mot de passe :\n\n'
          '1. Allez dans Profil → Sécurité\n'
          '2. Cliquez sur "Modifier le mot de passe"\n'
          '3. Entrez votre ancien et nouveau mot de passe\n\n'
          'Si vous avez oublié votre mot de passe, contactez support@jobpulseai.com';
    }
    if (lower.contains('cv') || lower.contains('resume')) {
      return '📄 Pour analyser un CV :\n\n'
          '1. Allez dans l\'onglet CV\n'
          '2. Sélectionnez un fichier PDF\n'
          '3. Cliquez sur "Analyser le CV"\n\n'
          'L\'IA détectera automatiquement vos compétences.';
    }
    if (lower.contains('salaire') || lower.contains('salary')) {
      return '💰 Pour prédire un salaire :\n\n'
          '1. Depuis l\'accueil, cliquez sur "Prédiction Salaire"\n'
          '2. Remplissez les informations du poste\n'
          '3. Cliquez sur "Prédire"\n\n'
          'La fourchette est donnée à ±15%.';
    }
    if (lower.contains('favori') || lower.contains('favorite')) {
      return '❤️ Pour ajouter une offre aux favoris :\n\n'
          '1. Allez dans l\'onglet Recos\n'
          '2. Cliquez sur le ❤️ à côté d\'une offre\n'
          '3. Retrouvez-la dans l\'onglet Favoris (depuis l\'accueil)';
    }
    if (lower.contains('recommandation') || lower.contains('reco')) {
      return '🎯 Pour obtenir des recommandations :\n\n'
          '1. Analysez d\'abord votre CV\n'
          '2. Allez dans l\'onglet Recos\n'
          '3. Cliquez sur "Obtenir les recommandations"\n\n'
          'Le système vous proposera les 10 offres les plus pertinentes.';
    }
    if (lower.contains('bonjour') ||
        lower.contains('salut') ||
        lower.contains('hello')) {
      return 'Bonjour ! 😊 Comment puis-je vous aider ?';
    }
    if (lower.contains('merci') || lower.contains('thanks')) {
      return 'Avec plaisir ! 🙌 N\'hésitez pas si vous avez d\'autres questions.';
    }
    if (lower.contains('bug') ||
        lower.contains('erreur') ||
        lower.contains('probleme')) {
      return '🐛 Désolé pour ce désagrément.\n\n'
          'Pouvez-vous décrire le problème ?\n'
          'Vous pouvez aussi nous écrire à support@jobpulseai.com';
    }
    if (lower.contains('compte') || lower.contains('account')) {
      return '👤 Pour gérer votre compte :\n\n'
          '• Modifier vos infos : Profil → Informations personnelles\n'
          '• Changer votre mot de passe : Profil → Sécurité\n'
          '• Supprimer votre compte : Profil → bas de page';
    }
    return 'Merci pour votre message ! 🤔\n\n'
        'Je vais transmettre votre demande à notre équipe.\n'
        'En attendant, vous pouvez consulter notre FAQ ou écrire à support@jobpulseai.com';
  }

  void _scroll() {
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

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E2E) : Colors.white;

    return Scaffold(
      backgroundColor:
          isDark ? const Color(0xFF0A0A15) : Colors.grey.shade100,
      appBar: AppBar(
        title: Row(
          children: [
            Stack(
              children: [
                const CircleAvatar(
                  radius: 18,
                  backgroundColor: Color(0xFF7C5CFF),
                  child: Text('S',
                      style: TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold)),
                ),
                Positioned(
                  right: 0,
                  bottom: 0,
                  child: Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: Colors.green,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 1.5),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Support JobPulseAI',
                    style: TextStyle(
                        fontSize: 15, fontWeight: FontWeight.bold)),
                Text('En ligne',
                    style: TextStyle(fontSize: 11, color: Colors.green)),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollCtrl,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_typing ? 1 : 0),
              itemBuilder: (_, i) {
                if (i == _messages.length && _typing) {
                  return _buildTyping(isDark);
                }
                return _buildBubble(_messages[i], isDark);
              },
            ),
          ),
          SafeArea(
            top: false,
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: cardColor,
                border: Border(
                    top: BorderSide(
                        color: isDark
                            ? Colors.grey.shade800
                            : Colors.grey.shade300)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _msgCtrl,
                      decoration: InputDecoration(
                        hintText: 'Écrivez votre message...',
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
                    backgroundColor: const Color(0xFF7C5CFF),
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: _typing ? null : _send,
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

  Widget _buildBubble(_SupportMsg msg, bool isDark) {
    final isUser = msg.role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.78),
        decoration: BoxDecoration(
          color: isUser
              ? const Color(0xFF7C5CFF)
              : (isDark ? const Color(0xFF2A2A3E) : Colors.grey.shade200),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: Text(
          msg.content,
          style: TextStyle(
            color: isUser
                ? Colors.white
                : (isDark ? Colors.white : Colors.black87),
            fontSize: 14.5,
            height: 1.4,
          ),
        ),
      ),
    );
  }

  Widget _buildTyping(bool isDark) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF2A2A3E) : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 10),
            Text('Sarah est en train d\'écrire...',
                style: TextStyle(fontSize: 13)),
          ],
        ),
      ),
    );
  }
}

class _SupportMsg {
  final String role;
  final String content;
  _SupportMsg({required this.role, required this.content});
}