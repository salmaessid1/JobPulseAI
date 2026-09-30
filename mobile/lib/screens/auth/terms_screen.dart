// lib/screens/auth/terms_screen.dart
import 'package:flutter/material.dart';

class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Conditions d\'utilisation')),
      body: const SingleChildScrollView(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Conditions d\'utilisation',
                style:
                    TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            SizedBox(height: 20),
            Text('1. ACCEPTATION\n'
                'En utilisant JobPulseAI, vous acceptez les présentes conditions.\n'),
            Text('2. COMPTE UTILISATEUR\n'
                'Vous êtes responsable de la confidentialité de vos identifiants.\n'),
            Text('3. DONNÉES PERSONNELLES\n'
                'Vos données sont stockées localement et utilisées pour améliorer votre expérience.\n'),
            Text('4. CONTENU\n'
                'Les analyses sont indicatives et ne remplacent pas un conseil professionnel.\n'),
            Text('5. RESPONSABILITÉ\n'
                'JobPulseAI ne peut être tenu responsable des décisions prises sur base des analyses.\n'),
            Text('6. MODIFICATIONS\n'
                'Ces conditions peuvent être modifiées à tout moment.\n'),
            SizedBox(height: 30),
            Text('© 2026 JobPulseAI',
                style: TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}