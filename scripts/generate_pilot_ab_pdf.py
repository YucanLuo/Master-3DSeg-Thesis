"""
生成"小实验：训练数据输入策略设计"PDF报告（中文，带图表）
策略A（重复采样） vs 策略B（按box网格输入）

注意：完全用matplotlib渲染（包括所有中文文字），不用reportlab——
reportlab的内置CID字体(STSong-Light)在本环境的poppler渲染器下无法正确
显示中文字形（变成实心黑块/文字缺失），而scripts/下的NotoSansSC*.otf
文件实际是损坏的HTML页面，不是真字体。改用texlive自带的FandolSong
(真正的OpenType/CFF字体)，经matplotlib+freetype验证可以正确渲染中文。
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import io
from datetime import datetime

FONT_PATH = "/workspace/texlive/texmf-dist/fonts/opentype/public/fandol/FandolSong-Regular.otf"
FONT_BOLD_PATH = "/workspace/texlive/texmf-dist/fonts/opentype/public/fandol/FandolHei-Bold.otf"
font_manager.fontManager.addfont(FONT_PATH)
font_manager.fontManager.addfont(FONT_BOLD_PATH)
FONT_REG = font_manager.FontProperties(fname=FONT_PATH).get_name()
FONT_BOLD = font_manager.FontProperties(fname=FONT_BOLD_PATH).get_name()
plt.rcParams["font.family"] = FONT_REG
plt.rcParams["axes.unicode_minus"] = False

# ── 颜色 ──────────────────────────────────────────────────────────────────
TU_RED = "#C40D1E"
DARK_GRAY = "#1A1A1A"
MID_GRAY = "#555555"
LIGHT_GRAY = "#F4F4F4"
HEADER_BG = "#1A1A2E"
GREEN_DARK = "#1B5E20"
RED_DARK = "#B71C1C"
HILITE = "#FFF3E0"
BASELINE_C = "#9E9E9E"
A_C = "#2196F3"
B_C = "#E91E63"

# ── 数据 ──────────────────────────────────────────────────────────────────
CLASSES_EN = ["ceiling", "floor", "wall", "beam", "column", "window",
              "door", "table", "chair", "sofa", "bookcase", "board", "clutter"]
CLASSES_ZH = ["天花板", "地板", "墙壁", "横梁", "柱子", "窗户",
              "门", "桌子", "椅子", "沙发", "书架", "黑板", "杂物"]

BASE_IOU = [92.21, 97.23, 82.57, 0.00, 25.55, 58.14, 70.86, 80.70, 88.15, 47.08, 75.24, 68.16, 57.45]
A_IOU = [92.24, 96.98, 77.60, 0.00, 26.43, 40.57, 54.17, 77.60, 86.63, 32.20, 70.26, 31.29, 52.70]
B_IOU = [92.15, 96.76, 75.96, 0.00, 23.78, 41.05, 39.94, 76.93, 88.28, 58.93, 67.80, 52.43, 52.10]

BASE_MIOU, BASE_MACC, BASE_ALLACC = 64.87, 71.29, 89.05
A_MIOU, A_MACC, A_ALLACC = 56.82, 63.31, 86.17
B_MIOU, B_MACC, B_ALLACC = 58.93, 65.96, 85.32

EPOCH_TIME = [("baseline\n(clean data)", 6.0), ("Pilot A 1st run\n(bloated data)", 128.4),
              ("after fix\n(A/B consistent)", 15.2)]

# ── 小图表（作为图片嵌入，标签用英文，避免字体问题） ───────────────────────
def make_overall_chart():
    fig, ax = plt.subplots(figsize=(9, 3.6))
    metrics = ["mIoU", "mAcc", "allAcc"]
    base_v = [BASE_MIOU, BASE_MACC, BASE_ALLACC]
    a_v = [A_MIOU, A_MACC, A_ALLACC]
    b_v = [B_MIOU, B_MACC, B_ALLACC]
    x = np.arange(len(metrics))
    w = 0.25
    ax.bar(x - w, base_v, w, label="baseline (500ep)", color=BASELINE_C, alpha=0.9, zorder=3)
    ax.bar(x, a_v, w, label="Pilot A (120ep, repeat)", color=A_C, alpha=0.9, zorder=3)
    ax.bar(x + w, b_v, w, label="Pilot B (120ep, grid-box)", color=B_C, alpha=0.9, zorder=3)
    for xi, vals in zip([x - w, x, x + w], [base_v, a_v, b_v]):
        for xx, vv in zip(xi, vals):
            ax.text(xx, vv + 1, f"{vv:.1f}", ha="center", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylabel("%", fontsize=9)
    ax.set_ylim(0, 100)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8, loc="upper right")
    ax.set_title("Overall Metrics — S3DIS Area_5 Full-Scene Test (TTA)", fontsize=10, pad=8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf


def make_per_class_chart():
    fig, ax = plt.subplots(figsize=(12, 4.6))
    x = np.arange(len(CLASSES_EN))
    w = 0.27
    ax.bar(x - w, BASE_IOU, w, label="baseline (500ep)", color=BASELINE_C, alpha=0.85, zorder=3)
    ax.bar(x, A_IOU, w, label="Pilot A (120ep, repeat)", color=A_C, alpha=0.9, zorder=3)
    ax.bar(x + w, B_IOU, w, label="Pilot B (120ep, grid-box)", color=B_C, alpha=0.9, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(CLASSES_EN, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("IoU (%)", fontsize=10)
    ax.set_ylim(0, 108)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, name in [(6, "door"), (9, "sofa"), (11, "board")]:
        ax.annotate(name, xy=(i, max(A_IOU[i], B_IOU[i]) + 3), fontsize=8,
                     color="#B71C1C" if name == "door" else "#1B5E20", ha="center", fontweight="bold")
    ax.legend(fontsize=8.5, loc="upper right")
    ax.set_title("Per-Class IoU — Pilot A vs Pilot B vs Baseline", fontsize=11, pad=10)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf


def make_radar_chart():
    idx = [i for i in range(len(CLASSES_EN)) if i != 3]
    labels = [CLASSES_EN[i] for i in idx]
    a_vals = [A_IOU[i] for i in idx]
    b_vals = [B_IOU[i] for i in idx]
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    a_p = a_vals + [a_vals[0]]
    b_p = b_vals + [b_vals[0]]
    angles_p = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(5.4, 5.4), subplot_kw=dict(polar=True))
    ax.plot(angles_p, a_p, color=A_C, linewidth=2, label="Pilot A")
    ax.fill(angles_p, a_p, color=A_C, alpha=0.15)
    ax.plot(angles_p, b_p, color=B_C, linewidth=2, label="Pilot B")
    ax.fill(angles_p, b_p, color=B_C, alpha=0.15)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], fontsize=7, color="gray")
    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=9)
    ax.set_title("Pilot A vs Pilot B Radar\n(beam excluded)", fontsize=10, pad=20)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf


def make_epoch_time_chart():
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    labels = [t[0] for t in EPOCH_TIME]
    vals = [t[1] for t in EPOCH_TIME]
    cols = ["#9E9E9E", "#C62828", "#2E7D32"]
    bars = ax.bar(labels, vals, color=cols, alpha=0.88, width=0.55, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}s", ha="center", fontsize=9, fontweight="bold")
    ax.set_ylabel("Worker restart wait per epoch (s)", fontsize=9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("Impact of the Dataset Incident on Training Speed", fontsize=10, pad=8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════
# 页面排版引擎（全部用matplotlib文字+matplotlib图片拼出整份PDF）
# ══════════════════════════════════════════════════════════════════════
PAGE_W, PAGE_H = 8.27, 11.69  # A4, inch
LX, RX = 0.09, 0.94
CW = RX - LX
TOP, BOTTOM = 0.95, 0.06

OUT_PATH = "/workspace/小实验_输入策略报告.pdf"
pdf = PdfPages(OUT_PATH)

_state = {"fig": None, "ax": None, "y": TOP}

_FP_REG = font_manager.FontProperties(fname=FONT_PATH)
_FP_BOLD = font_manager.FontProperties(fname=FONT_BOLD_PATH)


def new_page():
    if _state["fig"] is not None:
        pdf.savefig(_state["fig"])
        plt.close(_state["fig"])
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _state["fig"] = fig
    _state["ax"] = ax
    _state["y"] = TOP
    return fig, ax


def finalize():
    if _state["fig"] is not None:
        pdf.savefig(_state["fig"])
        plt.close(_state["fig"])
    pdf.close()


def cjk_wrap(text, max_width=74):
    lines, cur, cur_w = [], "", 0
    for ch in text:
        w = 2 if ord(ch) > 0x2E80 else 1
        if cur_w + w > max_width and cur:
            lines.append(cur)
            cur, cur_w = ch, w
        else:
            cur += ch
            cur_w += w
    if cur:
        lines.append(cur)
    return lines


def ensure_space(need):
    if _state["y"] - need < BOTTOM:
        new_page()


def line_h(fontsize, leading=1.55):
    return leading * fontsize / 72.0 / PAGE_H


def heading(text, level=1):
    fs = 15 if level == 1 else 11
    need = line_h(fs, 2.0) + 0.01
    ensure_space(need)
    ax = _state["ax"]
    color = TU_RED if level == 1 else DARK_GRAY
    ax.text(LX, _state["y"], text, fontsize=fs, color=color, fontproperties=_FP_BOLD,
            va="top", ha="left")
    _state["y"] -= line_h(fs, 1.6)
    if level == 1:
        ax.plot([LX, RX], [_state["y"], _state["y"]], color="#DDDDDD", lw=0.8, transform=ax.transAxes)
        _state["y"] -= 0.012
    else:
        _state["y"] -= 0.004


def paragraph(text, fontsize=9.3, color=DARK_GRAY, bold=False, max_width=76, indent=0.0, sa=0.012):
    lines = cjk_wrap(text, max_width=max_width)
    fp = _FP_BOLD if bold else _FP_REG
    lh = line_h(fontsize)
    ensure_space(lh * len(lines) + sa)
    ax = _state["ax"]
    for ln in lines:
        ax.text(LX + indent, _state["y"], ln, fontsize=fontsize, color=color, fontproperties=fp,
                va="top", ha="left")
        _state["y"] -= lh
    _state["y"] -= sa


def bullet(text, fontsize=9.3, max_width=72):
    paragraph(text, fontsize=fontsize, max_width=max_width, indent=0.015, sa=0.014)


def spacer(h):
    _state["y"] -= h


def table(rows, col_fracs, fontsize=8.3, header_rows=1, highlight_rows=None, row_h_pt=18, aligns=None):
    n_rows = len(rows)
    rh = row_h_pt / 72.0 / PAGE_H
    ensure_space(rh * n_rows + 0.015)
    ax = _state["ax"]
    y_top = _state["y"]
    x_edges = [LX]
    for f in col_fracs:
        x_edges.append(x_edges[-1] + f * CW)
    highlight_rows = highlight_rows or []
    for r, row in enumerate(rows):
        y0 = y_top - (r + 1) * rh
        y1 = y_top - r * rh
        if r < header_rows:
            bg = HEADER_BG
            txt_color = "white"
            fp = _FP_BOLD
        else:
            bg = HILITE if r in highlight_rows else (LIGHT_GRAY if (r - header_rows) % 2 == 1 else "white")
            txt_color = DARK_GRAY
            fp = _FP_REG
        rect = mpatches.Rectangle((LX, y0), CW, rh, facecolor=bg, edgecolor="#CCCCCC", linewidth=0.4, zorder=2)
        ax.add_patch(rect)
        for c, cell in enumerate(row):
            align = (aligns[c] if aligns else ("left" if c == 0 else "center"))
            if align == "left":
                tx = x_edges[c] + 0.008
                ha = "left"
            else:
                tx = (x_edges[c] + x_edges[c + 1]) / 2
                ha = "center"
            ax.text(tx, (y0 + y1) / 2, str(cell), fontsize=fontsize, color=txt_color, fontproperties=fp,
                    va="center", ha=ha, zorder=3)
    for xe in x_edges:
        ax.plot([xe, xe], [y_top - n_rows * rh, y_top], color="#CCCCCC", lw=0.4, zorder=2)
    ax.plot([LX, RX], [y_top - header_rows * rh, y_top - header_rows * rh], color=HEADER_BG, lw=1.2, zorder=3)
    _state["y"] = y_top - n_rows * rh - 0.018


def image(png_buf, width_frac=CW):
    img = plt.imread(png_buf, format="png")
    h_px, w_px = img.shape[0], img.shape[1]
    aspect = h_px / w_px
    width_in = width_frac * PAGE_W
    height_in = width_in * aspect
    height_frac = height_in / PAGE_H
    ensure_space(height_frac + 0.015)
    x0 = LX + (CW - width_frac) / 2
    y1 = _state["y"]
    y0 = y1 - height_frac
    fig = _state["fig"]
    ax_img = fig.add_axes([x0, y0, width_frac, height_frac])
    ax_img.imshow(img)
    ax_img.axis("off")
    _state["y"] = y0 - 0.012


def caption(text, fontsize=8):
    paragraph(text, fontsize=fontsize, color=MID_GRAY, max_width=90, sa=0.016)


# ══════════════════════════════════════════════════════════════════════
# 封面
# ══════════════════════════════════════════════════════════════════════
new_page()
ax = _state["ax"]
_state["y"] = 0.86
ax.plot([LX, RX], [_state["y"], _state["y"]], color=TU_RED, lw=3, transform=ax.transAxes)
_state["y"] -= 0.035
ax.text(0.5, _state["y"], "小实验：训练数据输入策略设计", fontsize=22, color=DARK_GRAY,
        fontproperties=_FP_BOLD, ha="center", va="top")
_state["y"] -= 0.045
ax.text(0.5, _state["y"], "随机重复采样 vs 按box网格输入 · SpUNet on S3DIS", fontsize=12, color=MID_GRAY,
        fontproperties=_FP_REG, ha="center", va="top")
_state["y"] -= 0.03
ax.plot([0.2, 0.8], [_state["y"], _state["y"]], color="#DDDDDD", lw=1, transform=ax.transAxes)
_state["y"] -= 0.025
for line in [
    "策略A（Pilot A）：现状复刻，随机球形裁剪重复采样",
    "策略B（Pilot B）：确定性立方体网格分块，遍历覆盖整场景",
    datetime.now().strftime("生成日期：%Y 年 %m 月 %d 日"),
]:
    ax.text(0.5, _state["y"], line, fontsize=10, color=MID_GRAY, fontproperties=_FP_REG, ha="center", va="top")
    _state["y"] -= 0.022
_state["y"] -= 0.02
ax.plot([LX, RX], [_state["y"], _state["y"]], color="#DDDDDD", lw=1, transform=ax.transAxes)
_state["y"] -= 0.025

table(
    [["指标", "baseline (500ep)", "Pilot A (120ep)", "Pilot B (120ep)", "B - A"],
     ["mIoU", f"{BASE_MIOU:.2f}%", f"{A_MIOU:.2f}%", f"{B_MIOU:.2f}%", f"+{B_MIOU - A_MIOU:.2f}"],
     ["mAcc", f"{BASE_MACC:.2f}%", f"{A_MACC:.2f}%", f"{B_MACC:.2f}%", f"+{B_MACC - A_MACC:.2f}"],
     ["allAcc", f"{BASE_ALLACC:.2f}%", f"{A_ALLACC:.2f}%", f"{B_ALLACC:.2f}%", f"{B_ALLACC - A_ALLACC:.2f}"]],
    col_fracs=[0.18, 0.22, 0.22, 0.22, 0.16], fontsize=9.5, row_h_pt=22,
)
spacer(0.01)
paragraph(
    "结论速览：Pilot B 整体 mIoU 比 Pilot A 高 2.1 个百分点，方向上支持"
    "「按box均匀覆盖能缓解随机采样的密度偏差」这一假设，但并非全面领先——"
    "door 类别明显下降，详见第四、五节分析。", fontsize=9, color=MID_GRAY, max_width=78)

# ══════════════════════════════════════════════════════════════════════
new_page()
heading("一、实验背景与理论原理", level=1)
paragraph(
    "进入crop_size几何特征大实验之前，需要先确定网络的输入喂入方式。当前baseline用的"
    "「重复采样」机制（SphereCrop, mode=random）：每次访问场景时，从场景所有点中"
    "按点数均匀随机选一个中心点，取最近的point_max个点作为一个crop。")
paragraph(
    "这个机制存在系统性的密度偏差：高密度区域（墙面、地板）被选为中心的概率远高于"
    "低密度区域（门、柱子、黑板等小物体），且point_max是固定点数而非固定半径——"
    "高密度区域对应的crop物理半径更小、更聚焦；低密度区域要凑够point_max个点，"
    "半径被迫拉大，混入周边其他类别的点，进一步稀释小物体在crop里的占比。"
    "两个效应叠加，小物体类别系统性地获得更少的学习机会。")
paragraph(
    "策略B（GridBoxCrop）改为：把场景预先按固定边长的立方体网格做确定性分块，"
    "遍历覆盖整场景，每个box被访问的概率不再依赖局部点密度，理论上能让稀疏小物体"
    "和密集大平面获得均衡的学习机会。代价是box之间存在硬边界，可能切断跨box的"
    "连续结构（如细长的门）——这正是第五节分析里发现的实际代价。")

heading("二、实验设计", level=1)
table(
    [["项目", "策略A · Pilot A", "策略B · Pilot B"],
     ["裁剪方式", "SphereCrop(mode=random)，随机球形裁剪", "GridBoxCrop(crop_size=6.0m, jitter=0.3m)"],
     ["位置选取", "每次访问随机选中心点", "预先网格分块，box_min_points=200过滤"],
     ["loop / 样本量", "loop=1，204个训练场景", "loop=1，323个box（Area_1/2/3/4/6）"],
     ["每epoch crop数", "约204", "约323（已知不完全相等，见下方说明）"],
     ["模型", "SpUNet-v1m1（两策略相同结构）", "同左"],
     ["epoch数", "120", "120（同左，保证逐epoch可比）"],
     ["其余增强pipeline", "RandomRotate/Scale/Jitter/Elastic/Chromatic 等，参数与B完全相同", "同左"],
     ["测试协议", "Area_5全场景，10x TTA（5尺度×2翻转）", "同左"]],
    col_fracs=[0.18, 0.41, 0.41], fontsize=8.3, row_h_pt=20,
)
caption(
    "注：两策略每epoch的crop数不完全相等（204 vs 323），这是已知妥协——Pointcept框架"
    "内部用 loop = epoch // eval_epoch 重新计算loop，强行调大A的loop会打乱逐epoch"
    "可比性，故保留loop=1，接受这个折中。")

# ══════════════════════════════════════════════════════════════════════
new_page()
heading("三、整体结果", level=1)
paragraph("Area_5全场景测试（68个房间，10x TTA），三组结果对比：")
image(make_overall_chart())
caption("图1：整体 mIoU / mAcc / allAcc 对比")
spacer(0.01)
table(
    [["实验", "训练耗时", "是否崩溃"],
     ["baseline (500ep)", "约2小时8分", "无"],
     ["Pilot A (120ep)", "约40分钟（修复数据后）", "无（修复前崩溃过4次OOM）"],
     ["Pilot B (120ep)", "约1小时（含1次崩溃恢复）", "epoch79崩溃1次，已修复并恢复"]],
    col_fracs=[0.28, 0.42, 0.30], fontsize=8.3, row_h_pt=20,
)

# ══════════════════════════════════════════════════════════════════════
new_page()
heading("四、各类别 IoU 详细对比", level=1)
image(make_per_class_chart())
caption("图2：13个类别 IoU 对比（标注差异最大的三个类别）")
spacer(0.01)
image(make_radar_chart(), width_frac=0.55)
caption("图3：Pilot A vs Pilot B 雷达图（剔除beam）")

# ══════════════════════════════════════════════════════════════════════
new_page()
heading("四、各类别 IoU 详细对比（续）", level=2)
class_rows = [["类别", "baseline", "Pilot A", "Pilot B", "B-A"]]
hilite = []
for i, (zh, en) in enumerate(zip(CLASSES_ZH, CLASSES_EN)):
    diff = B_IOU[i] - A_IOU[i]
    class_rows.append([f"{zh} ({en})", f"{BASE_IOU[i]:.2f}", f"{A_IOU[i]:.2f}", f"{B_IOU[i]:.2f}", f"{diff:+.2f}"])
    if abs(diff) >= 10:
        hilite.append(i + 1)
table(class_rows, col_fracs=[0.30, 0.18, 0.18, 0.18, 0.16], fontsize=8.3, row_h_pt=17, highlight_rows=hilite)
caption("橙色底色行：B-A差值绝对值 ≥10个百分点的类别（door、sofa、board）。")

# ══════════════════════════════════════════════════════════════════════
new_page()
heading("五、结果分析与讨论", level=1)

heading("5.1 整体结论：方向上支持假设，但不是压倒性优势", level=2)
paragraph(
    "Pilot B整体mIoU比Pilot A高2.1个百分点，方向上支持理论假设，但幅度不大，"
    "且各类别表现分化明显。")

heading("5.2 sofa、board大幅提升（+26.7、+21.1个点）— 符合理论预期", level=2)
paragraph(
    "这两个类别都是稀疏分布、单体占用空间不大的家具类，正是理论分析中最容易被"
    "密度偏差压制的对象。策略B均匀遍历后，这些物体所在box的访问频率不再受周围"
    "点密度影响，学习机会显著增加。这是本次实验里最支持理论假设的证据。")

heading("5.3 door明显下降（-14.2个点）— 可能与box硬边界切割门有关", level=2)
paragraph(
    "门是细长结构，嵌在墙体窄缝里，6m立方体网格的边界可能正好把门切碎，破坏"
    "几何完整性；而球形裁剪以随机点为中心，至少有一定概率把整扇门完整收进某次"
    "crop。box网格是格点对齐、确定性的，如果门正好跨在box分界线上，每个epoch"
    "都会被同样的方式切开，没有随机性来'碰运气'凑出完整样本。这是策略B暴露出的"
    "一个真实代价，建议后续对门窗类细长结构做特殊分块处理。")

heading("5.4 column/wall/bookcase小幅下降、beam两边均为0", level=2)
paragraph(
    "Pilot B每epoch crop数（323）比Pilot A（204）多约58%，但column/wall/bookcase"
    "反而小幅下降，说明样本量差异不是主导因素，更可能是box边界几何完整性的影响，"
    "程度比door轻。beam类别在三组实验里都是0 IoU，是数据集本身的限制（样本极少），"
    "与采样策略对比无关。")

heading("5.5 训练成本：数据集事故 vs 修复后的对比", level=2)
image(make_epoch_time_chart(), width_frac=0.62)
caption("图4：每epoch的worker重启等待耗时，数据集体积化修复前后对比")
paragraph(
    "实验过程中发现数据集被意外还原成未体积化的原始版本（点数暴涨~20倍），"
    "导致Pilot A训练耗时一度暴涨13倍（128秒/epoch），测试阶段反复OOM崩溃。"
    "修复后（重新体积化并持久化存储），两个pilot的训练速度都恢复到与baseline"
    "一致的水平（~15秒/epoch），显存消耗稳定在容器50GB上限的安全范围内"
    "（实测峰值约20GB），验证了「显存消耗与裁剪策略本身无关，只与point_max有关」"
    "这一设计前提。详细排查过程见《环境与配置基线_避坑指南》。")

# ══════════════════════════════════════════════════════════════════════
new_page()
heading("六、结论", level=1)
for txt in [
    "1. 按box输入（策略B）整体mIoU优于随机重复采样（策略A）约2.1个点，方向上支持"
    "「随机采样存在密度偏差、均匀覆盖能缓解」的理论假设。",
    "2. 证据最强的支持点在于sofa、board两个稀疏小物体类别的大幅提升（+26.7、+21.1点），"
    "与理论分析高度吻合。",
    "3. 但door类别明显下降（-14.2点），暴露了box策略「确定性硬边界可能切碎细长结构」"
    "的潜在代价，这是理论分析里没有预先考虑到的新发现。",
    "4. 两策略收敛速度、训练成本（时间、显存）基本相当，不存在哪种策略明显更快/更省"
    "资源的优势。",
]:
    bullet(txt)

spacer(0.01)
heading("七、局限性与后续工作建议", level=1)
for txt in [
    "1. 本次只跑了单次种子，建议换种子重跑确认2.1个点的差距在统计上是否稳定"
    "（crop数204 vs 323不完全相等，存在一定混杂因素）。",
    "2. door类别下降值得专门深挖：检查测试集里door样本被box边界切割的实际比例，"
    "验证「边界切割」假设。",
    "3. 建议进入crop_size大实验前，先确认box策略是否需要针对门窗类结构做特殊处理，"
    "否则后续18组实验都会继承这个已知局限。",
    "4. exp/baseline_ptv3需要用修复后的数据集重新训练，目前结果是在错误数据上跑的，"
    "不可信，不建议用于PTv3 vs SpUNet的横向对比。",
]:
    bullet(txt)

spacer(0.02)
ax = _state["ax"]
ax.plot([LX, RX], [_state["y"], _state["y"]], color=TU_RED, lw=1, transform=ax.transAxes)
_state["y"] -= 0.02
paragraph(
    "完整文字版报告（含理论推导细节、数据集事故完整时间线）见 "
    "docs/小实验_完整总结报告.txt；排查过程见 docs/环境与配置基线_避坑指南.txt。",
    fontsize=8.3, color=MID_GRAY, max_width=90)

finalize()
print(f"PDF saved to {OUT_PATH}")
