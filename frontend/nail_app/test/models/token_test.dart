import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/token.dart';

void main() {
  group('Token', () {
    test('fromJson creates correct Token', () {
      final json = {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
        'token_type': 'bearer',
        'refresh_token': 'refresh_token_value',
      };
      final token = Token.fromJson(json);
      expect(token.accessToken, json['access_token']);
      expect(token.tokenType, 'bearer');
      expect(token.refreshToken, 'refresh_token_value');
    });

    test('toJson roundtrip', () {
      final json = {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
        'token_type': 'bearer',
        'refresh_token': null,
      };
      final t1 = Token.fromJson(json);
      final t2 = Token.fromJson(t1.toJson());
      expect(t2.accessToken, t1.accessToken);
      expect(t2.tokenType, t1.tokenType);
    });

    test('default tokenType is bearer', () {
      final json = {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
      };
      final token = Token.fromJson(json);
      expect(token.tokenType, 'bearer');
    });

    test('nullable refreshToken', () {
      final json = {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
        'token_type': 'bearer',
      };
      final token = Token.fromJson(json);
      expect(token.refreshToken, isNull);
    });

    test('toString masks access token', () {
      final json = {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
        'token_type': 'bearer',
      };
      final token = Token.fromJson(json);
      final str = token.toString();
      expect(str, contains('...'));
      expect(str, isNot(contains('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test')));
    });
  });
}
