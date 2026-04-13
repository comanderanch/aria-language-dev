import torch
from pathlib import Path

ckpt_dir = Path("aria-core/training/checkpoints")
rounds = range(81, 144)

print(f"{'Round':<10} {'Loss':<15}")
print("-" * 25)

for r in rounds:
    ckpt_path = ckpt_dir / f"round{r}_best.pt"
    if ckpt_path.exists():
        try:
            ckpt = torch.load(ckpt_path, map_location="cpu")
            loss = ckpt.get("best_loss", "N/A")
            print(f"{r:<10} {loss:<15}")
        except Exception as e:
            print(f"{r:<10} Error: {e}")
    else:
        print(f"{r:<10} Missing")
