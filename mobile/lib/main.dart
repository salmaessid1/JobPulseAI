// lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/cv_screen.dart';
import 'screens/matching_screen.dart';
import 'screens/recommendations_screen.dart';
import 'screens/salary_screen.dart';
import 'services/api_service.dart';
import 'models/job_models.dart';
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => AppState(),
      child: const JobPulseApp(),
    ),
  );
}

class AppState extends ChangeNotifier {
 Profile? _profile;
  Profile? get profile => _profile;
  List<JobRecommendation>? recommendations;
  MatchResult? matchResult;
  SalaryPrediction? salaryPrediction;
  Map<String, dynamic>? skillGap;

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

  void clear() {
    _profile = null;
    recommendations = null;
    matchResult = null;
    salaryPrediction = null;
    skillGap = null;
    notifyListeners();
  }
}

class JobPulseApp extends StatelessWidget {
  const JobPulseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JobPulseAI',
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF7C5CFF),
          secondary: Color(0xFF4FD1C5),
        ),
        fontFamily: 'Inter',
      ),
      home: const MainScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  final ApiService _apiService = ApiService();

  final List<Widget> _screens = [
    const HomeScreen(),
    const CvScreen(),
    const MatchingScreen(),
    const RecommendationsScreen(),
    const SalaryScreen(),
  ];

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Accueil'),
          NavigationDestination(icon: Icon(Icons.upload_file), label: 'CV'),
          NavigationDestination(icon: Icon(Icons.compare_arrows), label: 'Matching'),
          NavigationDestination(icon: Icon(Icons.recommend), label: 'Recommandations'),
          NavigationDestination(icon: Icon(Icons.attach_money), label: 'Salaire'),
        ],
      ),
    );
  }
}