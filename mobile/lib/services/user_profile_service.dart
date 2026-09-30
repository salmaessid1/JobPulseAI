// lib/services/user_profile_service.dart
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_profile.dart';

class UserProfileService {
  static const String _key = 'user_profile';

  static Future<UserProfileData> load() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_key);
    if (data == null) return UserProfileData();
    try {
      return UserProfileData.fromJson(jsonDecode(data));
    } catch (_) {
      return UserProfileData();
    }
  }

  static Future<void> save(UserProfileData profile) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, jsonEncode(profile.toJson()));
  }
}