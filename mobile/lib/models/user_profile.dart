// lib/models/user_profile.dart
class UserProfileData {
  String fullName;
  String email;
  String phone;
  String phoneCountryCode; // ✅ NOUVEAU
  String birthDate;
  String location;
  String jobTitle;
  String education;
  String linkedin;
  String github;
  String portfolio;
  String bio;
  String experienceYears;
  String gender;
  String availability;
  List<String> spokenLanguages;
  String? photoPath;

  UserProfileData({
    this.fullName = '',
    this.email = '',
    this.phone = '',
    this.phoneCountryCode = '+33', // ✅ par défaut France
    this.birthDate = '',
    this.location = '',
    this.jobTitle = '',
    this.education = '',
    this.linkedin = '',
    this.github = '',
    this.portfolio = '',
    this.bio = '',
    this.experienceYears = '',
    this.gender = 'Non spécifié',
    this.availability = 'Immédiate',
    List<String>? spokenLanguages,
    this.photoPath,
  }) : spokenLanguages = spokenLanguages ?? [];

  Map<String, dynamic> toJson() => {
        'full_name': fullName,
        'email': email,
        'phone': phone,
        'phone_country_code': phoneCountryCode,
        'birth_date': birthDate,
        'location': location,
        'job_title': jobTitle,
        'education': education,
        'linkedin': linkedin,
        'github': github,
        'portfolio': portfolio,
        'bio': bio,
        'experience_years': experienceYears,
        'gender': gender,
        'availability': availability,
        'spoken_languages': spokenLanguages,
        'photo_path': photoPath,
      };

  factory UserProfileData.fromJson(Map<String, dynamic> json) {
    return UserProfileData(
      fullName: json['full_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      phoneCountryCode: json['phone_country_code'] ?? '+33',
      birthDate: json['birth_date'] ?? '',
      location: json['location'] ?? '',
      jobTitle: json['job_title'] ?? '',
      education: json['education'] ?? '',
      linkedin: json['linkedin'] ?? '',
      github: json['github'] ?? '',
      portfolio: json['portfolio'] ?? '',
      bio: json['bio'] ?? '',
      experienceYears: json['experience_years'] ?? '',
      gender: json['gender'] ?? 'Non spécifié',
      availability: json['availability'] ?? 'Immédiate',
      spokenLanguages:
          List<String>.from(json['spoken_languages'] ?? const []),
      photoPath: json['photo_path'],
    );
  }

  /// Calcule le pourcentage de complétion du profil
  double get completionRate {
    final fields = [
      fullName.isNotEmpty,
      email.isNotEmpty,
      phone.isNotEmpty,
      birthDate.isNotEmpty,
      location.isNotEmpty,
      jobTitle.isNotEmpty,
      education.isNotEmpty,
      experienceYears.isNotEmpty,
      bio.isNotEmpty,
      spokenLanguages.isNotEmpty,
      linkedin.isNotEmpty || github.isNotEmpty || portfolio.isNotEmpty,
      photoPath != null && photoPath!.isNotEmpty,
    ];
    final filled = fields.where((f) => f).length;
    return filled / fields.length;
  }
}