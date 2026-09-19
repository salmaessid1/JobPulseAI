// lib/screens/recommendations_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../main.dart';
import '../models/job_models.dart';   // <-- AJOUTE CETTE LIGNE

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = false;

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }

  Future<void> _fetchRecommendations() async {
    final profile = Provider.of<AppState>(context, listen: false).profile;
    if (profile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Veuillez d\'abord analyser votre CV dans l\'onglet "CV".')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final recs = await _apiService.getRecommendations(profile);
      if (!mounted) return;
      Provider.of<AppState>(context, listen: false).setRecommendations(recs);
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
    final recs = Provider.of<AppState>(context).recommendations;

    return Scaffold(
      appBar: AppBar(title: const Text('🎯 Recommandations'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _fetchRecommendations,
                child: _isLoading
                    ? const CircularProgressIndicator(strokeWidth: 2)
                    : const Text('🔄 Obtenir les recommandations', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: recs == null
                  ? const Center(child: Text('Cliquez sur le bouton pour charger les recommandations.'))
                  : ListView.builder(
                      itemCount: recs.length,
                      itemBuilder: (context, index) {
                        final r = recs[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: r.score >= 70 ? Colors.green : r.score >= 50 ? Colors.orange : Colors.red,
                              child: Text('${r.score.round()}%', style: const TextStyle(color: Colors.white, fontSize: 12)),
                            ),
                            title: Text(r.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text('${r.company}\n${r.location}'),
                            isThreeLine: true,
                            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                            onTap: () {
                              _showDetails(context, r);
                            },
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  void _showDetails(BuildContext context, JobRecommendation rec) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        expand: false,
        builder: (context, scrollController) {
          return Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(rec.title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                Text(rec.company, style: const TextStyle(color: Colors.grey)),
                const SizedBox(height: 8),
                Text('📍 ${rec.location}'),
                const SizedBox(height: 12),
                Text('Score: ${rec.score}%', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.purple)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: rec.commonSkills.map((s) => Chip(label: Text(s), backgroundColor: Colors.green.withValues(alpha: 0.2))).toList(),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: rec.missingSkills.map((s) => Chip(label: Text(s), backgroundColor: Colors.red.withValues(alpha: 0.2))).toList(),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}