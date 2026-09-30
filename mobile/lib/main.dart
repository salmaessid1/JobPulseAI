// lib/main.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:jobpulseai_mobile/screens/notifications_screen.dart';
import 'package:jobpulseai_mobile/services/notification_service.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'services/user_profile_service.dart';
import 'screens/home_screen.dart';
import 'screens/cv_screen.dart';
import 'screens/matching_screen.dart';
import 'screens/recommendations_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/favorites_screen.dart';
import 'screens/history_screen.dart';
import 'screens/support_screen.dart';
import 'screens/auth/login_screen.dart';
import 'package:flutter_localizations/flutter_localizations.dart';   // ✅ INDISPENSABLE

import 'services/auth_service.dart';
import 'l10n/translations.dart';
import 'models/job_models.dart';
import 'models/user_model.dart';
import 'services/biometric_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await NotificationService.load().timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('⚠️ Échec chargement notifications : $e');
  }

  runApp(
    ChangeNotifierProvider(
      create: (_) => AppState()..init(),
      child: const JobPulseApp(),
    ),
  );
}

class JobPulseApp extends StatelessWidget {
  const JobPulseApp({super.key});

  @override
  Widget build(BuildContext context) {
    final appState = Provider.of<AppState>(context);

    // ✅ Sécuriser la locale : 'fr' par défaut si vide
    final lang = appState.language.isEmpty ? 'fr' : appState.language;

    return MaterialApp(
      title: 'JobPulseAI',
      debugShowCheckedModeBanner: false,
      themeMode: appState.themeMode,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        colorScheme: const ColorScheme.light(
          primary: Color(0xFF7C5CFF),
          secondary: Color(0xFF4FD1C5),
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF7C5CFF),
          secondary: Color(0xFF4FD1C5),
        ),
      ),

      // ✅ LOCALISATION COMPLÈTE
      locale: Locale(lang),
      supportedLocales: const [
        Locale('fr', 'FR'),
        Locale('en', 'US'),
        Locale('ar', 'SA'),
        Locale('es', 'ES'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      home: const AuthGate(),
      routes: {
        '/favorites': (_) => const FavoritesScreen(),
        '/history': (_) => const HistoryScreen(),
        '/support': (_) => const SupportScreen(),
        '/notifications': (_) => const NotificationsScreen(),
      },
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

  void _onAuthSuccess() => _checkAuth();

  void _onLogout() {
    setState(() => _user = null);
    _checkAuth();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (_user == null) {
      return LoginScreen(onLoginSuccess: _onAuthSuccess);
    }
    return MainScreen(user: _user!, onLogout: _onLogout);
  }
}

// ============================================================
// MAIN SCREEN
// ============================================================
class MainScreen extends StatefulWidget {
  final User user;
  final VoidCallback onLogout;

  const MainScreen({super.key, required this.user, required this.onLogout});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final t = Provider.of<AppState>(context);
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
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.home_outlined),
            selectedIcon: const Icon(Icons.home),
            label: t.t('home'),
          ),
          NavigationDestination(
            icon: const Icon(Icons.upload_file_outlined),
            selectedIcon: const Icon(Icons.upload_file),
            label: t.t('cv'),
          ),
          NavigationDestination(
            icon: const Icon(Icons.compare_arrows_outlined),
            selectedIcon: const Icon(Icons.compare_arrows),
            label: t.t('matching'),
          ),
          NavigationDestination(
            icon: const Icon(Icons.recommend_outlined),
            selectedIcon: const Icon(Icons.recommend),
            label: t.t('recos'),
          ),
          NavigationDestination(
            icon: const Icon(Icons.person_outline),
            selectedIcon: const Icon(Icons.person),
            label: t.t('profile'),
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

  // ✅ Nouveaux états persistants
  ThemeMode _themeMode = ThemeMode.dark;
  String _language = 'fr';
  bool _notificationsEnabled = true;
  bool _twoFactorEnabled = false;
  bool _biometricEnabled = false;

  Profile? get profile => _profile;
  List<JobRecommendation> get favorites => _favorites;
  List<Map<String, dynamic>> get analysisHistory => _analysisHistory;
  ThemeMode get themeMode => _themeMode;
  String get language => _language;
  bool get notificationsEnabled => _notificationsEnabled;
  bool get twoFactorEnabled => _twoFactorEnabled;
  bool get biometricEnabled => _biometricEnabled;

  /// Traduction : t('home') → "Accueil"
  String t(String key) => AppTranslations.tr(_language, key);

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _themeMode =
        (prefs.getBool('dark_mode') ?? true) ? ThemeMode.dark : ThemeMode.light;
    _language = prefs.getString('language') ?? 'fr';
    _notificationsEnabled = prefs.getBool('notifications') ?? true;
    _twoFactorEnabled = prefs.getBool('two_factor') ?? false;
    _biometricEnabled = prefs.getBool('biometric') ?? false;

    // ✅ Synchroniser dès le démarrage
    await NotificationService.setEnabled(_notificationsEnabled);

    await _loadFavorites();
    await _loadHistory();
    notifyListeners();
  }

// Dans AppState
  Future<void> reloadUserProfile() async {
    final p = await UserProfileService.load();
    if (p.fullName.isNotEmpty) {
      // Met à jour l'utilisateur si un profil existe
      notifyListeners();
    }
  }

  // dans AppState
  Future<bool> setBiometricEnabled(bool enabled) async {
    if (enabled) {
      // Vérifie que la biométrie est disponible
      final available = await BiometricService.isAvailable();
      if (!available) {
        return false;
      }
      // Demande l'authentification pour activer
      final auth = await BiometricService.authenticate(
        reason: 'Authentifiez-vous pour activer la biométrie',
      );
      if (!auth) return false;
    }
    _biometricEnabled = enabled;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('biometric', enabled);
    return true;
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

  // ==================== THÈME ====================
  Future<void> setDarkMode(bool enabled) async {
    _themeMode = enabled ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('dark_mode', enabled);
  }

  // ==================== LANGUE ====================
  Future<void> setLanguage(String lang) async {
    _language = lang;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('language', lang);
  }

  // ==================== NOTIFICATIONS ====================
// Dans AppState
  Future<void> setNotificationsEnabled(bool enabled) async {
    _notificationsEnabled = enabled;
    notifyListeners();

    // ✅ Synchroniser avec NotificationService
    await NotificationService.setEnabled(enabled);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('notifications', enabled);
  }

  // ==================== 2FA ====================
  Future<void> setTwoFactorEnabled(bool enabled) async {
    _twoFactorEnabled = enabled;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('two_factor', enabled);
  }

  // ==================== FAVORIS ====================
  Future<void> _loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString('favorites');
    if (data != null) {
      final List<dynamic> list = jsonDecode(data);
      _favorites = list.map((e) => JobRecommendation.fromJson(e)).toList();
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

  bool isFavorite(String jobId) => _favorites.any((j) => j.jobId == jobId);

  // ==================== HISTORIQUE ====================
  Future<void> _loadHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString('analysis_history');
    if (data != null) {
      _analysisHistory = List<Map<String, dynamic>>.from(jsonDecode(data));
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
