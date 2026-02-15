#!/usr/bin/env bash
#
# Nail 服务管理脚本
# 用法: ./scripts/nail-service.sh {start|stop|restart|status|logs|init-db|test|docker-start|docker-stop|docker-logs}
#

set -euo pipefail

# ============================================
# 配置
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
PID_FILE="$BACKEND_DIR/.pid"
LOG_DIR="$BACKEND_DIR/logs"
LOG_FILE="$LOG_DIR/app.log"

HOST="${NAIL_HOST:-0.0.0.0}"
PORT="${NAIL_PORT:-8002}"

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

check_conda() {
    # 1. 检查 conda 是否已安装
    if ! command -v conda >/dev/null 2>&1; then
        error "未检测到 conda，请先安装 conda："
        info ""
        info "  推荐安装 Miniconda（轻量版）："
        info "    macOS:  brew install miniconda"
        info "    Linux:  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh"
        info ""
        info "  或安装 Anaconda（完整版）："
        info "    https://www.anaconda.com/download"
        info ""
        info "  安装完成后请重新打开终端，然后运行："
        info "    conda create -n nail python=3.11"
        info "    conda activate nail"
        exit 1
    fi

    # 2. 检查是否已激活 conda 环境
    if [ -z "${CONDA_DEFAULT_ENV:-}" ] || [ "${CONDA_DEFAULT_ENV:-}" = "base" ]; then
        warn "未激活项目 conda 环境（当前: ${CONDA_DEFAULT_ENV:-无}）"

        # 列出可用环境，查找是否有 nail 环境
        local nail_env=""
        if conda env list 2>/dev/null | grep -q "^nail "; then
            nail_env="nail"
        fi

        if [ -n "$nail_env" ]; then
            info "检测到 nail 环境，正在自动激活..."
            # 初始化 conda shell 函数（脚本中 conda activate 需要先 source）
            eval "$(conda shell.bash hook)"
            conda activate nail
            ok "已自动激活 conda 环境: nail"
        else
            warn "未找到 nail 环境，可用的 conda 环境："
            conda env list 2>/dev/null | grep -v "^#" | grep -v "^$" | while read -r line; do
                info "    $line"
            done
            info ""
            info "  建议创建专用环境："
            info "    conda create -n nail python=3.11"
            info "    conda activate nail"
            info "    pip install -r $BACKEND_DIR/requirements.txt"
            exit 1
        fi
    fi

    info "使用 conda 环境: $CONDA_DEFAULT_ENV"
}

check_env_file() {
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        warn ".env 文件不存在，正在从 .env.example 创建..."
        if [ -f "$BACKEND_DIR/.env.example" ]; then
            cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
            warn "已创建 .env 文件，请编辑 $BACKEND_DIR/.env 设置必要的配置项（如 OPENAI_API_KEY）"
        else
            error ".env.example 也不存在，请手动创建 .env 文件"
            exit 1
        fi
    fi
}

get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    fi
}

is_running() {
    local pid
    pid=$(get_pid)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    return 1
}

# ============================================
# 命令实现
# ============================================

do_start() {
    if is_running; then
        warn "服务已在运行中 (PID: $(get_pid))"
        return 0
    fi

    check_conda
    check_env_file

    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKEND_DIR/uploads"/{nails,inspirations,designs,actuals}

    info "启动 Nail 后端服务..."
    info "  地址: http://$HOST:$PORT"
    info "  日志: $LOG_FILE"

    cd "$BACKEND_DIR"

    nohup uvicorn app.main:app \
        --host "$HOST" \
        --port "$PORT" \
        >> "$LOG_FILE" 2>&1 < /dev/null &
    disown

    local pid=$!
    echo "$pid" > "$PID_FILE"

    # 等待服务启动
    sleep 2
    if is_running; then
        ok "服务已启动 (PID: $pid)"
        info "Swagger 文档: http://localhost:$PORT/docs"
    else
        error "服务启动失败，请查看日志: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

do_stop() {
    if ! is_running; then
        warn "服务未在运行"
        rm -f "$PID_FILE"
        return 0
    fi

    local pid
    pid=$(get_pid)
    info "正在停止服务 (PID: $pid)..."

    kill "$pid"

    # 等待进程退出，最多 10 秒
    local count=0
    while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done

    if kill -0 "$pid" 2>/dev/null; then
        warn "进程未响应，强制终止..."
        kill -9 "$pid" 2>/dev/null || true
    fi

    rm -f "$PID_FILE"
    ok "服务已停止"
}

do_restart() {
    do_stop
    sleep 1
    do_start
}

do_status() {
    echo "=============================="
    echo "  Nail 服务状态"
    echo "=============================="

    # 后端进程
    if is_running; then
        ok "后端服务: 运行中 (PID: $(get_pid))"
    else
        error "后端服务: 未运行"
    fi

    # 端口检查
    if lsof -i ":$PORT" >/dev/null 2>&1; then
        ok "端口 $PORT: 已占用"
    else
        warn "端口 $PORT: 空闲"
    fi

    # 数据库文件
    if [ -f "$BACKEND_DIR/nail.db" ]; then
        local db_size
        db_size=$(du -h "$BACKEND_DIR/nail.db" | cut -f1)
        ok "SQLite 数据库: $db_size"
    else
        warn "SQLite 数据库: 不存在（需要执行 init-db）"
    fi

    # .env 文件
    if [ -f "$BACKEND_DIR/.env" ]; then
        ok ".env 配置文件: 存在"
    else
        error ".env 配置文件: 缺失"
    fi

    # Conda 环境
    if [ -n "${CONDA_DEFAULT_ENV:-}" ]; then
        ok "Conda 环境: $CONDA_DEFAULT_ENV ($CONDA_PREFIX)"
    else
        warn "Conda 环境: 未激活"
    fi

    # 上传目录
    if [ -d "$BACKEND_DIR/uploads" ]; then
        local upload_count
        upload_count=$(find "$BACKEND_DIR/uploads" -type f 2>/dev/null | wc -l | tr -d ' ')
        ok "上传目录: $upload_count 个文件"
    else
        warn "上传目录: 不存在"
    fi

    # Redis
    if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
        ok "Redis: 可用"
    else
        warn "Redis: 不可用（非必须）"
    fi

    # Docker
    if command -v docker >/dev/null 2>&1 && docker-compose -f "$PROJECT_DIR/docker-compose.yml" ps --quiet 2>/dev/null | head -1 >/dev/null 2>&1; then
        local running
        running=$(docker-compose -f "$PROJECT_DIR/docker-compose.yml" ps --status running --quiet 2>/dev/null | wc -l | tr -d ' ')
        ok "Docker 容器: $running 个运行中"
    fi
}

do_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        warn "日志文件不存在: $LOG_FILE"
        exit 1
    fi
    info "显示实时日志 (Ctrl+C 退出)..."
    tail -f "$LOG_FILE"
}

do_init_db() {
    check_conda
    check_env_file

    info "初始化数据库..."
    cd "$BACKEND_DIR"

    alembic upgrade head

    mkdir -p "$BACKEND_DIR/uploads"/{nails,inspirations,designs,actuals}

    ok "数据库初始化完成"
}

do_test() {
    check_conda

    info "运行后端测试..."
    cd "$BACKEND_DIR"

    pytest "${@:2}"

    ok "测试完成"
}

do_docker_start() {
    info "启动 Docker 服务..."
    cd "$PROJECT_DIR"
    docker-compose up -d
    ok "Docker 服务已启动"
    info "后端 API: http://localhost:8000"
    info "Swagger 文档: http://localhost:8000/docs"
    docker-compose ps
}

do_docker_stop() {
    info "停止 Docker 服务..."
    cd "$PROJECT_DIR"
    docker-compose down
    ok "Docker 服务已停止"
}

do_docker_logs() {
    info "显示 Docker 日志 (Ctrl+C 退出)..."
    cd "$PROJECT_DIR"
    docker-compose logs -f "${@:2}"
}

do_web_build() {
    "$SCRIPT_DIR/nail-web.sh" build
}

do_web_serve() {
    "$SCRIPT_DIR/nail-web.sh" serve
}

do_web_run() {
    "$SCRIPT_DIR/nail-web.sh" run
}

do_help() {
    cat <<'USAGE'
Nail 服务管理脚本

用法:
  ./scripts/nail-service.sh <命令>

本地开发命令:
  start       启动后端服务（后台运行）
  stop        停止后端服务
  restart     重启后端服务
  status      查看服务和环境状态
  logs        查看实时日志
  init-db     初始化/迁移数据库
  test        运行 pytest 测试

Web 前端命令:
  web-build   构建 Web 发布版本
  web-serve   启动本地静态服务器预览构建产物
  web-run     以开发模式在 Chrome 中运行

Docker 命令:
  docker-start   启动 Docker 全栈服务 (PostgreSQL + Redis + Backend)
  docker-stop    停止 Docker 服务
  docker-logs    查看 Docker 服务日志

环境变量:
  NAIL_HOST      监听地址 (默认: 0.0.0.0)
  NAIL_PORT      监听端口 (默认: 8002)
  API_BASE_URL   前端 API 地址 (默认: http://localhost:8002/api/v1)
  SERVE_PORT     Web 预览端口 (默认: 9000)

示例:
  ./scripts/nail-service.sh start              # 启动服务
  ./scripts/nail-service.sh status             # 查看状态
  ./scripts/nail-service.sh test -k test_auth  # 运行特定测试
  ./scripts/nail-service.sh web-build          # 构建 Web 前端
  ./scripts/nail-service.sh web-run            # 开发模式运行 Web
  NAIL_PORT=9000 ./scripts/nail-service.sh start  # 指定端口启动
USAGE
}

# ============================================
# 入口
# ============================================

case "${1:-help}" in
    start)        do_start ;;
    stop)         do_stop ;;
    restart)      do_restart ;;
    status)       do_status ;;
    logs)         do_logs ;;
    init-db)      do_init_db ;;
    test)         do_test "$@" ;;
    web-build)    do_web_build ;;
    web-serve)    do_web_serve ;;
    web-run)      do_web_run ;;
    docker-start) do_docker_start ;;
    docker-stop)  do_docker_stop ;;
    docker-logs)  do_docker_logs "$@" ;;
    help|--help|-h) do_help ;;
    *)
        error "未知命令: $1"
        do_help
        exit 1
        ;;
esac
