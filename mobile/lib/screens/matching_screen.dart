// lib/screens/matching_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../main.dart';

class MatchingScreen extends StatefulWidget {
  const MatchingScreen({super.key});

  @override
  State<MatchingScreen> createState() => _MatchingScreenState();
}

class _MatchingScreenState extends State<MatchingScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _cvController = TextEditingController();
  final TextEditingController _jobController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _apiService.dispose();
    _cvController.dispose();
    _jobController.dispose();
    super.dispose();
  }

  Future<void> _performMatch() async {
    if (_cvController.text.isEmpty || _jobController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Veuillez remplir les deux champs.')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final result = await _apiService.matchCvJob(_cvController.text, _jobController.text);
      if (!mounted) return;
      Provider.of<AppState>(context, listen: false).setMatchResult(result);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('✅ Score : ${result.score}%'), backgroundColor: Colors.green),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Erreur : $e'), backgroundColor: Colors.red),
      );
    }
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    final match = Provider.of<AppState>(context).matchResult;

    return Scaffold(
      appBar: AppBar(title: const Text('🤝 Matching'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    TextField(
                      controller: _cvController,
                      maxLines: 6,
                      decoration: const InputDecoration(
                        labelText: '📄 Texte de votre CV',
                        border: OutlineInputBorder(),
                        filled: true,
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _jobController,
                      maxLines: 6,
                      decoration: const InputDecoration(
                        labelText: '📋 Description du poste',
                        border: OutlineInputBorder(),
                        filled: true,
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _performMatch,
                        child: _isLoading
                            ? const CircularProgressIndicator(strokeWidth: 2)
                            : const Text('🔍 Analyser', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                    ),
                    const SizedBox(height: 16),
                    if (match != null) ...[
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(Icons.speed, color: Colors.purple),
                                  const SizedBox(width: 8),
                                  Text(
                                    '${match.score}%',
                                    style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.purple),
                                  ),
                                ],
                              ),
                              const Divider(),
                              _buildSkillList('✅ Compétences communes', match.commonSkills, Colors.green),
                              _buildSkillList('❌ Compétences manquantes', match.missingSkills, Colors.red),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkillList(String title, List<String> skills, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontWeight: FontWeight.bold, color: color)),
          Wrap(
            spacing: 6,
            children: skills.isEmpty
                ? [const Text('Aucune', style: TextStyle(color: Colors.grey))]
                : skills.map((s) => Chip(label: Text(s), backgroundColor: color.withValues(alpha: 0.1))).toList(),
          ),
        ],
      ),
    );
  }
}