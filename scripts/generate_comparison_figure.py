"""
Generate a summary comparison figure: Pointcept vs Fan Qinyuan's augmentation strategy.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager
import numpy as np

# ── Load CJK font ──────────────────────────────────────────────────────────────
font_path_regular = "/tmp/NotoSansSC.otf"
font_manager.fontManager.addfont(font_path_regular)
prop_regular = font_manager.FontProperties(fname=font_path_regular)
FONT_R = prop_regular.get_name()
FONT_B = FONT_R  # use same font for bold (weight handled by fontweight param)
plt.rcParams["font.family"] = FONT_R
plt.rcParams["axes.unicode_minus"] = False

# ── Color palette ──────────────────────────────────────────────────────────────
C_HEADER   = "#1A237E"   # dark navy
C_FAN      = "#1565C0"   # blue  – Fan's strategy
C_PCT      = "#2E7D32"   # green – Pointcept
C_MATCH    = "#4CAF50"   # light green  ✅
C_PARTIAL  = "#FF8F00"   # amber        ⚠️
C_MISSING  = "#C62828"   # red          ❌
C_ARCH     = "#6A1B9A"   # purple – architecture-level
C_BG_LIGHT = "#F5F5F5"
C_BG_BLUE  = "#E3F2FD"
C_BG_GREEN = "#E8F5E9"
C_BG_AMBER = "#FFF8E1"
C_BG_RED   = "#FFEBEE"
C_BG_PURP  = "#F3E5F5"
C_TEXT     = "#212121"

# ── Figure layout ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 28), facecolor="white")
fig.patch.set_facecolor("white")

# Title area
ax_title = fig.add_axes([0.02, 0.945, 0.96, 0.05])
ax_title.set_xlim(0, 1); ax_title.set_ylim(0, 1); ax_title.axis("off")
ax_title.add_patch(FancyBboxPatch((0,0), 1, 1, boxstyle="round,pad=0.02",
                                   facecolor=C_HEADER, edgecolor="none"))
ax_title.text(0.5, 0.65, "Pointcept 最新模型 vs Fan Qinyuan 增强策略  ——  降OOM预处理对比总结",
              ha="center", va="center", fontsize=18, fontweight="bold",
              color="white", fontfamily=FONT_B)
ax_title.text(0.5, 0.18, "面向大规模点云语义分割的自适应参数选择研究 | TU Berlin | Yucan Luo",
              ha="center", va="center", fontsize=11, color="#BBDEFB", fontfamily=FONT_R)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – PARAMETER COMPARISON TABLE
# ══════════════════════════════════════════════════════════════════════════════
ax_tbl = fig.add_axes([0.02, 0.58, 0.96, 0.355])
ax_tbl.set_xlim(0, 1); ax_tbl.set_ylim(0, 1); ax_tbl.axis("off")

# Section header
ax_tbl.add_patch(FancyBboxPatch((0, 0.93), 1, 0.07, boxstyle="round,pad=0.005",
                                 facecolor="#283593", edgecolor="none"))
ax_tbl.text(0.5, 0.965, "一、参数级对比：导师增强策略 vs Pointcept 标准预处理",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="white", fontfamily=FONT_B)

# Table column headers
cols = [0.0, 0.13, 0.26, 0.52, 0.76, 0.88]
col_labels = ["参数", "Fan 设计范围", "Pointcept 对应方法", "差异说明", "状态", "OOM控制力"]
col_widths = [0.13, 0.13, 0.26, 0.24, 0.12, 0.12]

header_y = 0.88
for i, (label, x, w) in enumerate(zip(col_labels, cols, col_widths)):
    ax_tbl.add_patch(FancyBboxPatch((x+0.002, header_y), w-0.004, 0.045,
                                     boxstyle="round,pad=0.003",
                                     facecolor="#37474F", edgecolor="none"))
    ax_tbl.text(x + w/2, header_y + 0.022, label,
                ha="center", va="center", fontsize=10.5, fontweight="bold",
                color="white", fontfamily=FONT_B)

# Table rows
rows = [
    # (param, fan_range, pointcept_method, diff_note, status, oom_ctrl, bg)
    ("scale\n坐标缩放因子",
     "20 – 100\n（绝对控制）",
     "RandomScale [0.9, 1.1]\nUtonia 固定 scale=0.5",
     "Pointcept 仅做小幅数据增强\n无大范围绝对坐标归一化",
     "[~] 部分", "中", C_BG_AMBER),

    ("spatial_shape\n空间裁剪尺寸",
     "[256^3]->[1024^3]\nBox 裁剪",
     "SphereCrop (球形)\npoint_max=204800 (点数上限)",
     "裁剪形状不同：Box vs 球形\n无 voxel grid 空间尺寸控制",
     "[X] 无", "低", C_BG_RED),

    ("step\n滑动窗口步长",
     "16 – 128\n（控制重叠率）",
     "sampling_chunking_data.py\nchunk_stride（仅离线）",
     "仅离线预处理脚本\n非在线训练参数，无法 DoE 控制",
     "[X] 无", "无", C_BG_RED),

    ("jitter_range\n平移抖动范围",
     "0 – +/-5m\n（绝对坐标）",
     "RandomJitter\nsigma=0.005, clip=0.02",
     "机制一致，参数名/单位不同\n(sigma+clip vs 绝对范围)",
     "[OK] 有", "低", C_BG_GREEN),

    ("voxel_size\n体素降采样尺寸",
     "0.005 – 0.05m\n（可变范围）",
     "GridSample grid_size\n固定：0.01 或 0.02m",
     "Pointcept 固定单值\n导师设计为动态范围（可 DoE）",
     "[~] 部分", "高", C_BG_AMBER),

    ("drop_prob\n点丢弃概率",
     "0 – 0.3",
     "RandomDropout\ndropout_ratio=0.2",
     "机制基本一致\n参数范围相近",
     "[OK] 有", "中", C_BG_GREEN),

    ("align_mode\n边界对齐模式",
     "对齐 / 非对齐\n（块合并策略）",
     "—— 无 ——",
     "Pointcept 推理时直接叠加\n无边界一致性处理逻辑",
     "[X] 无", "无", C_BG_RED),
]

row_h = 0.108
start_y = 0.855
for ri, (param, fan, pct, diff, status, oom, bg) in enumerate(rows):
    y = start_y - ri * row_h
    alt_bg = "#FAFAFA" if ri % 2 == 0 else "#F0F4F8"
    for i, (x, w) in enumerate(zip(cols, col_widths)):
        cell_bg = bg if i == 4 else alt_bg
        ax_tbl.add_patch(FancyBboxPatch((x+0.002, y - row_h + 0.003), w-0.004, row_h-0.005,
                                         boxstyle="round,pad=0.003",
                                         facecolor=cell_bg, edgecolor="#BDBDBD", linewidth=0.5))

    # param col
    ax_tbl.text(cols[0]+col_widths[0]/2, y - row_h/2, param,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=C_FAN, fontfamily=FONT_B)
    # fan range
    ax_tbl.text(cols[1]+col_widths[1]/2, y - row_h/2, fan,
                ha="center", va="center", fontsize=8.5, color="#1A237E", fontfamily=FONT_R)
    # pointcept method
    ax_tbl.text(cols[2]+col_widths[2]/2, y - row_h/2, pct,
                ha="center", va="center", fontsize=8.5, color="#1B5E20", fontfamily=FONT_R)
    # diff note
    ax_tbl.text(cols[3]+col_widths[3]/2, y - row_h/2, diff,
                ha="center", va="center", fontsize=8.0, color=C_TEXT, fontfamily=FONT_R)
    # status
    s_color = C_MATCH if "[OK]" in status else (C_PARTIAL if "[~]" in status else C_MISSING)
    ax_tbl.text(cols[4]+col_widths[4]/2, y - row_h/2, status,
                ha="center", va="center", fontsize=10, fontweight="bold",
                color=s_color, fontfamily=FONT_R)
    # OOM ctrl
    oom_color = C_MATCH if oom == "高" else (C_PARTIAL if oom in ("中", "低") else "#9E9E9E")
    ax_tbl.text(cols[5]+col_widths[5]/2, y - row_h/2, oom,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=oom_color, fontfamily=FONT_B)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – ARCHITECTURE-LEVEL OOM STRATEGIES
# ══════════════════════════════════════════════════════════════════════════════
ax_arch = fig.add_axes([0.02, 0.42, 0.96, 0.15])
ax_arch.set_xlim(0, 1); ax_arch.set_ylim(0, 1); ax_arch.axis("off")

ax_arch.add_patch(FancyBboxPatch((0, 0.87), 1, 0.13, boxstyle="round,pad=0.005",
                                  facecolor="#4A148C", edgecolor="none"))
ax_arch.text(0.5, 0.935, "二、架构级降OOM策略（Pointcept 特有，导师策略之外）",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color="white", fontfamily=FONT_B)

arch_items = [
    ("Flash Attention\n(enable_flash=True)",
     "PTv3 / Sonata / Utonia\n全部启用",
     "注意力计算从 O(N²) 降到 O(N)\n大幅减少显存占用",
     C_BG_PURP),
    ("序列化注意力\n(Serialized Attention)",
     "PTv3 核心设计\nZ-order / Hilbert curve",
     "点云转序列后分 patch 计算\n避免全局 attention 的 OOM",
     C_BG_PURP),
    ("稀疏卷积\n(Sparse Convolution)",
     "MinkowskiNet / SpUNet\nSPVCNN",
     "只对有效体素计算\n比密集卷积节省 60–80% 显存",
     C_BG_PURP),
    ("混合精度训练\n(AMP)",
     "enable_amp=True\n所有新模型默认启用",
     "FP16 计算减少约 50% 显存\n需配合梯度缩放",
     C_BG_PURP),
]

n = len(arch_items)
item_w = 1.0 / n
for i, (title, model, desc, bg) in enumerate(arch_items):
    x = i * item_w
    ax_arch.add_patch(FancyBboxPatch((x+0.005, 0.02), item_w-0.01, 0.83,
                                     boxstyle="round,pad=0.01",
                                     facecolor=bg, edgecolor="#CE93D8", linewidth=1))
    ax_arch.text(x + item_w/2, 0.75, title,
                 ha="center", va="center", fontsize=10, fontweight="bold",
                 color="#4A148C", fontfamily=FONT_B)
    ax_arch.text(x + item_w/2, 0.52, model,
                 ha="center", va="center", fontsize=8.5, color="#6A1B9A", fontfamily=FONT_R)
    ax_arch.text(x + item_w/2, 0.24, desc,
                 ha="center", va="center", fontsize=8.0, color="#424242", fontfamily=FONT_R)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – PIPELINE COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
ax_pipe = fig.add_axes([0.02, 0.225, 0.96, 0.185])
ax_pipe.set_xlim(0, 1); ax_pipe.set_ylim(0, 1); ax_pipe.axis("off")

ax_pipe.add_patch(FancyBboxPatch((0, 0.88), 1, 0.12, boxstyle="round,pad=0.005",
                                  facecolor="#004D40", edgecolor="none"))
ax_pipe.text(0.5, 0.94, "三、完整预处理 Pipeline 对比",
             ha="center", va="center", fontsize=13, fontweight="bold",
             color="white", fontfamily=FONT_B)

# Fan's pipeline
ax_pipe.add_patch(FancyBboxPatch((0.01, 0.01), 0.46, 0.86, boxstyle="round,pad=0.01",
                                  facecolor=C_BG_BLUE, edgecolor="#1565C0", linewidth=1.5))
ax_pipe.text(0.24, 0.83, "Fan Qinyuan 增强策略 Pipeline",
             ha="center", va="center", fontsize=11, fontweight="bold",
             color="#0D47A1", fontfamily=FONT_B)

fan_steps = [
    ("1. 坐标缩放", "scale × coord  →  归一化大场景", C_FAN),
    ("2. 滑动窗口切块", "spatial_shape + step  →  产生重叠 Block", C_FAN),
    ("3. 几何增强", "jitter / flip / rotate / scale_aug", C_FAN),
    ("4. 自适应降采样", "voxel_size_range + drop_prob  →  控制点数/显存", C_FAN),
    ("5. 模型推理", "PTv3 / MinkowskiNet / Cylinder3D", "#37474F"),
    ("6. 边界对齐合并", "align_mode  →  重叠区域一致性融合", C_FAN),
]
step_h = 0.115
for si, (name, desc, col) in enumerate(fan_steps):
    sy = 0.73 - si * step_h
    ax_pipe.add_patch(FancyBboxPatch((0.03, sy), 0.42, step_h-0.01,
                                     boxstyle="round,pad=0.008",
                                     facecolor="white", edgecolor=col, linewidth=1.2))
    ax_pipe.text(0.08, sy + (step_h-0.01)/2, name,
                 ha="left", va="center", fontsize=9, fontweight="bold",
                 color=col, fontfamily=FONT_B)
    ax_pipe.text(0.24, sy + (step_h-0.01)/2, desc,
                 ha="left", va="center", fontsize=8, color="#424242", fontfamily=FONT_R)

# Pointcept pipeline
ax_pipe.add_patch(FancyBboxPatch((0.53, 0.01), 0.46, 0.86, boxstyle="round,pad=0.01",
                                  facecolor=C_BG_GREEN, edgecolor="#2E7D32", linewidth=1.5))
ax_pipe.text(0.76, 0.83, "Pointcept 标准 Pipeline (S3DIS)",
             ha="center", va="center", fontsize=11, fontweight="bold",
             color="#1B5E20", fontfamily=FONT_B)

pct_steps = [
    ("1. CenterShift", "场景中心归一化", C_PCT),
    ("2. 随机点丢弃", "RandomDropout ratio=0.2", C_PCT),
    ("3. 几何增强", "Rotate / Scale[0.9–1.1] / Flip / Jitter", C_PCT),
    ("4. 体素降采样", "GridSample grid_size=0.02m (固定)", C_PCT),
    ("5. 球形裁剪", "SphereCrop: 60% → max 204,800 pts", C_PCT),
    ("6. 模型推理", "PTv3 + Flash Attn + AMP", "#37474F"),
]
for si, (name, desc, col) in enumerate(pct_steps):
    sy = 0.73 - si * step_h
    ax_pipe.add_patch(FancyBboxPatch((0.55, sy), 0.42, step_h-0.01,
                                     boxstyle="round,pad=0.008",
                                     facecolor="white", edgecolor=col, linewidth=1.2))
    ax_pipe.text(0.60, sy + (step_h-0.01)/2, name,
                 ha="left", va="center", fontsize=9, fontweight="bold",
                 color=col, fontfamily=FONT_B)
    ax_pipe.text(0.76, sy + (step_h-0.01)/2, desc,
                 ha="left", va="center", fontsize=8, color="#424242", fontfamily=FONT_R)

# VS badge
ax_pipe.add_patch(plt.Circle((0.5, 0.45), 0.045, color="#FF6F00", zorder=5))
ax_pipe.text(0.5, 0.45, "VS", ha="center", va="center", fontsize=12,
             fontweight="bold", color="white", fontfamily=FONT_B, zorder=6)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – KEY GAP & RESEARCH VALUE
# ══════════════════════════════════════════════════════════════════════════════
ax_gap = fig.add_axes([0.02, 0.07, 0.96, 0.145])
ax_gap.set_xlim(0, 1); ax_gap.set_ylim(0, 1); ax_gap.axis("off")

ax_gap.add_patch(FancyBboxPatch((0, 0.86), 1, 0.14, boxstyle="round,pad=0.005",
                                 facecolor="#B71C1C", edgecolor="none"))
ax_gap.text(0.5, 0.93, "四、核心研究空白与论文价值",
            ha="center", va="center", fontsize=13, fontweight="bold",
            color="white", fontfamily=FONT_B)

gaps = [
    ("[缺失] 大场景 Box 切块",
     "Pointcept 无 spatial_shape 控制\n大场景直接 SphereCrop 截断\n信息大量丢失",
     "#FFCDD2"),
    ("[缺失] 在线步长控制",
     "overlap/step 无法在线配置\n训练时无法响应硬件约束\n无法系统 DoE 实验",
     "#FFCDD2"),
    ("[缺失] 边界对齐合并",
     "多块推理直接叠加\n边界区域预测不稳定\n影响大场景评估指标",
     "#FFCDD2"),
    ("[贡献] 论文核心贡献",
     "DoE 量化 6 个参数交互影响\n推导 mIoU/Memory 预测模型\n构建自适应参数选择模块",
     "#FFF9C4"),
    ("[创新] 研究定位",
     "非模型改进，而是\n系统性参数研究方法论\n在现有论文中完全空白",
     "#C8E6C9"),
]

gap_w = 1.0 / len(gaps)
for i, (title, body, bg) in enumerate(gaps):
    x = i * gap_w
    ax_gap.add_patch(FancyBboxPatch((x+0.005, 0.02), gap_w-0.01, 0.82,
                                    boxstyle="round,pad=0.01",
                                    facecolor=bg, edgecolor="#757575", linewidth=0.8))
    ax_gap.text(x + gap_w/2, 0.74, title,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color="#212121", fontfamily=FONT_B)
    ax_gap.text(x + gap_w/2, 0.38, body,
                ha="center", va="center", fontsize=8.5, color="#424242", fontfamily=FONT_R)

# ── Legend / footnote ──────────────────────────────────────────────────────────
ax_leg = fig.add_axes([0.02, 0.01, 0.96, 0.055])
ax_leg.set_xlim(0, 1); ax_leg.set_ylim(0, 1); ax_leg.axis("off")
ax_leg.add_patch(FancyBboxPatch((0,0), 1, 1, boxstyle="round,pad=0.01",
                                 facecolor="#ECEFF1", edgecolor="#B0BEC5", linewidth=0.8))
legend_items = [
    ("[OK] 有", C_MATCH, "Pointcept 有对应实现"),
    ("[~] 部分有", C_PARTIAL, "机制相近但参数/形式不同"),
    ("[X] 无", C_MISSING, "Pointcept 完全缺失"),
    ("OOM控制力", "#37474F", "该参数对降显存的直接影响程度"),
    ("Pointcept 版本", C_PCT, "v1.7.0  |  最新 commit: 2026-05-21"),
    ("分析范围", C_FAN, "PTv3 / Sonata / Utonia / MinkowskiNet"),
]
for i, (label, color, desc) in enumerate(legend_items):
    x = i / len(legend_items) + 0.01
    ax_leg.add_patch(mpatches.Rectangle((x, 0.55), 0.01, 0.3, color=color))
    ax_leg.text(x + 0.013, 0.7, label, va="center", fontsize=8.5,
                fontweight="bold", color=color, fontfamily=FONT_B)
    ax_leg.text(x + 0.013, 0.28, desc, va="center", fontsize=7.5,
                color="#616161", fontfamily=FONT_R)

# ── Save ───────────────────────────────────────────────────────────────────────
out_path = "/workspace/docs/pointcept_vs_fan_augmentation_comparison.png"
plt.savefig(out_path, dpi=180, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print(f"Saved to: {out_path}")
