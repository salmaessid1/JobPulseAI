// lib/main.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'screens/home_screen.dart';
import 'screens/cv_screen.dart';
import 'screens/matching_screen.dart';
import 'screens/recommendations_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/auth/login_screen.dart';

import 'services/auth_service.dart';
import 'models/job_models.dart';
import 'models/user_model.dart';

// ============================================================
// POINT D'ENTRÉE
// ============================================================
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => AppState(),
      child: const JobPulseApp(),
    ),
  );
}

// ============================================================
// APPLICATION PRINCIPALE
// ============================================================
class JobPulseApp extends StatelessWidget {
  const JobPulseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JobPulseAI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF7C5CFF),
          secondary: Color(0xFF4FD1C5),
        ),
        fontFamily: 'Inter',
      ),
      home: const AuthGate(),
    );
  }
}

// ============================================================
// AUTH GATE
// ============================================================
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  User? _user;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final user = await AuthService().getCurrentUser();
    if (!mounted) return;
    setState(() {
      _user = user;
      _loading = false;
    });
  }

  void _onAuthSuccess() {
    _checkAuth();
  }

  void _onLogout() {
    setState(() {
      _user = null;
    });
    _checkAuth();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Chargement...'),
            ],
          ),
        ),
      );
    }

    if (_user == null) {
      return LoginScreen(onLoginSuccess: _onAuthSuccess);
    }

    return MainScreen(user: _user!, onLogout: _onLogout);
  }
}

// ============================================================
// ÉCRAN PRINCIPAL
// ============================================================
class MainScreen extends StatefulWidget {
  final User user;
  final VoidCallback onLogout;

  const MainScreen({
    super.key,
    required this.user,
    required this.onLogout,
  });

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final screens = [
      const HomeScreen(),
      const CvScreen(),
      const MatchingScreen(),
      const RecommendationsScreen(),
      ProfileScreen(user: widget.user, onLogout: widget.onLogout),
    ];

    return Scaffold(
      body: screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Accueil',
          ),
          NavigationDestination(
            icon: Icon(Icons.upload_file_outlined),
            selectedIcon: Icon(Icons.upload_file),
            label: 'CV',
          ),
          NavigationDestination(
            icon: Icon(Icons.compare_arrows_outlined),
            selectedIcon: Icon(Icons.compare_arrows),
            label: 'Matching',
          ),
          NavigationDestination(
            icon: Icon(Icons.recommend_outlined),
            selectedIcon: Icon(Icons.recommend),
            label: 'Recos',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profil',
          ),
        ],
      ),
    );
  }
}

// ============================================================
// APP STATE
// ============================================================
class AppState extends ChangeNotifier {
  Profile? _profile;
  List<JobRecommendation>? recommendations;
  MatchResult? matchResult;
  SalaryPrediction? salaryPrediction;
  Map<String, dynamic>? skillGap;

  List<JobRecommendation> _favorites = [];
  List<Map<String, dynamic>> _analysisHistory = [];

  Profile? get profile => _profile;
  List<JobRecommendation> get favorites => _favorites;
  List<Map<String, dynamic>> get analysisHistory => _analysisHistory;

  AppState() {
    _loadFavorites();
    _loadHistory();
  }

  void setProfile(Profile p) {
    _profile = p;
    notifyListeners();
  }

  void setRecommendations(List<JobRecommendation> r) {
    recommendations = r;
    notifyListeners();
  }

  void setMatchResult(MatchResult m) {
    matchResult = m;
    notifyListeners();
  }

  void setSalaryPrediction(SalaryPrediction s) {
    salaryPrediction = s;
    notifyListeners();
  }

  void setSkillGap(Map<String, dynamic> s) {
    skillGap = s;
    notifyListeners();
  }

  // ==================== FAVORIS ====================
  Future<void> _loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString('favorites');
    if (data != null) {
      final List<dynamic> list = jsonDecode(data);
      _favorites = list.map((e) => JobRecommendation.fromJson(e)).toList();
      notifyListeners();
    }
  }

  Future<void> _saveFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    prefs.setString(
      'favorites',
      jsonEncode(_favorites.map((e) => e.toJson()).toList()),
    );
  }

  void toggleFavorite(JobRecommendation job) {
    final index = _favorites.indexWhere((j) => j.jobId == job.jobId);
    if (index >= 0) {
      _favorites.removeAt(index);
    } else {
      _favorites.add(job);
    }
    _saveFavorites();
    notifyListeners();
  }

  bool isFavorite(String jobId) {
    return _favorites.any((j) => j.jobId == jobId);
  }

  // ==================== HISTORIQUE ====================
  Future<void> _loadHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString('analysis_history');
    if (data != null) {
      _analysisHistory = List<Map<String, dynamic>>.from(jsonDecode(data));
      notifyListeners();
    }
  }

  Future<void> _saveHistory() async {
    final prefs = await SharedPreferences.getInstance();
    prefs.setString('analysis_history', jsonEncode(_analysisHistory));
  }

  void addAnalysisToHistory(Profile profile) {
    _analysisHistory.add({
      'name': profile.name,
      'skills': profile.skills,
      'date': DateTime.now().toIso8601String(),
    });
    _saveHistory();
    notifyListeners();
  }

  void clearHistory() {
    _analysisHistory.clear();
    _saveHistory();
    notifyListeners();
  }

  void clear() {
    _profile = null;
    recommendations = null;
    matchResult = null;
    salaryPrediction = null;
    skillGap = null;
    notifyListeners();
  }
}