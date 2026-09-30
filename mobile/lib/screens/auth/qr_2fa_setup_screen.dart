// lib/screens/auth/qr_2fa_setup_screen.dart
// ignore_for_file: use_build_context_synchronously

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../services/totp_service.dart';

class Qr2faSetupScreen extends StatefulWidget {
  final String userEmail;
  const Qr2faSetupScreen({super.key, required this.userEmail});

  @override
  State<Qr2faSetupScreen> createState() => _Qr2faSetupScreenState();
}

class _Qr2faSetupScreenState extends State<Qr2faSetupScreen> {
  String _secret = '';
  String _demoCode = '';
  final _codeCtrl = TextEditingController();
  bool _verified = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _secret = TotpService.generateSecret();
    _demoCode = TotpService.generateDemoCode();
  }

  @override
  void dispose() {
    _codeCtrl.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    setState(() => _error = null);
    if (_codeCtrl.text.length != 6) {
      setState(() => _error = 'Entrez un code à 6 chiffres');
      return;
    }

    // Pour la démo : on accepte le code simulé
    if (!TotpService.verifyCode(_codeCtrl.text, _demoCode)) {
      setState(() => _error = 'Code incorrect. Réessayez.');
      return;
    }

    // Sauvegarder l'état 2FA
    // On stocke la clé secrète dans le profil (simulé)
    setState(() => _verified = true);

    if (!mounted) return;
    HapticFeedback.mediumImpact();
    await Future.delayed(const Duration(milliseconds: 500));
    if (!mounted) return;
    Navigator.pop(context, _secret);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0A0A15) : Colors.grey.shade100;
    final cardColor = isDark ? const Color(0xFF1E1E2E) : Colors.white;

    if (_verified) {
      return Scaffold(
        backgroundColor: bgColor,
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.verified_user,
                    color: Colors.green, size: 50),
              ),
              const SizedBox(height: 24),
              const Text('✅ 2FA activée !',
                  style:
                      TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text('Votre compte est maintenant protégé.',
                  style: TextStyle(color: Colors.grey.shade500)),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        title: const Text('🔐 Activer la 2FA'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // ÉTAPE 1
            _step(
              number: '1',
              title: 'Téléchargez Google Authenticator',
              subtitle:
                  'Disponible sur iOS et Android (gratuit).',
              isDone: true,
            ),

            const SizedBox(height: 16),

            // ÉTAPE 2 : QR CODE
            _step(
              number: '2',
              title: 'Scannez ce QR code',
              subtitle:
                  'Ouvrez Google Authenticator → + → Scanner un QR code.',
              isDone: false,
            ),
            const SizedBox(height: 12),

            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isDark
                      ? Colors.grey.shade800
                      : Colors.grey.shade300,
                ),
              ),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: QrImageView(
                      data: TotpService.buildOtpAuthUri(
                        secret: _secret,
                        email: widget.userEmail,
                      ),
                      version: QrVersions.auto,
                      size: 220,
                      backgroundColor: Colors.white,
                      errorStateBuilder: (ctx, err) => const Center(
                        child: Text('Erreur QR',
                            style: TextStyle(color: Colors.red)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Vous ne pouvez pas scanner ?',
                    style:
                        TextStyle(fontSize: 12, color: Colors.grey.shade500),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: isDark
                          ? const Color(0xFF252542)
                          : Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Flexible(
                          child: Text(
                            _secret,
                            style: const TextStyle(
                              fontFamily: 'monospace',
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 2,
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.copy, size: 18),
                          onPressed: () {
                            Clipboard.setData(
                                ClipboardData(text: _secret));
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('🔑 Clé copiée'),
                                duration: Duration(seconds: 1),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Saisissez cette clé manuellement dans Google Authenticator.',
                    textAlign: TextAlign.center,
                    style:
                        TextStyle(fontSize: 11, color: Colors.grey.shade500),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ÉTAPE 3 : CODE
            _step(
              number: '3',
              title: 'Entrez le code à 6 chiffres',
              subtitle:
                  'Ouvrez Google Authenticator et copiez le code affiché.',
              isDone: false,
            ),
            const SizedBox(height: 12),

            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isDark
                      ? Colors.grey.shade800
                      : Colors.grey.shade300,
                ),
              ),
              child: Column(
                children: [
                  TextField(
                    controller: _codeCtrl,
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 28,
                      letterSpacing: 12,
                      fontWeight: FontWeight.bold,
                    ),
                    decoration: const InputDecoration(
                      hintText: '000000',
                      counterText: '',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Info démo
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.amber.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                          color: Colors.amber.withValues(alpha: 0.4)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.info_outline,
                            size: 16, color: Colors.amber),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Démo : utilisez le code $_demoCode',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!,
                        style: const TextStyle(color: Colors.red)),
                  ],
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _verify,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF7C5CFF),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('✅ Vérifier et activer',
                          style: TextStyle(
                              fontSize: 15, fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _step({
    required String number,
    required String title,
    required String subtitle,
    required bool isDone,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: isDone ? Colors.green : const Color(0xFF7C5CFF),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: isDone
                ? const Icon(Icons.check, color: Colors.white, size: 18)
                : Text(
                    number,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: const TextStyle(
                      fontSize: 15, fontWeight: FontWeight.bold)),
              const SizedBox(height: 2),
              Text(subtitle,
                  style: TextStyle(
                      fontSize: 12, color: Colors.grey.shade500)),
            ],
          ),
        ),
      ],
    );
  }
}