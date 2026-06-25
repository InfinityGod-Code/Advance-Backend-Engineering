import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'api_endpoints.dart';

class SseEvent {
  final String event;
  final Map<String, dynamic> data;

  SseEvent({required this.event, required this.data});

  @override
  String toString() => 'SseEvent(event: $event, data: $data)';
}

class SseService {
  HttpClient? _client;
  StreamController<SseEvent>? _controller;
  bool _connected = false;
  bool _disposed = false;
  int _retryCount = 0;
  String _lineBuffer = '';
  static const int _maxRetries = 10;
  static const Duration _retryDelay = Duration(seconds: 3);

  Stream<SseEvent> get stream {
    _controller ??= StreamController<SseEvent>.broadcast();
    return _controller!.stream;
  }

  bool get isConnected => _connected;

  Future<void> connect() async {
    if (_connected || _disposed) return;
    _controller ??= StreamController<SseEvent>.broadcast();
    _lineBuffer = '';

    try {
      _client = HttpClient();
      final request = await _client!.getUrl(
        Uri.parse('${ApiEndpoints.baseUrl}/api/v1/events/stream'),
      );
      request.headers.set('Accept', 'text/event-stream');
      request.headers.set('Cache-Control', 'no-cache');
      request.headers.set('Connection', 'keep-alive');

      final response = await request.close();

      if (response.statusCode != 200) {
        throw HttpException(
          'SSE connection failed with status ${response.statusCode}',
        );
      }

      _connected = true;
      _retryCount = 0;

      String currentEvent = '';
      StringBuffer dataBuffer = StringBuffer();

      await for (final chunk in response.transform(utf8.decoder)) {
        if (_disposed) break;

        _lineBuffer += chunk;
        final lines = _lineBuffer.split('\n');
        _lineBuffer = lines.isNotEmpty ? lines.last : '';

        for (int i = 0; i < lines.length - 1; i++) {
          final line = lines[i];
          if (line.startsWith('event:')) {
            currentEvent = line.substring(6).trim();
          } else if (line.startsWith('data:')) {
            dataBuffer.write(line.substring(5).trim());
          } else if (line.isEmpty && currentEvent.isNotEmpty) {
            _emitEvent(currentEvent, dataBuffer.toString());
            currentEvent = '';
            dataBuffer = StringBuffer();
          }
        }
      }
    } catch (e) {
      _connected = false;
      _client?.close();
      _client = null;
      if (!_disposed) _scheduleReconnect(e);
      return;
    }

    _connected = false;
    _client?.close();
    _client = null;
    if (!_disposed) _scheduleReconnect(null);
  }

  void _emitEvent(String event, String dataStr) {
    try {
      final data = jsonDecode(dataStr) as Map<String, dynamic>;
      _controller?.add(SseEvent(event: event, data: data));
    } catch (_) {}
  }

  void _scheduleReconnect(Object? error) {
    if (_disposed || _retryCount >= _maxRetries) return;
    _retryCount++;
    Timer(_retryDelay, connect);
  }

  void disconnect() {
    _disposed = true;
    _connected = false;
    _client?.close();
    _client = null;
    _lineBuffer = '';
    _controller?.close();
    _controller = null;
  }
}
