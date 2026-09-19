// lib/models/job_models.dart
class SkillResult {
  final List<String> skills;
  final Map<String, List<String>> categorized;

  SkillResult({required this.skills, required this.categorized});

  factory SkillResult.fromJson(Map<String, dynamic> json) {
    return SkillResult(
      skills: List<String>.from(json['skills'] ?? []),
      categorized: Map.from(json['categorized'] ?? {}).map(
        (k, v) => MapEntry(k, List<String>.from(v)),
      ),
    );
  }
}

// lib/models/job_models.dart
class Profile {
  final String name;
  final List<String> skills;
  final List<String> domains;
  final String seniority;
  final Map<String, List<String>> categorizedSkills;

  Profile({
    required this.name,
    required this.skills,
    required this.domains,
    required this.seniority,
    required this.categorizedSkills,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      name: json['name'] ?? 'Inconnu',
      skills: List<String>.from(json['skills'] ?? []),
      domains: List<String>.from(json['domains'] ?? []),
      seniority: json['seniority'] ?? 'Non défini',
      categorizedSkills: Map.from(json['categorized_skills'] ?? {}).map(
        (k, v) => MapEntry(k, List<String>.from(v)),
      ),
    );
  }
}


class MatchResult {
  final double score;
  final List<String> commonSkills;
  final List<String> missingSkills;

  MatchResult({
    required this.score,
    required this.commonSkills,
    required this.missingSkills,
  });

  factory MatchResult.fromJson(Map<String, dynamic> json) {
    return MatchResult(
      score: (json['score'] ?? 0).toDouble(),
      commonSkills: List<String>.from(json['common_skills'] ?? []),
      missingSkills: List<String>.from(json['missing_skills'] ?? []),
    );
  }
}

class JobRecommendation {
  final String jobId;
  final String title;
  final String company;
  final String location;
  final double score;
  final List<String> commonSkills;
  final List<String> missingSkills;

  JobRecommendation({
    required this.jobId,
    required this.title,
    required this.company,
    required this.location,
    required this.score,
    required this.commonSkills,
    required this.missingSkills,
  });

  factory JobRecommendation.fromJson(Map<String, dynamic> json) {
    return JobRecommendation(
      jobId: json['job_id']?.toString() ?? '',
      title: json['title'] ?? 'Offre inconnue',
      company: json['company'] ?? 'Entreprise inconnue',
      location: json['location'] ?? 'Localisation non spécifiée',
      score: (json['score'] ?? 0).toDouble(),
      commonSkills: List<String>.from(json['common_skills'] ?? []),
      missingSkills: List<String>.from(json['missing_skills'] ?? []),
    );
  }
}

class SalaryPrediction {
  final double predictedSalary;
  final double minRange;
  final double maxRange;

  SalaryPrediction({
    required this.predictedSalary,
    required this.minRange,
    required this.maxRange,
  });

  factory SalaryPrediction.fromJson(Map<String, dynamic> json) {
    return SalaryPrediction(
      predictedSalary: (json['predicted_salary'] ?? 0).toDouble(),
      minRange: (json['min_range'] ?? 0).toDouble(),
      maxRange: (json['max_range'] ?? 0).toDouble(),
    );
  }
}