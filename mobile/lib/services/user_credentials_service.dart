// lib/services/user_credentials_service.dart
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class UserCredentialsService {
  static const String _keyPassword = 'user_password_hash';
  static const String _keyEmail = 'user_email';
  static const String _keyUser = 'user_data_local';

  // ============ HASH SIMPLE (démo) ============
  static String _hash(String password) {
    int hash = 0;
    for (var i = 0; i < password.length; i++) {
      hash = ((hash << 5) - hash) + password.codeUnitAt(i);
      hash = hash & 0x7fffffff;
    }
    return hash.toString();
  }

  // ============ MOT DE PASSE ============
  static Future<void> savePassword(String password) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyPassword, _hash(password));
  }

  static Future<bool> verifyPassword(String password) async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_keyPassword);
    if (stored == null) return false;
    return stored == _hash(password);
  }

  static Future<bool> hasPassword() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey(_keyPassword);
  }

  static Future<bool> changePassword(String oldPw, String newPw) async {
    if (!await hasPassword()) {
      await savePassword(newPw);
      return true;
    }
    if (!await verifyPassword(oldPw)) return false;
    await savePassword(newPw);
    return true;
  }

  // ============ EMAIL ============
  static Future<void> saveEmail(String email) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyEmail, email.toLowerCase().trim());
  }

  static Future<String?> getEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyEmail);
  }

  // ============ USER (données complètes) ============
  static Future<void> saveUser(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyUser, jsonEncode(user.toJson()));
  }

  static Future<User?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_keyUser);
    if (data == null) return null;
    try {
      return User.fromJson(jsonDecode(data));
    } catch (_) {
      return null;
    }
  }

  // ============ SAUVEGARDER TOUT (après login/register) ============
  static Future<void> saveCredentials({
    required String email,
    required String password,
    required User user,
  }) async {
    await saveEmail(email);
    await savePassword(password);
    await saveUser(user);
  }

  // ============ VÉRIFICATION LOCALE ============
  /// Retourne l'utilisateur si email + mot de passe correspondent localement.
  /// Retourne null sinon.
  static Future<User?> verifyLocalLogin(String email, String password) async {
    final savedEmail = await getEmail();
    if (savedEmail == null) return null;
    if (savedEmail != email.toLowerCase().trim()) return null;
    final ok = await verifyPassword(password);
    if (!ok) return null;
    return await getUser();
  }

  // ============ NETTOYER ============
  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyPassword);
    await prefs.remove(_keyEmail);
    await prefs.remove(_keyUser);
  }
}