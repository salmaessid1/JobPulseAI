// lib/screens/auth/register_screen.dart
// ignore_for_file: use_build_context_synchronously

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/auth_service.dart';
import 'terms_screen.dart';

class RegisterScreen extends StatefulWidget {
  final VoidCallback onRegisterSuccess;
  const RegisterScreen({super.key, required this.onRegisterSuccess});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen>
    with SingleTickerProviderStateMixin {
  final _nameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  final _authService = AuthService();

  bool _isLoading = false;
  bool _obscurePass = true;
  bool _obscureConfirm = true;
  bool _acceptTerms = false;
  String? _error;
  String? _success;

  // ============================================================
  // RÈGLES DU MOT DE PASSE
  // ============================================================
  bool _hasMinLength = false;
  bool _hasUppercase = false;
  bool _hasLowercase = false;
  bool _hasDigit = false;
  bool _hasSymbol = false;
  bool _noSpaces = true;

  double _passwordStrength = 0;
  String _passwordLabel = '';

  late final AnimationController _animCtrl;
  late final Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _fadeAnim = CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut);
    _animCtrl.forward();
    _passCtrl.addListener(_updatePasswordRules);
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _passCtrl.dispose();
    _confirmCtrl.dispose();
    _animCtrl.dispose();
    _passCtrl.removeListener(_updatePasswordRules);
    super.dispose();
  }

  // ============================================================
  // MISE À JOUR DES RÈGLES
  // ============================================================
  void _updatePasswordRules() {
    final pass = _passCtrl.text;

    final hasMinLength = pass.length >= 8;
    final hasUppercase = RegExp(r'[A-Z]').hasMatch(pass);
    final hasLowercase = RegExp(r'[a-z]').hasMatch(pass);
    final hasDigit = RegExp(r'[0-9]').hasMatch(pass);
    final hasSymbol = RegExp(r'[!@#\$%^&*(),.?":{}|<>_\-\[\]\\/;`~+=]').hasMatch(pass);
    final noSpaces = !pass.contains(' ');

    // Score de force
    int score = 0;
    if (hasMinLength) score++;
    if (hasUppercase) score++;
    if (hasLowercase) score++;
    if (hasDigit) score++;
    if (hasSymbol) score++;
    if (noSpaces && pass.length >= 12) score++;

    double strength = (score / 6).clamp(0.0, 1.0);

    String label;
    if (pass.isEmpty) {
      label = '';
    } else if (strength < 0.4) {
      label = 'Faible';
    } else if (strength < 0.7) {
      label = 'Moyen';
    } else if (strength < 0.9) {
      label = 'Fort';
    } else {
      label = 'Très fort';
    }

    setState(() {
      _hasMinLength = hasMinLength;
      _hasUppercase = hasUppercase;
      _hasLowercase = hasLowercase;
      _hasDigit = hasDigit;
      _hasSymbol = hasSymbol;
      _noSpaces = noSpaces;
      _passwordStrength = strength;
      _passwordLabel = label;
    });
  }

  Color _strengthColor() {
    if (_passwordStrength < 0.4) return Colors.red;
    if (_passwordStrength < 0.7) return Colors.orange;
    if (_passwordStrength < 0.9) return Colors.lightGreen;
    return Colors.green;
  }

  bool _isPasswordValid() {
    return _hasMinLength &&
        _hasUppercase &&
        _hasLowercase &&
        _hasDigit &&
        _hasSymbol &&
        _noSpaces;
  }

  // ============================================================
  // VALIDATION EMAIL
  // ============================================================
  bool _isValidEmail(String email) {
    return RegExp(r'^[\w\.\-]+@([\w\-]+\.)+[\w\-]{2,4}$')
        .hasMatch(email.trim());
  }

  // ============================================================
  // INSCRIPTION
  // ============================================================
  Future<void> _register() async {
    FocusScope.of(context).unfocus();
    setState(() {
      _error = null;
      _success = null;
    });

    if (!_formKey.currentState!.validate()) return;
    if (!_isPasswordValid()) {
      setState(() =>
          _error = 'Le mot de passe ne respecte pas toutes les règles');
      return;
    }
    if (!_acceptTerms) {
      setState(() =>
          _error = 'Vous devez accepter les conditions d\'utilisation');
      return;
    }

    setState(() => _isLoading = true);
    try {
      await _authService.register(
        _emailCtrl.text.trim(),
        _passCtrl.text,
        _nameCtrl.text.trim(),
      );
      if (!mounted) return;
      HapticFeedback.mediumImpact();
      setState(() => _success = '✅ Compte créé avec succès !');
      await Future.delayed(const Duration(milliseconds: 800));
      if (!mounted) return;
      widget.onRegisterSuccess();
    } catch (e) {
      if (!mounted) return;
      setState(() =>
          _error = e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // ============================================================
  // BUILD
  // ============================================================
  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final fieldColor = isDark ? const Color(0xFF1E1E2E) : Colors.white;

    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF0A0A15) : Colors.grey.shade100,
      appBar: AppBar(
        title: const Text('Créer un compte'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnim,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  // TITRE
                  Container(
                    width: 70,
                    height: 70,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF7C5CFF), Color(0xFF4FD1C5)],
                      ),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(Icons.person_add_alt_1,
                        color: Colors.white, size: 34),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Rejoignez JobPulseAI',
                    style:
                        TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Créez votre compte en quelques secondes',
                    style:
                        TextStyle(color: Colors.grey.shade500, fontSize: 14),
                  ),
                  const SizedBox(height: 32),

                  // NOM
                  TextFormField(
                    controller: _nameCtrl,
                    textInputAction: TextInputAction.next,
                    textCapitalization: TextCapitalization.words,
                    decoration: InputDecoration(
                      labelText: 'Nom complet',
                      hintText: 'Jean Dupont',
                      prefixIcon: const Icon(Icons.person_outline),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                      filled: true,
                      fillColor: fieldColor,
                    ),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) {
                        return 'Nom obligatoire';
                      }
                      if (v.trim().length < 2) {
                        return 'Nom trop court';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

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
                      if (!_isValidEmail(v)) return 'Email invalide';
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // MOT DE PASSE
                  TextFormField(
                    controller: _passCtrl,
                    obscureText: _obscurePass,
                    textInputAction: TextInputAction.next,
                    decoration: InputDecoration(
                      labelText: 'Mot de passe',
                      hintText: 'Min. 8 caractères',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(_obscurePass
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined),
                        onPressed: () =>
                            setState(() => _obscurePass = !_obscurePass),
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

                  // BARRE DE FORCE
                  if (_passCtrl.text.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: _passwordStrength,
                              minHeight: 6,
                              backgroundColor: Colors.grey.shade800,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                  _strengthColor()),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          _passwordLabel,
                          style: TextStyle(
                            color: _strengthColor(),
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],

                  // ====================================
                  // CHECKLIST DES RÈGLES
                  // ====================================
                  if (_passCtrl.text.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: fieldColor,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isDark
                              ? Colors.grey.shade800
                              : Colors.grey.shade300,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '🔐 Le mot de passe doit contenir :',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.grey.shade500,
                            ),
                          ),
                          const SizedBox(height: 10),
                          _ruleTile('Au moins 8 caractères', _hasMinLength),
                          _ruleTile('Une lettre majuscule (A-Z)', _hasUppercase),
                          _ruleTile('Une lettre minuscule (a-z)', _hasLowercase),
                          _ruleTile('Un chiffre (0-9)', _hasDigit),
                          _ruleTile(
                              'Un symbole (!@#\$%...)', _hasSymbol),
                          _ruleTile('Pas d\'espaces', _noSpaces),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),

                  // CONFIRMATION
                  TextFormField(
                    controller: _confirmCtrl,
                    obscureText: _obscureConfirm,
                    textInputAction: TextInputAction.done,
                    decoration: InputDecoration(
                      labelText: 'Confirmer le mot de passe',
                      prefixIcon: const Icon(Icons.lock_reset),
                      suffixIcon: IconButton(
                        icon: Icon(_obscureConfirm
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined),
                        onPressed: () =>
                            setState(() => _obscureConfirm = !_obscureConfirm),
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                      filled: true,
                      fillColor: fieldColor,
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) {
                        return 'Confirmation obligatoire';
                      }
                      if (v != _passCtrl.text) {
                        return 'Les mots de passe ne correspondent pas';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // CGU
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Checkbox(
                        value: _acceptTerms,
                        activeColor: const Color(0xFF7C5CFF),
                        onChanged: (v) =>
                            setState(() => _acceptTerms = v ?? false),
                      ),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.only(top: 12),
                          child: GestureDetector(
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const TermsScreen(),
                                ),
                              );
                            },
                            child: RichText(
                              text: TextSpan(
                                style: TextStyle(
                                  fontSize: 13,
                                  color: isDark
                                      ? Colors.grey.shade400
                                      : Colors.grey.shade700,
                                ),
                                children: const [
                                  TextSpan(text: 'J\'accepte les '),
                                  TextSpan(
                                    text: 'conditions d\'utilisation',
                                    style: TextStyle(
                                      color: Color(0xFF7C5CFF),
                                      fontWeight: FontWeight.bold,
                                      decoration: TextDecoration.underline,
                                    ),
                                  ),
                                  TextSpan(text: ' et la '),
                                  TextSpan(
                                    text: 'politique de confidentialité',
                                    style: TextStyle(
                                      color: Color(0xFF7C5CFF),
                                      fontWeight: FontWeight.bold,
                                      decoration: TextDecoration.underline,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),

                  // ERREUR / SUCCÈS
                  if (_error != null) ...[
                    const SizedBox(height: 12),
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
                  if (_success != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.green.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                            color: Colors.green.withValues(alpha: 0.4)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle,
                              color: Colors.green, size: 20),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(_success!,
                                style: const TextStyle(
                                    color: Colors.green, fontSize: 13)),
                          ),
                        ],
                      ),
                    ),
                  ],

                  const SizedBox(height: 24),

                  // BOUTON
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _register,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF7C5CFF),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                        elevation: 8,
                        shadowColor:
                            const Color(0xFF7C5CFF).withValues(alpha: 0.4),
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              width: 22,
                              height: 22,
                              child: CircularProgressIndicator(
                                  color: Colors.white, strokeWidth: 2.5),
                            )
                          : const Text(
                              'S\'inscrire',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 0.5,
                              ),
                            ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _ruleTile(String label, bool ok) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Icon(
            ok ? Icons.check_circle : Icons.radio_button_unchecked,
            size: 18,
            color: ok ? Colors.green : Colors.grey.shade600,
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 13,
              color: ok ? Colors.green : Colors.grey.shade500,
              fontWeight: ok ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}