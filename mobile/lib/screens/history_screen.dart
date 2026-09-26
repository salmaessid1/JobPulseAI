// lib/screens/history_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../main.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final history = Provider.of<AppState>(context).analysisHistory;

    return Scaffold(
      appBar: AppBar(
        title: const Text('📜 Historique'),
        centerTitle: true,
        actions: [
          if (history.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_sweep),
              tooltip: 'Effacer l\'historique',
              onPressed: () {
                Provider.of<AppState>(context, listen: false).clearHistory();
              },
            ),
        ],
      ),
      body: history.isEmpty
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.history, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('Aucune analyse enregistrée.',
                      style: TextStyle(color: Colors.grey)),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(8),
              itemCount: history.length,
              itemBuilder: (context, index) {
                final item = history[index];
                final date = DateTime.tryParse(item['date'] ?? '') ??
                    DateTime.now();
                final skills = List<String>.from(item['skills'] ?? []);
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: const CircleAvatar(
                      child: Icon(Icons.description),
                    ),
                    title: Text(item['name'] ?? 'CV sans nom',
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('${skills.length} compétences'),
                        Text(
                          '${date.day}/${date.month}/${date.year} à ${date.hour}:${date.minute.toString().padLeft(2, '0')}',
                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ],
                    ),
                    isThreeLine: true,
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (_) => AlertDialog(
                          title: Text(item['name'] ?? 'Détails'),
                          content: SingleChildScrollView(
                            child: Wrap(
                              spacing: 6,
                              children: skills
                                  .map((s) => Chip(label: Text(s)))
                                  .toList(),
                            ),
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context),
                              child: const Text('Fermer'),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                );
              },
            ),
    );
  }
}