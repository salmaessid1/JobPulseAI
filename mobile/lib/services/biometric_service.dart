// lib/services/biometric_service.dart
import 'package:flutter/foundation.dart';
import 'package:local_auth/local_auth.dart';

enum BiometricMethod { fingerprint, face, iris, strong, weak, none }

class BiometricService {
  static final LocalAuthentication _auth = LocalAuthentication();

  /// L'appareil supporte-t-il la biométrie ?
  static Future<bool> isAvailable() async {
    try {
      final canCheck = await _auth.canCheckBiometrics;
      final supported = await _auth.isDeviceSupported();
      return canCheck && supported;
    } catch (e) {
      debugPrint('⚠️ isAvailable error: $e');
      return false;
    }
  }

  /// Liste des biométries disponibles sur l'appareil
  static Future<List<BiometricType>> availableTypes() async {
    try {
      return await _auth.getAvailableBiometrics();
    } catch (e) {
      debugPrint('⚠️ availableTypes error: $e');
      return [];
    }
  }

  /// Le visage est-il disponible ?
  static Future<bool> isFaceAvailable() async {
    try {
      final types = await availableTypes();
      return types.contains(BiometricType.face) ||
          types.contains(BiometricType.strong);
    } catch (_) {
      return false;
    }
  }

  /// L'empreinte est-elle disponible ?
  static Future<bool> isFingerprintAvailable() async {
    try {
      final types = await availableTypes();
      return types.contains(BiometricType.fingerprint) ||
          types.contains(BiometricType.strong);
    } catch (_) {
      return false;
    }
  }

  /// Déclenche l'authentification biométrique (visage ou empreinte)
  static Future<bool> authenticate({
    String reason = 'Authentifiez-vous pour continuer',
  }) async {
    try {
      final ok = await _auth.authenticate(
        localizedReason: reason,
        options: const AuthenticationOptions(
          biometricOnly: false,
          stickyAuth: true,
          useErrorDialogs: true,
        ),
      );
      return ok;
    } catch (e) {
      debugPrint('⚠️ authenticate error: $e');
      return false;
    }
  }

  /// Force l'authentification par visage uniquement (si supporté)
  static Future<bool> authenticateWithFace({
    String reason = 'Regardez la caméra pour vous connecter',
  }) async {
    try {
      final ok = await _auth.authenticate(
        localizedReason: reason,
        options: const AuthenticationOptions(
          biometricOnly: true,
          stickyAuth: true,
          useErrorDialogs: true,
        ),
      );
      return ok;
    } catch (e) {
      debugPrint('⚠️ authenticateWithFace error: $e');
      return false;
    }
  }
}