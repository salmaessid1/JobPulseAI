// lib/services/totp_service.dart
import 'dart:math';

class TotpService {
  /// Génère une clé secrète (format Google Authenticator)
  /// Exemple : "JBSWY3DPEHPK3PXP"
  static String generateSecret({int length = 16}) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'; // Base32
    final rand = Random.secure();
    return List.generate(length, (_) => chars[rand.nextInt(chars.length)])
        .join();
  }

  /// Construit l'URI otpauth:// à encoder dans le QR code
  static String buildOtpAuthUri({
    required String secret,
    required String email,
    String issuer = 'JobPulseAI',
  }) {
    final encodedIssuer = Uri.encodeComponent(issuer);
    final encodedEmail = Uri.encodeComponent(email);
    return 'otpauth://totp/$encodedIssuer:$encodedEmail'
        '?secret=$secret&issuer=$encodedIssuer&algorithm=SHA1'
        '&digits=6&period=30';
  }

  /// Simule la vérification d'un code 6 chiffres (démo)
  /// Dans un vrai projet, on utilise la librairie `otp`.
  static bool verifyCode(String input, String expectedCode) {
    return input.trim() == expectedCode.trim();
  }

  /// Génère un code à 6 chiffres (pour la démo)
  static String generateDemoCode() {
    final rand = Random();
    return List.generate(6, (_) => rand.nextInt(10)).join();
  }
}