// lib/services/auth_service.dart
// ignore_for_file: avoid_print

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import 'user_credentials_service.dart';

class AuthService {
  static const String baseUrl = 'https://jobpulseai-ux5q.onrender.com';
  static const String _userKey = 'user_data';
  

  // ============================================================
  // REGISTER
  // ============================================================
  Future<User> register(String email, String password, String fullName) async {
    debugPrint('📤 POST $baseUrl/auth/register');

    try {
      final resp = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'full_name': fullName,
        }),
      ).timeout(const Duration(seconds: 120));

      debugPrint('📥 Status: ${resp.statusCode}');

      if (resp.statusCode == 200 || resp.statusCode == 201) {
        final user = User.fromJson(jsonDecode(resp.body));
        await _saveUser(user);

        // ✅ Sauvegarder les credentials localement
        await UserCredentialsService.saveCredentials(
          email: email,
          password: password,
          user: user,
        );
        return user;
      } else {
        String errorMsg = 'Erreur ${resp.statusCode}';
        try {
          final error = jsonDecode(resp.body);
          errorMsg = error['detail'] ?? errorMsg;
        } catch (_) {}
        throw Exception(errorMsg);
      }
    } on Exception catch (e) {
      debugPrint('❌ Register error: $e');
      rethrow;
    }
  }

  // ============================================================
  // LOGIN
  // ============================================================
  Future<User> login(String email, String password) async {
    debugPrint('🔐 Tentative de connexion pour $email');

    // =========================================================
    // 1) VÉRIFICATION LOCALE D'ABORD
    // =========================================================
    final localUser =
        await UserCredentialsService.verifyLocalLogin(email, password);
    if (localUser != null) {
      debugPrint('✅ Connexion locale réussie');
      await _saveUser(localUser);
      return localUser;
    }

    // Si des credentials locaux existent pour cet email mais mdp différent,
    // on refuse immédiatement (pas besoin d'appeler l'API).
    final savedEmail = await UserCredentialsService.getEmail();
    if (savedEmail != null &&
        savedEmail == email.toLowerCase().trim() &&
        await UserCredentialsService.hasPassword()) {
      debugPrint('❌ Mot de passe local incorrect');
      throw Exception('Email ou mot de passe incorrect');
    }

    // =========================================================
    // 2) SINON, APPEL À L'API
    // =========================================================
    debugPrint('📤 POST $baseUrl/auth/login');

    try {
      final resp = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      ).timeout(const Duration(seconds: 120));

      debugPrint('📥 Status: ${resp.statusCode}');

      if (resp.statusCode == 200) {
        final user = User.fromJson(jsonDecode(resp.body));
        await _saveUser(user);

        // ✅ Sauvegarder les credentials localement pour les prochaines fois
        await UserCredentialsService.saveCredentials(
          email: email,
          password: password,
          user: user,
        );
        return user;
      } else if (resp.statusCode == 401) {
        throw Exception('Email ou mot de passe incorrect');
      } else if (resp.statusCode == 404) {
        throw Exception('Utilisateur non trouvé. Inscrivez-vous d\'abord.');
      } else {
        String errorMsg = 'Erreur ${resp.statusCode}';
        try {
          final error = jsonDecode(resp.body);
          errorMsg = error['detail'] ?? errorMsg;
        } catch (_) {}
        throw Exception(errorMsg);
      }
    } on Exception catch (e) {
      debugPrint('❌ Login error: $e');
      rethrow;
    }
  }

  // ============================================================
  // UTILITAIRES
  // ============================================================
  Future<void> _saveUser(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user.toJson()));
  }

  Future<User?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_userKey);
    if (data == null) return null;
    return User.fromJson(jsonDecode(data));
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    // ⚠️ On garde les credentials locaux (email, mdp, user)
    // pour pouvoir se reconnecter avec le nouveau mot de passe.
  }

  /// Pour changer le mot de passe (appelé depuis le profil)
  Future<bool> changePassword(String oldPw, String newPw) async {
    return await UserCredentialsService.changePassword(oldPw, newPw);
  }

  /// Sauvegarde directe d'un utilisateur (pour la biométrie)
Future<void> saveUserDirectly(User user) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(_userKey, jsonEncode(user.toJson()));
}
}
