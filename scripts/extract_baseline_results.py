"""
提取 SpUNet + PTv3 基线结果，写入 baseline_results.md
"""
import re

LOG_DIR = "/workspace/logs"
EXP_DIR = "/workspace/Pointcept/exp"

CLASSES = ["ceiling","floor","wall","beam","column","window",
           "door","table","chair","sofa","bookcase","board","clutter"]

def read_log(path):
    try:
        with open(path, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        return []

def find_last(lines, pattern):
    """返回最后一条匹配的行"""
    result = None
    for l in lines:
        if re.search(pattern, l):
            result = l
    return result

def find_last_block(lines, trigger_pattern, block_pattern, n=13):
    """找到最后一次 trigger 出现后，收集接下来匹配 block_pattern 的 n 行"""
    last_idx = -1
    for i, l in enumerate(lines):
        if re.search(trigger_pattern, l):
            last_idx = i
    if last_idx == -1:
        return []
    block = []
    for l in lines[last_idx:]:
        if re.search(block_pattern, l):
            block.append(l)
        if len(block) == n:
            break
    return block

def parse_val(line):
    m = re.search(r"mIoU/mAcc/allAcc\s+([\d.]+)/([\d.]+)/([\d.]+)", line or "")
    return (float(m.group(1)), float(m.group(2)), float(m.group(3))) if m else (None,)*3

def parse_best(line):
    m = re.search(r"Best mIoU:\s*([\d.]+)", line or "")
    return float(m.group(1)) if m else None

def parse_class_line(line):
    # format: Class_0 - ceiling Result: iou/accuracy 0.9221/0.9650
    m = re.search(r"Class_\d+ - (\w+) Result: iou/accuracy ([\d.]+)/([\d.]+)", line)
    if m:
        return m.group(1), float(m.group(2)), float(m.group(3))
    return None, None, None

def pct(v, decimals=2):
    return f"{v*100:.{decimals}f}" if v is not None else "N/A"

# ── SpUNet ────────────────────────────────────────────────────────────────────
sp_lines = read_log(f"{LOG_DIR}/spunet_baseline.log")
sp_final_line = find_last(sp_lines, r"Val result: mIoU/mAcc/allAcc")
sp_best_line  = find_last(sp_lines, r"Best mIoU:")
sp_cls_lines  = find_last_block(sp_lines,
                    r"Val result: mIoU/mAcc/allAcc",
                    r"Class_\d+ - \w+ Result: iou/accuracy")

sp_miou, sp_macc, sp_allacc = parse_val(sp_final_line)
sp_best = parse_best(sp_best_line)
sp_cls  = {}
for l in sp_cls_lines:
    name, iou, acc = parse_class_line(l)
    if name:
        sp_cls[name] = (iou, acc)

# ── PTv3 ─────────────────────────────────────────────────────────────────────
pt_test_lines  = read_log(f"{LOG_DIR}/ptv3_baseline_test.log")
pt_train_lines = read_log(f"{LOG_DIR}/ptv3_baseline.log")

pt_final_line = find_last(pt_test_lines, r"Val result: mIoU/mAcc/allAcc")
pt_best_line  = find_last(pt_train_lines, r"Best mIoU:")
pt_cls_lines  = find_last_block(pt_test_lines,
                    r"Val result: mIoU/mAcc/allAcc",
                    r"Class_\d+ - \w+ Result: iou/accuracy")

pt_miou, pt_macc, pt_allacc = parse_val(pt_final_line)
pt_best = parse_best(pt_best_line)
pt_cls  = {}
for l in pt_cls_lines:
    name, iou, acc = parse_class_line(l)
    if name:
        pt_cls[name] = (iou, acc)

# ── 输出 ─────────────────────────────────────────────────────────────────────
out = []
out.append("# S3DIS Area_5 基线结果\n\n")
out.append("**数据集**: S3DIS · 测试集 Area_5 · 500 epoch · 默认参数\n\n")

out.append("## 汇总\n\n")
out.append("| 模型 | mIoU (%) | mAcc (%) | allAcc (%) | 训练 Best mIoU (%) |\n")
out.append("|------|----------|----------|------------|--------------------|\n")
out.append(f"| SpUNet (500ep) | {pct(sp_miou)} | {pct(sp_macc)} | {pct(sp_allacc)} | {pct(sp_best)} |\n")
out.append(f"| PTv3   (500ep) | {pct(pt_miou)} | {pct(pt_macc)} | {pct(pt_allacc)} | {pct(pt_best)} |\n\n")

out.append("## 各类别 IoU (%)\n\n")
out.append("| 类别 | SpUNet IoU | SpUNet Acc | PTv3 IoU | PTv3 Acc |\n")
out.append("|------|-----------|-----------|---------|----------|\n")
for cls in CLASSES:
    s_iou, s_acc = sp_cls.get(cls, (None, None))
    p_iou, p_acc = pt_cls.get(cls, (None, None))
    out.append(f"| {cls} | {pct(s_iou,1)} | {pct(s_acc,1)} | {pct(p_iou,1)} | {pct(p_acc,1)} |\n")

out.append("\n## 原始日志\n\n")
out.append(f"- SpUNet 训练+测评: `{LOG_DIR}/spunet_baseline.log`\n")
out.append(f"- PTv3   训练:       `{LOG_DIR}/ptv3_baseline.log`\n")
out.append(f"- PTv3   测评:       `{LOG_DIR}/ptv3_baseline_test.log`\n")
out.append(f"- SpUNet checkpoint: `{EXP_DIR}/baseline_spunet/model/model_best.pth`\n")
out.append(f"- PTv3   checkpoint: `{EXP_DIR}/baseline_ptv3/model/model_best.pth`\n")

out_path = "/workspace/baseline_results.md"
with open(out_path, "w") as f:
    f.writelines(out)

print(f"已写入: {out_path}\n")
print("=== 汇总 ===")
print(f"SpUNet  mIoU={pct(sp_miou)}%  mAcc={pct(sp_macc)}%  allAcc={pct(sp_allacc)}%  BestTrain={pct(sp_best)}%")
print(f"PTv3    mIoU={pct(pt_miou)}%  mAcc={pct(pt_macc)}%  allAcc={pct(pt_allacc)}%  BestTrain={pct(pt_best)}%")
print("\n=== 各类别 IoU ===")
print(f"{'类别':<12} {'SpUNet':>8} {'PTv3':>8}")
for cls in CLASSES:
    s = pct(sp_cls.get(cls,(None,None))[0], 1)
    p = pct(pt_cls.get(cls,(None,None))[0], 1)
    print(f"{cls:<12} {s:>8} {p:>8}")
