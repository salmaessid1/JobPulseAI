// lib/services/api_service.dart
// ignore_for_file: avoid_print

import 'dart:convert';
import 'dart:io' show File;
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;
import '../models/job_models.dart';
import '../config.dart';

class ApiService {
  static String get baseUrl => Config.baseUrl;

  final http.Client _client = http.Client();

  // ==================== CV ANALYSIS ====================
  Future<Profile> analyzeCv(File file) async {
    print('📤 Upload du fichier : ${file.path}');
    final uri = Uri.parse('$baseUrl/cv/upload');
    print('🌐 URL : $uri');
    var request = http.MultipartRequest('POST', uri);
    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        file.path,
        filename: path.basename(file.path),
      ),
    );
    final response = await request.send().timeout(const Duration(seconds: 60));
    final responseBody = await response.stream.bytesToString();
    print('📄 Réponse brute : $responseBody');
    print('📨 Status code : ${response.statusCode}');

    if (response.statusCode == 200) {
      final json = jsonDecode(responseBody);
      return Profile.fromJson(json['profile']);
    } else {
      throw Exception(
        'Erreur lors de l\'analyse du CV: ${response.statusCode}\nRéponse : $responseBody',
      );
    }
  }

  // ==================== MATCHING ====================
  Future<MatchResult> matchCvJob(String cvText, String jobText) async {
    final uri = Uri.parse('$baseUrl/matching/');
    final payload = jsonEncode({'cv_text': cvText, 'job_text': jobText});
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: payload,
    );
    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return MatchResult.fromJson(json);
    } else {
      throw Exception('Erreur lors du matching: ${response.statusCode}');
    }
  }

  // ==================== RECOMMENDATIONS ====================
  Future<List<JobRecommendation>> getRecommendations(Profile profile) async {
    final uri = Uri.parse('$baseUrl/recommendations/');
    final payload = jsonEncode({'profile': profile.toJson(), 'top_n': 10});
    print('📤 POST $uri');
    print('📤 Payload: $payload');

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: payload,
    );

    print('📨 Status: ${response.statusCode}');
    print('📄 Body: ${response.body}');

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => JobRecommendation.fromJson(e)).toList();
    } else {
      throw Exception(
        'Erreur ${response.statusCode}: ${response.body}',
      );
    }
  }

  // ==================== SKILL GAP ====================
  Future<Map<String, dynamic>> getSkillGap(
    Profile profile,
    String jobText,
  ) async {
    final uri = Uri.parse('$baseUrl/skill-gap/');
    final payload = jsonEncode({
      'profile': profile.toJson(),
      'job_text': jobText,
    });
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: payload,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur lors du skill gap: ${response.statusCode}');
    }
  }

  // ==================== SALARY PREDICTION ====================
  Future<SalaryPrediction> predictSalary(Map<String, dynamic> features) async {
    final uri = Uri.parse('$baseUrl/salary/predict');
    final payload = jsonEncode(features);
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: payload,
    );
    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return SalaryPrediction.fromJson(json);
    } else {
      throw Exception('Erreur lors de la prédiction: ${response.statusCode}');
    }
  }

  void dispose() {
    _client.close();
  }
}

// Extension pour sérialiser Profile
extension ProfileJson on Profile {
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'skills': skills,
      'domains': domains,
      'seniority': seniority,
      'categorized_skills': categorizedSkills,
    };
  }
}