"""
两周实验计划（更新版）PDF 生成脚本
基于已完成的基线实验结果，详细说明每一步操作
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
F = 'STSong-Light'

# ── 颜色 ──────────────────────────────────────────────────────────────────
TU_RED    = colors.HexColor("#C40D1E")
DARK_BG   = colors.HexColor("#1A1A2E")
BLUE_HDR  = colors.HexColor("#1a3a5c")
DONE_BG   = colors.HexColor("#1B5E20")
LIGHT_GRN = colors.HexColor("#E8F5E9")
LIGHT_BLU = colors.HexColor("#E3F2FD")
LIGHT_YLW = colors.HexColor("#FFFDE7")
ROW_A     = colors.HexColor("#f0f4fa")
ROW_B     = colors.white
GRAY_LT   = colors.HexColor("#F4F4F4")
GRAY_BD   = colors.HexColor("#bbbbbb")
RED_DARK  = colors.HexColor("#B71C1C")

# ── 样式 ──────────────────────────────────────────────────────────────────
def make_styles():
    def s(name, **kw):
        defaults = dict(fontName=F, fontSize=10, leading=16, wordWrap='CJK')
        defaults.update(kw)
        return ParagraphStyle(name, **defaults)

    return dict(
        title  = s('title', fontSize=17, leading=24, alignment=TA_CENTER,
                   textColor=DARK_BG, spaceAfter=4),
        sub    = s('sub',   fontSize=10, leading=15, alignment=TA_CENTER,
                   textColor=colors.HexColor('#555555'), spaceAfter=16),
        h1     = s('h1',   fontSize=13, leading=20, textColor=colors.white,
                   backColor=DARK_BG, spaceBefore=14, spaceAfter=6,
                   leftIndent=4, borderPad=5),
        h1done = s('h1done', fontSize=13, leading=20, textColor=colors.white,
                   backColor=DONE_BG, spaceBefore=14, spaceAfter=6,
                   leftIndent=4, borderPad=5),
        h2     = s('h2',   fontSize=11, leading=18, textColor=BLUE_HDR,
                   spaceBefore=10, spaceAfter=4),
        h3     = s('h3',   fontSize=10, leading=16, textColor=TU_RED,
                   spaceBefore=8, spaceAfter=3),
        body   = s('body', fontSize=9.5, leading=16, spaceAfter=4,
                   alignment=TA_JUSTIFY),
        blt    = s('blt',  fontSize=9.5, leading=16, leftIndent=14,
                   spaceAfter=3),
        blt2   = s('blt2', fontSize=9,   leading=15, leftIndent=28,
                   spaceAfter=2),
        note   = s('note', fontSize=9,   leading=14,
                   textColor=colors.HexColor('#555555'),
                   backColor=LIGHT_YLW,
                   borderColor=colors.HexColor('#f0c040'),
                   borderWidth=0.8, borderPad=5, leftIndent=6, spaceAfter=6),
        check  = s('check', fontSize=9, leading=15, leftIndent=14,
                   textColor=colors.HexColor('#333333'), spaceAfter=2),
        done   = s('done', fontSize=9.5, leading=16, leftIndent=14,
                   textColor=DONE_BG, spaceAfter=3),
    )

S = make_styles()

def H1(t):      return Paragraph(f'  {t}', S['h1'])
def H1d(t):     return Paragraph(f'  {t}  ✓ 已完成', S['h1done'])
def H2(t):      return Paragraph(t, S['h2'])
def H3(t):      return Paragraph(t, S['h3'])
def P(t):       return Paragraph(t, S['body'])
def B(t):       return Paragraph(f'• {t}', S['blt'])
def B2(t):      return Paragraph(f'◦ {t}', S['blt2'])
def NOTE(t):    return Paragraph(f'★  {t}', S['note'])
def CHK(t):     return Paragraph(f'☐  {t}', S['check'])
def DONE(t):    return Paragraph(f'✓  {t}', S['done'])
def SP(h=6):    return Spacer(1, h)
def HR():       return HRFlowable(width='100%', thickness=0.5,
                                  color=GRAY_BD, spaceAfter=4)

def tbl(data, col_w, hdr_bg=BLUE_HDR, row_colors=None, fontsize=8.5):
    if row_colors is None:
        row_colors = [ROW_A, ROW_B]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,-1), F),
        ('FONTSIZE',   (0,0), (-1,-1), fontsize),
        ('BACKGROUND', (0,0), (-1,0),  hdr_bg),
        ('TEXTCOLOR',  (0,0), (-1,0),  colors.white),
        ('FONTSIZE',   (0,0), (-1,0),  fontsize + 0.5),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), row_colors),
        ('GRID',       (0,0), (-1,-1), 0.4, GRAY_BD),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

# ══════════════════════════════════════════════════════════════════════════
def build():
    story = []
    W = A4[0] - 4*cm  # 可用宽度

    # ── 页眉横线 + 标题 ──────────────────────────────────────────────────
    story += [
        HRFlowable(width='100%', thickness=3, color=TU_RED, spaceAfter=8),
        Paragraph('大规模点云语义分割参数优化', S['title']),
        Paragraph('两周 DoE 实验计划（更新版 v2）', S['title']),
        Paragraph('TU Berlin · MDT 研究组 · Yucan Luo · 更新日期：2026-06-14', S['sub']),
        HRFlowable(width='100%', thickness=1, color=TU_RED, spaceAfter=12),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # 0. 总体目标
    # ══════════════════════════════════════════════════════════════════════
    story += [H1('0  论文核心目标与实验逻辑'), SP()]
    story += [P('本论文旨在通过实验设计方法（Design of Experiments, DoE），系统建立处理参数与分割精度之间的'
                '定量关系，最终实现自适应参数选择模块：给定场景统计特征（点密度、场景范围）和硬件约束（显存），'
                '自动推荐最优的 grid_size、point_max、step、jitter 等参数组合。')]
    story += [P('实验需要回答两个核心问题：')]
    story += [B('哪些参数对 mIoU 影响最显著？（筛选阶段，Plackett-Burman 设计，12 runs）'),
              B('显著参数与 mIoU / 显存之间的精确函数关系是什么？（建模阶段，Box-Behnken 设计，15 runs）')]
    story += [SP(4), NOTE('实验平台：Pointcept 框架（已在服务器上配置完毕）。所有参数均通过修改 Pointcept '
                          '的 .py 配置文件来控制，无需修改模型源码。')]

    # ══════════════════════════════════════════════════════════════════════
    # 1. 基线实验（已完成）
    # ══════════════════════════════════════════════════════════════════════
    story += [H1d('1  基线实验（第1天，2026-06-14）'), SP()]
    story += [P('已在 S3DIS Area_5 测试集上完成两个模型各 500 epoch 的训练与评测，获得以下基准数据。'
                '后续所有 DoE 实验结果均与此基线对比，量化参数变化对性能的影响。')]

    base_data = [
        ['指标', 'SpUNet（基线）', 'PTv3（基线）', 'PTv3 − SpUNet'],
        ['mIoU (%)',         '64.87', '67.01', '+2.14'],
        ['mAcc (%)',         '71.29', '73.28', '+1.99'],
        ['allAcc (%)',       '89.05', '90.10', '+1.05'],
        ['mIoU w/o beam (%)', '70.28', '72.58', '+2.30'],
        ['训练时长（估计）', '约 20 小时', '约 52 小时', 'PTv3 慢 ~2.6×'],
        ['训练 batch_size',  '12', '6', '—'],
        ['峰值显存',         '~8 GB', '~14 GB', '—'],
    ]
    story += [tbl(base_data, [4.5*cm, 3.5*cm, 3.5*cm, 3.5*cm],
                  hdr_bg=DONE_BG, fontsize=8.5), SP(8)]

    story += [H3('基线实验的关键发现（对 DoE 设计的启示）')]
    story += [
        B('PTv3 整体 mIoU（67.01%）优于 SpUNet（64.87%），提升 +2.14%，说明两种架构对参数变化的响应规律可能不同。'),
        B('门（door）类别：SpUNet（70.9%）反超 PTv3（61.1%），差值 −9.8%，提示块大小对门框结构影响显著，'
          'DoE 分析时应关注 per-class IoU 而非只看 mIoU。'),
        B('柱子（column）两者均低于 35%，是最难分类别，对空间分辨率（grid_size）最敏感，适合纳入重点分析。'),
        B('PTv3 的 batch_size 仅为 6，point_max 增大会更快导致 OOM，需为两模型分别设定参数上界。'),
        B('checkpoint 已保存：SpUNet → exp/baseline_spunet/model/model_best.pth（Best mIoU 62.75%），'
          'PTv3 → exp/baseline_ptv3/model/model_best.pth（Best mIoU 65.44%）。'),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # 2. 实验参数空间
    # ══════════════════════════════════════════════════════════════════════
    story += [H1('2  实验参数空间定义'), SP()]
    story += [P('下表列出本次 DoE 实验涉及的 4 个主要因子，以及在 Pointcept 配置文件中的对应位置。'
                '修改参数时，只需在对应配置文件中找到该字段并修改数值即可。')]

    param_data = [
        ['因子', '取值范围', 'Pointcept 配置文件中的字段', '物理含义'],
        ['grid_size\n（体素大小）',
         '低: 0.01 m\n中: 0.02 m\n高: 0.04 m',
         'transform 列表中\nGridSample 的 grid_size 字段',
         '体素分辨率：越小保留点越多，\n显存占用越大，细节越丰富'],
        ['point_max\n（块内最大点数）',
         '低: 40,000\n中: 80,000\n高: 120,000',
         'transform 列表中\nSphereCrop 的 point_max 字段',
         '每个训练块的点数上限：\n越大感受野越大，显存占用越高'],
        ['jitter_sigma\n（坐标抖动）',
         '低: 0.005 m\n中: 0.05 m\n高: 0.20 m',
         'transform 列表中\nRandomJitter 的 sigma 字段',
         '训练数据增强的扰动幅度：\n过大会破坏几何结构'],
        ['dropout_ratio\n（随机丢弃率）',
         '低: 0.0\n中: 0.1\n高: 0.2',
         'transform 列表中\nRandomDropout 的 dropout_ratio 字段',
         '随机丢弃训练实例的概率：\n防止过拟合，影响较小'],
    ]
    story += [tbl(param_data, [3.0*cm, 3.2*cm, 5.3*cm, 4.0*cm], fontsize=8.5), SP(6)]
    story += [NOTE('参数约束：grid_size 增大时，point_max 应相应调整，保持物理块尺寸（point_max × grid_size³）'
                   '基本一致，避免感受野差异干扰分析。中心点条件：grid_size=0.02, point_max=80k, '
                   'jitter=0.05, dropout=0.1（即默认配置，与基线一致）。')]

    # ══════════════════════════════════════════════════════════════════════
    # 3. DoE 实验矩阵
    # ══════════════════════════════════════════════════════════════════════
    story += [H1('3  DoE 实验设计矩阵'), SP()]

    # 3.1 PB
    story += [H2('3.1  第一阶段：Plackett-Burman 筛选实验（12 runs）')]
    story += [P('目标：用12次实验识别对 mIoU 影响最显著的参数。每个参数取高（+1）低（−1）两个水平，'
                '中心点（0）重复3次用于估计实验误差。先用 SpUNet 跑全部12组，再用 PTv3 跑其中6个代表性组次。')]

    pb_data = [
        ['Run', 'grid_size', 'point_max', 'jitter_sigma', 'dropout_ratio', '说明'],
        ['01', '+1  (0.04 m)', '−1  (40k)', '+1  (0.20 m)', '−1  (0.0)', ''],
        ['02', '−1  (0.01 m)', '+1  (120k)', '+1  (0.20 m)', '+1  (0.2)', ''],
        ['03', '+1  (0.04 m)', '+1  (120k)', '−1  (0.005 m)', '+1  (0.2)', ''],
        ['04', '−1  (0.01 m)', '+1  (120k)', '+1  (0.20 m)', '−1  (0.0)', ''],
        ['05', '+1  (0.04 m)', '−1  (40k)', '−1  (0.005 m)', '+1  (0.2)', ''],
        ['06', '−1  (0.01 m)', '−1  (40k)', '+1  (0.20 m)', '+1  (0.2)', ''],
        ['07', '+1  (0.04 m)', '+1  (120k)', '−1  (0.005 m)', '−1  (0.0)', ''],
        ['08', '−1  (0.01 m)', '−1  (40k)', '−1  (0.005 m)', '−1  (0.0)', ''],
        ['09', '0  (0.02 m)', '0  (80k)', '0  (0.05 m)', '0  (0.1)', '中心点 × 3'],
        ['10', '0  (0.02 m)', '0  (80k)', '0  (0.05 m)', '0  (0.1)', '中心点 × 3'],
        ['11', '0  (0.02 m)', '0  (80k)', '0  (0.05 m)', '0  (0.1)', '中心点 × 3'],
        ['12', '−1  (0.01 m)', '+1  (120k)', '−1  (0.005 m)', '+1  (0.2)', ''],
    ]
    story += [tbl(pb_data, [1.2*cm, 3.2*cm, 2.8*cm, 3.0*cm, 3.0*cm, 2.2*cm], fontsize=8), SP(4)]
    story += [P('PTv3 重点验证的6组：Run 01, 03, 04, 07, 08, 09（覆盖高低水平的代表性组合）。')]

    story += [SP(6), H2('3.2  第二阶段：Box-Behnken 精细实验（15 runs）')]
    story += [P('目标：对 PB 阶段筛选出的显著参数（预计 2~3 个）建立二阶响应面模型，捕捉交互效应和非线性关系。'
                '以下矩阵假设显著参数为 grid_size、point_max、jitter（实际参数根据第7天分析结果确定）。')]

    bbd_data = [
        ['Run', 'grid_size (x₁)', 'point_max (x₂)', 'jitter (x₃)', '实验目的'],
        ['01', '−1', '−1', '0', '边角点'],
        ['02', '+1', '−1', '0', '边角点'],
        ['03', '−1', '+1', '0', '边角点'],
        ['04', '+1', '+1', '0', '边角点'],
        ['05', '−1', '0', '−1', '边角点'],
        ['06', '+1', '0', '−1', '边角点'],
        ['07', '−1', '0', '+1', '边角点'],
        ['08', '+1', '0', '+1', '边角点'],
        ['09', '0', '−1', '−1', '边角点'],
        ['10', '0', '+1', '−1', '边角点'],
        ['11', '0', '−1', '+1', '边角点'],
        ['12', '0', '+1', '+1', '边角点'],
        ['13', '0', '0', '0', '中心点（重复3次）'],
        ['14', '0', '0', '0', '中心点（重复3次）'],
        ['15', '0', '0', '0', '中心点（重复3次）'],
    ]
    story += [tbl(bbd_data, [1.2*cm, 3.5*cm, 3.5*cm, 3.0*cm, 4.2*cm], fontsize=8.5), SP(4)]
    story += [P('拟合目标：mIoU = β₀ + β₁x₁ + β₂x₂ + β₃x₃ + β₁₂x₁x₂ + β₁₃x₁x₃ + β₂₃x₂x₃ + β₁₁x₁² + β₂₂x₂² + β₃₃x₃²'),
              P('显存模型：Memory = γ₀ + γ₁·point_max + γ₂·grid_size + γ₁₂·point_max·grid_size')]

    story += [SP(6), H2('3.3  附加实验：Spatial Alignment 对比')]
    story += [P('任务书要求量化 spatial alignment（滑窗推理时重叠区域一致性处理）对分割精度的影响：')]
    align_data = [
        ['条件', '处理方式', '预期效果'],
        ['条件 A（有 alignment）',
         '对重叠区域（相邻块的共有点）的预测 logits 取多次预测的加权平均，再输出最终标签',
         '边界处预测更一致，mIoU 更高，但推理时间略长'],
        ['条件 B（无 alignment）',
         '每个块独立推理，重叠区域随机保留最后一个块的预测结果，不做融合',
         '推理速度快，但边界点类别可能不一致'],
    ]
    story += [tbl(align_data, [4.0*cm, 6.5*cm, 5.0*cm], fontsize=8.5)]
    story += [SP(4), P('评估指标：mIoU 差值、边界点专项 IoU（距离相邻块边界 < 0.5m 的点）、推理时间差值。')]

    # ══════════════════════════════════════════════════════════════════════
    # 4. 详细日程
    # ══════════════════════════════════════════════════════════════════════
    story += [PageBreak(), H1('4  两周详细日程（剩余13天）'), SP()]

    # 总日程表
    sched_data = [
        ['时间', '日期', '任务', '预期产出', 'GPU 占用'],
        ['第1天', '6月14日\n（已完成）', 'SpUNet + PTv3 基线实验\n（500 epoch × 2）',
         'SpUNet 64.87%\nPTv3 67.01%', '~72 小时\n（已完成）'],
        ['第2天', '6月15日', 'DoE 配置文件准备\n（18个配置文件）',
         '12个SpUNet配置\n6个PTv3配置', '0 小时\n（配置工作）'],
        ['第3-4天', '6月16-17日', 'PB筛选实验：SpUNet\n（12 runs × 500 epoch）',
         '12组 mIoU +\n显存峰值数据', '~12 小时\n（连续运行）'],
        ['第5-6天', '6月18-19日', 'PB筛选实验：PTv3\n（6组关键 runs）',
         'PTv3 6组\nmIoU 数据', '~15 小时\n（连续运行）'],
        ['第7天', '6月20日', '统计分析 PB 结果\n主效应图 + 显著性检验',
         '显著参数列表\nBBD 实验矩阵', '0 小时\n（分析工作）'],
        ['第8-10天', '6月21-23日', 'BBD 精细实验\n（15 runs + PTv3验证）',
         '二阶响应面数据\n（共18组）', '~25 小时\n（连续运行）'],
        ['第11-12天', '6月24-25日', '回归模型拟合\nSpatial Alignment 对比实验',
         '回归公式（R²>0.85）\nAlignment 增益数据', '~4 小时\n（推理实验）'],
        ['第13-14天', '6月26-27日', '跨数据集验证\n数据整理 + 图表制作',
         '验证结果\n最终实验报告数据', '~8 小时'],
    ]
    story += [tbl(sched_data, [1.6*cm, 2.4*cm, 4.8*cm, 4.0*cm, 2.5*cm],
                  hdr_bg=DARK_BG, fontsize=8.5), SP(10)]

    # ── 第2天 ─────────────────────────────────────────────────────────────
    story += [KeepTogether([
        H2('第2天（6月15日）：DoE 配置文件准备'),
        P('目标：为12个PB实验和6个PTv3实验各创建一个独立的 Pointcept 配置文件，确保每个实验参数唯一、'
          '结果可复现。这是纯文件操作，不占用GPU。'),
        SP(4),
        H3('操作步骤'),
    ])]
    story += [
        B('进入 /workspace/Pointcept/configs/s3dis/ 目录，找到两个基准配置文件：'),
        B2('SpUNet 基准：semseg-spunet-v1m1-0-base.py'),
        B2('PTv3 基准：semseg-pt-v3m1-0-base.py'),
        B('在 /workspace/Pointcept/configs/ 下新建 doe/ 文件夹，用于存放所有DoE配置文件。'),
        B('复制 SpUNet 基准配置12份，分别命名为 pb_spunet_run01.py ~ pb_spunet_run12.py。'),
        B('对照第3.1节PB矩阵，逐一修改每个配置文件中的以下4个字段：'),
        B2('GridSample 的 grid_size：对应 PB 矩阵中 grid_size 列的值（0.01 / 0.02 / 0.04）'),
        B2('SphereCrop 的 point_max：对应 point_max 列（40000 / 80000 / 120000）'),
        B2('RandomJitter 的 sigma：对应 jitter_sigma 列（0.005 / 0.05 / 0.20）'),
        B2('RandomDropout 的 dropout_ratio：对应 dropout_ratio 列（0.0 / 0.1 / 0.2）'),
        B('在每个配置文件中增加或确认随机种子设置：seed = 42（保证可复现性）。'),
        B('修改每个配置文件的保存路径字段，例如 save_path = "exp/doe/pb_spunet_run01"，'
          '各文件对应编号，不得重复。'),
        B('同样操作复制PTv3基准配置6份（pb_ptv3_run01/03/04/07/08/09.py），修改相同字段。'),
        B('配置完成后，逐一打开每个文件快速核查：参数值是否与PB矩阵对应，保存路径是否唯一。'),
        SP(4),
        H3('完成检查清单'),
        CHK('doe/ 文件夹已创建，包含12个SpUNet + 6个PTv3配置文件（共18个）'),
        CHK('每个配置文件的4个参数值与PB矩阵完全一致（逐行核对）'),
        CHK('所有配置文件中 seed = 42 已设置'),
        CHK('18个文件的 save_path 各不相同，无重复'),
        CHK('中心点3次重复（Run 09, 10, 11）的参数值均为默认值，与基线配置一致'),
        SP(4),
        NOTE('如果 Pointcept 配置文件中没有 RandomDropout transform，可以不加 dropout 因子，'
             '将 PB 设计简化为3因子（grid_size, point_max, jitter），不影响实验有效性。'),
    ]

    story += [SP(8), HR()]

    # ── 第3-4天 ───────────────────────────────────────────────────────────
    story += [
        H2('第3-4天（6月16-17日）：PB筛选实验 SpUNet（12 runs）'),
        P('目标：系统运行12组PB参数配置，每组训练500 epoch，获取 mIoU 和显存峰值数据。'
          'SpUNet 每run约1小时，每天安排6个runs，两天内完成全部12组。'),
        SP(4),
        H3('第3天（6月16日）操作步骤'),
        B('进入 /workspace/Pointcept/ 工作目录，激活 thesis 环境（conda activate thesis）。'),
        B('按顺序运行 Run 01-06，每次执行训练命令时指定对应配置文件：'),
        B2('使用 Pointcept 的标准训练入口：python tools/train.py --config-file configs/doe/pb_spunet_run01.py'),
        B2('等待训练完成（约1小时），不要中途中断'),
        B('每个run训练结束后，立即执行以下两项记录操作：'),
        B2('查看日志文件最后几行，找到 "Val mIoU: XX.XX" 字样，记录最终 mIoU 数值'),
        B2('查看日志中的显存信息（或在训练过程中用 nvidia-smi 命令查看 Max-Used-Memory），'
           '记录峰值显存（单位 GB）'),
        B('将结果填入第5节的空白记录表（Run编号 + mIoU + 显存峰值 + 是否OOM）。'),
        B('完成Run 01-06后，运行 nvidia-smi 确认GPU空闲，再启动下一个run。'),
        SP(4),
        H3('第4天（6月17日）操作步骤'),
        B('运行 Run 07-12，操作流程与第3天相同。'),
        B('全部12组完成后，检查记录表的完整性：'),
        B2('12行数据均已填写，无缺漏'),
        B2('如有OOM错误，记录为"OOM"并在备注列说明，暂不重试（等第7天分析后决定是否调整范围）'),
        B('将12组结果数据整理成一个简单的表格或Excel文件，保存至 /workspace/docs/ 目录。'),
        SP(4),
        H3('完成检查清单'),
        CHK('12组SpUNet训练均已完成（无中途崩溃或中断）'),
        CHK('12组 mIoU 数据已记录（精确到小数点后2位）'),
        CHK('12组显存峰值已记录（精确到0.1 GB）'),
        CHK('如有OOM，已在记录表备注列标明（预计 Run 02、04的 point_max=120k + small grid_size 可能触发）'),
        CHK('Checkpoint 文件保存在各自的 exp/doe/ 子目录中'),
        SP(4),
        NOTE('每个run之间不需要手动操作，可以写一个简单的 shell 脚本按顺序自动依次运行所有12个配置，'
             '确保每个运行完成后再启动下一个（不要并行，避免显存冲突）。'),
    ]

    story += [SP(8), HR()]

    # ── 第5-6天 ───────────────────────────────────────────────────────────
    story += [
        H2('第5-6天（6月18-19日）：PB筛选实验 PTv3（6 runs）'),
        P('目标：用 PTv3 验证6个代表性参数组合，对比 SpUNet 和 PTv3 在相同参数下的响应是否一致。'
          'PTv3 每run约2.5小时，每天3个runs。'),
        SP(4),
        H3('操作步骤（与SpUNet相同，注意PTv3的差异）'),
        B('运行6个 PTv3 配置文件（pb_ptv3_run01/03/04/07/08/09.py）。'),
        B('PTv3 与 SpUNet 的关键配置差异，需注意：'),
        B2('batch_size = 6（SpUNet 为12），显存占用更大，point_max 上限约 80k（超过可能 OOM）'),
        B2('训练时间约2.5小时/run，两天内共运行6个run（第5天3个，第6天3个）'),
        B('记录格式与SpUNet一致，填入同一张记录表的PTv3列。'),
        B('第6天完成后，将全部PB数据（SpUNet 12组 + PTv3 6组）汇总到一份完整表格，'
          '为第7天的统计分析做准备。'),
        SP(4),
        NOTE('如果 PTv3 的 Run 02、04（point_max=120k）发生OOM，将 point_max 降为 80k 后重试，'
             '并在备注中说明调整原因。PTv3 的 OOM 阈值比 SpUNet 低，这本身也是一个有用的实验发现。'),
    ]

    story += [SP(8), HR()]

    # ── 第7天 ─────────────────────────────────────────────────────────────
    story += [
        H2('第7天（6月20日）：PB结果统计分析'),
        P('目标：对18组PB实验数据进行统计分析，确定对 mIoU 影响最显著的2-3个参数，'
          '并据此设计BBD精细实验的参数范围。这是纯数据分析工作，不占用GPU。'),
        SP(4),
        H3('分析步骤（逐步操作）'),
        B('整理数据：将12个SpUNet runs和6个PTv3 runs的结果放入同一个表格，'
          '列为：[Run编号, grid_size水平, point_max水平, jitter水平, dropout水平, SpUNet_mIoU, PTv3_mIoU, 显存]。'),
        B('计算每个参数的主效应（Main Effect）：'),
        B2('主效应 = 该参数取 +1 水平时的所有 mIoU 均值 − 取 −1 水平时的所有 mIoU 均值'),
        B2('分别对 grid_size、point_max、jitter、dropout 各计算一次，得到4个主效应值'),
        B2('主效应绝对值越大，说明该参数影响越显著'),
        B('绘制主效应柱状图：X轴为参数名，Y轴为主效应大小，按绝对值从大到小排列。'),
        B('进行显著性检验（选其一即可）：'),
        B2('简单方法：若主效应绝对值 > 实验误差标准差的2倍，视为显著'),
        B2('严格方法：用 Python scipy.stats 中的 ttest_ind 或 f_oneway 计算 p 值，p < 0.05 为显著'),
        B('对比 SpUNet 和 PTv3 的显著参数：若两者显著参数一致，说明该发现具有普适性；'
          '若不一致，取并集，两者都纳入后续分析。'),
        B('根据PB结果决定BBD阶段的参数范围：'),
        B2('聚焦于PB中表现最好的参数区域（不要照搬原计划的预设范围）'),
        B2('如 point_max=120k 在SpUNet中效果好但PTv3 OOM，BBD阶段可分别设定不同上限'),
        B('最终输出：① 显著参数列表（2-3个参数名），② BBD 实验矩阵（各参数的实际取值）。'),
        SP(4),
        H3('完成检查清单'),
        CHK('主效应图已绘制，可以清晰看出各参数的相对重要性'),
        CHK('已确定 2-3 个显著参数（基于主效应大小或显著性检验）'),
        CHK('BBD 实验矩阵已设计完毕（15组 × 3因子，含实际参数值）'),
        CHK('BBD 的15个 SpUNet 配置文件已创建（bbd_spunet_run01.py ~ bbd_spunet_run15.py）'),
    ]

    story += [SP(8), HR()]

    # ── 第8-10天 ──────────────────────────────────────────────────────────
    story += [
        H2('第8-10天（6月21-23日）：BBD精细实验（15 runs）'),
        P('目标：对显著参数建立二阶响应面模型，捕捉参数间的交互效应和非线性关系。'
          'SpUNet 运行全部15组，PTv3 选取4-6组关键点验证。'),
        SP(4),
        H3('每天安排'),
        B('第8天（6月21日）：运行 BBD Run 01-05。'),
        B2('Run 01-05 完成后，检查结果趋势是否合理（mIoU 应在基线 ±5% 范围内波动）'),
        B2('如有异常结果（mIoU 大幅低于基线），检查配置文件参数是否正确后再继续'),
        B('第9天（6月22日）：运行 BBD Run 06-10。'),
        B('第10天（6月23日）：运行 BBD Run 11-15（含3次中心点重复），同步启动 PTv3 验证实验。'),
        B2('中心点3次重复（Run 13-15）的 mIoU 应接近基线值（~64.87%），若偏差 >2%，说明实验存在系统误差，需排查'),
        SP(4),
        H3('操作要点'),
        B('每组完成后立即记录：mIoU（精确到0.01%）、显存峰值（精确到0.1GB）、训练时长。'),
        B('PTv3 验证实验：从15个BBD组次中选取4组（建议选 Run 01、04、09、13），'
          '用相同参数运行PTv3，对比两者响应规律是否一致。'),
        B('全部15组完成后，将数据整理为带参数编码的格式：'),
        B2('每行：[run编号, x₁（grid_size编码）, x₂（point_max编码）, x₃（jitter编码）, mIoU, 显存]'),
        B2('编码方式：低水平 = −1，中水平 = 0，高水平 = +1（便于后续直接拟合回归模型）'),
        SP(4),
        NOTE('BBD 的中心点重复（Run 13-15）应与基线实验的参数完全一致（grid_size=0.02, '
             'point_max=80k, jitter=0.05）。若结果显著偏离基线 64.87%，需检查是否有其他配置'
             '差异（如 epoch 数、seed 等）。'),
    ]

    story += [SP(8), HR()]

    # ── 第11-12天 ─────────────────────────────────────────────────────────
    story += [
        H2('第11天（6月24日）：回归模型拟合'),
        P('目标：用BBD全部15组数据拟合二阶响应面模型，评估模型质量，导出最优参数推荐。'),
        SP(4),
        H3('操作步骤'),
        B('整理BBD数据：将15组数据（含参数编码值和mIoU）整理好，同时准备对应的显存数据。'),
        B('使用 Python 拟合 mIoU 响应面模型（使用 statsmodels 或 sklearn 的多项式回归）：'),
        B2('将参数编码值（x₁, x₂, x₃）和它们的乘积项（x₁x₂, x₁x₃, x₂x₃）以及平方项（x₁², x₂², x₃²）作为自变量'),
        B2('mIoU 作为因变量，拟合线性回归模型'),
        B('评估模型质量：'),
        B2('R²（决定系数）：应 > 0.85，越接近1越好'),
        B2('RMSE（均方根误差）：反映预测误差大小'),
        B2('若 R² < 0.7，说明二阶模型不够，需检查是否有数据录入错误，或考虑增加实验点'),
        B('绘制等高线图（Contour Plot）：以两个显著参数为坐标轴，mIoU 为颜色/等高线，'
          '直观展示最优参数区域（论文图表的核心内容之一）。'),
        B('同样拟合显存预测模型：Memory = f(point_max, grid_size)，用于后续自适应参数选择模块。'),
        B('从模型中导出最优参数推荐值：在参数范围内搜索使 mIoU 最大且显存不超限的参数组合。'),
        SP(4),
        H2('第12天（6月25日）：Spatial Alignment 对比实验'),
        P('目标：量化滑窗推理时重叠区域处理方式对分割精度的影响。使用已有的 PTv3 最优 checkpoint，'
          '不需要重新训练。'),
        SP(4),
        H3('操作步骤'),
        B('使用 PTv3 最优 checkpoint（/workspace/Pointcept/exp/baseline_ptv3/model/model_best.pth）。'),
        B('在 S3DIS Area_5 中选取5个最大的房间（选点数最多的5个场景）进行推理测试。'),
        B('实现条件 A（有 alignment）：'),
        B2('将一个大房间切分为多个重叠块（overlap ratio = 50%），对重叠区域的每个点，'
           '收集所有覆盖该点的块的预测 logits，取平均后输出最终类别'),
        B2('记录：mIoU、边界点（距块边界 < 0.5m 的点）的专项 IoU、推理总时间'),
        B('实现条件 B（无 alignment）：'),
        B2('相同切分方式，但重叠区域直接取最后一个覆盖该点的块的预测结果，不做融合'),
        B2('记录相同指标'),
        B('对比两个条件的结果，分析 alignment 的收益（mIoU 提升）和代价（时间开销）。'),
        SP(4),
        NOTE('Spatial alignment 实验属于推理阶段的操作，与训练无关，不影响模型权重。'
             '实现时可以修改 Pointcept 的测试流程，或单独写一个推理脚本。'),
    ]

    story += [SP(8), HR()]

    # ── 第13-14天 ─────────────────────────────────────────────────────────
    story += [
        H2('第13-14天（6月26-27日）：跨数据集验证 + 数据整理'),
        SP(4),
        H3('第13天（6月26日）：跨数据集验证'),
        B('使用第11天导出的最优参数组合，在不同于DoE训练集的数据上进行验证：'),
        B2('首选：SemanticKITTI（室外驾驶场景，Pointcept 原生支持，下载容易）'),
        B2('备选：S3DIS 其他 Area（Area 1 或 Area 2，场景特性与 Area 5 有差异）'),
        B('将最优参数 vs 默认参数两种配置各运行一次推理，对比mIoU差异。'),
        B('记录结果时同时记录场景统计特征（点密度、场景范围），用于后续自适应模块的输入。'),
        SP(4),
        H3('第14天（6月27日）：数据整理与图表制作'),
        B('整理所有实验数据（PB + BBD + Alignment + 验证），汇总到一份完整的记录表格。'),
        B('制作论文所需的核心图表：'),
        B2('主效应图（Main Effects Plot）：对应论文第4章参数分析部分'),
        B2('响应面等高线图（Contour Plot）：展示两个显著参数的交互效应'),
        B2('Spatial alignment 对比图：mIoU 和推理时间的对比柱状图'),
        B2('跨数据集验证对比表：最优参数 vs 默认参数的性能比较'),
        B('将所有原始数据（训练日志、checkpoint、结果CSV）按照第5节的归档格式保存到 /workspace/docs/。'),
        B('撰写实验总结文档（对应论文第4-5章的实验结果部分），包括：'),
        B2('PB实验的显著参数分析结论及其物理解释'),
        B2('BBD 回归方程及 R² / RMSE'),
        B2('最优参数推荐表（按场景类型和显存约束分类）'),
        B2('Spatial alignment 的收益分析'),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # 5. 实验记录表（空白）
    # ══════════════════════════════════════════════════════════════════════
    story += [PageBreak(), H1('5  实验数据记录表（待填写）'), SP()]
    story += [P('以下表格在实验过程中逐行填写，每个run结束后立即记录，不要积累到最后再补填。')]

    story += [SP(6), H2('5.1  PB 筛选实验记录（SpUNet）')]
    pb_rec_data = [
        ['Run', 'grid_size', 'point_max', 'jitter', 'dropout',
         'SpUNet mIoU (%)', '显存峰值 (GB)', '是否 OOM', '备注'],
    ] + [[str(i).zfill(2), '', '', '', '', '', '', '', ''] for i in range(1, 13)]
    pb_rec_data[9][8]  = '中心点'
    pb_rec_data[10][8] = '中心点'
    pb_rec_data[11][8] = '中心点'
    story += [tbl(pb_rec_data,
                  [1.0*cm, 2.0*cm, 2.2*cm, 1.8*cm, 2.0*cm, 2.5*cm, 2.2*cm, 1.5*cm, 2.0*cm],
                  fontsize=8), SP(8)]

    story += [H2('5.2  PB 筛选实验记录（PTv3，6组关键 runs）')]
    ptv3_rec = [
        ['Run', 'grid_size', 'point_max', 'jitter', 'dropout',
         'PTv3 mIoU (%)', '显存峰值 (GB)', '对比 SpUNet\n差值 ΔmIoU'],
    ] + [['01', '', '', '', '', '', '', ''],
         ['03', '', '', '', '', '', '', ''],
         ['04', '', '', '', '', '', '', ''],
         ['07', '', '', '', '', '', '', ''],
         ['08', '', '', '', '', '', '', ''],
         ['09', '', '', '', '', '', '', '']]
    story += [tbl(ptv3_rec,
                  [1.0*cm, 2.2*cm, 2.2*cm, 1.8*cm, 2.0*cm, 2.5*cm, 2.2*cm, 2.5*cm],
                  fontsize=8), SP(8)]

    story += [H2('5.3  BBD 精细实验记录（SpUNet）')]
    bbd_rec = [
        ['Run', 'x₁\n(grid_size)', 'x₂\n(point_max)', 'x₃\n(jitter)',
         'mIoU (%)', '显存 (GB)', '备注'],
    ] + [[str(i).zfill(2), '', '', '', '', '', ''] for i in range(1, 16)]
    bbd_rec[13][6] = '中心点'
    bbd_rec[14][6] = '中心点'
    bbd_rec[15][6] = '中心点'
    story += [tbl(bbd_rec,
                  [1.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.0*cm, 2.2*cm],
                  fontsize=8), SP(8)]

    story += [H2('5.4  Spatial Alignment 对比记录')]
    align_rec = [
        ['房间名称', '条件A mIoU\n（有alignment）', '条件B mIoU\n（无alignment）',
         'ΔmIoU', '条件A时间(s)', '条件B时间(s)', '边界点ΔIoU'],
        ['大房间 1', '', '', '', '', '', ''],
        ['大房间 2', '', '', '', '', '', ''],
        ['大房间 3', '', '', '', '', '', ''],
        ['大房间 4', '', '', '', '', '', ''],
        ['大房间 5', '', '', '', '', '', ''],
        ['平均', '', '', '', '', '', ''],
    ]
    story += [tbl(align_rec,
                  [3.0*cm, 2.8*cm, 2.8*cm, 1.5*cm, 2.2*cm, 2.2*cm, 2.2*cm],
                  fontsize=8.5)]

    # ══════════════════════════════════════════════════════════════════════
    # 6. 注意事项 & 预期产出
    # ══════════════════════════════════════════════════════════════════════
    story += [PageBreak(), H1('6  关键注意事项'), SP()]
    items = [
        ('随机种子固定', 'seed = 42 必须在所有DoE配置文件中显式设置。如忘记设置，同组实验在不同时间运行'
         '可能产生不同结果，导致数据不可复现。'),
        ('OOM 处理原则', '遇到显存溢出（OOM）时，不要直接降低 point_max 或 grid_size 重试——'
         '这会破坏DoE矩阵的正交性。应在记录表中注明"OOM"，等PB分析结束后，'
         'BBD阶段再针对该模型调整参数上界。'),
        ('中心点数据的重要性', 'PB的Run 09-11和BBD的Run 13-15都是中心点重复实验，'
         '其结果的标准差用于估计实验误差。若三次中心点结果标准差 > 1%，说明实验条件不稳定，'
         '需检查是否有其他变量未控制（如GPU温度、系统负载等）。'),
        ('每个run完成后立即记录', '训练日志在磁盘上持续存在，但峰值显存需要在训练过程中或训练结束前通过'
         'nvidia-smi 查询，否则数据丢失。建议每次run开始时在另一个终端运行'
         '"watch -n 5 nvidia-smi"来持续监控显存。'),
        ('参数范围不要随意扩展', 'DoE的统计有效性依赖于预先设定的参数范围。如果中途改变范围，'
         '会导致已有数据与新数据不可直接比较。如确实需要调整，应在第7天分析后统一调整，'
         '而不是在实验过程中随机改变。'),
        ('DoE数据是论文核心', 'PB和BBD的实验数据将直接写入论文第4章，是论文最主要的原创贡献。'
         '务必保留所有原始数据（日志文件、checkpoint），不要随意清理磁盘空间。'),
    ]
    for title, desc in items:
        story += [B(f'<b>{title}：</b>{desc}'), SP(2)]

    story += [SP(8), H1('7  预期最终产出'), SP()]
    out_data = [
        ['产出类型', '具体内容', '对应论文章节'],
        ['PB 主效应分析',
         '4个参数的主效应图 + 显著性检验结果\n确定2-3个显著参数',
         '第4章：实验设计与分析'],
        ['BBD 响应面模型',
         'mIoU = f(x₁, x₂, x₃) 回归方程\nR²、RMSE 评估指标\n等高线图',
         '第4章：参数关系建模'],
        ['显存预测模型',
         'Memory = g(point_max, grid_size)\n用于资源约束下的参数选择',
         '第4章：资源约束分析'],
        ['自适应参数选择模块',
         '输入：场景点密度 + 可用显存\n输出：推荐的 grid_size, point_max, jitter\n形式：公式 + 查找表',
         '第5章：方法实现'],
        ['Spatial Alignment 分析',
         'mIoU 增益 vs 推理时间开销\n边界点专项分析\n推荐使用场景',
         '第5章：方法实现'],
        ['跨数据集验证',
         'SemanticKITTI 验证结果\n最优参数 vs 默认参数对比\n泛化性分析',
         '第5章：实验验证'],
    ]
    story += [tbl(out_data, [4.0*cm, 7.5*cm, 4.0*cm], hdr_bg=DARK_BG, fontsize=8.5)]

    story += [
        SP(12),
        HRFlowable(width='100%', thickness=1, color=TU_RED, spaceAfter=6),
        Paragraph('生成时间：2026-06-14  ·  TU Berlin · MDT · 硕士论文实验计划（更新版 v2）· Yucan Luo',
                  ParagraphStyle('footer', fontName=F, fontSize=8, alignment=TA_CENTER,
                                 textColor=colors.HexColor('#888888'), wordWrap='CJK')),
    ]

    return story


def main():
    out = '/workspace/docs/实验计划_两周DoE_v2.pdf'
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    doc.build(build())
    print(f'PDF generated: {out}')


if __name__ == '__main__':
    main()
