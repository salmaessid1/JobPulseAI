// lib/screens/cv_screen.dart
// ignore_for_file: avoid_print

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../main.dart';

class CvScreen extends StatefulWidget {
  const CvScreen({super.key});

  @override
  State<CvScreen> createState() => _CvScreenState();
}

class _CvScreenState extends State<CvScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  File? _selectedFile;
  String? _statusMessage;

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }

  Future<void> _pickAndAnalyze() async {
    print('🟢 Bouton pressé – sélection du fichier...');

    // API 10.3.8 : utiliser FilePicker.platform.pickFiles()
    final FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );

    if (result == null || result.files.isEmpty) {
      print('⚠️ Sélection annulée par l\'utilisateur.');
      return;
    }

    final platformFile = result.files.first;

    if (platformFile.path == null) {
      setState(() {
        _statusMessage = '❌ Impossible d\'accéder au fichier (path null).';
        _isLoading = false;
      });
      return;
    }

    setState(() {
      _selectedFile = File(platformFile.path!);
      _isLoading = true;
      _statusMessage = '📤 Upload en cours...';
    });

    try {
      print('📁 Fichier sélectionné : ${_selectedFile!.path}');
      print('🌐 Envoi vers l\'API...');
      final profile = await _apiService.analyzeCv(_selectedFile!);
      print('✅ Réponse reçue, profil : ${profile.name}');
      if (!mounted) return;
      Provider.of<AppState>(context, listen: false).setProfile(profile);
      setState(() {
        _statusMessage = '✅ CV analysé avec succès ! ${profile.skills.length} compétences trouvées.';
        _isLoading = false;
      });
    } catch (e) {
      print('❌ Erreur lors de l\'analyse : $e');
      if (!mounted) return;
      setState(() {
        _statusMessage = '❌ Erreur : $e';
        _isLoading = false;
      });
    }
  }
  @override
  Widget build(BuildContext context) {
    final appState = Provider.of<AppState>(context);
    final profile = appState.profile;

    return Scaffold(
      appBar: AppBar(title: const Text('📄 Analyse CV'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (_selectedFile != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      const Icon(Icons.picture_as_pdf, color: Colors.red),
                      const SizedBox(width: 8),
                      Expanded(child: Text(_selectedFile!.path.split('/').last)),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _pickAndAnalyze,
              icon: _isLoading
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.upload_file),
              label: Text(_isLoading ? 'Analyse en cours...' : 'Choisir un PDF'),
              style: ElevatedButton.styleFrom(minimumSize: const Size.fromHeight(50)),
            ),
            const SizedBox(height: 16),
            if (_statusMessage != null)
              Card(
                color: _statusMessage!.contains('✅')
                    ? Colors.green.shade900.withValues(alpha: 0.3)
                    : Colors.red.shade900.withValues(alpha: 0.3),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(_statusMessage!, textAlign: TextAlign.center),
                ),
              ),
            if (profile != null) ...[
              const Divider(height: 32),
              const Text('📊 Profil extrait', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              ListTile(title: const Text('Nom'), subtitle: Text(profile.name)),
              ListTile(
                title: const Text('Compétences'),
                subtitle: Wrap(
                  spacing: 8,
                  children: profile.skills.map((s) => Chip(label: Text(s))).toList(),
                ),
              ),
              ListTile(
                title: const Text('Domaines'),
                subtitle: Text(profile.domains.join(', ')),
              ),
              ListTile(title: const Text('Séniorité'), subtitle: Text(profile.seniority)),
            ],
          ],
        ),
      ),
    );
  }
}