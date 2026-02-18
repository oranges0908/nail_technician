"""
速率限制器配置
用于防止暴力破解和 AI API 滥用
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# 基于客户端 IP 的速率限制
limiter = Limiter(key_func=get_remote_address)
