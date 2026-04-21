import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/music_service.dart';
import '../theme/app_theme.dart';

class MiniPlayer extends StatelessWidget {
  const MiniPlayer({super.key});

  @override
  Widget build(BuildContext context) {
    final music = context.watch<MusicService>();

    if (music.currentTrack == null) return const SizedBox.shrink();

    final track    = music.currentTrack!;
    final progress = music.duration.inMilliseconds > 0
        ? music.position.inMilliseconds / music.duration.inMilliseconds
        : 0.0;

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 12,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Barre de progression
          LinearProgressIndicator(
            value: progress.clamp(0.0, 1.0),
            color: kAccentGreen,
            backgroundColor: kAccentGreen.withValues(alpha: 0.15),
            minHeight: 3,
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: [
                // Icône
                CircleAvatar(
                  backgroundColor: kAccentGreen.withValues(alpha: 0.15),
                  child: const Icon(Icons.music_note,
                      color: kAccentGreen, size: 20),
                ),
                const SizedBox(width: 12),

                // Titre + playlist
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        track.name,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 13),
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (music.currentPlaylist != null)
                        Text(
                          music.currentPlaylist!.name,
                          style: TextStyle(
                              fontSize: 11,
                              color: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.color),
                          overflow: TextOverflow.ellipsis,
                        ),
                    ],
                  ),
                ),

                // Contrôles
                IconButton(
                  icon: const Icon(Icons.skip_previous),
                  onPressed: () => context.read<MusicService>().playPrev(),
                  color: kAccentGreen,
                ),
                IconButton(
                  icon: Icon(
                    music.isPlaying ? Icons.pause_circle : Icons.play_circle,
                    size: 36,
                  ),
                  onPressed: () => context.read<MusicService>().playPause(),
                  color: kAccentGreen,
                ),
                IconButton(
                  icon: const Icon(Icons.skip_next),
                  onPressed: () => context.read<MusicService>().playNext(),
                  color: kAccentGreen,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
