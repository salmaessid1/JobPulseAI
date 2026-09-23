import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class AuthService {
  static const String baseUrl = 'https://jobpulseai-ux5q.onrender.com';
  static const String _userKey = 'user_data';

  Future<User> register(String email, String password, String fullName) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': fullName,
      }),
    ).timeout(const Duration(seconds: 30));

    if (resp.statusCode == 200) {
      final user = User.fromJson(jsonDecode(resp.body));
      await _saveUser(user);
      return user;
    } else {
      final error = jsonDecode(resp.body);
      throw Exception(error['detail'] ?? 'Erreur d\'inscription');
    }
  }

  Future<User> login(String email, String password) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    ).timeout(const Duration(seconds: 30));

    if (resp.statusCode == 200) {
      final user = User.fromJson(jsonDecode(resp.body));
      await _saveUser(user);
      return user;
    } else {
      throw Exception('Email ou mot de passe incorrect');
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