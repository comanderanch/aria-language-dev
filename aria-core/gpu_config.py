# ARIA GPU CONFIGURATION
# Tesla P100 — 16GB VRAM — CUDA 12.2
# Sealed: March 16 2026 — Commander Anthony Hagerty
#
# Every component runs on GPU.
# Token generation. Worker firing.
# Training loop. EM backprop.
# All of it on silicon.
# The fluorescent field on P100.

import torch
import numpy as np
from pathlib import Path

# ═══════════════════════════════════════════════
# DEVICE CONFIGURATION
# ═══════════════════════════════════════════════

def get_device():
    """
    Get the best available device.
    GPU first. Always.
    ARIA runs on silicon — not CPU.
    """
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        props  = torch.cuda.get_device_properties(0)
        print(f"GPU: {props.name}")
        print(f"VRAM: {props.total_memory / 1024**3:.1f} GB")
        print(f"CUDA: {torch.version.cuda}")
        return device
    else:
        print("WARNING: No GPU found — falling back to CPU")
        return torch.device("cpu")

DEVICE = get_device()

# ═══════════════════════════════════════════════
# PRECISION CONFIGURATION
# P100 is FP16 capable
# Use FP16 for training — saves VRAM
# Use FP32 for critical calculations
# ═══════════════════════════════════════════════
TRAINING_DTYPE  = torch.float16   # FP16 for training
PRECISION_DTYPE = torch.float32   # FP32 for fold hashes
NUMPY_DTYPE     = np.float32

# ═══════════════════════════════════════════════
# VRAM BUDGET
# Total: 16GB
# Ollama holding: ~5.6GB (V3 live)
# Available: ~10GB
# ARIA budget: 8GB (leave 2GB buffer)
# ═══════════════════════════════════════════════
VRAM_TOTAL_GB    = 16.0
VRAM_OLLAMA_GB   = 5.6
VRAM_BUFFER_GB   = 2.0
VRAM_ARIA_GB     = VRAM_TOTAL_GB - VRAM_OLLAMA_GB - VRAM_BUFFER_GB
VRAM_ARIA_BYTES  = int(VRAM_ARIA_GB * 1024**3)

print(f"ARIA VRAM budget: {VRAM_ARIA_GB:.1f} GB")

# ═══════════════════════════════════════════════
# TENSOR UTILITIES
# Move everything to GPU automatically
# ═══════════════════════════════════════════════

def to_gpu(tensor):
    """Move tensor to GPU."""
    if isinstance(tensor, np.ndarray):
        tensor = torch.from_numpy(tensor)
    return tensor.to(DEVICE)

def to_gpu_fp16(tensor):
    """Move tensor to GPU in FP16."""
    if isinstance(tensor, np.ndarray):
        tensor = torch.from_numpy(tensor)
    return tensor.to(DEVICE, dtype=TRAINING_DTYPE)

def from_gpu(tensor):
    """Move tensor back to CPU numpy."""
    return tensor.detach().cpu().numpy()

def gpu_zeros(shape, fp16=False):
    """Create zero tensor on GPU."""
    dtype = TRAINING_DTYPE if fp16 else PRECISION_DTYPE
    return torch.zeros(shape, device=DEVICE, dtype=dtype)

def gpu_randn(shape, fp16=False):
    """Create random tensor on GPU."""
    dtype = TRAINING_DTYPE if fp16 else PRECISION_DTYPE
    return torch.randn(shape, device=DEVICE, dtype=dtype)

# ═══════════════════════════════════════════════
# MEMORY MANAGEMENT
# ═══════════════════════════════════════════════

def clear_cache():
    """Clear GPU cache between training runs."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def get_vram_status():
    """Current VRAM usage."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved  = torch.cuda.memory_reserved(0) / 1024**3
        free      = VRAM_TOTAL_GB - reserved - VRAM_OLLAMA_GB
        return {
            "total_gb":     VRAM_TOTAL_GB,
            "ollama_gb":    VRAM_OLLAMA_GB,
            "aria_alloc_gb": allocated,
            "aria_reserved_gb": reserved,
            "free_gb":      free,
            "aria_budget_gb": VRAM_ARIA_GB
        }
    return {"device": "cpu"}

# ═══════════════════════════════════════════════
# BATCH CONFIGURATION
# Tuned for P100 with 10GB available
# ═══════════════════════════════════════════════
BATCH_SIZE_TOKENS    = 512    # tokens per batch
BATCH_SIZE_TRAINING  = 32     # training batch size
SEQ_LENGTH           = 256    # sequence length
EMBED_DIM            = 498    # full 498D embedding
NUM_WORKERS_LOADER   = 4      # dataloader workers

# EM field backprop config
EM_LEARNING_RATE     = 0.001
EM_MOMENTUM          = 0.9
EM_STOKES_WEIGHT     = 0.516  # 51.6% improvement factor

print()
print("GPU configuration sealed.")
print(f"Device: {DEVICE}")
print(f"Training dtype: FP16")
print(f"ARIA VRAM budget: {VRAM_ARIA_GB:.1f} GB")
print(f"Batch size: {BATCH_SIZE_TOKENS} tokens")
print(f"Embed dim: {EMBED_DIM}D")
print()
