#!/bin/bash
# Wait for training to finish, then copy checkpoint to /workspace
LOG=/workspace/logs/spunet_baseline.log
PIDFILE=/tmp/spunet_training_pid

echo "[save_checkpoint] Waiting for PID 62563 to finish..."
wait 62563 2>/dev/null || true

# Extra check: wait until process is gone
while kill -0 62563 2>/dev/null; do
    sleep 10
done

echo "[save_checkpoint] Training finished! Copying checkpoint..."
mkdir -p /workspace/Pointcept/exp/spunet_baseline
cp -r /tmp/spunet_baseline/. /workspace/Pointcept/exp/spunet_baseline/
echo "[save_checkpoint] Done! Checkpoint saved to /workspace/Pointcept/exp/spunet_baseline/"

# Extract final mIoU from log
echo "[save_checkpoint] Final results:"
grep "Best.*mIoU\|Val result" $LOG | tail -10
