"""
生成 S3DIS 基线实验 PDF 报告
依赖: reportlab, matplotlib
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import io
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── 颜色主题 ──────────────────────────────────────────────────────────────────
TU_RED      = colors.HexColor("#C40D1E")   # TU Berlin 红
DARK_GRAY   = colors.HexColor("#2C2C2C")
MID_GRAY    = colors.HexColor("#6B6B6B")
LIGHT_GRAY  = colors.HexColor("#F2F2F2")
HEADER_BG   = colors.HexColor("#1A1A2E")
SPUNET_C    = "#2196F3"   # 蓝
PTV3_C      = "#E91E63"   # 红粉

# ── 数据 ─────────────────────────────────────────────────────────────────────
CLASSES = ["ceiling","floor","wall","beam","column","window",
           "door","table","chair","sofa","bookcase","board","clutter"]

SP_CLASS_IOU = [92.2, 97.2, 82.6,  0.0, 25.6, 58.1, 70.9, 80.7, 88.1, 47.1, 75.2, 68.2, 57.5]
SP_CLASS_ACC = [96.5, 99.5, 96.6,  0.0, 27.6, 60.8, 84.7, 89.3, 94.5, 48.8, 83.3, 76.9, 68.1]
PT_CLASS_IOU = [94.1, 98.1, 83.6,  0.0, 32.8, 57.4, 61.1, 81.8, 90.5, 59.2, 75.3, 75.8, 61.3]
PT_CLASS_ACC = [96.6, 99.2, 97.1,  0.0, 35.6, 59.0, 68.2, 92.7, 96.6, 64.2, 84.1, 86.7, 72.5]

SP_MIOU, SP_MACC, SP_ALLACC, SP_BEST = 64.87, 71.29, 89.05, 62.75
PT_MIOU, PT_MACC, PT_ALLACC, PT_BEST = 67.01, 73.28, 90.10, 65.44

SP_MIOU_NB = np.mean([v for i,v in enumerate(SP_CLASS_IOU) if i != 3])  # w/o beam
PT_MIOU_NB = np.mean([v for i,v in enumerate(PT_CLASS_IOU) if i != 3])

# ── 图表生成 ──────────────────────────────────────────────────────────────────
def make_bar_chart():
    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = np.arange(len(CLASSES))
    w = 0.38
    bars1 = ax.bar(x - w/2, SP_CLASS_IOU, w, label="SpUNet", color=SPUNET_C, alpha=0.88, zorder=3)
    bars2 = ax.bar(x + w/2, PT_CLASS_IOU, w, label="PTv3",   color=PTV3_C,  alpha=0.88, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(CLASSES, rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("IoU (%)", fontsize=10)
    ax.set_ylim(0, 108)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # 标注 mIoU 均值线
    ax.axhline(SP_MIOU, color=SPUNET_C, linestyle=":", linewidth=1.4, alpha=0.7)
    ax.axhline(PT_MIOU, color=PTV3_C,   linestyle=":", linewidth=1.4, alpha=0.7)
    ax.text(12.7, SP_MIOU + 1.2, f"SpUNet\nmIoU={SP_MIOU:.1f}%", color=SPUNET_C, fontsize=7.5, ha="right")
    ax.text(12.7, PT_MIOU - 4.5, f"PTv3\nmIoU={PT_MIOU:.1f}%",   color=PTV3_C,   fontsize=7.5, ha="right")
    # beam 注释
    ax.annotate("beam\n(absent\nin Area_5)", xy=(3, 2), fontsize=7.5,
                color="gray", ha="center", va="bottom")
    ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
    ax.set_title("Per-Class IoU — S3DIS Area_5 (500 epoch)", fontsize=11, pad=10)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf

def make_radar_chart():
    # 去掉 beam(0.0)，做雷达图对比
    labels  = [c for i,c in enumerate(CLASSES) if i != 3]
    sp_vals = [v for i,v in enumerate(SP_CLASS_IOU) if i != 3]
    pt_vals = [v for i,v in enumerate(PT_CLASS_IOU) if i != 3]
    N = len(labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    sp_vals_p = sp_vals + [sp_vals[0]]
    pt_vals_p = pt_vals + [pt_vals[0]]
    angles_p  = angles  + [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles_p, sp_vals_p, color=SPUNET_C, linewidth=2, label="SpUNet")
    ax.fill(angles_p, sp_vals_p, color=SPUNET_C, alpha=0.15)
    ax.plot(angles_p, pt_vals_p, color=PTV3_C,   linewidth=2, label="PTv3")
    ax.fill(angles_p, pt_vals_p, color=PTV3_C,   alpha=0.15)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25","50","75","100"], fontsize=7, color="gray")
    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=9)
    ax.set_title("Per-Class IoU Radar\n(beam excluded)", fontsize=10, pad=18)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf

# ── PDF 构建 ──────────────────────────────────────────────────────────────────
OUT_PATH = "/workspace/baseline_report.pdf"
doc = SimpleDocTemplate(
    OUT_PATH, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
)
W = A4[0] - 4*cm   # 可用宽度

styles = getSampleStyleSheet()
def S(name, **kw):
    return ParagraphStyle(name, parent=styles["Normal"], **kw)

title_style   = S("Title",   fontSize=20, textColor=DARK_GRAY, spaceAfter=4,  alignment=TA_CENTER, fontName="Helvetica-Bold")
sub_style     = S("Sub",     fontSize=11, textColor=MID_GRAY,  spaceAfter=2,  alignment=TA_CENTER)
h1_style      = S("H1",      fontSize=13, textColor=TU_RED,    spaceBefore=14, spaceAfter=4, fontName="Helvetica-Bold")
h2_style      = S("H2",      fontSize=10, textColor=DARK_GRAY, spaceBefore=8,  spaceAfter=3, fontName="Helvetica-Bold")
body_style    = S("Body",    fontSize=9,  textColor=DARK_GRAY, spaceAfter=4,  leading=14)
caption_style = S("Caption", fontSize=8,  textColor=MID_GRAY,  spaceAfter=6,  alignment=TA_CENTER, fontName="Helvetica-Oblique")
note_style    = S("Note",    fontSize=8,  textColor=MID_GRAY,  spaceBefore=4, spaceAfter=4, leading=12)

def hr(): return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD"), spaceAfter=6, spaceBefore=2)

def table_style_base(header_rows=1):
    return TableStyle([
        # header
        ("BACKGROUND",  (0,0), (-1, header_rows-1), HEADER_BG),
        ("TEXTCOLOR",   (0,0), (-1, header_rows-1), colors.white),
        ("FONTNAME",    (0,0), (-1, header_rows-1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1, header_rows-1), 9),
        ("ALIGN",       (0,0), (-1, header_rows-1), "CENTER"),
        ("TOPPADDING",  (0,0), (-1, header_rows-1), 5),
        ("BOTTOMPADDING",(0,0),(-1, header_rows-1), 5),
        # body
        ("FONTSIZE",    (0, header_rows), (-1,-1), 8.5),
        ("ALIGN",       (1, header_rows), (-1,-1), "CENTER"),
        ("ALIGN",       (0, header_rows), (0,-1),  "LEFT"),
        ("TOPPADDING",  (0, header_rows), (-1,-1), 3),
        ("BOTTOMPADDING",(0,header_rows), (-1,-1), 3),
        ("ROWBACKGROUNDS",(0, header_rows),(-1,-1),[colors.white, LIGHT_GRAY]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("LINEBELOW",   (0,0), (-1,0),  1.2, HEADER_BG),
        ("ROUNDEDCORNERS", [3]),
    ])

story = []

# ─── 封面区 ───────────────────────────────────────────────────────────────────
story.append(Spacer(1, 0.8*cm))
story.append(Paragraph("Baseline Experiment Report", title_style))
story.append(Paragraph("S3DIS Area_5 · SpUNet &amp; PTv3 · 500 Epochs", sub_style))
story.append(Paragraph("TU Berlin · MDT · Yucan Luo", sub_style))
story.append(Paragraph(datetime.now().strftime("%Y-%m-%d"), sub_style))
story.append(Spacer(1, 0.3*cm))
story.append(HRFlowable(width="100%", thickness=2, color=TU_RED, spaceAfter=10))

# ─── 1. 实验概览 ──────────────────────────────────────────────────────────────
story.append(Paragraph("1. Experiment Overview", h1_style))
story.append(Paragraph(
    "This report summarizes the baseline experiments for the S3DIS indoor semantic segmentation benchmark. "
    "Two state-of-the-art architectures were trained under default configurations for 500 epochs on "
    "Areas 1–4 &amp; 6, and evaluated on the held-out <b>Area_5</b>. "
    "These results serve as the reference baseline for the subsequent Design of Experiments (DoE) study.",
    body_style
))

exp_data = [
    ["Parameter", "SpUNet", "PTv3"],
    ["Architecture", "Sparse U-Net (voxel-based)", "Point Transformer v3 (point-based)"],
    ["Dataset",      "S3DIS",                       "S3DIS"],
    ["Train split",  "Area 1, 2, 3, 4, 6",          "Area 1, 2, 3, 4, 6"],
    ["Test split",   "Area 5",                       "Area 5"],
    ["Epochs",       "500",                          "500"],
    ["Batch size",   "12",                           "6"],
    ["Optimizer",    "AdamW",                        "AdamW"],
    ["LR schedule",  "OneCycleLR",                   "OneCycleLR"],
    ["Grid size",    "0.02 m",                       "0.02 m"],
    ["TTA (test)",   "10-aug (scale + flip)",        "10-aug (scale + flip)"],
    ["VRAM",         "~24 GB peak",                  "~24 GB peak"],
]
t = Table(exp_data, colWidths=[4.5*cm, (W-4.5*cm)/2, (W-4.5*cm)/2])
t.setStyle(table_style_base())
story.append(t)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph("Table 1: Experimental configuration.", caption_style))

# ─── 2. 汇总结果 ──────────────────────────────────────────────────────────────
story.append(Paragraph("2. Summary Results", h1_style))

sum_data = [
    ["Metric", "SpUNet", "PTv3", "Delta (PTv3 - SpUNet)"],
    ["mIoU (%)",                 f"{SP_MIOU:.2f}", f"{PT_MIOU:.2f}", f"+{PT_MIOU-SP_MIOU:.2f}"],
    ["mIoU w/o beam (%)",        f"{SP_MIOU_NB:.2f}", f"{PT_MIOU_NB:.2f}", f"+{PT_MIOU_NB-SP_MIOU_NB:.2f}"],
    ["mAcc (%)",                 f"{SP_MACC:.2f}", f"{PT_MACC:.2f}", f"+{PT_MACC-SP_MACC:.2f}"],
    ["allAcc (%)",               f"{SP_ALLACC:.2f}", f"{PT_ALLACC:.2f}", f"+{PT_ALLACC-SP_ALLACC:.2f}"],
    ["Best mIoU during train (%)", f"{SP_BEST:.2f}", f"{PT_BEST:.2f}", f"+{PT_BEST-SP_BEST:.2f}"],
]
col_w = [W*0.38, W*0.18, W*0.18, W*0.26]
t2 = Table(sum_data, colWidths=col_w)
ts2 = table_style_base()
# highlight mIoU row
ts2.add("FONTNAME", (0,1), (-1,1), "Helvetica-Bold")
ts2.add("TEXTCOLOR", (1,1), (-1,1), colors.HexColor("#1565C0"))
ts2.add("TEXTCOLOR", (3,2), (3,-1), colors.HexColor("#2E7D32"))
t2.setStyle(ts2)
story.append(t2)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph("Table 2: Summary metrics on S3DIS Area_5.", caption_style))
story.append(Paragraph(
    "<b>Note:</b> PTv3 outperforms SpUNet by <b>+2.14% mIoU</b> on Area_5. "
    "The 'beam' class scores 0.0 IoU for both models due to its near-absence in Area_5 — "
    "this is a known property of the S3DIS dataset and consistent with published results. "
    "A separate mIoU excluding beam is reported for reference.",
    note_style
))

# ─── 3. 各类别 IoU ────────────────────────────────────────────────────────────
story.append(Paragraph("3. Per-Class Results", h1_style))

cls_header = ["Class", "SpUNet IoU", "SpUNet Acc", "PTv3 IoU", "PTv3 Acc", "Delta IoU"]
cls_data = [cls_header]
for i, cls in enumerate(CLASSES):
    delta = PT_CLASS_IOU[i] - SP_CLASS_IOU[i]
    delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
    cls_data.append([
        cls,
        f"{SP_CLASS_IOU[i]:.1f}",
        f"{SP_CLASS_ACC[i]:.1f}",
        f"{PT_CLASS_IOU[i]:.1f}",
        f"{PT_CLASS_ACC[i]:.1f}",
        delta_str,
    ])
col_w3 = [2.8*cm, 2.1*cm, 2.1*cm, 2.1*cm, 2.1*cm, 2.1*cm]
t3 = Table(cls_data, colWidths=col_w3)
ts3 = table_style_base()
# beam 行变灰
ts3.add("TEXTCOLOR",  (0, 4), (-1, 4), colors.HexColor("#AAAAAA"))
ts3.add("FONTNAME",   (0, 4), (-1, 4), "Helvetica-Oblique")
# 正 delta 绿、负 delta 红
for i, cls in enumerate(CLASSES):
    delta = PT_CLASS_IOU[i] - SP_CLASS_IOU[i]
    row = i + 1
    col = 5
    c = colors.HexColor("#2E7D32") if delta > 0 else (colors.HexColor("#C62828") if delta < 0 else DARK_GRAY)
    ts3.add("TEXTCOLOR", (col, row), (col, row), c)
    ts3.add("FONTNAME",  (col, row), (col, row), "Helvetica-Bold")
t3.setStyle(ts3)
story.append(t3)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "Table 3: Per-class IoU and accuracy. Green delta = PTv3 better; red = SpUNet better. "
    "Beam class (italic, gray) is near-absent in Area_5.",
    caption_style
))

# ─── 4. 可视化 ────────────────────────────────────────────────────────────────
story.append(Paragraph("4. Visualization", h1_style))

bar_buf = make_bar_chart()
radar_buf = make_radar_chart()

bar_img   = Image(bar_buf,   width=W,        height=W*0.38)
radar_img = Image(radar_buf, width=W*0.46,   height=W*0.46)

story.append(bar_img)
story.append(Paragraph("Figure 1: Per-class IoU comparison (dashed lines = overall mIoU).", caption_style))
story.append(Spacer(1, 0.3*cm))

# radar 居中
radar_table = Table([[radar_img]], colWidths=[W])
radar_table.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
story.append(radar_table)
story.append(Paragraph("Figure 2: Radar chart of per-class IoU (beam excluded).", caption_style))

# ─── 5. 关键发现 ──────────────────────────────────────────────────────────────
story.append(Paragraph("5. Key Findings", h1_style))

findings = [
    ["#", "Finding"],
    ["1", f"PTv3 achieves mIoU = {PT_MIOU:.2f}%, outperforming SpUNet ({SP_MIOU:.2f}%) by +{PT_MIOU-SP_MIOU:.2f}% on Area_5."],
    ["2", "Both models achieve near-perfect results on ceiling (>92%) and floor (>97%)."],
    ["3", f"PTv3 shows large gains on sofa (+{PT_CLASS_IOU[9]-SP_CLASS_IOU[9]:.1f}%) and board (+{PT_CLASS_IOU[11]-SP_CLASS_IOU[11]:.1f}%), likely benefiting from serialized attention."],
    ["4", f"SpUNet outperforms PTv3 on door (+{SP_CLASS_IOU[6]-PT_CLASS_IOU[6]:.1f}%), suggesting voxel-based methods capture thin structures differently."],
    ["5", "Beam scores 0.0 for both models — a known artifact of Area_5's class distribution, not a model deficiency."],
    ["6", "Both models show poor column IoU (<33%), indicating a challenging category for further DoE investigation."],
]
t4 = Table(findings, colWidths=[0.7*cm, W-0.7*cm])
t4.setStyle(table_style_base())
story.append(t4)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph("Table 4: Key experimental findings.", caption_style))

# ─── 6. 文件路径 ──────────────────────────────────────────────────────────────
story.append(Paragraph("6. Artifact Locations", h1_style))
paths_data = [
    ["Artifact", "Path"],
    ["SpUNet checkpoint",    "/workspace/Pointcept/exp/baseline_spunet/model/model_best.pth"],
    ["PTv3 checkpoint",      "/workspace/Pointcept/exp/baseline_ptv3/model/model_best.pth"],
    ["SpUNet log",           "/workspace/logs/spunet_baseline.log"],
    ["PTv3 training log",    "/workspace/logs/ptv3_baseline.log"],
    ["PTv3 test log",        "/workspace/logs/ptv3_baseline_test.log"],
    ["PTv3 pred files",      "/workspace/Pointcept/exp/baseline_ptv3/result/"],
    ["This report (MD)",     "/workspace/baseline_results.md"],
    ["This report (PDF)",    "/workspace/baseline_report.pdf"],
]
t5 = Table(paths_data, colWidths=[3.8*cm, W-3.8*cm])
ts5 = table_style_base()
ts5.add("FONTSIZE", (1,1), (1,-1), 7.5)
t5.setStyle(ts5)
story.append(t5)
story.append(Paragraph("Table 5: Artifact file locations (all on persistent network storage).", caption_style))

# ─── 页脚备注 ─────────────────────────────────────────────────────────────────
story.append(Spacer(1, 0.5*cm))
story.append(hr())
story.append(Paragraph(
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
    "TU Berlin MDT · Master Thesis: Development of an Enhanced Semantic Segmentation Method "
    "for Large-Scale Point Cloud Processing · Yucan Luo",
    note_style
))

# ─── 构建 ────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF saved: {OUT_PATH}")
