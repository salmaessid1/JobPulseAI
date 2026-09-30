// lib/widgets/country_picker.dart
import 'package:flutter/material.dart';

class Country {
  final String flag;
  final String name;
  final String code; // Indicatif téléphonique

  const Country(this.flag, this.name, this.code);
}

const List<Country> countries = [
  Country('🇫🇷', 'France', '+33'),
  Country('🇹🇳', 'Tunisie', '+216'),
  Country('🇲🇦', 'Maroc', '+212'),
  Country('🇩🇿', 'Algérie', '+213'),
  Country('🇧🇪', 'Belgique', '+32'),
  Country('🇨🇭', 'Suisse', '+41'),
  Country('🇨🇦', 'Canada', '+1'),
  Country('🇺🇸', 'États-Unis', '+1'),
  Country('🇬🇧', 'Royaume-Uni', '+44'),
  Country('🇩🇪', 'Allemagne', '+49'),
  Country('🇪🇸', 'Espagne', '+34'),
  Country('🇮🇹', 'Italie', '+39'),
  Country('🇵🇹', 'Portugal', '+351'),
  Country('🇳🇱', 'Pays-Bas', '+31'),
  Country('🇸🇦', 'Arabie Saoudite', '+966'),
  Country('🇦🇪', 'Émirats Arabes Unis', '+971'),
  Country('🇪🇬', 'Égypte', '+20'),
  Country('🇸🇳', 'Sénégal', '+221'),
  Country('🇨🇮', 'Côte d\'Ivoire', '+225'),
  Country('🇨🇳', 'Chine', '+86'),
  Country('🇯🇵', 'Japon', '+81'),
  Country('🇧🇷', 'Brésil', '+55'),
  Country('🇦🇺', 'Australie', '+61'),
];

class CountryPicker extends StatelessWidget {
  final String selectedCode;
  final ValueChanged<Country> onChanged;

  const CountryPicker({
    super.key,
    required this.selectedCode,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final current = countries.firstWhere(
      (c) => c.code == selectedCode,
      orElse: () => countries.first,
    );

    return GestureDetector(
      onTap: () => _showPicker(context),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
        decoration: BoxDecoration(
          border: Border.all(
            color: Theme.of(context).brightness == Brightness.dark
                ? Colors.grey.shade700
                : Colors.grey.shade400,
          ),
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(4),
            bottomLeft: Radius.circular(4),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(current.flag, style: const TextStyle(fontSize: 22)),
            const SizedBox(width: 6),
            Text(
              current.code,
              style: const TextStyle(
                  fontSize: 15, fontWeight: FontWeight.w600),
            ),
            const SizedBox(width: 4),
            const Icon(Icons.arrow_drop_down, size: 20),
          ],
        ),
      ),
    );
  }

  void _showPicker(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: isDark ? const Color(0xFF1E1E2E) : Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        builder: (_, scrollCtrl) => Column(
          children: [
            const SizedBox(height: 12),
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade600,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Choisir un pays',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            const Divider(height: 1),
            Expanded(
              child: ListView.builder(
                controller: scrollCtrl,
                itemCount: countries.length,
                itemBuilder: (_, i) {
                  final c = countries[i];
                  final isSelected = c.code == selectedCode;
                  return ListTile(
                    leading: Text(c.flag,
                        style: const TextStyle(fontSize: 28)),
                    title: Text(c.name),
                    trailing: Text(
                      c.code,
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    selected: isSelected,
                    selectedTileColor:
                        const Color(0xFF7C5CFF).withValues(alpha: 0.15),
                    onTap: () {
                      onChanged(c);
                      Navigator.pop(context);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}