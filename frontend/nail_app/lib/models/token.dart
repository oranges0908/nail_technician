import 'package:json_annotation/json_annotation.dart';

part 'token.g.dart';

/// Token data model
/// Corresponds to the backend Token Schema
@JsonSerializable()
class Token {
  @JsonKey(name: 'access_token')
  final String accessToken;

  @JsonKey(name: 'token_type')
  final String tokenType;

  @JsonKey(name: 'refresh_token')
  final String? refreshToken;

  Token({
    required this.accessToken,
    this.tokenType = 'bearer',
    this.refreshToken,
  });

  /// Create a Token object from JSON
  factory Token.fromJson(Map<String, dynamic> json) => _$TokenFromJson(json);

  /// Convert Token object to JSON
  Map<String, dynamic> toJson() => _$TokenToJson(this);

  @override
  String toString() {
    return 'Token(accessToken: ${accessToken.substring(0, 10)}..., tokenType: $tokenType)';
  }
}
