// lib/screens/profile_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';
import '../main.dart';
import 'auth/qr_2fa_setup_screen.dart';
import '../services/user_profile_service.dart';
import 'personal_info_screen.dart';

class ProfileScreen extends StatefulWidget {
  final User user;
  final VoidCallback onLogout;

  const ProfileScreen({super.key, required this.user, required this.onLogout});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _displayName = '';

  @override
  void initState() {
    super.initState();
    _displayName = widget.user.fullName;
    _loadName();
  }

Future<void> _loadName() async {
  final prefs = await SharedPreferences.getInstance();
  // 1) Essayer UserProfileService (nouveau système)
  final p = await UserProfileService.load();
  if (!mounted) return;

  if (p.fullName.isNotEmpty) {
    setState(() {
      _displayName = p.fullName;
    });
    return;
  }

  // 2) Fallback : display_name (ancien système)
  final legacyName = prefs.getString('display_name');
  if (!mounted) return;
  setState(() {
    _displayName = legacyName ?? widget.user.fullName;
  });
}



  @override
  Widget build(BuildContext context) {
    final appState = Provider.of<AppState>(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0A0A15) : Colors.grey.shade100;
    final cardColor = isDark ? const Color(0xFF1E1E2E) : Colors.white;
    final borderColor = isDark ? Colors.grey.shade800 : Colors.grey.shade300;

    return Scaffold(
      backgroundColor: bgColor,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 260,
            pinned: true,
            backgroundColor: cardColor,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF7C5CFF), Color(0xFF4FD1C5)],
                  ),
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const SizedBox(height: 20),
                      Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white.withValues(alpha: 0.2),
                        ),
                        child: CircleAvatar(
                          radius: 50,
                          backgroundColor: Colors.white,
                          child: Text(
                            _initials(_displayName),
                            style: const TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF7C5CFF),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        _displayName.isEmpty ? 'Utilisateur' : _displayName,
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        widget.user.email,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white.withValues(alpha: 0.8),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                              color: Colors.white.withValues(alpha: 0.4)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.verified,
                                size: 14, color: Colors.white),
                            const SizedBox(width: 4),
                            Text(
                              appState.t('verified_account'),
                              style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            title: Text(appState.t('my_profile')),
          ),

          // STATS
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  _buildStatCard(
                    icon: Icons.description,
                    label: appState.t('cv'),
                    value: '${appState.analysisHistory.length}',
                    color: Colors.purple,
                    cardColor: cardColor,
                    borderColor: borderColor,
                  ),
                  const SizedBox(width: 12),
                  _buildStatCard(
                    icon: Icons.favorite,
                    label: appState.t('favorites'),
                    value: '${appState.favorites.length}',
                    color: Colors.red,
                    cardColor: cardColor,
                    borderColor: borderColor,
                  ),
                  const SizedBox(width: 12),
                  _buildStatCard(
                    icon: Icons.star,
                    label: appState.t('skills_count'),
                    value: '${appState.profile?.skills.length ?? 0}',
                    color: Colors.amber,
                    cardColor: cardColor,
                    borderColor: borderColor,
                  ),
                ],
              ),
            ),
          ),

          // COMPTE
          SliverToBoxAdapter(
            child: _buildSection(
              title: '👤 ${appState.t('account')}',
              cardColor: cardColor,
              borderColor: borderColor,
              children: [
                _buildTile(
                  icon: Icons.person_outline,
                  title: appState.t('personal_info'),
                  subtitle: _displayName,
                  onTap: () => _showEditProfile(context, appState),
                ),
                _buildTile(
                  icon: Icons.badge_outlined,
                  title: appState.t('my_cv'),
                  subtitle: appState.profile != null
                      ? '${appState.profile!.skills.length} ${appState.t('skills_count')}'
                      : 'Aucun CV',
                  onTap: () => _showMyCV(context, appState),
                ),
                _buildTile(
                  icon: Icons.history,
                  title: appState.t('activity_history'),
                  subtitle: '${appState.analysisHistory.length}',
                  onTap: () => Navigator.pushNamed(context, '/history'),
                ),
              ],
            ),
          ),

          // SÉCURITÉ
          SliverToBoxAdapter(
            child: _buildSection(
              title: '🔐 ${appState.t('security')}',
              cardColor: cardColor,
              borderColor: borderColor,
              children: [
                _buildTile(
                  icon: Icons.lock_outline,
                  title: appState.t('change_password'),
                  onTap: () => _showChangePassword(context, appState),
                ),
                _buildSwitchTile(
  icon: Icons.fingerprint,
  title: appState.t('biometric'),
  value: appState.biometricEnabled,
  onChanged: (v) async {
    final success = await appState.setBiometricEnabled(v);
    if (!context.mounted) return;
    if (!success && v) {
      _snack(context, '⚠️ Biométrie non disponible sur cet appareil');
      return;
    }
    _snack(context, v
        ? '🔐 Biométrie ${appState.t('enabled')}'
        : '🔓 Biométrie ${appState.t('disabled')}');
  },
),
                _buildTile(
                  icon: Icons.devices,
                  title: appState.t('connected_devices'),
                  onTap: () => _showDevices(context, appState),
                ),
                _buildSwitchTile(
                  icon: Icons.security,
                  title: appState.t('two_factor'),
                  value: appState.twoFactorEnabled,
                  onChanged: (v) async {
                    if (v) {
                      await _show2FASetup(context, appState);
                    } else {
                      await appState.setTwoFactorEnabled(false);
                      if (!context.mounted) return;
                      _snack(context, '🔓 2FA ${appState.t('disabled')}');
                    }
                  },
                ),
              ],
            ),
          ),

          // PRÉFÉRENCES
          SliverToBoxAdapter(
            child: _buildSection(
              title: '⚙️ ${appState.t('preferences')}',
              cardColor: cardColor,
              borderColor: borderColor,
              children: [
                _buildSwitchTile(
                  icon: Icons.notifications_outlined,
                  title: appState.t('notifications'),
                  subtitle: appState.notificationsEnabled
                      ? appState.t('enabled')
                      : appState.t('disabled'),
                  value: appState.notificationsEnabled,
                  onChanged: (v) async {
                    await appState.setNotificationsEnabled(v);
                    if (!context.mounted) return;
                    _snack(
                      context,
                      v
                          ? '🔔 ${appState.t('enabled')}'
                          : '🔕 ${appState.t('disabled')}',
                    );
                  },
                ),
                _buildSwitchTile(
                  icon: Icons.dark_mode_outlined,
                  title: appState.t('dark_mode'),
                  value: appState.themeMode == ThemeMode.dark,
                  onChanged: (v) async {
                    await appState.setDarkMode(v);
                  },
                ),
                _buildTile(
                  icon: Icons.language_outlined,
                  title: appState.t('language'),
                  subtitle: _languageLabel(appState.language),
                  onTap: () => _showLanguage(context, appState),
                ),
              ],
            ),
          ),

          // CONFIDENTIALITÉ & AIDE
          SliverToBoxAdapter(
            child: _buildSection(
              title: '🛡️ ${appState.t('privacy_help')}',
              cardColor: cardColor,
              borderColor: borderColor,
              children: [
                _buildTile(
                  icon: Icons.privacy_tip_outlined,
                  title: appState.t('privacy'),
                  onTap: () => _showPrivacy(context, appState),
                ),
                _buildTile(
                  icon: Icons.description_outlined,
                  title: appState.t('terms'),
                  onTap: () => _showTerms(context, appState),
                ),
                _buildTile(
                  icon: Icons.help_outline,
                  title: appState.t('help'),
                  onTap: () => _showHelp(context, appState),
                ),
                _buildTile(
                  icon: Icons.support_agent,
                  title: appState.t('contact_support'),
                  subtitle: appState.t('support_online'),
                  trailing: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.green.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text('En ligne',
                        style: TextStyle(
                            color: Colors.green,
                            fontSize: 11,
                            fontWeight: FontWeight.bold)),
                  ),
                  onTap: () => Navigator.pushNamed(context, '/support'),
                ),
                _buildTile(
                  icon: Icons.info_outline,
                  title: appState.t('about'),
                  subtitle: 'JobPulseAI v1.0.0',
                  onTap: () => _showAbout(context, appState),
                ),
              ],
            ),
          ),

          // ACTIONS
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => _confirmLogout(context, appState),
                      icon: const Icon(Icons.logout),
                      label: Text(appState.t('logout')),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        side: const BorderSide(color: Colors.orange),
                        foregroundColor: Colors.orange,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: TextButton.icon(
                      onPressed: () => _confirmDelete(context, appState),
                      icon: const Icon(Icons.delete_forever, size: 18),
                      label: Text(appState.t('delete_account')),
                      style: TextButton.styleFrom(foregroundColor: Colors.red),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text('JobPulseAI v1.0.0 · © 2026',
                      style: TextStyle(
                          color: Colors.grey.shade600, fontSize: 11)),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================
  // HELPERS
  // ============================================================
  String _initials(String fullName) {
    if (fullName.isEmpty) return '?';
    final parts = fullName.trim().split(' ');
    if (parts.length == 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }

  String _languageLabel(String code) {
    switch (code) {
      case 'fr': return '🇫🇷 Français';
      case 'en': return '🇬🇧 English';
      case 'ar': return '🇸🇦 العربية';
      case 'es': return '🇪🇸 Español';
      default: return code;
    }
  }

  void _snack(BuildContext context, String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), duration: const Duration(seconds: 2)),
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
    required Color cardColor,
    required Color borderColor,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: borderColor),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 6),
            Text(value,
                style: const TextStyle(
                    fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 2),
            Text(label,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.grey, fontSize: 10)),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required List<Widget> children,
    required Color cardColor,
    required Color borderColor,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 8),
            child: Text(title,
                style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.5)),
          ),
          Container(
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: borderColor),
            ),
            child: Column(children: children),
          ),
        ],
      ),
    );
  }

  Widget _buildTile({
    required IconData icon,
    required String title,
    String? subtitle,
    Widget? trailing,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: const Color(0xFF7C5CFF).withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: const Color(0xFF7C5CFF), size: 20),
      ),
      title: Text(title,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
      subtitle: subtitle != null
          ? Text(subtitle,
              style: const TextStyle(color: Colors.grey, fontSize: 12))
          : null,
      trailing: trailing ??
          const Icon(Icons.chevron_right, color: Colors.grey, size: 20),
      onTap: onTap,
    );
  }

  Widget _buildSwitchTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      secondary: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: const Color(0xFF7C5CFF).withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: const Color(0xFF7C5CFF), size: 20),
      ),
      title: Text(title,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
      subtitle: subtitle != null
          ? Text(subtitle,
              style: const TextStyle(color: Colors.grey, fontSize: 12))
          : null,
      value: value,
      onChanged: onChanged,
      activeThumbColor: const Color(0xFF7C5CFF),
    );
  }

  // ============================================================
  // MODALES
  // ============================================================
void _showEditProfile(BuildContext context, AppState appState) async {
  final result = await Navigator.push(
    context,
    MaterialPageRoute(
      builder: (_) => const PersonalInfoScreen(),
    ),
  );

  // ✅ Si l'utilisateur a enregistré, recharger les données
  if (result == true) {
    await _loadName();
  }
}

  void _showMyCV(BuildContext context, AppState appState) {
    final profile = appState.profile;
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.7,
        maxChildSize: 0.95,
        builder: (_, scrollCtrl) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('📄 ${appState.t('my_cv')}',
                  style: const TextStyle(
                      fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Expanded(
                child: profile == null
                    ? const Center(child: Text('Aucun CV analysé'))
                    : ListView(
                        controller: scrollCtrl,
                        children: [
                          ListTile(
                            leading: const Icon(Icons.person,
                                color: Colors.purple),
                            title: Text(appState.t('personal_info')),
                            subtitle: Text(profile.name),
                          ),
                          ListTile(
                            leading: const Icon(Icons.work_outline,
                                color: Colors.purple),
                            title: Text(appState.t('seniority')),
                            subtitle: Text(profile.seniority),
                          ),
                          const SizedBox(height: 8),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: Text('🧠 ${appState.t('detected_skills')}',
                                style: const TextStyle(
                                    fontWeight: FontWeight.bold, fontSize: 15)),
                          ),
                          const SizedBox(height: 8),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: profile.skills
                                  .map((s) => Chip(
                                        label: Text(s),
                                        backgroundColor: Colors.purple
                                            .withValues(alpha: 0.2),
                                      ))
                                  .toList(),
                            ),
                          ),
                        ],
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showChangePassword(BuildContext context, AppState appState) {
  final oldCtrl = TextEditingController();
  final newCtrl = TextEditingController();
  final confirmCtrl = TextEditingController();
  final cardColor = Theme.of(context).brightness == Brightness.dark
      ? const Color(0xFF1E1E2E) : Colors.white;

  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: cardColor,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (ctx) => Padding(
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 20,
        bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('🔐 Modifier le mot de passe',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 20),
          TextField(
            controller: oldCtrl,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Mot de passe actuel',
              prefixIcon: Icon(Icons.lock_outline),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: newCtrl,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Nouveau mot de passe (min. 6)',
              prefixIcon: Icon(Icons.lock_reset),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: confirmCtrl,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Confirmer',
              prefixIcon: Icon(Icons.check_circle_outline),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () async {
                if (newCtrl.text.length < 6) {
                  _snack(ctx, '⚠️ Minimum 6 caractères');
                  return;
                }
                if (newCtrl.text != confirmCtrl.text) {
                  _snack(ctx, '⚠️ Les mots de passe ne correspondent pas');
                  return;
                }
                // ✅ Vraie vérification + modification
                final ok = await AuthService().changePassword(
  oldCtrl.text,
  newCtrl.text,
);
                if (!ctx.mounted) return;
                if (!ok) {
                  _snack(ctx, '❌ Ancien mot de passe incorrect');
                  return;
                }
                Navigator.pop(ctx);
                if (!context.mounted) return;
                _snack(context, '✅ Mot de passe modifié');
              },
              child: const Text('Confirmer'),
            ),
          ),
        ],
      ),
    ),
  );
}

  // ============================================================
  // 2FA
  // ============================================================
  Future<void> _show2FASetup(BuildContext context, AppState appState) async {
  // Ouvre l'écran QR
  final secret = await Navigator.push<String>(
    context,
    MaterialPageRoute(
      builder: (_) => Qr2faSetupScreen(userEmail: widget.user.email),
    ),
  );

  if (secret != null && secret.isNotEmpty) {
    await appState.setTwoFactorEnabled(true);
    if (!context.mounted) return;
    _snack(context, '✅ 2FA activée');
  } else {
    if (!context.mounted) return;
    _snack(context, '❌ 2FA désactivée');
  }
}

  void _showDevices(BuildContext context, AppState appState) {
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;
    showModalBottomSheet(
      context: context,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('📱 ${appState.t('connected_devices')}',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: Colors.green,
                child: Icon(Icons.phone_android, color: Colors.white),
              ),
              title: const Text('Cet appareil',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              subtitle: const Text('Actif maintenant'),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Text('En ligne',
                    style: TextStyle(color: Colors.green, fontSize: 11)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showLanguage(BuildContext context, AppState appState) {
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;
    final langs = {
      'fr': '🇫🇷 Français',
      'en': '🇬🇧 English',
      'ar': '🇸🇦 العربية',
      'es': '🇪🇸 Español',
    };

    showModalBottomSheet(
      context: context,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🌐 ${appState.t('language')}',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            ...langs.entries.map((e) {
              final isSelected = appState.language == e.key;
              return ListTile(
                title: Text(e.value),
                trailing: isSelected
                    ? const Icon(Icons.check_circle, color: Color(0xFF7C5CFF))
                    : null,
                onTap: () async {
                  Navigator.pop(ctx);
                  await appState.setLanguage(e.key);
                  if (!context.mounted) return;
                  _snack(context, '🌐 ${e.value}');
                },
              );
            }),
          ],
        ),
      ),
    );
  }

  void _showPrivacy(BuildContext context, AppState appState) {
    _showTextModal(context,
        title: '🛡️ ${appState.t('privacy')}',
        content: '''
JobPulseAI protège votre vie privée.

1. DONNÉES COLLECTÉES
Email, nom, CV analysés.

2. UTILISATION
Recommandations, analyse de profil.

3. PARTAGE
Aucun partage avec des tiers.

4. SÉCURITÉ
Données chiffrées et sécurisées.

5. VOS DROITS
Suppression sur demande.

© 2026 JobPulseAI''');
  }

  void _showTerms(BuildContext context, AppState appState) {
    _showTextModal(context,
        title: '📄 ${appState.t('terms')}',
        content: '''
En utilisant JobPulseAI, vous acceptez :

1. USAGE PERSONNEL
2. RESPONSABILITÉ DU MOT DE PASSE
3. ANALYSES INDICATIVES
4. AUCUNE GARANTIE DE RÉSULTAT
5. MODIFICATIONS POSSIBLES

© 2026 JobPulseAI''');
  }

  void _showHelp(BuildContext context, AppState appState) {
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.7,
        builder: (_, scrollCtrl) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('❓ ${appState.t('help')}',
                  style: const TextStyle(
                      fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Expanded(
                child: ListView(
                  controller: scrollCtrl,
                  children: [
                    Card(
                      color: Colors.green.withValues(alpha: 0.15),
                      child: ListTile(
                        leading: const Icon(Icons.support_agent,
                            color: Colors.green),
                        title: Text(appState.t('contact_support'),
                            style: const TextStyle(
                                fontWeight: FontWeight.bold)),
                        subtitle: Text(appState.t('support_online')),
                        trailing: const Icon(Icons.arrow_forward_ios,
                            size: 16, color: Colors.green),
                        onTap: () {
                          Navigator.pop(ctx);
                          Navigator.pushNamed(context, '/support');
                        },
                      ),
                    ),
                    const SizedBox(height: 8),
                    const _FaqItem(
                      q: 'Comment analyser mon CV ?',
                      a: 'Onglet CV → Sélectionner un PDF → Analyser.',
                    ),
                    const _FaqItem(
                      q: 'Comment obtenir des recommandations ?',
                      a: 'Analyser le CV → Onglet Recos → Obtenir les recommandations.',
                    ),
                    const _FaqItem(
                      q: 'Comment prédire mon salaire ?',
                      a: 'Accueil → Prédiction Salaire → Remplir → Prédire.',
                    ),
                    const _FaqItem(
                      q: 'Comment ajouter un favori ?',
                      a: 'Onglet Recos → Cliquer sur ❤️.',
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showAbout(BuildContext context, AppState appState) {
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cardColor,
        title: const Row(
          children: [
            Icon(Icons.work_outline, color: Color(0xFF7C5CFF)),
            SizedBox(width: 8),
            Text('JobPulseAI'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Version 1.0.0'),
            SizedBox(height: 8),
            Text(
              'Plateforme intelligente d\'analyse du marché de l\'emploi propulsée par l\'IA.',
              style: TextStyle(fontSize: 13),
            ),
            SizedBox(height: 12),
            Text('© 2026 JobPulseAI',
                style: TextStyle(fontSize: 11, color: Colors.grey)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(appState.t('close')),
          ),
        ],
      ),
    );
  }

  void _showTextModal(BuildContext context,
      {required String title, required String content}) {
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.75,
        builder: (_, scrollCtrl) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: const TextStyle(
                      fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Expanded(
                child: SingleChildScrollView(
                  controller: scrollCtrl,
                  child: Text(content,
                      style: const TextStyle(fontSize: 14, height: 1.6)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _confirmLogout(BuildContext context, AppState appState) {
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cardColor,
        title: Text(appState.t('logout_question')),
        content: Text(appState.t('logout_message')),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(appState.t('cancel')),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await AuthService().logout();
              widget.onLogout();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
            child: Text(appState.t('logout')),
          ),
        ],
      ),
    );
  }

  void _confirmDelete(BuildContext context, AppState appState) {
    final cardColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF1E1E2E) : Colors.white;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cardColor,
        title: Row(
          children: [
            const Icon(Icons.warning, color: Colors.red),
            const SizedBox(width: 8),
            Text(appState.t('delete_question')),
          ],
        ),
        content: Text(appState.t('delete_message')),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(appState.t('cancel')),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _snack(context, '📧 Email envoyé à support@jobpulseai.com');
            },
            child: const Text('Contacter',
                style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}

// ============================================================
// FAQ
// ============================================================
class _FaqItem extends StatelessWidget {
  final String q;
  final String a;
  const _FaqItem({required this.q, required this.a});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: isDark ? const Color(0xFF252542) : Colors.grey.shade100,
      child: ExpansionTile(
        iconColor: const Color(0xFF7C5CFF),
        collapsedIconColor: Colors.grey,
        title: Text(q,
            style: const TextStyle(
                fontSize: 14, fontWeight: FontWeight.w600)),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Text(a,
                style: const TextStyle(
                    fontSize: 13, color: Colors.grey, height: 1.5)),
          ),
        ],
      ),
    );
  }
}