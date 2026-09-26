// lib/screens/cv_screen.dart
// ignore_for_file: avoid_print

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../models/job_models.dart';   // ← AJOUT de l'import
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
  bool _success = false;

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );
    if (result == null || result.files.isEmpty) return;
    final platformFile = result.files.first;
    if (platformFile.path == null) return;

    setState(() {
      _selectedFile = File(platformFile.path!);
      _statusMessage = null;
    });
  }

  Future<void> _analyze() async {
    if (_selectedFile == null) {
      setState(() {
        _statusMessage = '⚠️ Veuillez d\'abord sélectionner un fichier PDF.';
        _success = false;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _statusMessage = '📤 Upload en cours...';
      _success = false;
    });

    try {
      final profile = await _apiService.analyzeCv(_selectedFile!);
      if (!mounted) return;
      Provider.of<AppState>(context, listen: false).setProfile(profile);
      Provider.of<AppState>(context, listen: false).addAnalysisToHistory(profile);
      setState(() {
        _statusMessage =
        '✅ CV analysé ! ${profile.skills.length} compétences trouvées.';
        _success = true;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _statusMessage = '❌ Erreur : $e';
        _success = false;
        _isLoading = false;
      });
    }
  }

  void _reset() {
    setState(() {
      _selectedFile = null;
      _statusMessage = null;
      _success = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final appState = Provider.of<AppState>(context);
    final profile = appState.profile;

    return Scaffold(
      appBar: AppBar(
        title: const Text('📄 Analyse CV'),
        centerTitle: true,
        actions: [
          if (_selectedFile != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Réinitialiser',
              onPressed: _reset,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildUploadCard(),
            const SizedBox(height: 16),
            SizedBox(
              height: 52,
              child: ElevatedButton.icon(
                onPressed: (_isLoading || _selectedFile == null) ? null : _analyze,
                icon: _isLoading
                    ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
                    : const Icon(Icons.auto_awesome),
                label: Text(
                  _isLoading ? 'Analyse en cours...' : 'Analyser le CV',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF7C5CFF),
                  foregroundColor: Colors.white,
                ),
              ),
            ),
            if (_statusMessage != null) ...[
              const SizedBox(height: 16),
              Card(
                color: _success
                    ? Colors.green.shade900.withValues(alpha: 0.3)
                    : Colors.red.shade900.withValues(alpha: 0.3),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Icon(
                        _success ? Icons.check_circle : Icons.error,
                        color: _success ? Colors.green : Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(_statusMessage!)),
                    ],
                  ),
                ),
              ),
            ],
            if (profile != null) ...[
              const SizedBox(height: 24),
              _buildProfileCard(profile),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildUploadCard() {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: _isLoading ? null : _pickFile,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              Icon(
                _selectedFile == null
                    ? Icons.cloud_upload_outlined
                    : Icons.picture_as_pdf,
                size: 64,
                color: _selectedFile == null ? Colors.purple : Colors.red,
              ),
              const SizedBox(height: 12),
              Text(
                _selectedFile == null
                    ? 'Appuyez pour choisir un PDF'
                    : _selectedFile!.path.split(Platform.pathSeparator).last,
                style: const TextStyle(
                    fontSize: 15, fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                _selectedFile == null
                    ? 'Formats acceptés : PDF'
                    : 'Fichier prêt à être analysé',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ⚠️ ICI : le paramètre est maintenant typé Profile, plus dynamic
  Widget _buildProfileCard(Profile profile) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.badge, color: Colors.purple),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    profile.name,
                    style: const TextStyle(
                        fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            _buildInfoRow(Icons.work_outline, 'Séniorité', profile.seniority),
            const SizedBox(height: 12),
            _buildInfoRow(
              Icons.category_outlined,
              'Domaines',
              profile.domains.isEmpty
                  ? 'Non identifiés'
                  : profile.domains.join(', '),
            ),
            const SizedBox(height: 16),
            const Text(
              '💡 Compétences détectées',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
            const SizedBox(height: 8),
            if (profile.skills.isEmpty)
              const Text('Aucune compétence détectée.',
                  style: TextStyle(color: Colors.grey))
            else
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: profile.skills
                    .map((s) => Chip(
                  label: Text(s),
                  backgroundColor:
                  Colors.purple.withValues(alpha: 0.2),
                ))
                    .toList(),
              ),
            if (profile.categorizedSkills.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                '📂 Par catégorie',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 8),
              ...profile.categorizedSkills.entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '• ${entry.key}',
                        style: const TextStyle(
                            fontWeight: FontWeight.w600, fontSize: 13),
                      ),
                      const SizedBox(height: 4),
                      Wrap(
                        spacing: 4,
                        runSpacing: 4,
                        children: entry.value
                            .map((s) => Chip(
                          label: Text(s,
                              style: const TextStyle(fontSize: 12)),
                          materialTapTargetSize:
                          MaterialTapTargetSize.shrinkWrap,
                          visualDensity: VisualDensity.compact,
                        ))
                            .toList(),
                      ),
                    ],
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Colors.grey),
        const SizedBox(width: 8),
        Text('$label : ',
            style: const TextStyle(fontWeight: FontWeight.w600)),
        Expanded(
          child: Text(value, style: const TextStyle(color: Colors.grey)),
        ),
      ],
    );
  }
}