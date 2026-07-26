#!/bin/bash
# ds4 distributed inference — start workers only
# Coordinator: GPU0 (32GB) layers 0:9  — start manually
# Worker 1:   GPU1 (16GB) layers 10:21
# Worker 2:   GPU2 (16GB) layers 22:29
# Worker 3:   GPU3 (32GB) layers 30:output
#
# Usage:
#   ./start-ds4-workers.sh              # start all workers in background
#   ./start-ds4-workers.sh stop         # kill all ds4 processes

set -e

DS4_DIR="/home/paolo/ds4-main"
MODEL="/home/paolo/ds4-v100/ds4flash.gguf"
COORD_PORT=9000
LOG_DIR="/tmp/ds4-logs"

mkdir -p "$LOG_DIR"

stop_all() {
    echo "=== Stopping all ds4 processes ==="
    pkill -f "ds4.*role worker" 2>/dev/null || true
    pkill -f "ds4.*role coordinator" 2>/dev/null || true
    rm -f /tmp/ds4-worker*.lock /tmp/ds4-coordinator.lock /tmp/ds4.lock
    sleep 1
    echo "Done."
}

if [ "${1:-}" = "stop" ]; then
    stop_all
    exit 0
fi

stop_all

echo "=== Starting ds4 distributed workers ==="

# Worker 1 — GPU1 (16GB), layers 10:21
DS4_LOCK_FILE=/tmp/ds4-worker1.lock \
CUDA_VISIBLE_DEVICES=1 \
LD_LIBRARY_PATH="$DS4_DIR" \
nohup "$DS4_DIR/ds4" --role worker --layers 10:21 \
    --coordinator 127.0.0.1 $COORD_PORT \
    -m "$MODEL" > "$LOG_DIR/worker1.log" 2>&1 &
echo "  Worker 1 (GPU1, layers 10:21) pid=$!"

# Worker 2 — GPU2 (16GB), layers 22:29
DS4_LOCK_FILE=/tmp/ds4-worker2.lock \
CUDA_VISIBLE_DEVICES=2 \
LD_LIBRARY_PATH="$DS4_DIR" \
nohup "$DS4_DIR/ds4" --role worker --layers 22:29 \
    --coordinator 127.0.0.1 $COORD_PORT \
    -m "$MODEL" > "$LOG_DIR/worker2.log" 2>&1 &
echo "  Worker 2 (GPU2, layers 22:29) pid=$!"

# Worker 3 — GPU3 (32GB), layers 30:output
DS4_LOCK_FILE=/tmp/ds4-worker3.lock \
CUDA_VISIBLE_DEVICES=3 \
LD_LIBRARY_PATH="$DS4_DIR" \
nohup "$DS4_DIR/ds4" --role worker --layers 30:output \
    --coordinator 127.0.0.1 $COORD_PORT \
    -m "$MODEL" > "$LOG_DIR/worker3.log" 2>&1 &
echo "  Worker 3 (GPU3, layers 30:output) pid=$!"

echo ""
echo "=== Workers started, waiting for coordinator on port $COORD_PORT ==="
echo "  Start coordinator in another terminal:"
echo "    cd $DS4_DIR"
echo "    DS4_LOCK_FILE=/tmp/ds4-coordinator.lock \\"
echo "    CUDA_VISIBLE_DEVICES=0 \\"
echo "    LD_LIBRARY_PATH=$DS4_DIR \\"
echo "    $DS4_DIR/ds4 --role coordinator --layers 0:9 \\"
echo "        --listen 0.0.0.0 $COORD_PORT \\"
echo "        -m \"$MODEL\""
echo ""
echo "  Logs: $LOG_DIR/"
echo "  Stop: ./start-ds4-workers.sh stop"
