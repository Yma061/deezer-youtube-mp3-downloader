import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:multicast_dns/multicast_dns.dart';
import 'package:path_provider/path_provider.dart';
import 'music_service.dart';

class RemotePlaylist {
  final String name;
  final List<RemoteTrack> tracks;
  RemotePlaylist({required this.name, required this.tracks});
  factory RemotePlaylist.fromJson(Map<String, dynamic> j) => RemotePlaylist(
        name: j['name'] as String,
        tracks: (j['tracks'] as List)
            .map((t) => RemoteTrack.fromJson(t as Map<String, dynamic>))
            .toList(),
      );
}

class RemoteTrack {
  final String name;
  final String file;
  final int size;
  RemoteTrack({required this.name, required this.file, required this.size});
  factory RemoteTrack.fromJson(Map<String, dynamic> j) => RemoteTrack(
        name: j['name'] as String,
        file: j['file'] as String,
        size: j['size'] as int? ?? 0,
      );
}

class SyncProgress {
  final int done, total;
  final String current;
  const SyncProgress(this.done, this.total, this.current);
}

class SyncDone {
  final int saved;
  const SyncDone(this.saved);
}

class SyncError {
  final String message;
  const SyncError(this.message);
}

class SyncService {
  bool _cancelled = false;
  void cancel() => _cancelled = true;

  // ── Découverte mDNS ──────────────────────────────────────────────────────

  Future<String?> discoverDesktop({
    Duration timeout = const Duration(seconds: 5),
  }) async {
    final client = MDnsClient();
    try {
      await client.start();
      final found = StringBuffer();

      await for (final PtrResourceRecord ptr in client
          .lookup<PtrResourceRecord>(
            ResourceRecordQuery.serverPointer('_playlist._tcp'),
          )
          .timeout(timeout, onTimeout: (_) {})) {
        await for (final SrvResourceRecord srv in client
            .lookup<SrvResourceRecord>(
              ResourceRecordQuery.service(ptr.domainName),
            )
            .timeout(const Duration(seconds: 2), onTimeout: (_) {})) {
          await for (final IPAddressResourceRecord ip in client
              .lookup<IPAddressResourceRecord>(
                ResourceRecordQuery.addressIPv4(srv.target),
              )
              .timeout(const Duration(seconds: 2), onTimeout: (_) {})) {
            found.write('${ip.address.address}:${srv.port}');
            break;
          }
          if (found.isNotEmpty) break;
        }
        if (found.isNotEmpty) break;
      }

      return found.isEmpty ? null : found.toString();
    } catch (_) {
      return null;
    } finally {
      client.stop();
    }
  }

  // ── Bibliothèque distante ─────────────────────────────────────────────────

  Future<List<RemotePlaylist>> fetchLibrary(String host) async {
    final uri = Uri.parse('http://$host/api/library');
    final resp = await http.get(uri).timeout(const Duration(seconds: 10));
    if (resp.statusCode != 200) throw Exception('HTTP ${resp.statusCode}');
    final list = jsonDecode(resp.body) as List;
    return list
        .map((e) => RemotePlaylist.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ── Synchronisation ───────────────────────────────────────────────────────

  Stream<Object> syncPlaylist({
    required String host,
    required RemotePlaylist playlist,
    required MusicService music,
  }) async* {
    _cancelled = false;
    final tracks = playlist.tracks;
    final total  = tracks.length;
    int saved    = 0;

    yield SyncProgress(0, total, 'Démarrage...');

    for (int i = 0; i < tracks.length; i++) {
      if (_cancelled) break;
      final track = tracks[i];
      yield SyncProgress(i + 1, total, track.name);

      try {
        final uri = Uri.parse(
            'http://$host/music/${Uri.encodeComponent(playlist.name)}/${Uri.encodeComponent(track.file)}');
        final resp = await http.get(uri).timeout(const Duration(minutes: 5));
        if (resp.statusCode != 200) throw Exception('HTTP ${resp.statusCode}');

        final tmpDir  = await getTemporaryDirectory();
        final tmpPath = '${tmpDir.path}/${track.file}';
        await File(tmpPath).writeAsBytes(resp.bodyBytes);

        final path = await music.saveTrack(
          playlistName: playlist.name,
          fileName:     track.file,
          sourcePath:   tmpPath,
        );
        await music.addTrackToPlaylist(
          playlistName: playlist.name,
          trackName:    track.name,
          trackPath:    path,
        );
        saved++;
      } catch (e) {
        yield SyncProgress(i + 1, total, '⚠ Échec: ${track.name}');
      }
    }

    yield SyncDone(saved);
  }
}
