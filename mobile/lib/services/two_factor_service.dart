// lib/services/two_factor_service.dart
import 'dart:math';

class TwoFactorService {
  /// Génère un code à 6 chiffres
  static String generateCode() {
    final rand = Random();
    return List.generate(6, (_) => rand.nextInt(10)).join();
  }

  /// Simule l'envoi du code (dans un vrai projet, ce serait un appel API)
  static Future<bool> sendCode(String email) async {
    await Future.delayed(const Duration(seconds: 1));
    return true;
  }

  /// Vérifie que le code saisi correspond
  static bool verifyCode(String input, String expected) {
    return input.trim() == expected.trim();
  }
}