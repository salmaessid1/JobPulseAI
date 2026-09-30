// lib/screens/auth/login_screen.dart
// ignore_for_file: use_build_context_synchronously

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/auth_service.dart';
import '../../services/biometric_service.dart';
import '../../services/user_credentials_service.dart';
import 'register_screen.dart';
import 'forgot_password_screen.dart';

class LoginScreen extends StatefulWidget {
  final VoidCallback onLoginSuccess;
  const LoginScreen({super.key, required this.onLoginSuccess});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  final _authService = AuthService();

  bool _isLoading = false;
  bool _obscure = true;
  bool _rememberMe = false;

  // Biométrie
  bool _faceAvailable = false;
  bool _fingerprintAvailable = false;
  bool _hasSavedCredentials = false;

  String? _error;

  late final AnimationController _animCtrl;
  late final Animation<double> _fadeAnim;
  late final Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _fadeAnim = CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animCtrl, curve: Curves.easeOutCubic));
    _animCtrl.forward();
    _initBiometric();
  }

  Future<void> _initBiometric() async {
    final faceAvail = await BiometricService.isFaceAvailable();
    final fpAvail = await BiometricService.isFingerprintAvailable();
    final savedEmail = await UserCredentialsService.getEmail();
    final hasPw = await UserCredentialsService.hasPassword();

    if (!mounted) return;
    setState(() {
      _faceAvailable = faceAvail;
      _fingerprintAvailable = fpAvail;
      _hasSavedCredentials = savedEmail != null && hasPw;
    });

    if (savedEmail != null && mounted) {
      _emailCtrl.text = savedEmail;
    }
  }

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passCtrl.dispose();
    _animCtrl.dispose();
    super.dispose();
  }

  bool _isValidEmail(String email) {
    return RegExp(r'^[\w\.\-]+@([\w\-]+\.)+[\w\-]{2,4}$')
        .hasMatch(email.trim());
  }

  // ============================================================
  // LOGIN CLASSIQUE
  // ============================================================
  Future<void> _login() async {
    FocusScope.of(context).unfocus();
    setState(() => _error = null);

    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    try {
      await _authService.login(_emailCtrl.text.trim(), _passCtrl.text);
      if (!mounted) return;
      HapticFeedback.mediumImpact();

      if (_rememberMe &&
          (_faceAvailable || _fingerprintAvailable) &&
          !_hasSavedCredentials) {
        await _askEnableBiometric();
      }

      widget.onLoginSuccess();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // ============================================================
  // LOGIN PAR VISAGE
  // ============================================================
  Future<void> _loginWithFace() async {
    FocusScope.of(context).unfocus();
    setState(() => _error = null);

    final savedEmail = await UserCredentialsService.getEmail();
    if (savedEmail == null || savedEmail.isEmpty) {
      setState(() => _error =
          '⚠️ Aucun compte enregistré. Connectez-vous d\'abord avec votre mot de passe.');
      return;
    }

    final ok = await BiometricService.authenticateWithFace(
      reason: 'Regardez la caméra pour vous connecter à JobPulseAI',
    );
    if (!ok) {
      if (!mounted) return;
      setState(() => _error = '❌ Reconnaissance faciale annulée');
      return;
    }

    await _finishBiometricLogin();
  }

  // ============================================================
  // LOGIN PAR EMPREINTE
  // ============================================================
  Future<void> _loginWithFingerprint() async {
    FocusScope.of(context).unfocus();
    setState(() => _error = null);

    final savedEmail = await UserCredentialsService.getEmail();
    if (savedEmail == null || savedEmail.isEmpty) {
      setState(() => _error =
          '⚠️ Aucun compte enregistré. Connectez-vous d\'abord avec votre mot de passe.');
      return;
    }

    final ok = await BiometricService.authenticate(
      reason: 'Posez votre doigt sur le capteur',
    );
    if (!ok) {
      if (!mounted) return;
      setState(() => _error = '❌ Empreinte annulée');
      return;
    }

    await _finishBiometricLogin();
  }

  // ============================================================
  // TERMINER LE LOGIN BIOMÉTRIQUE
  // ============================================================
  Future<void> _finishBiometricLogin() async {
    final savedUser = await UserCredentialsService.getUser();
    if (savedUser == null) {
      if (!mounted) return;
      setState(() => _error =
          '⚠️ Données du compte introuvables. Reconnectez-vous manuellement.');
      return;
    }

    await _authService.saveUserDirectly(savedUser);
    if (!mounted) return;

    HapticFeedback.mediumImpact();
    widget.onLoginSuccess();
  }

  // ============================================================
  // DEMANDER D'ACTIVER LA BIOMÉTRIE
  // ============================================================
  Future<void> _askEnableBiometric() async {
    final enable = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('🔐 Activer la connexion rapide ?'),
        content: const Text(
          'Vous pourrez vous connecter plus rapidement avec votre visage ou votre empreinte la prochaine fois.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Plus tard'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF7C5CFF),
            ),
            child: const Text('Activer'),
          ),
        ],
      ),
    );

    if (enable == true && mounted) {
      await UserCredentialsService.savePassword(_passCtrl.text);
      await UserCredentialsService.saveEmail(_emailCtrl.text.trim());
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Connexion rapide activée'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  // ============================================================
  // BUILD
  // ============================================================
  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0A0A15) : Colors.grey.shade100;
    final fieldColor = isDark ? const Color(0xFF1E1E2E) : Colors.white;
    final anyBiometric = _faceAvailable || _fingerprintAvailable;

    return Scaffold(
      backgroundColor: bgColor,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: FadeTransition(
              opacity: _fadeAnim,
              child: SlideTransition(
                position: _slideAnim,
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // LOGO
                      Container(
                        width: 90,
                        height: 90,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF7C5CFF), Color(0xFF4FD1C5)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF7C5CFF)
                                  .withValues(alpha: 0.3),
                              blurRadius: 24,
                              offset: const Offset(0, 12),
                            ),
                          ],
                        ),
                        child: const Icon(Icons.work_outline,
                            size: 44, color: Colors.white),
                      ),
                      const SizedBox(height: 24),
                      const Text(
                        'JobPulseAI',
                        style: TextStyle(
                          fontSize: 30,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Bienvenue 👋 Connectez-vous à votre compte',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            color: Colors.grey.shade500, fontSize: 14),
                      ),
                      const SizedBox(height: 36),

                      // EMAIL
                      TextFormField(
                        controller: _emailCtrl,
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        decoration: InputDecoration(
                          labelText: 'Email',
                          hintText: 'vous@exemple.com',
                          prefixIcon: const Icon(Icons.email_outlined),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                          filled: true,
                          fillColor: fieldColor,
                        ),
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) {
                            return 'Email obligatoire';
                          }
                          if (!_isValidEmail(v)) {
                            return 'Email invalide';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      // MOT DE PASSE
                      TextFormField(
                        controller: _passCtrl,
                        obscureText: _obscure,
                        textInputAction: TextInputAction.done,
                        onFieldSubmitted: (_) => _login(),
                        decoration: InputDecoration(
                          labelText: 'Mot de passe',
                          prefixIcon: const Icon(Icons.lock_outline),
                          suffixIcon: IconButton(
                            icon: Icon(_obscure
                                ? Icons.visibility_outlined
                                : Icons.visibility_off_outlined),
                            onPressed: () =>
                                setState(() => _obscure = !_obscure),
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                          filled: true,
                          fillColor: fieldColor,
                        ),
                        validator: (v) {
                          if (v == null || v.isEmpty) {
                            return 'Mot de passe obligatoire';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 12),

                      // SE SOUVENIR + OUBLIÉ
                      Row(
                        children: [
                          Checkbox(
                            value: _rememberMe,
                            activeColor: const Color(0xFF7C5CFF),
                            onChanged: (v) =>
                                setState(() => _rememberMe = v ?? false),
                          ),
                          const Text('Se souvenir de moi',
                              style: TextStyle(fontSize: 13)),
                          const Spacer(),
                          TextButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) =>
                                      const ForgotPasswordScreen(),
                                ),
                              );
                            },
                            child: const Text(
                              'Mot de passe oublié ?',
                              style: TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),

                      // ERREUR
                      if (_error != null) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.red.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                                color: Colors.red.withValues(alpha: 0.4)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.error_outline,
                                  color: Colors.red, size: 20),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(_error!,
                                    style: const TextStyle(
                                        color: Colors.red, fontSize: 13)),
                              ),
                            ],
                          ),
                        ),
                      ],

                      const SizedBox(height: 24),

                      // BOUTON SE CONNECTER
                      SizedBox(
                        width: double.infinity,
                        height: 54,
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _login,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF7C5CFF),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                            elevation: 8,
                            shadowColor: const Color(0xFF7C5CFF)
                                .withValues(alpha: 0.4),
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  width: 22,
                                  height: 22,
                                  child: CircularProgressIndicator(
                                      color: Colors.white, strokeWidth: 2.5),
                                )
                              : const Text(
                                  'Se connecter',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                        ),
                      ),

                      // ==========================================
                      // BIOMÉTRIE (VISAGE + EMPREINTE)
                      // ==========================================
                      if (anyBiometric) ...[
                        const SizedBox(height: 20),
                        Row(
                          children: [
                            const Expanded(child: Divider()),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 12),
                              child: Text('ou connexion rapide',
                                  style: TextStyle(
                                      color: Colors.grey.shade500,
                                      fontSize: 12)),
                            ),
                            const Expanded(child: Divider()),
                          ],
                        ),
                        const SizedBox(height: 16),

                        // BOUTON VISAGE
                        if (_faceAvailable) ...[
                          _biometricButton(
                            icon: Icons.face_retouching_natural,
                            label: _hasSavedCredentials
                                ? 'Connexion par visage'
                                : 'Visage (après 1ère connexion)',
                            enabled: _hasSavedCredentials && !_isLoading,
                            onPressed: _loginWithFace,
                            color: const Color(0xFF4FD1C5),
                          ),
                          const SizedBox(height: 12),
                        ],

                        // BOUTON EMPREINTE
                        if (_fingerprintAvailable) ...[
                          _biometricButton(
                            icon: Icons.fingerprint,
                            label: _hasSavedCredentials
                                ? 'Connexion par empreinte'
                                : 'Empreinte (après 1ère connexion)',
                            enabled: _hasSavedCredentials && !_isLoading,
                            onPressed: _loginWithFingerprint,
                            color: const Color(0xFF7C5CFF),
                          ),
                        ],

                        if (!_hasSavedCredentials) ...[
                          const SizedBox(height: 12),
                          Text(
                            '💡 Connectez-vous une première fois pour activer la connexion rapide',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                                fontSize: 11,
                                color: Colors.grey.shade500,
                                fontStyle: FontStyle.italic),
                          ),
                        ],
                      ],

                      const SizedBox(height: 24),

                      // INSCRIPTION
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Pas encore de compte ?',
                            style: TextStyle(
                                color: Colors.grey.shade500, fontSize: 14),
                          ),
                          TextButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => RegisterScreen(
                                    onRegisterSuccess:
                                        widget.onLoginSuccess,
                                  ),
                                ),
                              );
                            },
                            child: const Text(
                              'S\'inscrire',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF7C5CFF),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ============================================================
  // BOUTON BIOMÉTRIQUE RÉUTILISABLE
  // ============================================================
  Widget _biometricButton({
    required IconData icon,
    required String label,
    required bool enabled,
    required VoidCallback onPressed,
    required Color color,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 54,
      child: OutlinedButton.icon(
        onPressed: enabled ? onPressed : null,
        icon: Icon(icon, size: 26, color: enabled ? color : Colors.grey),
        label: Text(
          label,
          style: TextStyle(
            fontSize: 14.5,
            fontWeight: FontWeight.w600,
            color: enabled ? color : Colors.grey,
          ),
        ),
        style: OutlinedButton.styleFrom(
          side: BorderSide(
            color: enabled ? color : Colors.grey.shade600,
            width: 1.5,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
    );
  }
}