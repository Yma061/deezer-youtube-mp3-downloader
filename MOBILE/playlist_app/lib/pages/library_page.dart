import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../theme/app_theme.dart';
import '../theme/theme_provider.dart';
import '../services/music_service.dart';
import 'library_detail_page.dart';
import 'sync_page.dart';

class LibraryPage extends StatelessWidget {
  const LibraryPage({super.key});

  @override
  Widget build(BuildContext context) {
    final loc      = context.watch<AppLocalizations>();
    final theme    = context.watch<ThemeProvider>();
    final music    = context.watch<MusicService>();
    final fg2      = Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: kAccentGreen,
        foregroundColor: Colors.white,
        title: Text(loc.t('library_title'),
            style: const TextStyle(fontWeight: FontWeight.bold)),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: Icon(theme.isDark ? Icons.wb_sunny : Icons.nightlight_round),
            onPressed: theme.toggle,
          ),
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ElevatedButton(
              onPressed: loc.toggle,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: kAccentGreen,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20)),
                textStyle: const TextStyle(
                    fontSize: 13, fontWeight: FontWeight.bold),
              ),
              child: Text(loc.t('lang_btn')),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: kAccentGreen,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.download),
        label: const Text('Sync bureau'),
        onPressed: () => Navigator.push(context,
            MaterialPageRoute(builder: (_) => const SyncPage())),
      ),
      body: music.playlists.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.library_music_outlined,
                      size: 72, color: fg2.withValues(alpha: 0.4)),
                  const SizedBox(height: 16),
                  Text(loc.t('library_empty'),
                      style: TextStyle(fontSize: 16, color: fg2)),
                  const SizedBox(height: 8),
                  Text(loc.t('library_empty_hint'),
                      style: TextStyle(fontSize: 13, color: fg2),
                      textAlign: TextAlign.center),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
              itemCount: music.playlists.length,
              itemBuilder: (context, i) {
                final pl = music.playlists[i];
                final isCurrent = music.currentPlaylist?.name == pl.name;
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 8),
                    leading: CircleAvatar(
                      backgroundColor:
                          kAccentGreen.withValues(alpha: isCurrent ? 1 : 0.15),
                      child: Icon(Icons.queue_music,
                          color: isCurrent ? Colors.white : kAccentGreen),
                    ),
                    title: Text(pl.name,
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text(
                        '${pl.tracks.length} ${loc.t('library_tracks')}',
                        style: TextStyle(fontSize: 12, color: fg2)),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: Icon(
                            isCurrent && music.isPlaying
                                ? Icons.pause_circle
                                : Icons.play_circle,
                            color: kAccentGreen,
                            size: 36,
                          ),
                          onPressed: () {
                            if (isCurrent) {
                              context.read<MusicService>().playPause();
                            } else {
                              context
                                  .read<MusicService>()
                                  .playPlaylist(pl);
                            }
                          },
                        ),
                        IconButton(
                          icon: Icon(Icons.delete_outline,
                              color: fg2.withValues(alpha: 0.6)),
                          onPressed: () => _confirmDelete(context, loc, pl.name),
                        ),
                      ],
                    ),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) => LibraryDetailPage(playlist: pl)),
                    ),
                  ),
                );
              },
            ),
    );
  }

  void _confirmDelete(
      BuildContext context, AppLocalizations loc, String name) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(loc.t('library_delete_title')),
        content: Text(loc.t('library_delete_confirm').replaceAll('%s', name)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(loc.t('cancel')),
          ),
          TextButton(
            onPressed: () {
              context.read<MusicService>().deletePlaylist(name);
              Navigator.pop(context);
            },
            child: Text(loc.t('delete'),
                style: const TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
