// lib/screens/recommendations_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/notification_service.dart';
import '../main.dart';
import '../models/job_models.dart';

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
        const SnackBar(
            content:
                Text('Veuillez d\'abord analyser votre CV dans l\'onglet "CV".')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final recs = await _apiService.getRecommendations(profile);
      if (!mounted) return;
      Provider.of<AppState>(context, listen: false).setRecommendations(recs);

      // ✅ Notification automatique
      await NotificationService.add(
        title: '🎯 ${recs.length} recommandations',
        body: 'De nouvelles offres correspondent à votre profil.',
        type: 'recommendation',
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Erreur : $e'), backgroundColor: Colors.red),
      );
    }
    if (mounted) setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    final appState = Provider.of<AppState>(context);
    final recs = appState.recommendations;

    return Scaffold(
      appBar: AppBar(
        title: const Text('🎯 Recommandations'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.favorite),
            tooltip: 'Voir mes favoris',
            onPressed: () => Navigator.pushNamed(context, '/favorites'),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _fetchRecommendations,
                icon: _isLoading
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.refresh),
                label: Text(
                  _isLoading
                      ? 'Chargement...'
                      : '🔄 Obtenir les recommandations',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: recs == null
                  ? const Center(
                      child: Text(
                        'Cliquez sur le bouton pour charger les recommandations.',
                        textAlign: TextAlign.center,
                      ),
                    )
                  : ListView.builder(
                      itemCount: recs.length,
                      itemBuilder: (context, index) {
                        final r = recs[index];
                        final isFav = appState.isFavorite(r.jobId);
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: r.score >= 70
                                  ? Colors.green
                                  : r.score >= 50
                                      ? Colors.orange
                                      : Colors.red,
                              child: Text(
                                '${r.score.round()}%',
                                style: const TextStyle(
                                    color: Colors.white, fontSize: 12),
                              ),
                            ),
                            title: Text(
                              r.title,
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold),
                            ),
                            subtitle: Text('${r.company}\n${r.location}'),
                            isThreeLine: true,
                            trailing: IconButton(
                              icon: Icon(
                                isFav
                                    ? Icons.favorite
                                    : Icons.favorite_border,
                                color: isFav ? Colors.red : null,
                              ),
                              tooltip: isFav
                                  ? 'Retirer des favoris'
                                  : 'Ajouter aux favoris',
                              onPressed: () async {
                                appState.toggleFavorite(r);
                                if (!isFav) {
                                  // ✅ Notification ajout favori
                                  await NotificationService.add(
                                    title: '❤️ Offre ajoutée aux favoris',
                                    body: '${r.title} chez ${r.company}.',
                                    type: 'job',
                                  );
                                }
                                if (!context.mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    duration: const Duration(seconds: 1),
                                    content: Text(
                                      isFav
                                          ? '💔 Retiré des favoris'
                                          : '❤️ Ajouté aux favoris',
                                    ),
                                  ),
                                );
                              },
                            ),
                            onTap: () => _showDetails(context, r, appState),
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

  void _showDetails(
      BuildContext context, JobRecommendation rec, AppState appState) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        expand: false,
        builder: (context, scrollController) {
          final isFav = appState.isFavorite(rec.jobId);
          return Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        rec.title,
                        style: const TextStyle(
                            fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        isFav ? Icons.favorite : Icons.favorite_border,
                        color: isFav ? Colors.red : null,
                      ),
                      onPressed: () {
                        appState.toggleFavorite(rec);
                        Navigator.pop(context);
                      },
                    ),
                  ],
                ),
                Text(rec.company, style: const TextStyle(color: Colors.grey)),
                const SizedBox(height: 8),
                Text('📍 ${rec.location}'),
                const SizedBox(height: 12),
                Text(
                  'Score: ${rec.score}%',
                  style: const TextStyle(
                      fontWeight: FontWeight.bold, color: Colors.purple),
                ),
                const SizedBox(height: 16),
                const Text('✅ Compétences communes',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: rec.commonSkills
                      .map((s) => Chip(
                            label: Text(s),
                            backgroundColor:
                                Colors.green.withValues(alpha: 0.2),
                          ))
                      .toList(),
                ),
                const SizedBox(height: 12),
                const Text('❌ Compétences manquantes',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: rec.missingSkills
                      .map((s) => Chip(
                            label: Text(s),
                            backgroundColor:
                                Colors.red.withValues(alpha: 0.2),
                          ))
                      .toList(),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}