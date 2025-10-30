#!/bin/bash
# NLP Meme Services Management Script
# Manages ws_server and realtime_ca_detector as background processes

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

WS_SERVER_SCRIPT="ws_server.py"
CA_DETECTOR_SCRIPT="realtime_ca_detector.py"
WS_SERVER_LOG="ws_server.txt"
CA_DETECTOR_LOG="realtime_ca_detector.txt"
PID_DIR="$SCRIPT_DIR/.pids"
WS_SERVER_PID="$PID_DIR/ws_server.pid"
CA_DETECTOR_PID="$PID_DIR/ca_detector.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create PID directory if not exists
mkdir -p "$PID_DIR"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if process is running
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# Start ws_server
start_ws_server() {
    if is_running "$WS_SERVER_PID"; then
        print_warning "ws_server is already running (PID: $(cat $WS_SERVER_PID))"
        return 1
    fi
    
    print_info "Starting ws_server..."
    nohup python3 -u "$WS_SERVER_SCRIPT" \
        --host 0.0.0.0 \
        --port 8765 \
        --watch-file data/ws.json \
        > "$WS_SERVER_LOG" 2>&1 &
    
    local pid=$!
    echo $pid > "$WS_SERVER_PID"
    sleep 2
    
    if is_running "$WS_SERVER_PID"; then
        print_success "ws_server started successfully (PID: $pid)"
        print_info "Log file: $WS_SERVER_LOG"
        return 0
    else
        print_error "Failed to start ws_server"
        rm -f "$WS_SERVER_PID"
        return 1
    fi
}

# Start ca_detector
start_ca_detector() {
    if is_running "$CA_DETECTOR_PID"; then
        print_warning "realtime_ca_detector is already running (PID: $(cat $CA_DETECTOR_PID))"
        return 1
    fi
    
    print_info "Starting realtime_ca_detector..."
    nohup python3 -u "$CA_DETECTOR_SCRIPT" \
        --no-bert \
        --no-ai \
        --min-confidence 0.5 \
        --min-context 0.2 \
        --ping-interval 30 \
        --ping-timeout 10 \
        > "$CA_DETECTOR_LOG" 2>&1 &
    
    local pid=$!
    echo $pid > "$CA_DETECTOR_PID"
    sleep 2
    
    if is_running "$CA_DETECTOR_PID"; then
        print_success "realtime_ca_detector started successfully (PID: $pid)"
        print_info "Log file: $CA_DETECTOR_LOG"
        return 0
    else
        print_error "Failed to start realtime_ca_detector"
        rm -f "$CA_DETECTOR_PID"
        return 1
    fi
}

# Stop ws_server
stop_ws_server() {
    if ! is_running "$WS_SERVER_PID"; then
        print_warning "ws_server is not running"
        return 1
    fi
    
    local pid=$(cat "$WS_SERVER_PID")
    print_info "Stopping ws_server (PID: $pid)..."
    kill "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while is_running "$WS_SERVER_PID" && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if is_running "$WS_SERVER_PID"; then
        print_warning "Force killing ws_server..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    rm -f "$WS_SERVER_PID"
    print_success "ws_server stopped"
}

# Stop ca_detector
stop_ca_detector() {
    if ! is_running "$CA_DETECTOR_PID"; then
        print_warning "realtime_ca_detector is not running"
        return 1
    fi
    
    local pid=$(cat "$CA_DETECTOR_PID")
    print_info "Stopping realtime_ca_detector (PID: $pid)..."
    kill "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while is_running "$CA_DETECTOR_PID" && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if is_running "$CA_DETECTOR_PID"; then
        print_warning "Force killing realtime_ca_detector..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    rm -f "$CA_DETECTOR_PID"
    print_success "realtime_ca_detector stopped"
}

# Check status
status() {
    echo "=========================================="
    echo "Service Status"
    echo "=========================================="
    
    # ws_server status
    if is_running "$WS_SERVER_PID"; then
        local pid=$(cat "$WS_SERVER_PID")
        print_success "ws_server: RUNNING (PID: $pid)"
        echo "  Log: $WS_SERVER_LOG"
        echo "  Uptime: $(ps -p $pid -o etime= | xargs)"
    else
        print_error "ws_server: STOPPED"
    fi
    
    echo ""
    
    # ca_detector status
    if is_running "$CA_DETECTOR_PID"; then
        local pid=$(cat "$CA_DETECTOR_PID")
        print_success "realtime_ca_detector: RUNNING (PID: $pid)"
        echo "  Log: $CA_DETECTOR_LOG"
        echo "  Uptime: $(ps -p $pid -o etime= | xargs)"
    else
        print_error "realtime_ca_detector: STOPPED"
    fi
    
    echo "=========================================="
}

# Show logs
logs() {
    local service=$1
    local lines=${2:-20}
    
    case $service in
        ws|ws_server)
            if [ -f "$WS_SERVER_LOG" ]; then
                echo "=========================================="
                echo "ws_server logs (last $lines lines):"
                echo "=========================================="
                tail -n "$lines" "$WS_SERVER_LOG"
            else
                print_error "Log file not found: $WS_SERVER_LOG"
            fi
            ;;
        ca|ca_detector|realtime)
            if [ -f "$CA_DETECTOR_LOG" ]; then
                echo "=========================================="
                echo "realtime_ca_detector logs (last $lines lines):"
                echo "=========================================="
                tail -n "$lines" "$CA_DETECTOR_LOG"
            else
                print_error "Log file not found: $CA_DETECTOR_LOG"
            fi
            ;;
        all)
            logs ws "$lines"
            echo ""
            logs ca "$lines"
            ;;
        *)
            print_error "Unknown service: $service"
            print_info "Usage: $0 logs {ws|ca|all} [lines]"
            return 1
            ;;
    esac
}

# Follow logs
follow_logs() {
    local service=$1
    
    case $service in
        ws|ws_server)
            if [ -f "$WS_SERVER_LOG" ]; then
                print_info "Following ws_server logs (Ctrl+C to stop)..."
                tail -f "$WS_SERVER_LOG"
            else
                print_error "Log file not found: $WS_SERVER_LOG"
            fi
            ;;
        ca|ca_detector|realtime)
            if [ -f "$CA_DETECTOR_LOG" ]; then
                print_info "Following realtime_ca_detector logs (Ctrl+C to stop)..."
                tail -f "$CA_DETECTOR_LOG"
            else
                print_error "Log file not found: $CA_DETECTOR_LOG"
            fi
            ;;
        *)
            print_error "Unknown service: $service"
            print_info "Usage: $0 follow {ws|ca}"
            return 1
            ;;
    esac
}

# Main command handler
case "${1:-}" in
    start)
        echo "=========================================="
        echo "Starting NLP Meme Services"
        echo "=========================================="
        start_ws_server
        echo ""
        start_ca_detector
        echo ""
        status
        ;;
    
    stop)
        echo "=========================================="
        echo "Stopping NLP Meme Services"
        echo "=========================================="
        stop_ca_detector
        echo ""
        stop_ws_server
        echo ""
        status
        ;;
    
    restart)
        echo "=========================================="
        echo "Restarting NLP Meme Services"
        echo "=========================================="
        stop_ca_detector
        stop_ws_server
        sleep 2
        start_ws_server
        echo ""
        start_ca_detector
        echo ""
        status
        ;;
    
    status)
        status
        ;;
    
    logs)
        logs "${2:-all}" "${3:-20}"
        ;;
    
    follow)
        follow_logs "${2:-ws}"
        ;;
    
    start-ws)
        start_ws_server
        ;;
    
    start-ca)
        start_ca_detector
        ;;
    
    stop-ws)
        stop_ws_server
        ;;
    
    stop-ca)
        stop_ca_detector
        ;;
    
    *)
        echo "NLP Meme Services Management Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|follow} [options]"
        echo ""
        echo "Commands:"
        echo "  start         - Start all services"
        echo "  stop          - Stop all services"
        echo "  restart       - Restart all services"
        echo "  status        - Show service status"
        echo "  logs [service] [lines] - Show logs (service: ws|ca|all, default: all, lines: default 20)"
        echo "  follow [service] - Follow logs in real-time (service: ws|ca)"
        echo ""
        echo "Individual service commands:"
        echo "  start-ws      - Start ws_server only"
        echo "  start-ca      - Start ca_detector only"
        echo "  stop-ws       - Stop ws_server only"
        echo "  stop-ca       - Stop ca_detector only"
        echo ""
        echo "Examples:"
        echo "  $0 start              # Start all services"
        echo "  $0 status             # Check status"
        echo "  $0 logs ws 50         # Show last 50 lines of ws_server logs"
        echo "  $0 follow ca          # Follow ca_detector logs"
        echo ""
        exit 1
        ;;
esac
