// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../main.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final appState = Provider.of<AppState>(context);
    final profile = appState.profile;

    return Scaffold(
      appBar: AppBar(
        title: const Text('JobPulseAI'),
        centerTitle: true,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF7C5CFF), Color(0xFF4FD1C5)],
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Bonjour 👋',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          profile?.name ?? 'Connectez-vous avec votre CV',
                          style: const TextStyle(fontSize: 14, color: Colors.white70),
                        ),
                        const SizedBox(height: 8),
                        if (profile != null)
                          Row(
                            children: [
                              const Icon(Icons.stars, color: Colors.white, size: 16),
                              const SizedBox(width: 4),
                              Text(
                                '${profile.skills.length} compétences',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                      ],
                    ),
                  ),
                  const Icon(Icons.person_outline, color: Colors.white, size: 48),
                ],
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              '📊 En un coup d\'œil',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildStatCard('📄', 'CV', profile != null ? 'Analysé' : 'En attente', profile != null),
                const SizedBox(width: 12),
                _buildStatCard('🤝', 'Matching', profile != null ? 'Prêt' : 'Indisponible', profile != null),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildStatCard('🎯', 'Recommandations', 'Top 10', true),
                const SizedBox(width: 12),
                _buildStatCard('💰', 'Salaire', 'Estimation', true),
              ],
            ),
            const SizedBox(height: 24),
            if (profile == null)
              Card(
                color: Colors.amber.withValues(alpha: 0.1),
                child: const Padding(
                  padding: EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.amber),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text('Téléchargez votre CV dans l\'onglet "CV" pour commencer.'),
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

  Widget _buildStatCard(String icon, String label, String value, bool active) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: active ? const Color(0xFF1E1E2E) : Colors.grey.shade800.withValues(alpha: 0.3),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: active ? Colors.transparent : Colors.grey.shade600),
        ),
        child: Column(
          children: [
            Text(icon, style: const TextStyle(fontSize: 28)),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}