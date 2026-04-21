import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'theme/app_theme.dart';
import 'theme/theme_provider.dart';
import 'l10n/app_localizations.dart';
import 'services/music_service.dart';
import 'pages/onboarding_page.dart';
import 'pages/library_page.dart';
import 'widgets/mini_player.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => AppLocalizations()),
        ChangeNotifierProvider(create: (_) => MusicService()),
      ],
      child: const PlaylistManagerApp(),
    ),
  );
}

class PlaylistManagerApp extends StatelessWidget {
  const PlaylistManagerApp({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.watch<ThemeProvider>();
    return MaterialApp(
      title: 'Playlist Manager',
      debugShowCheckedModeBanner: false,
      theme:     lightTheme(),
      darkTheme: darkTheme(),
      themeMode: theme.themeMode,
      home: const _Startup(),
    );
  }
}

class _Startup extends StatefulWidget {
  const _Startup();
  @override
  State<_Startup> createState() => _StartupState();
}

class _StartupState extends State<_Startup> {
  bool? _onboardingDone;

  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() => _onboardingDone = prefs.getBool('onboarding_done') ?? false);
  }

  @override
  Widget build(BuildContext context) {
    if (_onboardingDone == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (!_onboardingDone!) {
      return OnboardingPage(onDone: () => setState(() => _onboardingDone = true));
    }
    return const _AppShell();
  }
}

class _AppShell extends StatelessWidget {
  const _AppShell();
  @override
  Widget build(BuildContext context) => const Scaffold(
        body: LibraryPage(),
        bottomNavigationBar: MiniPlayer(),
      );
}
