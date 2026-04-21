import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../theme/app_theme.dart';
import '../services/music_service.dart';

class LibraryDetailPage extends StatelessWidget {
  final Playlist playlist;
  const LibraryDetailPage({super.key, required this.playlist});

  @override
  Widget build(BuildContext context) {
    final loc   = context.watch<AppLocalizations>();
    final music = context.watch<MusicService>();
    final fg2   = Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: kAccentGreen,
        foregroundColor: Colors.white,
        title: Text(playlist.name,
            style: const TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.play_circle_outline, size: 28),
            tooltip: loc.t('library_play_all'),
            onPressed: () =>
                context.read<MusicService>().playPlaylist(playlist),
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.fromLTRB(0, 8, 0, 100),
        itemCount: playlist.tracks.length,
        itemBuilder: (context, i) {
          final track      = playlist.tracks[i];
          final isCurrent  = music.currentPlaylist?.name == playlist.name &&
              music.currentIndex == i;

          return ListTile(
            leading: CircleAvatar(
              backgroundColor:
                  kAccentGreen.withValues(alpha: isCurrent ? 1 : 0.1),
              child: isCurrent && music.isPlaying
                  ? const Icon(Icons.volume_up,
                      color: Colors.white, size: 18)
                  : Text('${i + 1}',
                      style: TextStyle(
                          fontSize: 13,
                          color: isCurrent ? Colors.white : kAccentGreen,
                          fontWeight: FontWeight.bold)),
            ),
            title: Text(
              track.name,
              style: TextStyle(
                fontWeight:
                    isCurrent ? FontWeight.bold : FontWeight.normal,
                color: isCurrent ? kAccentGreen : null,
              ),
              overflow: TextOverflow.ellipsis,
            ),
            trailing: isCurrent
                ? IconButton(
                    icon: Icon(
                      music.isPlaying ? Icons.pause : Icons.play_arrow,
                      color: kAccentGreen,
                    ),
                    onPressed: () =>
                        context.read<MusicService>().playPause(),
                  )
                : Icon(Icons.music_note_outlined,
                    color: fg2.withValues(alpha: 0.4)),
            onTap: () => context
                .read<MusicService>()
                .playPlaylist(playlist, index: i),
          );
        },
      ),
    );
  }
}
