#!/usr/bin/env bash
#
# Nail All-in-One Docker 管理脚本
# 用法: ./scripts/nail-docker.sh {build|run|stop|restart|status|logs|shell|clean|push}
#

set -euo pipefail

# ============================================
# 配置
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE_NAME="${NAIL_IMAGE:-nail-app}"
CONTAINER_NAME="${NAIL_CONTAINER:-nail-app}"
HOST_PORT="${NAIL_PORT:-80}"

# 数据卷
DATA_VOLUME="${NAIL_DATA_VOLUME:-nail_data}"
UPLOADS_VOLUME="${NAIL_UPLOADS_VOLUME:-nail_uploads}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }
title() { echo -e "${CYAN}$*${NC}"; }

# ============================================
# 辅助函数
# ============================================

check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        error "未检测到 Docker，请先安装 Docker："
        info "  macOS: brew install --cask docker"
        info "  Linux: https://docs.docker.com/engine/install/"
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        error "Docker 未启动，请先启动 Docker Desktop 或 Docker 服务"
        exit 1
    fi
}

is_running() {
    docker ps --filter "name=^${CONTAINER_NAME}$" --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"
}

container_exists() {
    docker ps -a --filter "name=^${CONTAINER_NAME}$" --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"
}

image_exists() {
    docker images --format '{{.Repository}}' 2>/dev/null | grep -q "^${IMAGE_NAME}$"
}

# 收集环境变量参数
collect_env_args() {
    local env_args=""

    # 从 backend/.env 文件读取（如果存在）
    if [ -f "$PROJECT_DIR/backend/.env" ]; then
        while IFS='=' read -r key value; do
            # 跳过注释和空行
            [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
            # 去除前后空格
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            # 去除引号
            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"
            [ -n "$key" ] && [ -n "$value" ] && env_args="$env_args -e $key=$value"
        done < "$PROJECT_DIR/backend/.env"
    fi

    # 环境变量覆盖（命令行设置的环境变量优先级更高）
    [ -n "${SECRET_KEY:-}" ] && env_args="$env_args -e SECRET_KEY=$SECRET_KEY"
    [ -n "${OPENAI_API_KEY:-}" ] && env_args="$env_args -e OPENAI_API_KEY=$OPENAI_API_KEY"
    [ -n "${GEMINI_API_KEY:-}" ] && env_args="$env_args -e GEMINI_API_KEY=$GEMINI_API_KEY"
    [ -n "${AI_PROVIDER:-}" ] && env_args="$env_args -e AI_PROVIDER=$AI_PROVIDER"
    [ -n "${DATABASE_URL:-}" ] && env_args="$env_args -e DATABASE_URL=$DATABASE_URL"

    echo "$env_args"
}

# ============================================
# 命令实现
# ============================================

do_build() {
    check_docker

    title "==============================="
    title "  构建 Nail All-in-One 镜像"
    title "==============================="

    local build_args=""

    # 可选：无缓存构建
    if [ "${1:-}" = "--no-cache" ]; then
        build_args="--no-cache"
        info "无缓存模式构建"
    fi

    info "镜像名称: $IMAGE_NAME"
    info "项目目录: $PROJECT_DIR"
    echo ""

    cd "$PROJECT_DIR"
    docker build $build_args -t "$IMAGE_NAME" .

    echo ""
    ok "镜像构建完成！"
    docker images "$IMAGE_NAME" --format "  大小: {{.Size}}  创建时间: {{.CreatedSince}}"
}

do_run() {
    check_docker

    if is_running; then
        warn "容器已在运行中: $CONTAINER_NAME"
        info "使用 './scripts/nail-docker.sh restart' 重启"
        return 0
    fi

    if ! image_exists; then
        warn "镜像不存在，先执行构建..."
        do_build
        echo ""
    fi

    # 如果旧容器存在但已停止，先删除
    if container_exists; then
        info "清理已停止的旧容器..."
        docker rm "$CONTAINER_NAME" >/dev/null
    fi

    title "==============================="
    title "  启动 Nail 容器"
    title "==============================="

    local env_args
    env_args=$(collect_env_args)

    info "容器名称: $CONTAINER_NAME"
    info "端口映射: $HOST_PORT -> 80"
    info "数据卷:   $DATA_VOLUME, $UPLOADS_VOLUME"
    echo ""

    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "${HOST_PORT}:80" \
        -v "${DATA_VOLUME}:/app/backend/data" \
        -v "${UPLOADS_VOLUME}:/app/backend/uploads" \
        --restart unless-stopped \
        $env_args \
        "$IMAGE_NAME"

    # 等待服务就绪
    info "等待服务启动..."
    local count=0
    local max_wait=30
    while [ $count -lt $max_wait ]; do
        if curl -sf "http://localhost:${HOST_PORT}/api/v1/health" >/dev/null 2>&1; then
            break
        fi
        sleep 1
        count=$((count + 1))
    done

    echo ""
    if [ $count -lt $max_wait ]; then
        ok "Nail 服务已启动！"
    else
        warn "服务启动中（健康检查暂未响应，可能仍在初始化）"
    fi

    echo ""
    info "访问地址:"
    info "  前端:     http://localhost:${HOST_PORT}"
    info "  API:      http://localhost:${HOST_PORT}/api/v1"
    info "  文档:     http://localhost:${HOST_PORT}/docs"
    info ""
    info "管理命令:"
    info "  查看日志: ./scripts/nail-docker.sh logs"
    info "  停止服务: ./scripts/nail-docker.sh stop"
    info "  进入容器: ./scripts/nail-docker.sh shell"
}

do_stop() {
    check_docker

    if ! is_running; then
        warn "容器未在运行"
        # 清理已停止的容器
        if container_exists; then
            docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
        fi
        return 0
    fi

    info "正在停止容器: $CONTAINER_NAME ..."
    docker stop "$CONTAINER_NAME" >/dev/null
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    ok "容器已停止"
}

do_restart() {
    do_stop
    sleep 1
    do_run
}

do_status() {
    check_docker

    title "==============================="
    title "  Nail Docker 状态"
    title "==============================="

    # 镜像
    if image_exists; then
        local image_info
        image_info=$(docker images "$IMAGE_NAME" --format "{{.Size}} ({{.CreatedSince}})")
        ok "镜像: $IMAGE_NAME - $image_info"
    else
        warn "镜像: $IMAGE_NAME - 未构建"
    fi

    # 容器
    if is_running; then
        local container_info
        container_info=$(docker ps --filter "name=^${CONTAINER_NAME}$" --format "运行 {{.RunningFor}} | 端口 {{.Ports}}")
        ok "容器: $CONTAINER_NAME - $container_info"

        # 健康检查
        if curl -sf "http://localhost:${HOST_PORT}/api/v1/health" >/dev/null 2>&1; then
            ok "健康检查: 正常"
        else
            warn "健康检查: 无响应"
        fi

        # 资源使用
        local stats
        stats=$(docker stats "$CONTAINER_NAME" --no-stream --format "CPU: {{.CPUPerc}} | 内存: {{.MemUsage}}" 2>/dev/null || echo "无法获取")
        info "资源使用: $stats"
    elif container_exists; then
        warn "容器: $CONTAINER_NAME - 已停止"
    else
        warn "容器: $CONTAINER_NAME - 不存在"
    fi

    # 数据卷
    echo ""
    info "数据卷:"
    for vol in "$DATA_VOLUME" "$UPLOADS_VOLUME"; do
        if docker volume inspect "$vol" >/dev/null 2>&1; then
            local mount
            mount=$(docker volume inspect "$vol" --format '{{.Mountpoint}}')
            ok "  $vol -> $mount"
        else
            warn "  $vol - 未创建"
        fi
    done
}

do_logs() {
    check_docker

    if ! container_exists; then
        error "容器不存在: $CONTAINER_NAME"
        exit 1
    fi

    local follow=""
    local tail_lines="100"

    # 解析参数
    while [ $# -gt 0 ]; do
        case "$1" in
            -f|--follow) follow="-f" ;;
            -n|--lines)  tail_lines="$2"; shift ;;
            --all)       tail_lines="all" ;;
            *)           ;;
        esac
        shift
    done

    if [ -n "$follow" ]; then
        info "显示实时日志 (Ctrl+C 退出)..."
        docker logs "$follow" --tail "$tail_lines" "$CONTAINER_NAME"
    else
        docker logs --tail "$tail_lines" "$CONTAINER_NAME"
    fi
}

do_shell() {
    check_docker

    if ! is_running; then
        error "容器未在运行: $CONTAINER_NAME"
        info "请先启动: ./scripts/nail-docker.sh run"
        exit 1
    fi

    info "进入容器 (exit 退出)..."
    docker exec -it "$CONTAINER_NAME" /bin/bash
}

do_clean() {
    check_docker

    title "==============================="
    title "  清理 Nail Docker 资源"
    title "==============================="

    # 停止并删除容器
    if is_running; then
        info "停止容器..."
        docker stop "$CONTAINER_NAME" >/dev/null
    fi
    if container_exists; then
        info "删除容器..."
        docker rm "$CONTAINER_NAME" >/dev/null
    fi

    # 删除镜像
    if image_exists; then
        info "删除镜像..."
        docker rmi "$IMAGE_NAME" >/dev/null
    fi

    ok "清理完成"

    # 提示数据卷
    echo ""
    warn "数据卷未删除（保留用户数据）："
    info "  $DATA_VOLUME (数据库)"
    info "  $UPLOADS_VOLUME (上传文件)"
    info ""
    info "如需删除数据卷："
    info "  docker volume rm $DATA_VOLUME $UPLOADS_VOLUME"
}

do_backup() {
    check_docker

    local backup_dir="${2:-$PROJECT_DIR/backups}"
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/nail_backup_${timestamp}.tar.gz"

    mkdir -p "$backup_dir"

    title "==============================="
    title "  备份 Nail 数据"
    title "==============================="

    info "备份目标: $backup_file"

    # 使用临时容器挂载数据卷进行备份
    docker run --rm \
        -v "${DATA_VOLUME}:/data/db:ro" \
        -v "${UPLOADS_VOLUME}:/data/uploads:ro" \
        -v "$backup_dir:/backup" \
        alpine:latest \
        tar czf "/backup/nail_backup_${timestamp}.tar.gz" -C /data .

    local size
    size=$(du -h "$backup_file" | cut -f1)
    ok "备份完成: $backup_file ($size)"
}

do_restore() {
    check_docker

    local backup_file="${2:-}"

    if [ -z "$backup_file" ]; then
        # 列出可用备份
        local backup_dir="$PROJECT_DIR/backups"
        if [ -d "$backup_dir" ] && ls "$backup_dir"/nail_backup_*.tar.gz >/dev/null 2>&1; then
            info "可用备份:"
            ls -lh "$backup_dir"/nail_backup_*.tar.gz | awk '{print "  " $NF " (" $5 ")"}'
            echo ""
            info "用法: ./scripts/nail-docker.sh restore <备份文件路径>"
        else
            error "未找到备份文件"
            info "用法: ./scripts/nail-docker.sh restore <备份文件路径>"
        fi
        exit 1
    fi

    if [ ! -f "$backup_file" ]; then
        error "备份文件不存在: $backup_file"
        exit 1
    fi

    title "==============================="
    title "  恢复 Nail 数据"
    title "==============================="

    if is_running; then
        warn "检测到容器正在运行，需要先停止"
        info "正在停止容器..."
        docker stop "$CONTAINER_NAME" >/dev/null
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi

    local backup_dir
    backup_dir="$(cd "$(dirname "$backup_file")" && pwd)"
    local backup_name
    backup_name="$(basename "$backup_file")"

    info "恢复文件: $backup_file"

    docker run --rm \
        -v "${DATA_VOLUME}:/data/db" \
        -v "${UPLOADS_VOLUME}:/data/uploads" \
        -v "$backup_dir:/backup:ro" \
        alpine:latest \
        sh -c "rm -rf /data/db/* /data/uploads/* && tar xzf /backup/$backup_name -C /data"

    ok "数据恢复完成"
    info "请重新启动: ./scripts/nail-docker.sh run"
}

do_help() {
    cat <<'USAGE'
Nail All-in-One Docker 管理脚本

用法:
  ./scripts/nail-docker.sh <命令> [选项]

基本命令:
  build [--no-cache]   构建 Docker 镜像
  run                  运行容器（自动构建镜像如不存在）
  stop                 停止并删除容器
  restart              重启容器
  status               查看 Docker 状态（镜像/容器/数据卷）

日志与调试:
  logs [-f] [-n 行数]  查看容器日志（-f 实时跟踪）
  shell                进入容器 bash

数据管理:
  backup [目录]        备份数据库和上传文件
  restore <文件>       从备份恢复数据
  clean                删除容器和镜像（保留数据卷）

环境变量:
  NAIL_IMAGE           镜像名称 (默认: nail-app)
  NAIL_CONTAINER       容器名称 (默认: nail-app)
  NAIL_PORT            宿主机端口 (默认: 80)
  NAIL_DATA_VOLUME     数据库卷名 (默认: nail_data)
  NAIL_UPLOADS_VOLUME  上传文件卷名 (默认: nail_uploads)
  SECRET_KEY           JWT 密钥
  OPENAI_API_KEY       OpenAI API 密钥
  AI_PROVIDER          AI 提供商 (默认: openai)

示例:
  ./scripts/nail-docker.sh build                   # 构建镜像
  ./scripts/nail-docker.sh run                     # 启动服务
  NAIL_PORT=8080 ./scripts/nail-docker.sh run      # 指定端口启动
  ./scripts/nail-docker.sh logs -f                 # 实时查看日志
  ./scripts/nail-docker.sh shell                   # 进入容器调试
  ./scripts/nail-docker.sh backup                  # 备份数据
  ./scripts/nail-docker.sh restore backups/xxx.tar.gz  # 恢复数据
  ./scripts/nail-docker.sh clean                   # 清理资源

快速开始:
  ./scripts/nail-docker.sh build && ./scripts/nail-docker.sh run
USAGE
}

# ============================================
# 入口
# ============================================

case "${1:-help}" in
    build)          do_build "${2:-}" ;;
    run)            do_run ;;
    stop)           do_stop ;;
    restart)        do_restart ;;
    status)         do_status ;;
    logs)           shift; do_logs "$@" ;;
    shell)          do_shell ;;
    clean)          do_clean ;;
    backup)         do_backup "$@" ;;
    restore)        do_restore "$@" ;;
    help|--help|-h) do_help ;;
    *)
        error "未知命令: $1"
        do_help
        exit 1
        ;;
esac
