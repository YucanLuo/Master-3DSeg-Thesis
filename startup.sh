#!/bin/bash
# RunPod startup script — runs in background on pod start
exec > >(tee -a /workspace/logs/startup.log) 2>&1
echo "=========================================="
echo "[startup] Begin: $(date)"

CONDA=/workspace/miniconda3/bin/conda
CONDA_ENV=thesis
POINTCEPT=/workspace/Pointcept
export DEBIAN_FRONTEND=noninteractive

# ── Step 1: System packages ────────────────────────────────────────────────
echo "[1/7] System packages..."
apt-get update -qq -o Acquire::Retries=3 || echo "  WARNING: apt-get update failed, continuing..."
apt-get install -y -qq build-essential cmake ninja-build \
    libopenblas-dev libsparsehash-dev git wget curl \
    || echo "  WARNING: some packages failed, continuing..."
echo "  Done."

# ── Step 2: Miniconda ─────────────────────────────────────────────────────
echo "[2/7] Miniconda..."
if [ -f "$CONDA" ]; then
    echo "  Already present, skipping."
else
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p /workspace/miniconda3
    rm /tmp/miniconda.sh
fi

# ── Step 3: Conda environment ─────────────────────────────────────────────
echo "[3/7] Conda environment '$CONDA_ENV'..."
if $CONDA env list | grep -q "^$CONDA_ENV "; then
    echo "  Already exists, skipping."
else
    $CONDA create -n $CONDA_ENV python=3.10 -y -q
fi

# ── Step 4: PyTorch ───────────────────────────────────────────────────────
echo "[4/7] PyTorch..."
if $CONDA run -n $CONDA_ENV python -c "import torch; assert torch.__version__.startswith('2.5')" 2>/dev/null; then
    echo "  Already installed, skipping."
else
    echo "  Installing PyTorch (this takes a few minutes)..."
    $CONDA run -n $CONDA_ENV pip install -q torch==2.5.0 torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cu124 || echo "  WARNING: PyTorch install failed"
    $CONDA run -n $CONDA_ENV pip install -q torch-geometric || true
    $CONDA run -n $CONDA_ENV pip install -q torch_scatter torch_sparse torch_cluster \
        -f https://data.pyg.org/whl/torch-2.5.0+cu124.html || true
fi

# ── Step 5: spconv ────────────────────────────────────────────────────────
echo "[5/7] spconv..."
if $CONDA run -n $CONDA_ENV python -c "import spconv" 2>/dev/null; then
    echo "  Already installed, skipping."
else
    $CONDA run -n $CONDA_ENV pip install -q spconv-cu124 || echo "  WARNING: spconv install failed"
fi

# ── Step 5.5: Pointcept dependencies ──────────────────────────────────────
echo "[5.5/7] Pointcept dependencies..."
if $CONDA run -n $CONDA_ENV python -c "import mmengine" 2>/dev/null; then
    echo "  mmengine already installed, skipping."
else
    $CONDA run -n $CONDA_ENV pip install -q mmengine SharedArray || true
fi
if $CONDA run -n $CONDA_ENV python -c "import flash_attn" 2>/dev/null; then
    echo "  flash_attn already installed, skipping."
else
    echo "  Installing flash-attn (10-20 min compile, please wait)..."
    $CONDA run -n $CONDA_ENV pip install -q flash-attn --no-build-isolation || \
        echo "  WARNING: flash-attn install failed, PTv3 may not work"
fi

# ── Step 6: Pointcept ─────────────────────────────────────────────────────
echo "[6/7] Pointcept..."
if [ -d "$POINTCEPT" ]; then
    echo "  Already present, skipping git pull to avoid conflicts."
else
    git clone -q https://github.com/Pointcept/Pointcept.git $POINTCEPT || \
        echo "  WARNING: git clone failed"
fi
if $CONDA run -n $CONDA_ENV python -c "import pointcept" 2>/dev/null; then
    echo "  pointcept already installed, skipping."
else
    $CONDA run -n $CONDA_ENV pip install -q -e $POINTCEPT || true
fi

if [ -d "$POINTCEPT/libs/pointops/build/lib.linux-x86_64-cpython-310" ]; then
    echo "  pointops already compiled, skipping."
else
    cd $POINTCEPT && $CONDA run -n $CONDA_ENV pip install -q libs/pointops || \
        echo "  WARNING: pointops compile failed"
fi

if ls $POINTCEPT/libs/pointgroup_ops/build/lib*/pointgroup_ops_cuda*.so 2>/dev/null | grep -q .; then
    echo "  pointgroup_ops already compiled, skipping."
else
    cd $POINTCEPT && $CONDA run -n $CONDA_ENV pip install -q libs/pointgroup_ops || \
        echo "  WARNING: pointgroup_ops compile failed"
fi

# ── Step 6.5: S3DIS cache ─────────────────────────────────────────────────
echo "[6.5/7] S3DIS local SSD cache..."
if [ -d "/tmp/s3dis/Area_6" ]; then
    echo "  Already cached in /tmp/s3dis, skipping."
elif [ -d "/workspace/data/s3dis" ]; then
    echo "  Copying S3DIS to /tmp/s3dis (8.5GB, ~5 min)..."
    cp -r /workspace/data/s3dis /tmp/s3dis && echo "  S3DIS cached." || \
        echo "  WARNING: S3DIS copy failed, using /workspace directly"
else
    echo "  S3DIS not found in /workspace/data/s3dis, skipping cache."
fi
if [ -d "/tmp/s3dis" ]; then
    ln -sfn /tmp/s3dis $POINTCEPT/data/s3dis
else
    ln -sfn /workspace/data/s3dis $POINTCEPT/data/s3dis
fi

# ── Step 7: Shell & PATH ──────────────────────────────────────────────────
echo "[7/7] Shell configuration..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1 || true
    apt-get install -y -qq nodejs > /dev/null 2>&1 || true
fi
if [ ! -f "/workspace/.npm-global/bin/claude" ]; then
    echo "  Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code --prefix /workspace/.npm-global > /dev/null 2>&1 || \
        echo "  WARNING: Claude Code install failed"
else
    echo "  Claude Code already installed, skipping."
fi

$CONDA init bash > /dev/null 2>&1 || true
grep -qxF "conda activate $CONDA_ENV" /root/.bashrc || \
    echo "conda activate $CONDA_ENV" >> /root/.bashrc
grep -qxF 'export PATH="/workspace/.npm-global/bin:$PATH"' /root/.bashrc || \
    echo 'export PATH="/workspace/.npm-global/bin:$PATH"' >> /root/.bashrc
grep -qxF 'export PATH="/workspace/texlive/bin/x86_64-linux:$PATH"' /root/.bashrc || \
    echo 'export PATH="/workspace/texlive/bin/x86_64-linux:$PATH"' >> /root/.bashrc

printf 'export PATH="/workspace/.npm-global/bin:$PATH"\nexport PATH="/workspace/texlive/bin/x86_64-linux:$PATH"\n' \
    > /etc/profile.d/workspace-path.sh

echo "=========================================="
echo "[startup] Complete: $(date)"
