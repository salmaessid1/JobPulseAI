// lib/screens/favorites_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../main.dart';

class FavoritesScreen extends StatelessWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final favorites = Provider.of<AppState>(context).favorites;

    return Scaffold(
      appBar: AppBar(title: const Text('❤️ Favoris'), centerTitle: true),
      body: favorites.isEmpty
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.favorite_border, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('Aucun favori pour le moment.',
                      style: TextStyle(color: Colors.grey)),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(8),
              itemCount: favorites.length,
              itemBuilder: (context, index) {
                final job = favorites[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: job.score >= 70
                          ? Colors.green
                          : job.score >= 50
                              ? Colors.orange
                              : Colors.red,
                      child: Text('${job.score.round()}%',
                          style: const TextStyle(
                              color: Colors.white, fontSize: 12)),
                    ),
                    title: Text(job.title,
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('${job.company}\n${job.location}'),
                    isThreeLine: true,
                    trailing: IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      onPressed: () {
                        Provider.of<AppState>(context, listen: false)
                            .toggleFavorite(job);
                      },
                    ),
                  ),
                );
              },
            ),
    );
  }
}