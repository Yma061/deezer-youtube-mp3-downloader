import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../theme/app_theme.dart';
import '../services/music_service.dart';
import '../services/sync_service.dart';

class SyncPage extends StatefulWidget {
  const SyncPage({super.key});

  @override
  State<SyncPage> createState() => _SyncPageState();
}

class _SyncPageState extends State<SyncPage> {
  final _sync       = SyncService();
  final _ipCtrl     = TextEditingController();

  bool   _searching = false;
  bool   _syncing   = false;
  String? _host;
  String? _error;

  List<RemotePlaylist> _remote   = [];
  Set<String>          _selected = {};

  int    _done    = 0;
  int    _total   = 0;
  String _current = '';
  int    _saved   = 0;

  @override
  void dispose() {
    _sync.cancel();
    _ipCtrl.dispose();
    super.dispose();
  }

  // ── Découverte ────────────────────────────────────────────────────────────

  Future<void> _discover() async {
    setState(() { _searching = true; _error = null; });
    final host = await _sync.discoverDesktop();
    if (!mounted) return;
    if (host != null) {
      await _connectTo(host);
    } else {
      setState(() { _searching = false; _error = 'Bureau non trouvé. Saisissez l\'IP manuellement.'; });
    }
  }

  Future<void> _connectManual() async {
    final ip = _ipCtrl.text.trim();
    if (ip.isEmpty) return;
    final host = ip.contains(':') ? ip : '$ip:8888';
    await _connectTo(host);
  }

  Future<void> _connectTo(String host) async {
    setState(() { _searching = true; _error = null; });
    try {
      final playlists = await _sync.fetchLibrary(host);
      if (!mounted) return;
      setState(() {
        _host      = host;
        _remote    = playlists;
        _selected  = {};
        _searching = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _searching = false; _error = 'Impossible de se connecter : $e'; });
    }
  }

  // ── Synchronisation ───────────────────────────────────────────────────────

  Future<void> _startSync() async {
    if (_host == null || _selected.isEmpty) return;
    final music = context.read<MusicService>();
    final toSync = _remote.where((p) => _selected.contains(p.name)).toList();

    setState(() {
      _syncing = true;
      _done    = 0;
      _total   = toSync.fold(0, (s, p) => s + p.tracks.length);
      _current = '';
      _saved   = 0;
      _error   = null;
    });

    int globalDone = 0;
    for (final playlist in toSync) {
      if (!mounted) return;
      await for (final event in _sync.syncPlaylist(
        host:     _host!,
        playlist: playlist,
        music:    music,
      )) {
        if (!mounted) return;
        if (event is SyncProgress) {
          setState(() { _current = event.current; _done = globalDone + event.done; });
        } else if (event is SyncDone) {
          globalDone += playlist.tracks.length;
          setState(() { _saved += event.saved; });
        } else if (event is SyncError) {
          setState(() { _error = event.message; });
        }
      }
    }

    if (mounted) setState(() { _syncing = false; });
  }

  void _stop() {
    _sync.cancel();
    setState(() { _syncing = false; });
  }

  // ── UI ────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final loc = context.watch<AppLocalizations>();
    final fg2 = Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: kAccentGreen,
        foregroundColor: Colors.white,
        title: const Text('Sync avec le bureau',
            style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Connexion ──────────────────────────────────────────────────
            _SectionCard(
              title: '1. Connecter au bureau',
              child: Column(
                children: [
                  ElevatedButton.icon(
                    onPressed: _searching || _syncing ? null : _discover,
                    icon: _searching
                        ? const SizedBox(width: 18, height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.wifi_find),
                    label: Text(_searching ? 'Recherche...' : 'Détecter automatiquement'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: kAccentGreen,
                      foregroundColor: Colors.white,
                      minimumSize: const Size.fromHeight(48),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(children: [
                    Expanded(
                      child: TextField(
                        controller: _ipCtrl,
                        keyboardType: TextInputType.url,
                        decoration: InputDecoration(
                          hintText: '192.168.1.x:8888',
                          hintStyle: TextStyle(color: fg2),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                          isDense: true,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    OutlinedButton(
                      onPressed: _searching || _syncing ? null : _connectManual,
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: kAccentGreen),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      ),
                      child: const Text('Connecter', style: TextStyle(color: kAccentGreen)),
                    ),
                  ]),
                  if (_host != null) ...[
                    const SizedBox(height: 10),
                    Row(children: [
                      const Icon(Icons.check_circle, color: kAccentGreen, size: 16),
                      const SizedBox(width: 6),
                      Text('Connecté : $_host',
                          style: const TextStyle(color: kAccentGreen, fontSize: 13)),
                    ]),
                  ],
                  if (_error != null) ...[
                    const SizedBox(height: 8),
                    Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 13)),
                  ],
                ],
              ),
            ),

            // ── Sélection des playlists ────────────────────────────────────
            if (_remote.isNotEmpty) ...[
              _SectionCard(
                title: '2. Choisir les playlists à synchroniser',
                child: Column(
                  children: _remote.map((pl) {
                    final sel = _selected.contains(pl.name);
                    return CheckboxListTile(
                      value: sel,
                      onChanged: _syncing ? null : (v) {
                        setState(() {
                          if (v == true) _selected.add(pl.name);
                          else _selected.remove(pl.name);
                        });
                      },
                      title: Text(pl.name, style: const TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: Text('${pl.tracks.length} titres',
                          style: TextStyle(fontSize: 12, color: fg2)),
                      activeColor: kAccentGreen,
                      contentPadding: EdgeInsets.zero,
                      dense: true,
                    );
                  }).toList(),
                ),
              ),

              // ── Boutons sync ───────────────────────────────────────────────
              Row(children: [
                Expanded(
                  child: SizedBox(
                    height: 50,
                    child: ElevatedButton(
                      onPressed: (_syncing || _selected.isEmpty) ? null : _startSync,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: kAccentGreen,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      child: _syncing
                          ? const SizedBox(width: 22, height: 22,
                              child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                          : const Text('Synchroniser'),
                    ),
                  ),
                ),
                if (_syncing) ...[
                  const SizedBox(width: 10),
                  SizedBox(
                    height: 50,
                    child: ElevatedButton.icon(
                      onPressed: _stop,
                      icon: const Icon(Icons.stop),
                      label: const Text('Stop'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                ],
              ]),

              // ── Progression ────────────────────────────────────────────────
              if (_syncing || _saved > 0) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (_syncing && _total > 0) ...[
                        Text('$_done / $_total',
                            style: const TextStyle(fontWeight: FontWeight.bold,
                                color: kAccentGreen, fontSize: 15)),
                        const SizedBox(height: 8),
                        LinearProgressIndicator(
                          value: _total > 0 ? _done / _total : 0,
                          color: kAccentGreen,
                          backgroundColor: kAccentGreen.withValues(alpha: 0.2),
                          minHeight: 8,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        if (_current.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(_current,
                              style: TextStyle(fontSize: 13, color: fg2),
                              overflow: TextOverflow.ellipsis),
                        ],
                      ],
                      if (!_syncing && _saved > 0)
                        Text('✅  $_saved titres synchronisés dans la bibliothèque',
                            style: const TextStyle(color: Colors.green, fontSize: 14)),
                    ],
                  ),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final Widget child;
  const _SectionCard({required this.title, required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }
}
