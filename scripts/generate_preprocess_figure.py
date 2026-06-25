"""
Focused figure: Preprocessing pipelines across latest Pointcept models.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager
import numpy as np

# ── Font ──────────────────────────────────────────────────────────────────────
font_manager.fontManager.addfont("/tmp/NotoSansSC.otf")
prop = font_manager.FontProperties(fname="/tmp/NotoSansSC.otf")
FONT = prop.get_name()
plt.rcParams["font.family"] = FONT
plt.rcParams["axes.unicode_minus"] = False

# ── Colors ────────────────────────────────────────────────────────────────────
COL = {
    "ptv3":   "#1565C0",
    "sonata": "#6A1B9A",
    "utonia": "#AD1457",
    "mink":   "#2E7D32",
    "spunet": "#00695C",
    "litept": "#E65100",
    "header": "#1A237E",
    "step_bg": {
        "center":   "#E8F5E9",
        "dropout":  "#FFF8E1",
        "geo_aug":  "#E3F2FD",
        "voxel":    "#FCE4EC",
        "crop":     "#EDE7F6",
        "color":    "#F3E5F5",
        "norm":     "#E0F2F1",
    },
    "step_edge": {
        "center":   "#43A047",
        "dropout":  "#F9A825",
        "geo_aug":  "#1E88E5",
        "voxel":    "#E91E63",
        "crop":     "#7B1FA2",
        "color":    "#8E24AA",
        "norm":     "#00897B",
    },
}

# ── Model definitions ─────────────────────────────────────────────────────────
# Each step: (label, detail, category)
MODELS = [
    {
        "name": "PTv3",
        "subtitle": "CVPR 2024 Oral",
        "dataset": "S3DIS",
        "color": COL["ptv3"],
        "steps": [
            ("CenterShift",    "apply_z=True",                "center"),
            ("RandomDropout",  "ratio=0.2  p=0.2",            "dropout"),
            ("Rotate x3",      "z:[-π,π]  x/y:[-π/64,π/64]", "geo_aug"),
            ("RandomScale",    "[0.9, 1.1]",                  "geo_aug"),
            ("RandomFlip",     "p=0.5",                       "geo_aug"),
            ("RandomJitter",   "σ=0.005  clip=0.02",          "geo_aug"),
            ("ChromaticAug x3","AutoContrast/Trans/Jitter",   "color"),
            ("GridSample",     "grid=0.02m",                  "voxel"),
            ("SphereCrop",     "rate=0.6",                    "crop"),
            ("SphereCrop",     "max=204,800 pts",             "crop"),
            ("CenterShift",    "apply_z=False",               "center"),
            ("NormalizeColor", "",                            "norm"),
        ],
    },
    {
        "name": "Sonata",
        "subtitle": "CVPR 2025 Highlight",
        "dataset": "S3DIS fine-tune",
        "color": COL["sonata"],
        "steps": [
            ("CenterShift",    "apply_z=True",                "center"),
            ("RandomDropout",  "ratio=0.2  p=1.0",            "dropout"),
            ("Rotate x3",      "z:[-π,π]  x/y:[-π/64,π/64]", "geo_aug"),
            ("RandomScale",    "[0.9, 1.1]",                  "geo_aug"),
            ("RandomFlip",     "p=0.5",                       "geo_aug"),
            ("RandomJitter",   "σ=0.005  clip=0.02",          "geo_aug"),
            ("ElasticDistort", "[[0.2,0.4],[0.8,1.6]]",       "geo_aug"),
            ("ChromaticAug x3","AutoContrast/Trans/Jitter",   "color"),
            ("GridSample",     "grid=0.02m",                  "voxel"),
            ("SphereCrop",     "rate=0.6",                    "crop"),
            ("SphereCrop",     "max=204,800 pts",             "crop"),
            ("CenterShift",    "apply_z=False",               "center"),
            ("NormalizeColor", "",                            "norm"),
        ],
    },
    {
        "name": "Utonia",
        "subtitle": "2026 Latest",
        "dataset": "S3DIS fine-tune",
        "color": COL["utonia"],
        "steps": [
            ("RandomScale",    "[0.5, 0.5]  coord normalize",  "voxel"),
            ("CenterShift",    "apply_z=True",                 "center"),
            ("RandomDropout",  "ratio=0.2  p=1.0",             "dropout"),
            ("Rotate x3",      "z:[-π,π]  x/y:[-π/64,π/64]",  "geo_aug"),
            ("RandomScale",    "[0.9, 1.1]  aug",              "geo_aug"),
            ("RandomFlip",     "p=0.5",                        "geo_aug"),
            ("RandomJitter",   "σ=0.0025  clip=0.01  (finer)", "geo_aug"),
            ("ElasticDistort", "[[0.1,0.2],[0.4,0.8]]  (finer)","geo_aug"),
            ("ChromaticAug x3","AutoContrast/Trans/Jitter",    "color"),
            ("GridSample",     "grid=0.01m  (finer)",          "voxel"),
            ("SphereCrop",     "rate=0.6",                     "crop"),
            ("SphereCrop",     "max=204,800 pts",              "crop"),
            ("CenterShift",    "apply_z=False",                "center"),
            ("NormalizeColor", "",                             "norm"),
        ],
    },
    {
        "name": "MinkowskiNet\n/ SpUNet",
        "subtitle": "Sparse Conv baseline",
        "dataset": "S3DIS",
        "color": COL["mink"],
        "steps": [
            ("CenterShift",    "apply_z=True",                "center"),
            ("RandomDropout",  "ratio=0.2  p=0.2",            "dropout"),
            ("Rotate x3",      "z:[-π,π]  x/y:[-π/64,π/64]", "geo_aug"),
            ("RandomScale",    "[0.9, 1.1]",                  "geo_aug"),
            ("RandomFlip",     "p=0.5",                       "geo_aug"),
            ("RandomJitter",   "σ=0.005  clip=0.02",          "geo_aug"),
            ("ElasticDistort", "[[0.2,0.4],[0.8,1.6]]",       "geo_aug"),
            ("ChromaticAug x3","AutoContrast/Trans/Jitter",   "color"),
            ("GridSample",     "grid=0.05m  (coarser)",       "voxel"),
            ("SphereCrop",     "max=100,000 pts",             "crop"),
            ("CenterShift",    "apply_z=False",               "center"),
            ("NormalizeColor", "",                            "norm"),
        ],
    },
    {
        "name": "LitePT",
        "subtitle": "2024 Efficient",
        "dataset": "ScanNet",
        "color": COL["litept"],
        "steps": [
            ("CenterShift",    "apply_z=True",                "center"),
            ("RandomDropout",  "ratio=0.2  p=0.2",            "dropout"),
            ("Rotate x3",      "z:[-π,π]  x/y:[-π/64,π/64]", "geo_aug"),
            ("RandomScale",    "[0.9, 1.1]",                  "geo_aug"),
            ("RandomFlip",     "p=0.5",                       "geo_aug"),
            ("RandomJitter",   "σ=0.005  clip=0.02",          "geo_aug"),
            ("ElasticDistort", "[[0.2,0.4],[0.8,1.6]]",       "geo_aug"),
            ("ChromaticAug x3","AutoContrast/Trans/Jitter",   "color"),
            ("GridSample",     "grid=0.02m",                  "voxel"),
            ("SphereCrop",     "max=102,400 pts",             "crop"),
            ("CenterShift",    "apply_z=False",               "center"),
            ("NormalizeColor", "",                            "norm"),
        ],
    },
]

# ── Category legend ───────────────────────────────────────────────────────────
CAT_LABELS = {
    "center":  "坐标归一化",
    "dropout": "随机点丢弃",
    "geo_aug": "几何增强",
    "color":   "颜色增强",
    "voxel":   "体素降采样",
    "crop":    "球形裁剪",
    "norm":    "归一化输出",
}

# ── Layout ────────────────────────────────────────────────────────────────────
N = len(MODELS)
fig_w = 5.5 * N
fig_h = 24
fig, axes = plt.subplots(1, N, figsize=(fig_w, fig_h), facecolor="#F8F9FA")
fig.patch.set_facecolor("#F8F9FA")

# Title
fig.text(0.5, 0.975, "Pointcept 最新模型 — 训练预处理 Pipeline 完整对比",
         ha="center", va="center", fontsize=22, fontweight="bold",
         color=COL["header"], fontfamily=FONT)
fig.text(0.5, 0.962, "数据集：S3DIS (主)  |  分析范围：PTv3 / Sonata / Utonia / MinkowskiNet+SpUNet / LitePT",
         ha="center", va="center", fontsize=13, color="#555", fontfamily=FONT)

# ── Draw each model column ────────────────────────────────────────────────────
STEP_H   = 0.053   # height per step block (axes units 0-1)
STEP_GAP = 0.008
TOP_START = 0.92   # y where steps start

for ax, model in zip(axes, MODELS):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("#F8F9FA")

    # Model header box
    ax.add_patch(FancyBboxPatch((0.02, 0.935), 0.96, 0.060,
                                boxstyle="round,pad=0.01",
                                facecolor=model["color"], edgecolor="none"))
    ax.text(0.5, 0.973, model["name"],
            ha="center", va="center", fontsize=16, fontweight="bold",
            color="white", fontfamily=FONT)
    ax.text(0.5, 0.950, model["subtitle"],
            ha="center", va="center", fontsize=10, color="#E0E0E0", fontfamily=FONT)
    ax.text(0.5, 0.938, f"Dataset: {model['dataset']}",
            ha="center", va="center", fontsize=9, color="#B0BEC5", fontfamily=FONT)

    # Step number label
    ax.text(0.5, 0.926, f"共 {len(model['steps'])} 步",
            ha="center", va="center", fontsize=9.5, color="#757575",
            style="italic", fontfamily=FONT)

    # Draw steps top-to-bottom
    y = TOP_START - 0.01
    for si, (label, detail, cat) in enumerate(model["steps"]):
        step_top = y - si * (STEP_H + STEP_GAP)
        step_bot = step_top - STEP_H

        bg   = COL["step_bg"][cat]
        edge = COL["step_edge"][cat]

        ax.add_patch(FancyBboxPatch((0.04, step_bot), 0.92, STEP_H,
                                    boxstyle="round,pad=0.008",
                                    facecolor=bg, edgecolor=edge, linewidth=1.5))

        # Step index dot
        ax.add_patch(plt.Circle((0.115, step_bot + STEP_H/2), 0.028,
                                color=edge, zorder=3))
        ax.text(0.115, step_bot + STEP_H/2, str(si+1),
                ha="center", va="center", fontsize=8.5, fontweight="bold",
                color="white", fontfamily=FONT, zorder=4)

        # Label
        ax.text(0.20, step_bot + STEP_H * 0.65, label,
                ha="left", va="center", fontsize=10, fontweight="bold",
                color=edge, fontfamily=FONT)

        # Detail
        if detail:
            ax.text(0.20, step_bot + STEP_H * 0.28, detail,
                    ha="left", va="center", fontsize=8.2, color="#424242",
                    fontfamily=FONT)

        # Category tag (right side)
        ax.text(0.96, step_bot + STEP_H/2, CAT_LABELS[cat],
                ha="right", va="center", fontsize=7.5, color=edge,
                style="italic", fontfamily=FONT)

        # Arrow connector (except last)
        if si < len(model["steps"]) - 1:
            arrow_y = step_bot - STEP_GAP / 2
            ax.annotate("", xy=(0.5, arrow_y - 0.001),
                        xytext=(0.5, arrow_y + 0.001),
                        arrowprops=dict(arrowstyle="-|>", color="#9E9E9E",
                                        lw=1.2, mutation_scale=8))

# ── Legend at bottom ─────────────────────────────────────────────────────────
legend_ax = fig.add_axes([0.03, 0.005, 0.94, 0.038])
legend_ax.set_xlim(0, 1); legend_ax.set_ylim(0, 1); legend_ax.axis("off")
legend_ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                    facecolor="#ECEFF1", edgecolor="#B0BEC5", lw=0.8))

cats = list(CAT_LABELS.items())
n_cats = len(cats)
legend_ax.text(0.01, 0.75, "图例：",
               ha="left", va="center", fontsize=10, fontweight="bold",
               color="#212121", fontfamily=FONT)
for i, (cat, lbl) in enumerate(cats):
    x = 0.07 + i * (0.93 / n_cats)
    legend_ax.add_patch(FancyBboxPatch((x, 0.15), 0.11, 0.65,
                                       boxstyle="round,pad=0.01",
                                       facecolor=COL["step_bg"][cat],
                                       edgecolor=COL["step_edge"][cat], lw=1.2))
    legend_ax.text(x + 0.055, 0.52, lbl,
                   ha="center", va="center", fontsize=9, fontweight="bold",
                   color=COL["step_edge"][cat], fontfamily=FONT)

# ── Highlight summary annotation ─────────────────────────────────────────────
# Add a thin summary bar under the title
sum_ax = fig.add_axes([0.03, 0.048, 0.94, 0.025])
sum_ax.set_xlim(0, 1); sum_ax.set_ylim(0, 1); sum_ax.axis("off")
sum_ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.005",
                                 facecolor="#E8EAF6", edgecolor="#5C6BC0", lw=0.8))

notes = [
    "GridSample (体素降采样): 所有模型必用，grid_size 0.01~0.05m",
    "SphereCrop (球形裁剪): Transformer 系必用，max 10~20万点控显存",
    "RandomDropout: 全部使用，ratio=0.2 统一",
    "ElasticDistortion: 除 PTv3 外全部启用",
    "Utonia 独有: 先 scale×0.5 归一化坐标",
]
note_text = "   |   ".join(notes)
sum_ax.text(0.5, 0.5, note_text,
            ha="center", va="center", fontsize=8.8, color="#283593",
            fontfamily=FONT)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "/workspace/docs/pointcept_preprocessing_pipeline_comparison.png"
plt.tight_layout(rect=[0, 0.075, 1, 0.958])
plt.savefig(out, dpi=160, bbox_inches="tight",
            facecolor="#F8F9FA", edgecolor="none")
print(f"Saved: {out}")
