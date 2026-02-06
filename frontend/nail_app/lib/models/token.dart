import 'package:json_annotation/json_annotation.dart';

part 'token.g.dart';

/// Token 数据模型
/// 与后端 Token Schema 对应
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

  /// 从 JSON 创建 Token 对象
  factory Token.fromJson(Map<String, dynamic> json) => _$TokenFromJson(json);

  /// 将 Token 对象转换为 JSON
  Map<String, dynamic> toJson() => _$TokenToJson(this);

  @override
  String toString() {
    return 'Token(accessToken: ${accessToken.substring(0, 10)}..., tokenType: $tokenType)';
  }
}
