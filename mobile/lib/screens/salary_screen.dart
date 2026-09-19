// lib/screens/salary_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../main.dart';

class SalaryScreen extends StatefulWidget {
  const SalaryScreen({super.key});

  @override
  State<SalaryScreen> createState() => _SalaryScreenState();
}

class _SalaryScreenState extends State<SalaryScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _titleController = TextEditingController(text: 'Data Scientist');
  final TextEditingController _locationController = TextEditingController(text: 'New York, NY');
  final TextEditingController _minController = TextEditingController(text: '70000');
  final TextEditingController _maxController = TextEditingController(text: '110000');
  String _experience = 'Mid-Level';
  String _workType = 'Full-time';
  int _remote = 1;
  bool _isLoading = false;

  final List<String> _experienceOptions = ['Entry-Level', 'Mid-Level', 'Senior', 'Lead'];
  final List<String> _workTypeOptions = ['Full-time', 'Part-time', 'Contract'];

  @override
  void dispose() {
    _apiService.dispose();
    _titleController.dispose();
    _locationController.dispose();
    _minController.dispose();
    _maxController.dispose();
    super.dispose();
  }

  Future<void> _predict() async {
    final features = {
      'title': _titleController.text.trim(),
      'formatted_experience_level': _experience,
      'remote_allowed': _remote,
      'work_type': _workType,
      'location': _locationController.text.trim(),
      'min_salary': double.tryParse(_minController.text.trim()) ?? 0,
      'max_salary': double.tryParse(_maxController.text.trim()) ?? 0,
    };

    setState(() => _isLoading = true);
    try {
      final result = await _apiService.predictSalary(features);
      if (!mounted) return;
      Provider.of<AppState>(context, listen: false).setSalaryPrediction(result);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('💰 Salaire estimé : \$${result.predictedSalary.toStringAsFixed(0)}'), backgroundColor: Colors.green),
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
    final pred = Provider.of<AppState>(context).salaryPrediction;

    return Scaffold(
      appBar: AppBar(title: const Text('💰 Prédiction Salaire'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: SingleChildScrollView(
          child: Column(
            children: [
              TextField(
                controller: _titleController,
                decoration: const InputDecoration(labelText: 'Intitulé du poste', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _experience,
                decoration: const InputDecoration(labelText: 'Niveau d\'expérience', border: OutlineInputBorder()),
                items: _experienceOptions.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                onChanged: (v) => setState(() => _experience = v!),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _workType,
                decoration: const InputDecoration(labelText: 'Type de contrat', border: OutlineInputBorder()),
                items: _workTypeOptions.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                onChanged: (v) => setState(() => _workType = v!),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _locationController,
                decoration: const InputDecoration(labelText: 'Localisation', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _minController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Salaire min (USD)', border: OutlineInputBorder()),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextField(
                      controller: _maxController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Salaire max (USD)', border: OutlineInputBorder()),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              SwitchListTile(
                title: const Text('Remote autorisé'),
                value: _remote == 1,
                onChanged: (v) => setState(() => _remote = v ? 1 : 0),
                secondary: Icon(_remote == 1 ? Icons.wifi : Icons.wifi_off),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _predict,
                  child: _isLoading
                      ? const CircularProgressIndicator(strokeWidth: 2)
                      : const Text('🔮 Prédire', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ),
              const SizedBox(height: 16),
              if (pred != null) ...[
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        const Text('💰 Salaire estimé', style: TextStyle(fontSize: 14, color: Colors.grey)),
                        Text('\$${pred.predictedSalary.toStringAsFixed(0)}', style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Colors.purple)),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Chip(label: Text('\$${pred.minRange.toStringAsFixed(0)}'), backgroundColor: Colors.red.shade100),
                            const SizedBox(width: 8),
                            const Icon(Icons.arrow_forward, size: 16),
                            const SizedBox(width: 8),
                            Chip(label: Text('\$${pred.maxRange.toStringAsFixed(0)}'), backgroundColor: Colors.green.shade100),
                          ],
                        ),
                        const SizedBox(height: 4),
                        const Text('Fourchette estimée (±15%)', style: TextStyle(fontSize: 12, color: Colors.grey)),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}