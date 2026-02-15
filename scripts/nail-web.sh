#!/usr/bin/env bash
#
# Nail Web 前端管理脚本
# 用法: ./scripts/nail-web.sh {build|serve|run|clean|help}
#

set -euo pipefail

# ============================================
# 配置
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend/nail_app"
BUILD_DIR="$FRONTEND_DIR/build/web"

API_BASE_URL="${API_BASE_URL:-http://localhost:8002/api/v1}"
SERVE_PORT="${SERVE_PORT:-9000}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ============================================
# 辅助函数
# ============================================

check_flutter() {
    if ! command -v flutter >/dev/null 2>&1; then
        error "未检测到 Flutter SDK，请先安装 Flutter："
        info ""
        info "  macOS:  brew install flutter"
        info "  其他:   https://docs.flutter.dev/get-started/install"
        info ""
        info "  安装完成后请确保 flutter 在 PATH 中"
        exit 1
    fi
    info "Flutter: $(flutter --version 2>&1 | head -1)"
}

# ============================================
# 命令实现
# ============================================

do_build() {
    check_flutter

    info "构建 Web 发布版本..."
    info "  API_BASE_URL: $API_BASE_URL"
    info "  输出目录: $BUILD_DIR"

    cd "$FRONTEND_DIR"

    flutter build web --release \
        --dart-define="API_BASE_URL=$API_BASE_URL"

    ok "Web 构建完成"
    info "构建产物: $BUILD_DIR"
}

do_serve() {
    if [ ! -d "$BUILD_DIR" ]; then
        error "构建产物不存在: $BUILD_DIR"
        info "请先运行: ./scripts/nail-web.sh build"
        exit 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        error "未检测到 python3，无法启动静态服务器"
        exit 1
    fi

    info "启动本地静态文件服务器..."
    info "  目录: $BUILD_DIR"
    info "  地址: http://localhost:$SERVE_PORT"
    info "  按 Ctrl+C 停止"

    cd "$BUILD_DIR"
    python3 -m http.server "$SERVE_PORT"
}

do_run() {
    check_flutter

    info "以开发模式在 Chrome 中运行..."
    info "  API_BASE_URL: $API_BASE_URL"

    cd "$FRONTEND_DIR"

    flutter run -d chrome \
        --dart-define="API_BASE_URL=$API_BASE_URL"
}

do_clean() {
    check_flutter

    info "清理构建产物..."

    cd "$FRONTEND_DIR"
    flutter clean

    ok "清理完成"
}

do_help() {
    cat <<'USAGE'
Nail Web 前端管理脚本

用法:
  ./scripts/nail-web.sh <命令>

命令:
  build       构建 Web 发布版本 (flutter build web --release)
  serve       启动本地静态服务器预览构建产物 (端口默认 9000)
  run         以开发模式在 Chrome 中运行 (支持热重载)
  clean       清理构建产物 (flutter clean)
  help        显示此帮助信息

环境变量:
  API_BASE_URL   后端 API 地址 (默认: http://localhost:8002/api/v1)
  SERVE_PORT     本地预览服务端口 (默认: 9000)

示例:
  ./scripts/nail-web.sh build                                    # 默认构建
  API_BASE_URL=https://api.example.com/api/v1 ./scripts/nail-web.sh build  # 指定后端地址
  ./scripts/nail-web.sh serve                                    # 预览构建结果
  ./scripts/nail-web.sh run                                      # 开发模式运行
USAGE
}

# ============================================
# 入口
# ============================================

case "${1:-help}" in
    build)  do_build ;;
    serve)  do_serve ;;
    run)    do_run ;;
    clean)  do_clean ;;
    help|--help|-h) do_help ;;
    *)
        error "未知命令: $1"
        do_help
        exit 1
        ;;
esac
