import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import '../theme/app_theme.dart';

class OnboardingPage extends StatefulWidget {
  final VoidCallback onDone;
  const OnboardingPage({super.key, required this.onDone});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final _controller = PageController();
  int _page = 0;

  final _pages = const [
    _OnboardStep(
      icon: Icons.music_note,
      color: kAccentGreen,
      title: 'Bienvenue !',
      body: 'Playlist Manager te permet de télécharger tes playlists YouTube sur ordinateur et de les écouter hors-ligne sur ton téléphone.',
    ),
    _OnboardStep(
      icon: Icons.computer,
      color: kAccentBlue,
      title: 'Installe le serveur bureau',
      body: 'Télécharge et lance le serveur desktop sur ton PC ou Mac. Il s\'occupe de télécharger la musique depuis YouTube.',
      hasGithubButton: true,
    ),
    _OnboardStep(
      icon: Icons.wifi,
      color: Color(0xFF8b5cf6),
      title: 'Même réseau Wi-Fi',
      body: 'Connecte ton téléphone et ton ordinateur au même réseau Wi-Fi. Le serveur bureau doit être lancé.',
    ),
    _OnboardStep(
      icon: Icons.sync,
      color: kAccentGreen,
      title: 'Synchronise ta musique',
      body: 'Dans la bibliothèque, appuie sur "Sync bureau". L\'app détecte automatiquement ton PC et transfère les playlists.',
    ),
  ];

  Future<void> _finish() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboarding_done', true);
    widget.onDone();
  }

  void _next() {
    if (_page < _pages.length - 1) {
      _controller.nextPage(
          duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
    } else {
      _finish();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isLast = _page == _pages.length - 1;

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: _finish,
                child: Text('Passer',
                    style: TextStyle(color: Colors.grey.shade500, fontSize: 14)),
              ),
            ),
            Expanded(
              child: PageView.builder(
                controller: _controller,
                itemCount: _pages.length,
                onPageChanged: (i) => setState(() => _page = i),
                itemBuilder: (_, i) => _pages[i],
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                _pages.length,
                (i) => AnimatedContainer(
                  duration: const Duration(milliseconds: 250),
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  width: i == _page ? 20 : 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: i == _page ? kAccentGreen : Colors.grey.shade400,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _next,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: kAccentGreen,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14)),
                    textStyle: const TextStyle(
                        fontSize: 17, fontWeight: FontWeight.bold),
                  ),
                  child: Text(isLast ? 'C\'est parti !' : 'Suivant'),
                ),
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

class _OnboardStep extends StatelessWidget {
  final IconData icon;
  final Color    color;
  final String   title;
  final String   body;
  final bool     hasGithubButton;

  const _OnboardStep({
    required this.icon,
    required this.color,
    required this.title,
    required this.body,
    this.hasGithubButton = false,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, size: 52, color: color),
          ),
          const SizedBox(height: 32),
          Text(title,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          Text(body,
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontSize: 16, color: Colors.grey.shade600, height: 1.5)),
          if (hasGithubButton) ...[
            const SizedBox(height: 24),
            OutlinedButton.icon(
              onPressed: () => launchUrl(
                Uri.parse('https://github.com/Yma061/playlist_deezer'),
                mode: LaunchMode.externalApplication,
              ),
              icon: const Icon(Icons.open_in_new, size: 18),
              label: const Text('Télécharger sur GitHub'),
              style: OutlinedButton.styleFrom(
                foregroundColor: kAccentBlue,
                side: const BorderSide(color: kAccentBlue),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
