// lib/screens/personal_info_screen.dart
// ignore_for_file: use_build_context_synchronously

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import '../models/user_profile.dart';
import '../services/user_profile_service.dart';
import '../widgets/country_picker.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
class PersonalInfoScreen extends StatefulWidget {
  const PersonalInfoScreen({super.key});

  @override
  State<PersonalInfoScreen> createState() => _PersonalInfoScreenState();
}

class _PersonalInfoScreenState extends State<PersonalInfoScreen> {
  final _formKey = GlobalKey<FormState>();

  final _nameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _birthCtrl = TextEditingController();
  final _locationCtrl = TextEditingController();
  final _jobCtrl = TextEditingController();
  final _educationCtrl = TextEditingController();
  final _linkedinCtrl = TextEditingController();
  final _githubCtrl = TextEditingController();
  final _portfolioCtrl = TextEditingController();
  final _bioCtrl = TextEditingController();
  final _experienceCtrl = TextEditingController();

  String _phoneCountryCode = '+33';
  String _gender = 'Non spécifié';
  String _availability = 'Immédiate';
  List<String> _spokenLanguages = [];

  UserProfileData _profile = UserProfileData();
  bool _loading = true;
  bool _saving = false;
  bool _hasChanges = false;
  final bool _emailVerified = true;   
  DateTime? _lastSaveTime;

  final List<String> _genderOptions = [
    'Non spécifié',
    'Homme',
    'Femme',
    'Autre',
  ];
  final List<String> _availabilityOptions = [
    'Immédiate',
    'Dans 1 mois',
    'Dans 3 mois',
    'En poste actuellement',
  ];
  final List<String> _allLanguages = [
    'Français',
    'Anglais',
    'Arabe',
    'Espagnol',
    'Allemand',
    'Italien',
    'Chinois',
    'Portugais',
    'Russe',
  ];

  @override
  void initState() {
    super.initState();
    _load();

    // Écouteurs pour détecter les modifications
    for (final ctrl in [
      _nameCtrl,
      _emailCtrl,
      _phoneCtrl,
      _birthCtrl,
      _locationCtrl,
      _jobCtrl,
      _educationCtrl,
      _linkedinCtrl,
      _githubCtrl,
      _portfolioCtrl,
      _bioCtrl,
      _experienceCtrl,
    ]) {
      ctrl.addListener(_markChanged);
    }
  }

  void _markChanged() {
    if (!_hasChanges && mounted) {
      setState(() => _hasChanges = true);
    }
  }

  Future<void> _load() async {
    final p = await UserProfileService.load();
    if (!mounted) return;
    setState(() {
      _profile = p;
      _nameCtrl.text = p.fullName;
      _emailCtrl.text = p.email;
      _phoneCtrl.text = p.phone;
      _phoneCountryCode = p.phoneCountryCode;
      _birthCtrl.text = p.birthDate;
      _locationCtrl.text = p.location;
      _jobCtrl.text = p.jobTitle;
      _educationCtrl.text = p.education;
      _linkedinCtrl.text = p.linkedin;
      _githubCtrl.text = p.github;
      _portfolioCtrl.text = p.portfolio;
      _bioCtrl.text = p.bio;
      _experienceCtrl.text = p.experienceYears;
      _gender = p.gender;
      _availability = p.availability;
      _spokenLanguages = List<String>.from(p.spokenLanguages);
      _loading = false;
      _hasChanges = false;
    });
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 80,
      maxWidth: 500,
    );
    if (picked == null) return;
    setState(() {
      _profile.photoPath = picked.path;
      _hasChanges = true;
    });
  }

Future<void> _pickBirthDate() async {
  final initial = _birthCtrl.text.isNotEmpty
      ? DateTime.tryParse(_birthCtrl.text) ?? DateTime(2000)
      : DateTime(2000);

  // ✅ On n'impose pas de locale ici - l'app utilise celle du MaterialApp
  final picked = await showDatePicker(
    context: context,
    initialDate: initial,
    firstDate: DateTime(1950),
    lastDate: DateTime.now(),
    helpText: 'Date de naissance',
    cancelText: 'Annuler',
    confirmText: 'OK',
    fieldLabelText: 'Date',
    fieldHintText: 'JJ/MM/AAAA',
  );

  if (picked != null) {
    final f = '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
    setState(() {
      _birthCtrl.text = f;
      _hasChanges = true;
    });
  }
}

  /// Calcule l'âge depuis la date de naissance
  int? _calculateAge() {
    if (_birthCtrl.text.isEmpty) return null;
    final date = DateTime.tryParse(_birthCtrl.text);
    if (date == null) return null;
    final now = DateTime.now();
    int age = now.year - date.year;
    if (now.month < date.month ||
        (now.month == date.month && now.day < date.day)) {
      age--;
    }
    return age;
  }

  /// Calcule le taux de complétion en temps réel
  double _completionRate() {
    final fields = [
      _nameCtrl.text.trim().isNotEmpty,
      _emailCtrl.text.trim().isNotEmpty,
      _phoneCtrl.text.trim().isNotEmpty,
      _birthCtrl.text.trim().isNotEmpty,
      _locationCtrl.text.trim().isNotEmpty,
      _jobCtrl.text.trim().isNotEmpty,
      _educationCtrl.text.trim().isNotEmpty,
      _experienceCtrl.text.trim().isNotEmpty,
      _bioCtrl.text.trim().isNotEmpty,
      _spokenLanguages.isNotEmpty,
      _linkedinCtrl.text.trim().isNotEmpty ||
          _githubCtrl.text.trim().isNotEmpty ||
          _portfolioCtrl.text.trim().isNotEmpty,
      _profile.photoPath != null && _profile.photoPath!.isNotEmpty,
    ];
    final filled = fields.where((f) => f).length;
    return filled / fields.length;
  }

  Future<void> _save() async {
  if (!_formKey.currentState!.validate()) return;
  setState(() => _saving = true);

  _profile.fullName = _nameCtrl.text.trim();
  _profile.email = _emailCtrl.text.trim();
  _profile.phone = _phoneCtrl.text.trim();
  _profile.phoneCountryCode = _phoneCountryCode;
  _profile.birthDate = _birthCtrl.text.trim();
  _profile.location = _locationCtrl.text.trim();
  _profile.jobTitle = _jobCtrl.text.trim();
  _profile.education = _educationCtrl.text.trim();
  _profile.linkedin = _linkedinCtrl.text.trim();
  _profile.github = _githubCtrl.text.trim();
  _profile.portfolio = _portfolioCtrl.text.trim();
  _profile.bio = _bioCtrl.text.trim();
  _profile.experienceYears = _experienceCtrl.text.trim();
  _profile.gender = _gender;
  _profile.availability = _availability;
  _profile.spokenLanguages = _spokenLanguages;

  // 1) Sauvegarder dans UserProfileService
  await UserProfileService.save(_profile);

  // ✅ 2) Synchroniser avec le système legacy (display_name)
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString('display_name', _profile.fullName);

  // ✅ 3) Synchroniser avec le User object (AuthService)
  final userData = prefs.getString('user_data');
  if (userData != null) {
    try {
      final Map<String, dynamic> userMap = jsonDecode(userData);
      userMap['full_name'] = _profile.fullName;
      userMap['email'] = _profile.email;
      await prefs.setString('user_data', jsonEncode(userMap));
    } catch (_) {}
  }

  if (!mounted) return;
  setState(() {
    _saving = false;
    _hasChanges = false;
    _lastSaveTime = DateTime.now();
  });

  HapticFeedback.mediumImpact();
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: const Row(
        children: [
          Icon(Icons.check_circle, color: Colors.white),
          SizedBox(width: 8),
          Text('Profil enregistré'),
        ],
      ),
      backgroundColor: Colors.green.shade700,
      behavior: SnackBarBehavior.floating,
      duration: const Duration(seconds: 2),
    ),
  );

  // ✅ 4) Retourner un signal au ProfileScreen pour recharger
  Navigator.pop(context, true);
}

  Future<bool> _confirmExit() async {
    if (!_hasChanges) return true;
    final result = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning_amber, color: Colors.orange),
            SizedBox(width: 8),
            Text('Modifications non enregistrées'),
          ],
        ),
        content: const Text(
            'Voulez-vous quitter sans enregistrer vos modifications ?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Annuler'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Quitter', style: TextStyle(color: Colors.red)),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context, true);
              await _save();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF7C5CFF),
            ),
            child: const Text('Enregistrer'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  @override
  void dispose() {
    for (final ctrl in [
      _nameCtrl,
      _emailCtrl,
      _phoneCtrl,
      _birthCtrl,
      _locationCtrl,
      _jobCtrl,
      _educationCtrl,
      _linkedinCtrl,
      _githubCtrl,
      _portfolioCtrl,
      _bioCtrl,
      _experienceCtrl,
    ]) {
      ctrl.dispose();
    }
    super.dispose();
  }

  // ============================================================
  // BUILD
  // ============================================================
  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0A0A15) : Colors.grey.shade100;
    final cardColor = isDark ? const Color(0xFF1E1E2E) : Colors.white;
    final borderColor = isDark ? Colors.grey.shade800 : Colors.grey.shade300;
    final completion = _completionRate();

    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return PopScope(
      canPop: !_hasChanges,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        final ok = await _confirmExit();
        if (ok && mounted) Navigator.pop(context);
      },
      child: Scaffold(
        backgroundColor: bgColor,
        appBar: AppBar(
          title: const Text('Informations personnelles'),
          actions: [
            IconButton(
              icon: _saving
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Icon(
                      _hasChanges ? Icons.save : Icons.check,
                      color: _hasChanges ? const Color(0xFF7C5CFF) : null,
                    ),
              tooltip: 'Enregistrer',
              onPressed: _saving || !_hasChanges ? null : _save,
            ),
          ],
        ),
        body: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // ==========================================
              // CARTE PROFIL AVEC COMPLÉTION
              // ==========================================
              _buildProfileHeaderCard(completion, isDark, cardColor),
              const SizedBox(height: 24),

              // ==========================================
              // SECTION 1 : IDENTITÉ
              // ==========================================
              _buildSection(
                title: 'Identité',
                icon: Icons.badge_outlined,
                color: Colors.blue,
                cardColor: cardColor,
                borderColor: borderColor,
                children: [
                  _smartField(
                    controller: _nameCtrl,
                    label: 'Nom complet',
                    icon: Icons.person_outline,
                    hint: 'Jean Dupont',
                    required: true,
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) {
                        return 'Obligatoire';
                      }
                      if (v.trim().length < 2) return 'Trop court';
                      return null;
                    },
                  ),
                  _emailFieldWithBadge(),
                  _phoneField(),
                  _birthDateField(),
                  _dropdownField(
                    label: 'Genre',
                    icon: Icons.wc,
                    value: _gender,
                    items: _genderOptions,
                    onChanged: (v) => setState(() {
                      _gender = v!;
                      _hasChanges = true;
                    }),
                  ),
                  _smartField(
                    controller: _locationCtrl,
                    label: 'Localisation',
                    icon: Icons.location_on_outlined,
                    hint: 'Paris, France',
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // ==========================================
              // SECTION 2 : PROFESSIONNEL
              // ==========================================
              _buildSection(
                title: 'Profil professionnel',
                icon: Icons.work_outline,
                color: Colors.purple,
                cardColor: cardColor,
                borderColor: borderColor,
                children: [
                  _smartField(
                    controller: _jobCtrl,
                    label: 'Titre professionnel',
                    icon: Icons.business_center,
                    hint: 'Ex: Data Scientist',
                  ),
                  _smartField(
                    controller: _educationCtrl,
                    label: 'Niveau d\'études',
                    icon: Icons.school_outlined,
                    hint: 'Ex: Master en Data Science',
                  ),
                  _smartField(
                    controller: _experienceCtrl,
                    label: 'Années d\'expérience',
                    icon: Icons.timelapse,
                    hint: 'Ex: 3',
                    keyboard: TextInputType.number,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                  ),
                  _dropdownField(
                    label: 'Disponibilité',
                    icon: Icons.event_available,
                    value: _availability,
                    items: _availabilityOptions,
                    onChanged: (v) => setState(() {
                      _availability = v!;
                      _hasChanges = true;
                    }),
                  ),
                  _bioField(),
                ],
              ),
              const SizedBox(height: 20),

              // ==========================================
              // SECTION 3 : LANGUES
              // ==========================================
              _buildSection(
                title: 'Langues parlées',
                icon: Icons.language,
                color: Colors.teal,
                cardColor: cardColor,
                borderColor: borderColor,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _allLanguages.map((lang) {
                        final selected = _spokenLanguages.contains(lang);
                        return FilterChip(
                          label: Text(lang),
                          selected: selected,
                          selectedColor:
                              const Color(0xFF7C5CFF).withValues(alpha: 0.25),
                          checkmarkColor: const Color(0xFF7C5CFF),
                          onSelected: (v) {
                            setState(() {
                              if (v) {
                                _spokenLanguages.add(lang);
                              } else {
                                _spokenLanguages.remove(lang);
                              }
                              _hasChanges = true;
                            });
                          },
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // ==========================================
              // SECTION 4 : RÉSEAUX
              // ==========================================
              _buildSection(
                title: 'Réseaux & Portfolio',
                icon: Icons.link,
                color: Colors.orange,
                cardColor: cardColor,
                borderColor: borderColor,
                children: [
                  _urlField(
                    controller: _linkedinCtrl,
                    label: 'LinkedIn',
                    icon: Icons.work,
                    hint: 'https://linkedin.com/in/...',
                    regex: r'linkedin\.com',
                  ),
                  _urlField(
                    controller: _githubCtrl,
                    label: 'GitHub',
                    icon: Icons.code,
                    hint: 'https://github.com/...',
                    regex: r'github\.com',
                  ),
                  _urlField(
                    controller: _portfolioCtrl,
                    label: 'Portfolio',
                    icon: Icons.web,
                    hint: 'https://monsite.com',
                    regex: r'^https?://',
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // ==========================================
              // BOUTON ENREGISTRER
              // ==========================================
              SizedBox(
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: (_saving || !_hasChanges) ? null : _save,
                  icon: _saving
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2.5, color: Colors.white),
                        )
                      : const Icon(Icons.save),
                  label: Text(
                    _saving ? 'Enregistrement...' : 'Enregistrer les modifications',
                    style: const TextStyle(
                        fontSize: 15, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor:
                        _hasChanges ? const Color(0xFF7C5CFF) : Colors.grey,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                    elevation: _hasChanges ? 6 : 0,
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Info dernière sauvegarde
              if (_lastSaveTime != null)
                Center(
                  child: Text(
                    'Dernière sauvegarde : ${_lastSaveTime!.hour}:${_lastSaveTime!.minute.toString().padLeft(2, '0')}',
                    style: TextStyle(
                        fontSize: 11, color: Colors.grey.shade500),
                  ),
                ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  // ============================================================
  // CARTE PROFIL AVEC COMPLÉTION
  // ============================================================
  Widget _buildProfileHeaderCard(
      double completion, bool isDark, Color cardColor) {
    final percent = (completion * 100).round();
    final age = _calculateAge();
    final completionColor = percent < 40
        ? Colors.orange
        : percent < 80
            ? Colors.blue
            : Colors.green;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark
              ? [const Color(0xFF2A1E4E), const Color(0xFF1E1E2E)]
              : [const Color(0xFFEDE7FF), Colors.white],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
            color: const Color(0xFF7C5CFF).withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Photo
              Stack(
                children: [
                  CircleAvatar(
                    radius: 45,
                    backgroundColor: const Color(0xFF7C5CFF),
                    backgroundImage: _profile.photoPath != null &&
                            File(_profile.photoPath!).existsSync()
                        ? FileImage(File(_profile.photoPath!))
                        : null,
                    child: _profile.photoPath == null
                        ? Text(
                            _initials(_nameCtrl.text),
                            style: const TextStyle(
                                color: Colors.white,
                                fontSize: 28,
                                fontWeight: FontWeight.bold),
                          )
                        : null,
                  ),
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: GestureDetector(
                      onTap: _pickImage,
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: const BoxDecoration(
                          color: Color(0xFF7C5CFF),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.camera_alt,
                            color: Colors.white, size: 14),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _nameCtrl.text.isEmpty
                          ? 'Votre nom'
                          : _nameCtrl.text,
                      style: const TextStyle(
                          fontSize: 18, fontWeight: FontWeight.bold),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (_jobCtrl.text.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        _jobCtrl.text,
                        style: TextStyle(
                            fontSize: 13, color: Colors.grey.shade500),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    const SizedBox(height: 6),
                    if (age != null)
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFF7C5CFF)
                              .withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          '$age ans',
                          style: const TextStyle(
                              fontSize: 11,
                              color: Color(0xFF7C5CFF),
                              fontWeight: FontWeight.bold),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Barre de complétion
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.trending_up,
                      size: 16, color: Color(0xFF7C5CFF)),
                  const SizedBox(width: 6),
                  const Text(
                    'Complétion du profil',
                    style:
                        TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                  ),
                  const Spacer(),
                  Text(
                    '$percent%',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                      color: completionColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: LinearProgressIndicator(
                  value: completion,
                  minHeight: 8,
                  backgroundColor: isDark
                      ? Colors.grey.shade800
                      : Colors.grey.shade200,
                  valueColor:
                      AlwaysStoppedAnimation<Color>(completionColor),
                ),
              ),
              const SizedBox(height: 6),
              Text(
                percent < 40
                    ? '💡 Complétez votre profil pour de meilleures recommandations'
                    : percent < 80
                        ? '✨ Bon début ! Encore quelques infos...'
                        : '🎉 Profil presque complet !',
                style:
                    TextStyle(fontSize: 11, color: Colors.grey.shade500),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ============================================================
  // SECTION
  // ============================================================
  Widget _buildSection({
    required String title,
    required IconData icon,
    required Color color,
    required Color cardColor,
    required Color borderColor,
    required List<Widget> children,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 10),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 16),
              ),
              const SizedBox(width: 8),
              Text(
                title,
                style:
                    const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: cardColor,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: borderColor),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.03),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(children: children),
        ),
      ],
    );
  }

  // ============================================================
  // CHAMP INTELLIGENT (avec validation temps réel)
  // ============================================================
  Widget _smartField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    String? hint,
    bool required = false,
    TextInputType? keyboard,
    int maxLines = 1,
    List<TextInputFormatter>? inputFormatters,
    String? Function(String?)? validator,
  }) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboard,
        maxLines: maxLines,
        inputFormatters: inputFormatters,
        decoration: InputDecoration(
          labelText: required ? '$label *' : label,
          hintText: hint,
          prefixIcon: Icon(icon),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: Theme.of(context).brightness == Brightness.dark
                  ? Colors.grey.shade800
                  : Colors.grey.shade300,
            ),
          ),
        ),
        validator: validator ??
            (required
                ? (v) => (v == null || v.trim().isEmpty)
                    ? 'Ce champ est obligatoire'
                    : null
                : null),
      ),
    );
  }

  // ============================================================
  // CHAMP EMAIL AVEC BADGE VÉRIFIÉ
  // ============================================================
  Widget _emailFieldWithBadge() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: TextFormField(
        controller: _emailCtrl,
        keyboardType: TextInputType.emailAddress,
        decoration: InputDecoration(
          labelText: 'Email',
          prefixIcon: const Icon(Icons.email_outlined),
          suffixIcon: _emailVerified
              ? const Tooltip(
                  message: 'Email vérifié',
                  child: Icon(Icons.verified,
                      color: Colors.green, size: 20),
                )
              : IconButton(
                  icon: const Icon(Icons.warning_amber,
                      color: Colors.orange, size: 20),
                  onPressed: () {},
                  tooltip: 'Non vérifié',
                ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        validator: (v) {
          if (v == null || v.trim().isEmpty) return 'Email obligatoire';
          if (!RegExp(r'^[\w\.\-]+@([\w\-]+\.)+[\w\-]{2,4}$')
              .hasMatch(v.trim())) {
            return 'Email invalide';
          }
          return null;
        },
      ),
    );
  }

  // ============================================================
  // CHAMP TÉLÉPHONE AVEC SÉLECTEUR DE PAYS
  // ============================================================
  Widget _phoneField() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CountryPicker(
            selectedCode: _phoneCountryCode,
            onChanged: (c) => setState(() {
              _phoneCountryCode = c.code;
              _hasChanges = true;
            }),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: TextFormField(
              controller: _phoneCtrl,
              keyboardType: TextInputType.phone,
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[0-9 ]')),
              ],
              decoration: InputDecoration(
                labelText: 'Téléphone',
                hintText: '6 12 34 56 78',
                prefixIcon: const Icon(Icons.phone_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return null;
                final digits = v.replaceAll(RegExp(r'\D'), '');
                if (digits.length < 6 || digits.length > 15) {
                  return 'Numéro invalide';
                }
                return null;
              },
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================
  // CHAMP DATE DE NAISSANCE
  // ============================================================
  Widget _birthDateField() {
    final age = _calculateAge();
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: TextFormField(
        controller: _birthCtrl,
        readOnly: true,
        onTap: _pickBirthDate,
        decoration: InputDecoration(
          labelText: 'Date de naissance',
          prefixIcon: const Icon(Icons.cake_outlined),
          suffixIcon: age != null
              ? Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF7C5CFF).withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Center(
                    widthFactor: 1,
                    child: Text(
                      '$age ans',
                      style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF7C5CFF)),
                    ),
                  ),
                )
              : const Icon(Icons.edit_calendar_outlined),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  // ============================================================
  // CHAMP DROPDOWN
  // ============================================================
  Widget _dropdownField({
    required String label,
    required IconData icon,
    required String value,
    required List<String> items,
    required ValueChanged<String?> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: DropdownButtonFormField<String>(
        initialValue: value,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        items: items
            .map((e) => DropdownMenuItem(value: e, child: Text(e)))
            .toList(),
        onChanged: onChanged,
      ),
    );
  }

  // ============================================================
  // CHAMP URL INTELLIGENT
  // ============================================================
  Widget _urlField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    required String hint,
    required String regex,
  }) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: TextFormField(
        controller: controller,
        keyboardType: TextInputType.url,
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          prefixIcon: Icon(icon),
          suffixIcon: controller.text.isNotEmpty &&
                  RegExp(regex).hasMatch(controller.text)
              ? const Icon(Icons.check_circle,
                  color: Colors.green, size: 20)
              : null,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        validator: (v) {
          if (v == null || v.trim().isEmpty) return null;
          if (!RegExp(regex).hasMatch(v.trim())) {
            return 'Lien invalide';
          }
          return null;
        },
      ),
    );
  }

  // ============================================================
  // CHAMP BIO
  // ============================================================
  Widget _bioField() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
      child: TextFormField(
        controller: _bioCtrl,
        maxLines: 4,
        maxLength: 300,
        decoration: InputDecoration(
          labelText: 'Bio',
          hintText: 'Parlez-nous brièvement de vous...',
          prefixIcon: const Padding(
            padding: EdgeInsets.only(bottom: 60),
            child: Icon(Icons.description_outlined),
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          alignLabelWithHint: true,
        ),
      ),
    );
  }

  // ============================================================
  // INITIALES
  // ============================================================
  String _initials(String name) {
    if (name.isEmpty) return '?';
    final parts = name.trim().split(' ');
    if (parts.length == 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
}