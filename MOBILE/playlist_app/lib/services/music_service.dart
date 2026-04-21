import 'dart:convert';
import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';

// ── Modèles ───────────────────────────────────────────────────────────────────

class Track {
  final String name;
  final String path;

  Track({required this.name, required this.path});

  Map<String, dynamic> toJson() => {'name': name, 'path': path};
  factory Track.fromJson(Map<String, dynamic> j) =>
      Track(name: j['name'] as String, path: j['path'] as String);
}

class Playlist {
  final String  name;
  final List<Track> tracks;

  Playlist({required this.name, required this.tracks});

  Map<String, dynamic> toJson() => {
    'name':   name,
    'tracks': tracks.map((t) => t.toJson()).toList(),
  };
  factory Playlist.fromJson(Map<String, dynamic> j) => Playlist(
    name:   j['name'] as String,
    tracks: (j['tracks'] as List)
        .map((t) => Track.fromJson(t as Map<String, dynamic>))
        .toList(),
  );
}

// ── Service ───────────────────────────────────────────────────────────────────

class MusicService extends ChangeNotifier {
  final _player = AudioPlayer();

  List<Playlist> _playlists = [];
  Playlist?      _currentPlaylist;
  int            _currentIndex = 0;
  bool           _isPlaying    = false;
  Duration       _position     = Duration.zero;
  Duration       _duration     = Duration.zero;

  List<Playlist> get playlists       => _playlists;
  Playlist?      get currentPlaylist => _currentPlaylist;
  int            get currentIndex    => _currentIndex;
  bool           get isPlaying       => _isPlaying;
  Duration       get position        => _position;
  Duration       get duration        => _duration;
  Track?         get currentTrack    =>
      (_currentPlaylist != null && _currentPlaylist!.tracks.isNotEmpty)
          ? _currentPlaylist!.tracks[_currentIndex]
          : null;

  MusicService() {
    _init();
  }

  Future<void> _init() async {
    await _loadPlaylists();
    _player.onPositionChanged.listen((p) {
      _position = p;
      notifyListeners();
    });
    _player.onDurationChanged.listen((d) {
      _duration = d;
      notifyListeners();
    });
    _player.onPlayerComplete.listen((_) => playNext());
    _player.onPlayerStateChanged.listen((s) {
      _isPlaying = s == PlayerState.playing;
      notifyListeners();
    });
  }

  // ── Stockage ─────────────────────────────────────────────────────────────

  Future<Directory> get _musicDir async {
    final docs = await getApplicationDocumentsDirectory();
    final dir  = Directory('${docs.path}/music');
    if (!await dir.exists()) await dir.create(recursive: true);
    return dir;
  }

  Future<File> get _metaFile async {
    final dir = await _musicDir;
    return File('${dir.path}/playlists.json');
  }

  Future<void> _loadPlaylists() async {
    try {
      final f = await _metaFile;
      if (await f.exists()) {
        final raw = await f.readAsString();
        final list = jsonDecode(raw) as List;
        _playlists = list
            .map((e) => Playlist.fromJson(e as Map<String, dynamic>))
            .toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> _savePlaylists() async {
    final f = await _metaFile;
    await f.writeAsString(
        jsonEncode(_playlists.map((p) => p.toJson()).toList()));
  }

  // Déplace un fichier temporaire vers le dossier de la playlist, retourne le chemin final
  Future<String> saveTrack({
    required String playlistName,
    required String fileName,
    required String sourcePath,
  }) async {
    final dir    = await _musicDir;
    final plDir  = Directory('${dir.path}/$playlistName');
    if (!await plDir.exists()) await plDir.create(recursive: true);
    final destPath = '${plDir.path}/$fileName';
    await File(sourcePath).rename(destPath).catchError((_) async {
      // rename échoue si on change de partition (ex: tmpfs → data)
      await File(sourcePath).copy(destPath);
      await File(sourcePath).delete();
      return File(destPath);
    });
    return destPath;
  }

  // Ajoute ou met à jour une playlist avec les tracks téléchargés
  Future<void> addTrackToPlaylist({
    required String playlistName,
    required String trackName,
    required String trackPath,
  }) async {
    final idx = _playlists.indexWhere((p) => p.name == playlistName);
    if (idx == -1) {
      _playlists.add(Playlist(
        name:   playlistName,
        tracks: [Track(name: trackName, path: trackPath)],
      ));
    } else {
      final existing = _playlists[idx].tracks;
      if (!existing.any((t) => t.path == trackPath)) {
        existing.add(Track(name: trackName, path: trackPath));
      }
    }
    await _savePlaylists();
    notifyListeners();
  }

  Future<void> deletePlaylist(String name) async {
    _playlists.removeWhere((p) => p.name == name);
    final dir   = await _musicDir;
    final plDir = Directory('${dir.path}/$name');
    if (await plDir.exists()) await plDir.delete(recursive: true);
    await _savePlaylists();
    if (_currentPlaylist?.name == name) {
      await _player.stop();
      _currentPlaylist = null;
    }
    notifyListeners();
  }

  // ── Lecture ───────────────────────────────────────────────────────────────

  Future<void> playPlaylist(Playlist playlist, {int index = 0}) async {
    _currentPlaylist = playlist;
    _currentIndex    = index;
    await _playCurrentTrack();
  }

  Future<void> _playCurrentTrack() async {
    final track = currentTrack;
    if (track == null) return;
    final f = File(track.path);
    final exists = await f.exists();
    final size   = exists ? await f.length() : 0;
    print('[PLAY] path: ${track.path}');
    print('[PLAY] exists: $exists, size: $size bytes');
    // Utilise file:// URI pour éviter les problèmes avec DeviceFileSource sur Android 9
    await _player.play(UrlSource('file://${track.path}'));
  }

  Future<void> playPause() async {
    if (_isPlaying) {
      await _player.pause();
    } else if (currentTrack != null) {
      if (_position == Duration.zero) {
        await _playCurrentTrack();
      } else {
        await _player.resume();
      }
    }
  }

  Future<void> playNext() async {
    if (_currentPlaylist == null) return;
    if (_currentIndex < _currentPlaylist!.tracks.length - 1) {
      _currentIndex++;
      await _playCurrentTrack();
    } else {
      _currentIndex = 0;
      await _player.stop();
      _isPlaying = false;
      notifyListeners();
    }
  }

  Future<void> playPrev() async {
    if (_currentPlaylist == null) return;
    if (_position.inSeconds > 3) {
      await _player.seek(Duration.zero);
    } else if (_currentIndex > 0) {
      _currentIndex--;
      await _playCurrentTrack();
    }
  }

  Future<void> seekTo(Duration position) async {
    await _player.seek(position);
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }
}
