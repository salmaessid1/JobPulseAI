// ignore_for_file: avoid_print

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class AuthService {
  // ⚠️ URL Render (production)
  static const String baseUrl = 'https://jobpulseai-ux5q.onrender.com';
  static const String _userKey = 'user_data';

  Future<User> register(String email, String password, String fullName) async {
    print('📤 POST $baseUrl/auth/register');
    print('📤 Body: email=$email, fullName=$fullName');

    try {
      final resp = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'full_name': fullName,
        }),
      ).timeout(const Duration(seconds: 60));

      print('📥 Status: ${resp.statusCode}');
      print('📥 Body: ${resp.body}');

      if (resp.statusCode == 200) {
        final user = User.fromJson(jsonDecode(resp.body));
        await _saveUser(user);
        return user;
      } else {
        String errorMsg = 'Erreur ${resp.statusCode}';
        try {
          final error = jsonDecode(resp.body);
          errorMsg = error['detail'] ?? errorMsg;
        } catch (_) {}
        throw Exception(errorMsg);
      }
    } catch (e) {
      print('❌ Register error: $e');
      rethrow;
    }
  }

  Future<User> login(String email, String password) async {
    print('📤 POST $baseUrl/auth/login');

    try {
      final resp = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      ).timeout(const Duration(seconds: 60));

      print('📥 Status: ${resp.statusCode}');
      print('📥 Body: ${resp.body}');

      if (resp.statusCode == 200) {
        final user = User.fromJson(jsonDecode(resp.body));
        await _saveUser(user);
        return user;
      } else {
        throw Exception('Email ou mot de passe incorrect');
      }
    } catch (e) {
      print('❌ Login error: $e');
      rethrow;
    }
  }

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
  }
}