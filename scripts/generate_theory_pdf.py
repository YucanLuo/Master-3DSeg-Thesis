"""
DoE 实验理论详解 PDF 生成脚本
为 Yucan Luo 硕士论文提供完整实验设计理论支撑
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
TU_RED   = colors.HexColor("#C40D1E")
DARK_BG  = colors.HexColor("#1A1A2E")
BLUE_HDR = colors.HexColor("#1a3a5c")
TEAL_HDR = colors.HexColor("#00695C")
PUR_HDR  = colors.HexColor("#4A148C")
ORG_HDR  = colors.HexColor("#E65100")
GRN_HDR  = colors.HexColor("#1B5E20")
ROW_A    = colors.HexColor("#f0f4fa")
ROW_B    = colors.white
ROW_G    = colors.HexColor("#F1F8E9")
ROW_P    = colors.HexColor("#F3E5F5")
GRAY_BD  = colors.HexColor("#bbbbbb")
YLW_BG   = colors.HexColor("#FFFDE7")
BLUE_LT  = colors.HexColor("#E3F2FD")
RED_LT   = colors.HexColor("#FFEBEE")
GRN_LT   = colors.HexColor("#E8F5E9")

# ── 样式工厂 ──────────────────────────────────────────────────────────────
def s(name, **kw):
    d = dict(fontName=F, fontSize=10, leading=17, wordWrap='CJK')
    d.update(kw)
    return ParagraphStyle(name, **d)

ST = dict(
    title  = s('title', fontSize=20, leading=28, alignment=TA_CENTER,
                textColor=DARK_BG, spaceAfter=4),
    sub    = s('sub',   fontSize=11, leading=17, alignment=TA_CENTER,
                textColor=colors.HexColor('#555555'), spaceAfter=20),
    h1     = s('h1',   fontSize=14, leading=22, textColor=colors.white,
                backColor=DARK_BG, spaceBefore=18, spaceAfter=8,
                leftIndent=4, borderPad=6),
    h2     = s('h2',   fontSize=12, leading=20, textColor=BLUE_HDR,
                spaceBefore=14, spaceAfter=5),
    h2t    = s('h2t',  fontSize=12, leading=20, textColor=TEAL_HDR,
                spaceBefore=14, spaceAfter=5),
    h2p    = s('h2p',  fontSize=12, leading=20, textColor=PUR_HDR,
                spaceBefore=14, spaceAfter=5),
    h2o    = s('h2o',  fontSize=12, leading=20, textColor=ORG_HDR,
                spaceBefore=14, spaceAfter=5),
    h2g    = s('h2g',  fontSize=12, leading=20, textColor=GRN_HDR,
                spaceBefore=14, spaceAfter=5),
    h3     = s('h3',   fontSize=10.5, leading=18, textColor=TU_RED,
                spaceBefore=10, spaceAfter=4),
    body   = s('body', fontSize=9.5, leading=17, spaceAfter=5,
                alignment=TA_JUSTIFY),
    blt    = s('blt',  fontSize=9.5, leading=17, leftIndent=16, spaceAfter=4),
    blt2   = s('blt2', fontSize=9,   leading=16, leftIndent=32, spaceAfter=3),
    math   = s('math', fontSize=9.5, leading=18, spaceAfter=6,
                backColor=BLUE_LT, leftIndent=20, rightIndent=20, borderPad=6,
                fontName=F),
    note   = s('note', fontSize=9,   leading=15, spaceAfter=6,
                backColor=YLW_BG, leftIndent=8, borderPad=5,
                textColor=colors.HexColor('#555500')),
    key    = s('key',  fontSize=9.5, leading=16, spaceAfter=4,
                backColor=GRN_LT, leftIndent=8, borderPad=5,
                textColor=colors.HexColor('#1B5E20')),
    warn   = s('warn', fontSize=9,   leading=15, spaceAfter=6,
                backColor=RED_LT, leftIndent=8, borderPad=5,
                textColor=colors.HexColor('#B71C1C')),
    caption= s('caption', fontSize=8.5, leading=14, alignment=TA_CENTER,
                textColor=colors.HexColor('#555555'), spaceAfter=6),
    footer = s('footer', fontSize=8, leading=13, alignment=TA_CENTER,
                textColor=colors.HexColor('#888888')),
)

def H1(t):    return Paragraph(f'  {t}', ST['h1'])
def H2(t):    return Paragraph(t, ST['h2'])
def H2T(t):   return Paragraph(t, ST['h2t'])
def H2P(t):   return Paragraph(t, ST['h2p'])
def H2O(t):   return Paragraph(t, ST['h2o'])
def H2G(t):   return Paragraph(t, ST['h2g'])
def H3(t):    return Paragraph(t, ST['h3'])
def P(t):     return Paragraph(t, ST['body'])
def B(t):     return Paragraph(f'• {t}', ST['blt'])
def B2(t):    return Paragraph(f'◦ {t}', ST['blt2'])
def MATH(t):  return Paragraph(t.replace('\n', '<br/>'), ST['math'])
def NOTE(t):  return Paragraph(f'💡  {t}', ST['note'])
def KEY(t):   return Paragraph(f'★  {t}', ST['key'])
def WARN(t):  return Paragraph(f'⚠  {t}', ST['warn'])
def CAP(t):   return Paragraph(t, ST['caption'])
def SP(h=6):  return Spacer(1, h)
def HR():     return HRFlowable(width='100%', thickness=0.5, color=GRAY_BD, spaceAfter=4)

def pc(text, fs=8.5, align=TA_LEFT):
    return Paragraph(text.replace('\n', '<br/>'), ParagraphStyle('cell', fontName=F, fontSize=fs,
                                          leading=fs*1.55, wordWrap='CJK', alignment=align))

def tbl(data, col_w, hdr_bg=BLUE_HDR, row_colors=None, fontsize=8.5, extra_style=None):
    if row_colors is None:
        row_colors = [ROW_A, ROW_B]
    t = Table(data, colWidths=col_w, repeatRows=1)
    style = [
        ('FONTNAME',      (0,0), (-1,-1), F),
        ('FONTSIZE',      (0,0), (-1,-1), fontsize),
        ('BACKGROUND',    (0,0), (-1,0),  hdr_bg),
        ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
        ('FONTSIZE',      (0,0), (-1,0),  fontsize + 0.5),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), row_colors),
        ('GRID',          (0,0), (-1,-1), 0.4, GRAY_BD),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]
    if extra_style:
        style.extend(extra_style)
    t.setStyle(TableStyle(style))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# 正文构建
# ══════════════════════════════════════════════════════════════════════════════
def build():
    story = []
    W = A4[0] - 4*cm

    # ── 封面 ─────────────────────────────────────────────────────────────────
    story += [
        SP(30),
        HRFlowable(width='100%', thickness=4, color=TU_RED, spaceAfter=16),
        Paragraph('实验设计方法论完全指南', ST['title']),
        Paragraph('DoE · 全因子实验 · 响应面方法', ST['title']),
        SP(12),
        Paragraph('理论基础 · 数学原理 · 应用实践', ST['sub']),
        Paragraph('为 PTv3 超大场景点云分割的空间切割策略优化提供完整理论支撑', ST['sub']),
        SP(8),
        Paragraph('TU Berlin · MDT 研究组 · Yucan Luo · 2026', ST['sub']),
        HRFlowable(width='100%', thickness=2, color=TU_RED, spaceAfter=30),
        SP(20),
    ]

    # 目录式概览
    toc_data = [
        ['章节', '内容', '页码参考'],
        ['第1章', pc('为什么需要实验设计——从暴力枚举到智能采样', fs=9), '第2页'],
        ['第2章', pc('基础统计概念——效应、误差与显著性', fs=9), '第4页'],
        ['第3章', pc('Plackett-Burman 筛选设计完整理论', fs=9), '第7页'],
        ['第4章', pc('响应面方法论（RSM）理论基础', fs=9), '第13页'],
        ['第5章', pc('Box-Behnken 设计完整理论', fs=9), '第16页'],
        ['第6章', pc('回归模型拟合、评估与诊断', fs=9), '第21页'],
        ['第7章', pc('本课题实验参数选择的理论依据', fs=9), '第27页'],
        ['第8章', pc('Spatial Alignment 的统计分析理论', fs=9), '第31页'],
        ['附录A', pc('数学推导：最小二乘估计详解', fs=9), '第34页'],
        ['附录B', pc('本课题完整实验矩阵对照表', fs=9), '第36页'],
    ]
    story += [tbl(toc_data, [2.5*cm, 10.5*cm, 2.5*cm], hdr_bg=DARK_BG, fontsize=9)]
    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第1章
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 1 章　为什么需要实验设计'), SP()]

    story += [H2('1.1　问题的起源：参数优化的困境'), SP(4)]
    story += [P('你的论文需要为大规模点云语义分割找到最优的处理参数。直觉上，最简单的方法是'
                '把所有可能的参数组合都试一遍，观察哪种组合效果最好。这种方法叫做<b>全因子实验</b>。')]
    story += [P('然而，你面对的情况是：')]
    story += [
        B('研究目标：为 PTv3 在超大场景中设计最优空间切割与补偿（Spatial Alignment）策略'),
        B('2 个核心因子：chunk_range（切割尺寸，m×m）和 chunk_stride（步长，m）'),
        B('每个因子有 3 个候选水平（低、中、高）'),
        B('3² 全因子实验组合数：3² = 9 种（加入3次中心点重复后共 12 次实验）'),
        B('PTv3 每组实验约 2.5 小时，12 次实验约 30 小时——在两周计划内完全可行'),
    ]

    # 全因子表格示意
    story += [SP(8), H3('全因子实验的组合爆炸'), SP(4)]
    exp_data = [
        ['参数个数', '每参数取值数', '实验总次数（含重复）', 'PTv3 所需时间', '实际可行性'],
        [pc('2 个（本课题）'), '3', '12（9 种 + 3 次重复）', '约 30 小时', pc('✓ 可行')],
        ['3 个', '3', '27 + 3', '约 75 小时', pc('勉强可行')],
        ['4 个', '3', '81', '约 200 小时', pc('不可行')],
        ['6 个', '3', '729', '约 75 天', pc('完全不可能')],
        ['10 个', '3', '59,049', pc('约 17 年'), pc('荒谬')],
    ]
    story += [tbl(exp_data, [3.0*cm, 2.8*cm, 3.5*cm, 3.0*cm, 3.2*cm],
                  extra_style=[('BACKGROUND', (0,1), (-1,1), colors.HexColor('#C8E6C9')),
                                ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#FFCDD2')),
                                ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#FFCDD2')),
                                ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFF9C4'))])]
    story += [CAP('表 1.1　参数个数与实验规模的关系——本课题 2 个因子使全因子实验完全可行')]

    story += [SP(8), H2('1.2　实验设计的核心思想：信息最大化原则'), SP(4)]
    story += [P('实验设计（Design of Experiments, DoE）由英国统计学家 Ronald Fisher 在 20 世纪 20 年代发展，'
                '最初用于农业实验——如何用最少的地块实验确定最优的施肥方案。')]
    story += [P('DoE 的核心思想是：<b>通过精心安排实验点的位置，使得每次实验都能同时提供关于多个参数的信息，'
                '从而用远少于全因子的实验次数，获得几乎同等质量的结论。</b>')]

    story += [KEY('关键洞察：全因子实验中存在大量"信息冗余"。如果你已经知道了参数 A 的高水平和低水平下B的效果，'
                  '那么 A 的中水平下 B 的行为很大程度上可以通过插值推断，无需额外实验。')]

    story += [SP(6), H3('一个直观类比：采样定理'), SP(4)]
    story += [P('想象你要描述一条曲线的形状。如果曲线是直线，只需要 2 个点；如果是抛物线，需要 3 个点；'
                '如果是三次曲线，需要 4 个点。你不需要在曲线上取 100 个点来描述它——只需取满足描述其形状'
                '所需的最少点数。')]
    story += [P('DoE 的逻辑与此完全相同：')]
    story += [
        B('如果参数效应是线性的（直线），只需要高低两个水平就够了——这是 PB 筛选设计的基础'),
        B('如果参数效应有交互和弯曲（抛物线），需要三个水平——这是全因子和 Box-Behnken 设计的基础'),
        B('本课题只有 2 个因子，3² = 9 种组合，用全因子设计就能充分建模，无需担心组合爆炸'),
    ]

    story += [SP(6), H2('1.3　实验策略：2 因子直接全因子设计'), SP(4)]
    story += [P('本课题采用<b>直接 3² 全因子设计</b>，而非多因子场景下常用的 PB + BBD 两阶段策略。'
                '原因：已明确只有 chunk_range 和 chunk_stride 两个关键因子，无需筛选阶段。')]

    two_stage = [
        ['策略', '设计方法', '实验次数', '回答的问题', '数学模型'],
        [pc('本课题采用\n（2因子）'), pc('3² 全因子\n+ 中心点重复'), pc('12 次\n（PTv3）'),
         pc('两个切割参数如何\n共同影响分割精度？'),
         pc('二阶响应面\ny = β₀ + β₁x₁ + β₂x₂ + β₁₁x₁² + β₂₂x₂² + β₁₂x₁x₂')],
        [pc('多因子场景\n（仅供对比）'), pc('PB 筛选\n+ BBD 建模'), pc('12 + 15\n= 27 次'),
         pc('先筛选显著因子，\n再精细建模'),
         pc('一阶筛选模型 → 二阶响应面模型')],
    ]
    story += [tbl(two_stage, [2.5*cm, 2.8*cm, 2.0*cm, 4.2*cm, 4.0*cm],
                  row_colors=[ROW_G, ROW_A])]
    story += [CAP('表 1.2　本课题的实验策略与多因子两阶段策略的比较')]

    story += [SP(6),
              NOTE('PB 筛选设计和 Box-Behnken 设计的理论仍在第3章和第5章详细讲解——这些是 DoE '
                   '工具箱中的重要方法，理解它们有助于将来遇到多因子问题时做出正确的设计选择。')]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第2章
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 2 章　基础统计概念'), SP()]

    story += [H2('2.1　响应变量与因子'), SP(4)]
    story += [P('在 DoE 术语中：')]
    story += [
        B('<b>响应变量（Response）</b>：你想优化的目标，即整体 mIoU（%）、边界 mIoU（%）、显存峰值（GB）和推理时间（s）'),
        B('<b>因子（Factor）</b>：你可以控制的参数，即 chunk_range（切割尺寸）和 chunk_stride（步长）'),
        B('<b>水平（Level）</b>：每个因子的取值，例如 chunk_range 有三个水平：4m×4m（低）、6m×6m（中）、8m×8m（高）'),
        B('<b>固定控制变量</b>：grid_size = 0.02m（传感器本征分辨率，不纳入 DoE 因子）'),
        B('<b>实验点（Run）</b>：一次完整的训练+评测实验，对应一种参数组合'),
    ]

    story += [SP(6), H2('2.2　效应（Effect）的概念'), SP(4)]
    story += [P('效应是 DoE 中最核心的概念，它描述"改变某个参数，响应会如何变化"。')]

    story += [H3('主效应（Main Effect）'), SP(4)]
    story += [P('某因子的<b>主效应</b>定义为：该因子从低水平（−1）变化到高水平（+1）时，'
                '响应变量的平均变化量。')]
    story += [MATH('主效应(A) = 平均值(A取高水平时所有实验的响应) − 平均值(A取低水平时所有实验的响应)')]
    story += [P('举个具体例子：假设 chunk_range 取低水平（4m）时，3次实验的 mIoU 分别为 64.2, 64.8, 63.9，'
                '取高水平（8m）时，3次实验的 mIoU 分别为 66.1, 66.8, 67.2：')]
    story += [MATH('主效应(chunk_range) = (66.1+66.8+67.2)/3 − (64.2+64.8+63.9)/3\n'
                   '                    = 66.7 − 64.3 = +2.4 (%)')]
    story += [P('这说明 chunk_range 从 4m 增大到 8m，平均使 mIoU 提升约 2.4%。'
                '正号表示该因子与响应正相关——更大的切块尺寸让模型看到更多上下文，有助于提升精度。')]

    story += [SP(6), H3('交互效应（Interaction Effect）'), SP(4)]
    story += [P('两个因子 A 和 B 的<b>交互效应</b>描述："A 的效应是否取决于 B 的水平"。')]
    story += [P('例如：chunk_range 大（8m）时，减小 chunk_stride（增大重叠）使边界 IoU 显著提升；'
                'chunk_range 小（4m）时，减小 chunk_stride 的收益有限（因为本身切块数就多）——这就是显著的交互效应。')]

    interact_data = [
        ['', 'chunk_stride = 4m（低重叠）', 'chunk_stride = 2m（高重叠）', '主效应(chunk_range)'],
        ['chunk_range = 4m（小块）', '64.0%', '65.0%', '平均 64.5%'],
        ['chunk_range = 8m（大块）', '64.5%', '67.5%', '平均 66.0%'],
        ['主效应(chunk_stride)', '平均 64.25%', '平均 66.25%', ''],
    ]
    story += [tbl(interact_data, [4.0*cm, 4.0*cm, 4.0*cm, 3.5*cm],
                  extra_style=[('BACKGROUND', (0,3), (-1,3), colors.HexColor('#E8EAF6')),
                                ('BACKGROUND', (3,0), (3,-1), colors.HexColor('#E8EAF6'))])]
    story += [CAP('表 2.1　交互效应示意：chunk_range 与 chunk_stride 的交互（假设数据）\n'
                  'chunk_range=大时 stride 减小带来 +3%，chunk_range=小时仅 +1%，这就是显著的交互效应')]

    story += [SP(6), H2('2.3　误差的来源与控制'), SP(4)]
    story += [P('实验中的误差来自多种来源：')]
    story += [
        B('<b>随机误差（Random Error）</b>：每次训练由于随机初始化、数据加载顺序等导致的结果波动，'
          '即使参数完全相同，重复实验的 mIoU 也会略有不同（通常 ±0.1%~0.5%）'),
        B('<b>系统误差（Systematic Error）</b>：GPU 温度变化、服务器负载不同、数据缓存状态等导致的偏差'),
        B('<b>模型误差（Model Error）</b>：真实的参数-响应关系可能不是完美的线性或二次，'
          '模型本身的假设带来的近似误差'),
    ]
    story += [KEY('这就是为什么实验计划中 PB 设计要重复 3 次中心点（Run 09/10/11）、'
                  'BBD 设计也要重复 3 次中心点（Run 13/14/15）。这 3 次重复完全相同的实验，'
                  '其结果的标准差就是对"纯随机误差"的直接测量，用于后续显著性检验的基准。')]

    story += [SP(6), H2('2.4　编码变量：为什么要把参数变成 −1/0/+1'), SP(4)]
    story += [P('在实验矩阵中，你看到的不是 grid_size = 0.01 m，而是 x₁ = −1。这种转换叫做<b>变量编码</b>。')]
    story += [P('编码公式为：')]
    story += [MATH('xᵢ = (实际值 − 中心值) / (范围的一半)\n\n'
                   '以 chunk_range 为例（中心值 6m，范围一半 = 2m）：\n'
                   '  chunk_range = 4m → x₁ = (4 − 6) / 2 = −1\n'
                   '  chunk_range = 6m → x₁ = (6 − 6) / 2 =  0\n'
                   '  chunk_range = 8m → x₁ = (8 − 6) / 2 = +1\n\n'
                   '以 chunk_stride 为例（中心值 3m，范围一半 = 1m）：\n'
                   '  chunk_stride = 2m → x₂ = (2 − 3) / 1 = −1\n'
                   '  chunk_stride = 3m → x₂ = (3 − 3) / 1 =  0\n'
                   '  chunk_stride = 4m → x₂ = (4 − 3) / 1 = +1')]
    story += [P('编码的好处有三个：')]
    story += [
        B('所有参数都被缩放到同一量纲（−1 到 +1），使得不同参数的回归系数可以直接比较大小，'
          '系数越大说明该参数对响应影响越大'),
        B('保证设计矩阵的列正交，使每个参数的效应能被独立估计，不相互干扰'),
        B('回归模型的截距项 β₀ 直接等于所有实验点的平均响应，有明确的物理意义'),
    ]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第3章 PB 设计
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 3 章　Plackett-Burman 筛选设计完整理论'), SP()]

    story += [H2('3.1　历史背景与设计目标'), SP(4)]
    story += [P('Plackett-Burman 设计由英国统计学家 Robin Plackett 和 J.P. Burman 于 1946 年在论文'
                '"The Design of Optimum Multifactorial Experiments"中提出，'
                '最初用于工业质量控制领域。')]
    story += [P('PB 设计的设计目标是：<b>用最少的实验次数（4 的倍数），同时研究尽可能多的因子，'
                '且保证每个因子的主效应能被独立、无偏地估计。</b>')]
    story += [P('PB 设计的实验次数规律：')]
    pb_sizes = [
        ['实验次数 N', '最多可研究因子数', '你的情况'],
        ['8', '7 个因子', ''],
        ['12（你使用的）', '11 个因子', '✓ 用于研究 4 个因子，有充裕余量'],
        ['20', '19 个因子', ''],
        ['24', '23 个因子', ''],
    ]
    story += [tbl(pb_sizes, [3.5*cm, 4.5*cm, 7.5*cm],
                  extra_style=[('BACKGROUND', (0,2), (-1,2), colors.HexColor('#C8E6C9'))])]
    story += [CAP('表 3.1　PB 设计的规模系列')]

    story += [SP(6), H2('3.2　Hadamard 矩阵：PB 设计的数学基础'), SP(4)]
    story += [P('PB 设计的核心是<b>Hadamard 矩阵（H 矩阵）</b>。一个 N×N 的 Hadamard 矩阵满足：')]
    story += [MATH('H · Hᵀ = N · Iₙ\n\n'
                   '其中 I 是单位矩阵。这意味着矩阵的任意两列的内积为零，即任意两个因子的列正交。')]
    story += [P('12×12 的 Hadamard 矩阵（取前12行11列用于11因子实验）如下，'
                '+表示高水平，−表示低水平：')]

    # 12-run Hadamard matrix (first 4 factors shown for illustration)
    had_data = [
        ['Run', 'A', 'B', 'C', 'D', '...（共11列）'],
        ['01', '+', '−', '+', '+', '...'],
        ['02', '+', '+', '−', '+', '...'],
        ['03', '−', '+', '+', '+', '...'],
        ['04', '+', '+', '+', '−', '...'],
        ['05', '+', '+', '−', '−', '...'],
        ['06', '+', '−', '−', '+', '...'],
        ['07', '−', '+', '−', '+', '...'],
        ['08', '−', '−', '+', '−', '...'],
        ['09', '+', '−', '−', '−', '...'],
        ['10', '−', '+', '+', '+', '（中心点）'],
        ['11', '−', '−', '+', '+', '（中心点）'],
        ['12', '−', '−', '−', '−', '（中心点）'],
    ]
    story += [tbl(had_data, [1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 7.0*cm],
                  extra_style=[('BACKGROUND', (0,10), (-1,12), colors.HexColor('#E8EAF6'))])]
    story += [CAP('表 3.2　12-run Hadamard 矩阵结构示意（A=chunk_range, B=chunk_stride, C/D 为哑变量列）')]

    story += [SP(6),
              NOTE('正交性的物理含义：在12次实验中，每列 + 和 − 各出现 6 次，且任意两列的 +/− 组合（++、+−、−+、−−）'
                   '各出现 3 次。这意味着无论 B 取什么水平，A 的高低两种情况的实验次数完全相等，'
                   '所以计算 A 的主效应时，B 的影响会被完全抵消。')]

    story += [SP(6), H2('3.3　主效应计算的数学推导'), SP(4)]
    story += [P('设 N 次实验的响应值为 y₁, y₂, ..., yₙ，因子 A 对应的编码列为 x_{A,1}, x_{A,2}, ..., x_{A,N}（每个值为 +1 或 −1）。')]
    story += [P('因子 A 的主效应估计量为：')]
    story += [MATH('E(A) = (2/N) · Σᵢ x_{A,i} · yᵢ\n\n'
                   '等价写法：\n'
                   'E(A) = (所有 A=+1 时的 y 均值) − (所有 A=−1 时的 y 均值)')]
    story += [P('为什么乘以 2/N 而不是 1/N？')]
    story += [P('因为每个因子在 N 次实验中各有 N/2 次取 +1，N/2 次取 −1。乘以 2/N 等价于对高低两组分别取均值再相减，'
                '这样结果的单位和响应变量相同（即 mIoU 的百分比单位）。')]

    story += [SP(4), H3('数值示例：用 chunk_range 和 chunk_stride 演示'), SP(4)]
    story += [P('假设12次全因子实验后得到以下 mIoU 数据（模拟数据仅用于演示原理，A/B/C/D 为哑变量列）：')]

    calc_data = [
        ['Run', 'chunk_range\n(x₁)', 'chunk_stride\n(x₂)', '哑变量\n(A)', '哑变量\n(B)', 'mIoU(%)'],
        ['01', '−1 (4m)', '−1 (2m)', '+1', '−1', '65.2'],
        ['02', '0 (6m)', '−1 (2m)', '+1', '+1', '67.4'],
        ['03', '+1 (8m)', '−1 (2m)', '−1', '+1', '67.8'],
        ['04', '−1 (4m)', '0 (3m)', '+1', '−1', '64.1'],
        ['05', '0 (6m)', '0 (3m)', '+1', '+1', '67.0'],
        ['06', '+1 (8m)', '0 (3m)', '−1', '+1', '67.3'],
        ['07', '−1 (4m)', '+1 (4m)', '+1', '−1', '63.5'],
        ['08', '0 (6m)', '+1 (4m)', '−1', '−1', '66.2'],
        ['09', '0', '0', '0', '0', pc('67.0（中心点）')],
        ['10', '0', '0', '0', '0', pc('66.8（中心点）')],
        ['11', '0', '0', '0', '0', pc('67.2（中心点）')],
        ['12', '+1 (8m)', '+1 (4m)', '−1', '+1', '66.5'],
    ]
    story += [tbl(calc_data, [1.2*cm, 2.6*cm, 2.6*cm, 1.8*cm, 1.8*cm, 4.5*cm],
                  extra_style=[('BACKGROUND', (0,9), (-1,11), colors.HexColor('#E8EAF6'))])]
    story += [CAP('表 3.3　模拟全因子实验数据（实际数据在你的实验完成后填入）')]

    story += [SP(6), P('计算 chunk_range（x₁）的主效应（使用 Run 01-08，排除中心点）：')]
    story += [MATH('x₁ = −1 (4m) 的runs：01, 04, 07  →  mIoU 均值 = (65.2+64.1+63.5)/3 = 64.27%\n'
                   'x₁ = +1 (8m) 的runs：03, 06, 12  →  mIoU 均值 = (67.8+67.3+66.5)/3 = 67.20%\n\n'
                   '主效应(chunk_range) = 67.20 − 64.27 = +2.93%\n\n'
                   '解读：chunk_range 从 4m 增大到 8m，mIoU 平均提升 2.93 个百分点。\n'
                   '正效应说明更大的切块尺寸让模型看到更充分的空间上下文，显著有助于分割精度。')]

    story += [SP(6), H2('3.4　混叠（Aliasing）：PB 设计的局限性'), SP(4)]
    story += [P('PB 设计有一个重要局限：<b>主效应与两因子交互效应部分混叠</b>。')]
    story += [P('这意味着：在 12-run PB 设计中，因子 A 的主效应估计，其实包含了 A 本身的效应加上'
                '其他若干个两因子交互效应（如 BC、BD 等）的 1/3 分量：')]
    story += [MATH('估计到的 E(A) = 真实主效应(A) + (1/3)·E(BC) + (1/3)·E(BD) + ...')]
    story += [P('这就是为什么 PB 设计只能用于"筛选"而不能用于"精确建模"：')]
    story += [
        B('如果交互效应很小（相对于主效应），混叠带来的偏差可以忽略，结论可靠'),
        B('如果主效应很大（远超误差），我们有信心认为该因子确实显著，不是交互效应的伪影'),
        B('这就是为什么 PB 阶段之后还需要 BBD 阶段：BBD 能独立估计主效应和所有两因子交互效应'),
    ]
    story += [WARN('PB 设计的结论只能是"该因子的主效应估计显著"，不能说"该因子与其他因子无交互"。'
                   '混叠问题在 BBD 阶段会被完全解决。')]

    story += [SP(6), H2('3.5　显著性检验：如何判断效应是真实的还是随机噪声'), SP(4)]
    story += [P('计算出每个因子的主效应后，你需要判断这个效应是否"真实"，还是仅仅因为随机误差看起来像有影响。')]

    story += [H3('方法一：半正态概率图（Half-Normal Plot）'), SP(4)]
    story += [P('这是 DoE 中最常用的图形化显著性判断方法：')]
    story += [
        B('将所有主效应的绝对值从小到大排序'),
        B('在半正态概率纸上绘制这些点'),
        B('<b>不显著的效应</b>（随机噪声）应该近似服从半正态分布，落在一条通过原点的直线上'),
        B('<b>显著的效应</b>会显著偏离这条直线，在图的右上角"漂移"'),
        B('不需要 p 值，纯图形判断，直观有效'),
    ]

    story += [SP(4), H3('方法二：Lenth 方法（推荐）'), SP(4)]
    story += [P('Lenth（1989）提出了一种不依赖重复实验的显著性检验方法：')]
    story += [MATH('步骤 1：计算所有主效应绝对值的中位数 s₀\n'
                   '步骤 2：伪标准误差 PSE = 1.5 × median{|eᵢ| : |eᵢ| < 2.5·s₀}\n'
                   '步骤 3：若 |效应| > t_{α/2} × PSE，则显著\n\n'
                   '对于 12-run PB 设计，显著性阈值约为 PSE × 2.57（α = 0.05）')]

    story += [SP(4), H3('方法三：利用中心点估计误差（你的方案）'), SP(4)]
    story += [P('你的实验方案中有 3 次中心点重复（Run 09/10/11），这提供了一个非常干净的误差估计：')]
    story += [MATH('纯误差标准差 σ = √[Σ(yᵢ − ȳ)² / (n-1)]\n\n'
                   '以模拟数据为例：y₉ = 64.8, y₁₀ = 65.1, y₁₁ = 64.6\n'
                   '  ȳ = (64.8 + 65.1 + 64.6) / 3 = 64.833\n'
                   '  σ = √[(（64.8−64.833)²+(65.1−64.833)²+(64.6−64.833)²) / 2]\n'
                   '    = √[0.001089 + 0.071289 + 0.054289) / 2] = √[0.063334] ≈ 0.252%')]
    story += [P('判断准则：若某因子的主效应绝对值 > 2σ ≈ 0.50%，则认为该效应显著（置信度约 95%）。')]
    story += [KEY('这就是为什么中心点设计中要求三次重复结果的标准差不超过 1%——如果超过了 1%，'
                  '说明随机误差太大，任何主效应估计都不可靠。')]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第4章 RSM
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 4 章　响应面方法论（RSM）理论基础'), SP()]

    story += [H2T('4.1　响应面的概念'), SP(4)]
    story += [P('响应面方法（Response Surface Methodology, RSM）由 Box 和 Wilson 于 1951 年提出，'
                '用于在参数空间中寻找使响应最优的参数组合。')]
    story += [P('核心思路：把响应变量（mIoU）看做参数空间中的一个<b>"曲面"</b>：')]
    story += [
        B('参数（chunk_range, chunk_stride）确定了二维空间中的一个点的位置'),
        B('每个位置对应一个 mIoU 值（曲面的高度）'),
        B('你的目标是找到曲面上最高的那个点（最大 mIoU）'),
        B('RSM 用回归模型近似这个曲面，从而不用穷举就能找到最优的切割参数组合'),
    ]

    story += [SP(6), H2T('4.2　一阶模型：平面近似'), SP(4)]
    story += [P('最简单的近似是假设响应曲面是一个<b>超平面</b>（多维空间中的"平面"）：')]
    story += [MATH('y = β₀ + β₁x₁ + β₂x₂ + ... + βₖxₖ + ε\n\n'
                   '其中：\n'
                   '  y    = 响应变量（mIoU）\n'
                   '  xᵢ   = 第 i 个因子的编码值（−1 到 +1）\n'
                   '  βᵢ   = 第 i 个因子的回归系数（主效应的一半）\n'
                   '  ε    = 随机误差')]
    story += [P('一阶模型的特点：')]
    story += [
        B('参数少（k+1 个系数），需要的实验次数少'),
        B('描述的是整个参数空间的"整体趋势"，忽略非线性和交互效应'),
        B('适合于筛选阶段（PB 设计），快速识别重要因子的方向'),
        B('<b>局限</b>：如果响应曲面有明显弯曲（最优点不在边界而在内部），一阶模型会指向错误的方向'),
    ]
    story += [P('PB 筛选设计就是基于一阶模型——它的数学本质是在高低两个水平之间的线性近似。')]

    story += [SP(6), H2T('4.3　二阶模型：抛物面近似'), SP(4)]
    story += [P('当参数存在最优点（在参数范围内部）或因子间有交互时，需要二阶模型：')]
    story += [MATH('y = β₀ + Σᵢ βᵢxᵢ + Σᵢ βᵢᵢxᵢ² + ΣᵢΣⱼ₍ᵢ＜ⱼ₎ βᵢⱼxᵢxⱼ + ε\n\n'
                   '本课题 2 因子（chunk_range=x₁, chunk_stride=x₂）的完整二阶模型：\n\n'
                   'mIoU = β₀\n'
                   '     + β₁·x₁  + β₂·x₂               （线性主效应）\n'
                   '     + β₁₁·x₁² + β₂₂·x₂²             （二次效应，捕捉弯曲和最优点）\n'
                   '     + β₁₂·x₁x₂                      （交互效应）\n'
                   '     + ε')]
    story += [P('共有 <b>6 个回归系数</b>需要估计（1 个截距 + 2 个线性 + 2 个二次 + 1 个交互）。'
                '9 个独立实验点 > 6 个系数，模型充分可识别。')]
    story += [P('每个系数的物理含义：')]

    coef_data = [
        ['系数', '项', '物理含义', '本课题中的预期'],
        ['β₀', '截距', pc('所有参数取中心点时的预测 mIoU'), pc('约等于基线 67.01%（PTv3）')],
        ['β₁', pc('x₁（chunk_range）'), pc('chunk_range 增大一个单位（从中心 6m 到高水平 8m）的主效应'), pc('预计为正，更大切块提供更多上下文')],
        ['β₂', pc('x₂（chunk_stride）'), pc('chunk_stride 增大一个单位（步长变大，重叠减少）的主效应'), pc('预计为负，重叠少则边界精度下降')],
        ['β₁₁', 'x₁²', pc('chunk_range 的二次效应（曲面弯曲程度）'), pc('若显著且负，说明存在最优 chunk_range（过大会 OOM）')],
        ['β₂₂', 'x₂²', pc('chunk_stride 的二次效应'), pc('若显著，说明步长与精度的关系非线性')],
        ['β₁₂', 'x₁x₂', pc('chunk_range 与 chunk_stride 的交互效应'), pc('若显著，两者需联合优化（大块需更小步长）')],
    ]
    story += [tbl(coef_data, [1.5*cm, 2.5*cm, 5.0*cm, 5.5*cm],
                  row_colors=[ROW_A, ROW_B, ROW_G, ROW_A, ROW_B, ROW_G, ROW_A])]
    story += [CAP('表 4.1　二阶响应面模型各系数的物理含义（本课题 2 因子版本）')]

    story += [SP(6), H2T('4.4　为什么需要三个水平（−1、0、+1）'), SP(4)]
    story += [P('这是一个非常重要的问题。要估计二次项 β₁₁（x₁² 的系数），'
                '<b>必须</b>至少有三个不同的 x₁ 水平：')]
    story += [
        B('只有两个水平（±1）时，x₁² 对所有实验点取值相同（都等于 1），'
          '无法与截距项区分，因此无法估计二次系数'),
        B('加入中间水平（0）后，x₁² 在该水平取 0，与 ±1 水平的取值（1）不同，'
          '才能通过回归估计出 β₁₁'),
        B('这就是 BBD 使用三水平（−1/0/+1）而 PB 只使用两水平（±1）的根本原因'),
    ]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第5章 BBD
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 5 章　Box-Behnken 设计完整理论'), SP()]

    story += [H2P('5.1　BBD 的几何结构'), SP(4)]
    story += [P('Box-Behnken 设计由 G.E.P. Box 和 D.W. Behnken 于 1960 年提出，'
                '是专门用于估计二阶响应面模型的经济高效设计。')]
    story += [P('BBD 的几何结构非常优雅：<b>实验点位于超立方体的棱的中点和中心</b>，'
                '而不是顶点。')]

    story += [SP(4), P('对于3因子 BBD，参数空间是一个正方体（各维从 −1 到 +1）。实验点的分布：')]
    story += [
        B('12 个边中点：每次固定一个参数在中间水平（0），另外两个参数取 ±1 的四种组合'),
        B('3 个中心点重复：所有参数取 0，用于估计纯误差'),
        B('<b>关键特点</b>：BBD 不包含立方体的顶点（±1, ±1, ±1）——这正是它的优势之一'),
    ]

    story += [SP(4), P('为什么避开顶点？')]
    story += [
        B('顶点是极端条件下（所有参数同时取最大值或最小值），往往是实际中最危险的实验条件，'
          '例如 grid_size=0.01（最细）+ point_max=120k（最大）很可能导致 OOM'),
        B('BBD 通过避开所有"全极端"组合，在不损失太多统计效率的情况下，'
          '大幅降低了实验失败（OOM）的风险'),
    ]
    story += [NOTE('本课题采用 3² 全因子设计而非 BBD，原因是因子数只有 2 个（BBD 最少需要 3 因子）。'
                   '3² 全因子实际上包含了 2 因子情况下的所有角点（4个）、边中点（4个）和中心点（1个），'
                   '信息量等同于 2 因子 CCD，不存在 BBD 的顶点排除问题。')]

    story += [SP(6), H2P('5.2　15 组实验的构造原理（3因子示例）'), SP(4)]
    story += [P('3因子 BBD 的12个边中点是怎么来的？')]
    story += [P('在三维空间中，正方体有 12 条棱，每条棱的中点是两个参数取极值（±1），'
                '第三个参数取中间值（0）。12 条棱分为三组，每组对应一个参数固定为 0：')]

    bbd_construct = [
        ['固定为 0 的参数', '变化的两个参数', '对应 Run', '坐标示意'],
        [pc('因子 C（x₃=0）'),
         pc('x₁ 和 x₂ 取 ±1 的四种组合'),
         'Run 01-04',
         pc('(−1,−1,0), (+1,−1,0), (−1,+1,0), (+1,+1,0)')],
        [pc('因子 B（x₂=0）'),
         pc('x₁ 和 x₃ 取 ±1 的四种组合'),
         'Run 05-08',
         pc('(−1,0,−1), (+1,0,−1), (−1,0,+1), (+1,0,+1)')],
        [pc('因子 A（x₁=0）'),
         pc('x₂ 和 x₃ 取 ±1 的四种组合'),
         'Run 09-12',
         pc('(0,−1,−1), (0,+1,−1), (0,−1,+1), (0,+1,+1)')],
        [pc('全部为 0'), '—', pc('Run 13-15\n（中心点×3）'), pc('(0, 0, 0) 重复三次')],
    ]
    story += [tbl(bbd_construct, [3.5*cm, 4.5*cm, 2.5*cm, 5.0*cm],
                  extra_style=[('BACKGROUND', (0,4), (-1,4), colors.HexColor('#E8EAF6'))])]
    story += [CAP('表 5.1　3因子 BBD 的15个实验点构造原理（通用示例）')]

    story += [SP(4), P('本课题因子数只有 2 个，不适用 BBD（BBD 最少需要 3 因子）。'
                        '对应的 2 因子设计是 <b>3² 全因子 + 中心点重复</b>，详见附录 B。'
                        '下表展示 BBD 在 3 因子假设情境下的完整矩阵，供理论理解参考：')]

    bbd_actual = [
        ['Run', 'x₁ 编码', 'x₂ 编码', 'x₃ 编码',
         '因子 A 实际值', '因子 B 实际值', '因子 C 实际值', '实验目的'],
        ['01', '−1', '−1', '0', '低 (−1)', '低 (−1)', '中 (0)', '边角点'],
        ['02', '+1', '−1', '0', '高 (+1)', '低 (−1)', '中 (0)', '边角点'],
        ['03', '−1', '+1', '0', '低 (−1)', '高 (+1)', '中 (0)', '边角点'],
        ['04', '+1', '+1', '0', '高 (+1)', '高 (+1)', '中 (0)', '边角点'],
        ['05', '−1', '0', '−1', '低 (−1)', '中 (0)', '低 (−1)', '边角点'],
        ['06', '+1', '0', '−1', '高 (+1)', '中 (0)', '低 (−1)', '边角点'],
        ['07', '−1', '0', '+1', '低 (−1)', '中 (0)', '高 (+1)', '边角点'],
        ['08', '+1', '0', '+1', '高 (+1)', '中 (0)', '高 (+1)', '边角点'],
        ['09', '0', '−1', '−1', '中 (0)', '低 (−1)', '低 (−1)', '边角点'],
        ['10', '0', '+1', '−1', '中 (0)', '高 (+1)', '低 (−1)', '边角点'],
        ['11', '0', '−1', '+1', '中 (0)', '低 (−1)', '高 (+1)', '边角点'],
        ['12', '0', '+1', '+1', '中 (0)', '高 (+1)', '高 (+1)', '边角点'],
        ['13', '0', '0', '0', '中 (0)', '中 (0)', '中 (0)', '中心点'],
        ['14', '0', '0', '0', '中 (0)', '中 (0)', '中 (0)', '中心点'],
        ['15', '0', '0', '0', '中 (0)', '中 (0)', '中 (0)', '中心点'],
    ]
    story += [tbl(bbd_actual, [1.0*cm, 1.5*cm, 1.5*cm, 1.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.0*cm],
                  fontsize=8,
                  extra_style=[('BACKGROUND', (0,13), (-1,15), colors.HexColor('#E8EAF6'))])]
    story += [CAP('表 5.2　3因子 BBD 实验矩阵（通用结构，供理解设计原理）')]

    story += [SP(6), H2P('5.3　BBD 与中心复合设计（CCD）的比较'), SP(4)]

    ccd_bbd = [
        ['特性', 'Box-Behnken（你使用的）', '中心复合设计（CCD）'],
        [pc('实验次数（3因子）'), pc('15（12边中点 + 3中心点）'), pc('20（8顶点 + 6星形点 + 6中心点）')],
        [pc('包含顶点'), pc('否（避免极端组合）'), pc('是（包含所有角点）')],
        [pc('包含超出范围的点'), pc('否'), pc('是（星形点超出 ±1 范围）')],
        [pc('OOM 风险'), pc('低'), pc('较高（角点可能触发 OOM）')],
        [pc('统计效率'), pc('略低于 CCD'), pc('略高于 BBD')],
        [pc('适用场景'), pc('参数范围边界存在约束时\n（如显存限制）'), pc('参数范围可以自由探索时')],
    ]
    story += [tbl(ccd_bbd, [4.0*cm, 5.5*cm, 5.5*cm], row_colors=[ROW_A, ROW_B]*4)]
    story += [CAP('表 5.3　BBD 与 CCD 的比较')]

    story += [SP(4), NOTE('本课题采用 3² 全因子（而非 CCD 或 BBD）：因子数只有 2 个，3² 全因子涵盖所有因子水平组合，'
                           '且不含超出预设范围的星形点，兼顾了统计完整性和显存安全性。')]

    story += [SP(6), H2P('5.4　旋转性与均匀精度'), SP(4)]
    story += [P('BBD 是一种<b>近似旋转设计</b>，意味着预测方差在距离中心点等距的位置上近似相等。')]
    story += [P('实际含义：在参数空间的中心区域，BBD 的预测精度是均匀的，不会在某个方向上特别精确'
                '而在另一个方向上很差。这对于寻找最优点非常有利——无论最优点在哪个方向，'
                '你都能以类似的精度定位它。')]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第6章 回归模型拟合
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 6 章　回归模型拟合、评估与诊断'), SP()]

    story += [H2O('6.1　最小二乘法（OLS）原理'), SP(4)]
    story += [P('拟合响应面模型的标准方法是<b>普通最小二乘法（Ordinary Least Squares, OLS）</b>。')]
    story += [P('设你有 N 次实验，k 个因子，二阶模型有 p 个待估系数（对于3因子 p=10）。')]
    story += [P('将所有实验数据写成矩阵形式：')]
    story += [MATH('y = X · β + ε\n\n'
                   '其中：\n'
                   '  y  是 N×1 的响应向量（15个 mIoU 观测值）\n'
                   '  X  是 N×p 的设计矩阵（每行对应一次实验的参数编码及其乘积）\n'
                   '  β  是 p×1 的待估系数向量\n'
                   '  ε  是 N×1 的误差向量')]
    story += [P('以 BBD 前4个实验为例，设计矩阵 X 的前4行（对应 Run01-04）：')]

    xmat_data = [
        ['Run', '1（截距）', 'x₁', 'x₂', 'x₃', 'x₁²', 'x₂²', 'x₃²', 'x₁x₂', 'x₁x₃', 'x₂x₃'],
        ['01', '1', '−1', '−1', '0', '1', '1', '0', '1', '0', '0'],
        ['02', '1', '+1', '−1', '0', '1', '1', '0', '−1', '0', '0'],
        ['03', '1', '−1', '+1', '0', '1', '1', '0', '−1', '0', '0'],
        ['04', '1', '+1', '+1', '0', '1', '1', '0', '1', '0', '0'],
        ['...', '...', '...', '...', '...', '...', '...', '...', '...', '...', '...'],
    ]
    story += [tbl(xmat_data, [1.0*cm, 1.5*cm, 1.0*cm, 1.0*cm, 1.0*cm,
                               1.0*cm, 1.0*cm, 1.0*cm, 1.2*cm, 1.2*cm, 1.2*cm], fontsize=8)]
    story += [CAP('表 6.1　BBD 设计矩阵 X 的前4行示意（共15行10列）')]

    story += [SP(6), P('OLS 的目标是找到使残差平方和（SSE）最小的系数向量 β：')]
    story += [MATH('minimize  SSE = Σᵢ(yᵢ − ŷᵢ)² = ||y − Xβ||²\n\n'
                   '解析解（正规方程的解）：\n'
                   '  β̂ = (XᵀX)⁻¹ · Xᵀ · y\n\n'
                   '其中 (XᵀX)⁻¹ 是 10×10 矩阵的逆，Xᵀy 是 X 转置与 y 的乘积。\n'
                   '实际计算用 Python statsmodels 或 sklearn 自动完成，不需要手动算。')]

    story += [SP(6), H2O('6.2　模型质量评估指标'), SP(4)]

    story += [H3('R²（决定系数）'), SP(4)]
    story += [MATH('R² = 1 − SSE/SST = 1 − Σ(yᵢ−ŷᵢ)² / Σ(yᵢ−ȳ)²\n\n'
                   '取值范围：0 到 1\n'
                   '物理含义：模型能解释的响应变量变异占总变异的比例\n'
                   '你的目标：R² > 0.85')]
    story += [P('如何理解 R² = 0.85？意味着模型能解释 mIoU 变化的 85%，剩余 15% 是随机误差或模型无法捕捉的高阶效应。')]

    story += [SP(4), H3('调整 R²（Adjusted R²）'), SP(4)]
    story += [MATH('R²_adj = 1 − (1 − R²) · (N−1) / (N−p)\n\n'
                   '其中 N=15（实验次数），p=10（系数个数）\n'
                   '惩罚过多参数，避免过拟合。如果 R² 和 R²_adj 相差 > 0.2，说明模型可能过拟合。')]

    story += [SP(4), H3('RMSE（均方根误差）'), SP(4)]
    story += [MATH('RMSE = √(SSE / (N−p)) = √(Σ(yᵢ−ŷᵢ)² / (15−10))\n\n'
                   '物理含义：预测值与实测值的平均偏差，单位与 mIoU 相同（%）\n'
                   '期望值：RMSE < 1%（约为 mIoU 范围的 1/10 以内）')]

    story += [SP(6), H2O('6.3　方差分析（ANOVA）表'), SP(4)]
    story += [P('ANOVA 表将响应变量的总变异分解为"模型解释的部分"和"误差部分"，'
                '并用 F 检验判断模型整体是否显著：')]

    anova_data = [
        ['变异来源', '平方和（SS）', '自由度（df）', '均方（MS）', 'F 统计量', 'p 值'],
        [pc('回归模型'), pc('SSR = SST − SSE'), pc('p−1 = 9'), pc('MSR = SSR/9'), pc('F = MSR/MSE'), pc('< 0.05 显著')],
        [pc('误差'), pc('SSE'), pc('N−p = 5'), pc('MSE = SSE/5'), pc('—'), pc('—')],
        [pc('纯误差\n（中心点重复）'), pc('SS_PE'), pc('2（3次重复−1）'), pc('MS_PE'), pc('—'), pc('—')],
        [pc('失拟误差'), pc('SS_LOF = SSE − SS_PE'), pc('3'), pc('MS_LOF'), pc('F_LOF = MS_LOF/MS_PE'), pc('> 0.05 不显著为好')],
        [pc('总变异'), pc('SST'), pc('N−1 = 14'), pc('—'), pc('—'), pc('—')],
    ]
    story += [tbl(anova_data, [2.8*cm, 3.0*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.2*cm], fontsize=8,
                  extra_style=[('BACKGROUND', (0,5), (-1,5), colors.HexColor('#FFF9C4'))])]
    story += [CAP('表 6.2　BBD 响应面模型的 ANOVA 表结构')]

    story += [SP(4), P('特别关注<b>失拟检验（Lack-of-Fit Test）</b>：')]
    story += [
        B('失拟误差描述：模型预测值与实测均值的偏差，即"模型假设的函数形式是否正确"'),
        B('检验假设 H₀：模型形式（二阶）是正确的（失拟不显著）'),
        B('如果失拟 F 检验 p < 0.05：说明二阶模型不够用，真实关系有更高阶的效应，模型不可信'),
        B('如果失拟 F 检验 p > 0.05：说明二阶模型形式是合适的，不需要更复杂的模型'),
    ]

    story += [SP(6), H2O('6.4　回归系数的显著性检验'), SP(4)]
    story += [P('对于模型中的每个系数 βᵢ，用 t 检验判断它是否显著不为零：')]
    story += [MATH('t_i = β̂ᵢ / SE(β̂ᵢ)    其中  SE(β̂ᵢ) = √(MSE · [(XᵀX)⁻¹]ᵢᵢ)\n\n'
                   '如果 |tᵢ| > t_{α/2, N−p}（查表值，α=0.05 时约为 2.57），则该系数显著')]
    story += [P('这个检验告诉你二阶模型中哪些项可以删除：')]
    story += [
        B('如果某个交互项 βᵢⱼ 不显著（p > 0.05），可以考虑删除它，简化模型'),
        B('如果某个二次项 βᵢᵢ 不显著，说明该参数方向上曲面较平，无明显最优点'),
        B('主效应 βᵢ 即使不显著也通常保留（层级原则）'),
    ]

    story += [SP(6), H2O('6.5　残差分析：验证模型假设'), SP(4)]
    story += [P('回归分析的有效性依赖于以下假设，需要通过残差图来验证：')]

    resid_data = [
        ['假设', '验证方式', '如何通过图形判断'],
        [pc('误差正态性'), pc('残差正态概率图（QQ图）'), pc('残差点近似落在对角直线上')],
        [pc('误差等方差性'), pc('残差 vs 预测值散点图'), pc('残差随机分布在水平带内，无喇叭形')],
        [pc('误差独立性'), pc('残差 vs 实验顺序图'), pc('无明显趋势或周期性')],
        [pc('无异常点'), pc('残差 vs 预测值，标准化残差图'), pc('无|标准化残差| > 3 的点')],
    ]
    story += [tbl(resid_data, [3.5*cm, 5.0*cm, 7.0*cm])]
    story += [CAP('表 6.3　残差分析的四个假设检验')]

    story += [SP(6), H2O('6.6　模型用于优化：最优参数推荐'), SP(4)]
    story += [P('拟合得到回归模型后，可以用它进行参数优化：')]
    story += [MATH('目标：max mIoU = β₀ + β₁x₁ + β₂x₂ + β₁₁x₁² + β₂₂x₂² + β₁₂x₁x₂\n\n'
                   '其中：x₁ = (chunk_range − 6) / 2，x₂ = (chunk_stride − 3) / 1\n\n'
                   '约束：−1 ≤ x₁, x₂ ≤ +1（即 4m ≤ chunk_range ≤ 8m，2m ≤ chunk_stride ≤ 4m）\n'
                   '      chunk_stride ≤ chunk_range（步长不超过切块宽度，避免覆盖盲区）\n'
                   '      Memory(chunk_range) ≤ 可用显存上限\n\n'
                   '方法：\n'
                   '  1. 对 x₁ 和 x₂ 求偏导并令其为 0，解 2×2 方程组得到候选最优点\n'
                   '  2. 在参数范围内网格搜索（9个点，直接比较预测值）\n'
                   '  3. 验证最优点是极大值（Hessian 矩阵 2×2 负定：β₁₁<0, β₂₂<0, β₁₁β₂₂>β₁₂²/4）')]
    story += [KEY('这个最优化过程就是论文"最优切割参数选择"的核心数学内容：'
                  '给定硬件显存约束，在约束条件下求使 mIoU 最大的 chunk_range 和 chunk_stride 组合，'
                  '为超大场景点云分割提供自适应参数推荐。')]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第7章 本课题的理论依据
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 7 章　本课题实验参数选择的理论依据'), SP()]

    story += [H2G('7.1　研究背景：PTv3 的大场景瓶颈'), SP(4)]
    story += [P('本课题的核心研究问题是：<b>如何让 PTv3 模型在超大场景中进行高质量的点云语义分割？</b>')]
    story += [P('PTv3 当前的局限：测试配置中 <b>test_cfg.crop = None</b>，意味着推理时将整个场景一次性送入模型。'
                '对于大型室外场景（数百万点），这会导致 GPU 显存不足（OOM），无法完成推理。')]
    story += [KEY('解决方案分为两部分：\n'
                  '(1) 切割（Chunking）：用 sampling_chunking_data.py 将大场景按 chunk_range（切割尺寸）'
                  '和 chunk_stride（步长）离线切成重叠小块，每块独立推理，显存可控\n'
                  '(2) 补偿（Alignment）：推理时对重叠区域的每个点收集所有覆盖该点的块的原始 logits，'
                  '取平均后再 argmax，消除切割边界处的标签不一致伪影')]

    story += [SP(6), H2G('7.2　为什么选 chunk_range 和 chunk_stride 作为 DoE 因子'), SP(4)]
    story += [P('chunk_range（切割尺寸）和 chunk_stride（步长）是控制切割策略的两个独立维度，'
                '且两者对分割精度的影响方向和机理完全不同，非常适合作为 DoE 因子。')]

    factor_rationale = [
        ['因子', '物理含义', '效应机理', '参数取值范围'],
        [pc('x₁ = chunk_range\n（切割尺寸，m×m）', fs=8),
         pc('每个训练/推理切块\n覆盖的空间范围\n（正方形边长，单位 m）', fs=8),
         pc('决定模型感受野大小：\n过小 → 上下文不足，大型物体被切断\n'
            '过大 → 显存 OOM\n存在最优尺寸使精度最高', fs=8),
         pc('4m（低）\n6m（中，基线）\n8m（高）', fs=8)],
        [pc('x₂ = chunk_stride\n（步长，m）', fs=8),
         pc('相邻切块中心之间的距离\n（单位 m），决定重叠比例\n重叠 = (range−stride)/range', fs=8),
         pc('决定边界补偿质量：\n步长小 → 重叠多 → 边界精度高，切块数多，速度慢\n'
            '步长大 → 重叠少 → 推理快，但边界伪影多\n存在最优步长使精度/效率最均衡', fs=8),
         pc('2m（低）\n3m（中，基线）\n4m（高）', fs=8)],
    ]
    story += [tbl(factor_rationale, [2.5*cm, 3.0*cm, 5.5*cm, 3.5*cm], fontsize=8)]
    story += [CAP('表 7.1　DoE 因子及其物理含义')]

    story += [SP(4), P('重叠比例的计算公式：')]
    story += [MATH('重叠比例 = (chunk_range − chunk_stride) / chunk_range\n\n'
                   '例：chunk_range=6m，chunk_stride=3m  → 重叠 = (6−3)/6 = 50%\n'
                   '    chunk_range=4m，chunk_stride=4m  → 重叠 = (4−4)/4 =  0%  （无重叠，边界无法补偿）\n'
                   '    chunk_range=8m，chunk_stride=2m  → 重叠 = (8−2)/8 = 75% （高重叠，边界精度最高）')]

    story += [SP(6), H2G('7.3　为什么 grid_size 必须固定——不作为 DoE 因子'), SP(4)]
    story += [WARN('grid_size（体素化分辨率）在本研究中被固定为 0.02m，不纳入 DoE 因子。'
                   '这是一个关键的设计决策：grid_size 不是可以"优化"的参数，而是传感器特性决定的物理约束。')]
    story += [P('grid_size 代表的是<b>点云体素化步骤中的空间分辨率</b>——即把原始点云下采样时每个体素格的边长。')]
    story += [P('为什么不能随意改变 grid_size？')]
    story += [
        B('<b>传感器分辨率约束</b>：S3DIS 数据集由 Matterport 激光雷达采集，原始点间距约为 0.02m。'
          'grid_size = 0.02m 意味着以传感器的本征分辨率保留数据，不进行人为降采样。'),
        B('<b>增大 grid_size = 丢弃传感器信息</b>：将 grid_size 增大（如 0.04m）等价于强制降采样，'
          '每个体素格内多个点被合并为一个——这会不可逆地丢失几何细节，'
          '尤其是细长结构（门框、椅腿、桌腿）的形状信息。'),
        B('<b>不是可优化的参数</b>：与切割尺寸不同，grid_size 没有一个"更好的值"——它应当等于传感器分辨率。'
          '降低 grid_size（即 0.01m）会超出点间距导致空体素过多；'
          '增大 grid_size 会丢弃信息。两个方向都不是"优化"。'),
    ]
    story += [KEY('结论：grid_size = 0.02m 是固定的控制变量（常数），不是可以优化的实验因子。'
                  '在实验矩阵的每一行，grid_size 的值都固定为 0.02m。')]

    story += [SP(6), H2G('7.4　因子水平范围的物理依据'), SP(4)]

    range_data = [
        ['因子', '低水平 (−1)', '中心点 (0)', '高水平 (+1)', '范围选择依据'],
        [pc('chunk_range\n（切割尺寸）', fs=8),
         pc('4m × 4m\n（小块）', fs=8),
         pc('6m × 6m\n（基线默认值）', fs=8),
         pc('8m × 8m\n（大块）', fs=8),
         pc('S3DIS 室内房间尺寸约 5~20m。\n4m：小型办公区规模，点数约 40k~80k，显存友好。\n'
            '6m：标准办公室规模，与 sampling_chunking_data.py 默认参数一致。\n'
            '8m：大型开放区，点数约 160k~250k，接近 PTv3 在 44GB 显存下的上限。', fs=8)],
        [pc('chunk_stride\n（步长）', fs=8),
         pc('2m\n（高重叠，50%~75%）', fs=8),
         pc('3m\n（中重叠，基线默认值）', fs=8),
         pc('4m\n（低重叠，0%~50%）', fs=8),
         pc('步长约束：chunk_stride ≤ chunk_range（否则会出现覆盖盲区）。\n'
            '2m：重叠率最高，每个点被更多块覆盖，补偿效果最好，推理最慢。\n'
            '3m：与 sampling_chunking_data.py 默认参数一致，兼顾效率与精度。\n'
            '4m：当 chunk_range=4m 时步长=块宽，重叠率=0%（可作为无补偿基线的特殊点）。', fs=8)],
    ]
    story += [tbl(range_data, [2.5*cm, 2.0*cm, 2.5*cm, 2.0*cm, 6.5*cm], fontsize=8)]
    story += [CAP('表 7.2　因子水平取值范围及物理依据')]

    story += [SP(4), NOTE('特殊实验点 Run 07（chunk_range=4m，chunk_stride=4m）的重叠率为 0%，'
                          '相当于"无重叠切割 + 无边界补偿"的极端情况，可作为理解补偿机制效果的参照基准。')]

    story += [SP(6), H2G('7.5　为什么用 3² 全因子设计而非 PB + BBD 两阶段策略'), SP(4)]
    story += [P('传统的两阶段 DoE 策略（PB 筛选 + BBD 精细建模）适用于因子数多（通常 ≥ 4 个）'
                '且不确定哪些因子显著的场景。本课题的情况不同：')]
    story += [
        B('<b>因子数只有 2 个</b>：chunk_range 和 chunk_stride 都是空间切割策略的核心参数，'
          '根据物理分析两者必然都显著，无需 PB"筛选"步骤'),
        B('<b>BBD 最少需要 3 个因子</b>：Box-Behnken 设计的最小规模是 3 因子 15 次实验，'
          '对 2 个因子的情况无法直接套用'),
        B('<b>3² 全因子设计更直接高效</b>：9 个唯一实验点覆盖全部因子组合，加 3 次中心点重复 = 12 次实验，'
          '足以拟合完整的二阶响应面模型'),
    ]

    design_compare = [
        ['设计方法', '因子数要求', '实验次数', '可估计的模型', '适用情况'],
        [pc('PB + BBD（原始两阶段计划）'), pc('≥ 4 个因子'), pc('12 + 15 = 27'), pc('筛选 + 二阶'), pc('因子多且不知哪个显著')],
        [pc('3² 全因子（本课题采用）'), pc('2 个因子'), pc('9 + 3 = 12'), pc('完整二阶响应面'), pc('因子少且已知均显著')],
        [pc('PB 筛选（仅）'), pc('≥ 2 个因子'), pc('12'), pc('线性主效应'), pc('只需判断显著性，不建模')],
        [pc('BBD（仅）'), pc('≥ 3 个因子'), pc('15（3因子）'), pc('完整二阶响应面'), pc('因子数 ≥ 3 时更高效')],
    ]
    story += [tbl(design_compare, [3.5*cm, 2.5*cm, 2.5*cm, 3.0*cm, 3.5*cm],
                  row_colors=[ROW_A, ROW_G, ROW_B, ROW_A, ROW_B])]
    story += [CAP('表 7.3　不同 DoE 策略的比较——本课题选择 3² 全因子设计的依据')]

    story += [SP(4), P('3² 全因子设计能拟合的完整二阶模型（2 因子）：')]
    story += [MATH('mIoU = β₀ + β₁·x₁ + β₂·x₂ + β₁₁·x₁² + β₂₂·x₂² + β₁₂·x₁x₂ + ε\n\n'
                   '共 6 个待估系数，9 个独立实验点（> 6），模型充分可识别。\n\n'
                   '其中：\n'
                   '  x₁ = (chunk_range − 6) / 2    （编码：4m → −1, 6m → 0, 8m → +1）\n'
                   '  x₂ = (chunk_stride − 3) / 1   （编码：2m → −1, 3m →  0, 4m → +1）')]

    story += [SP(6), H2G('7.6　响应变量的选择'), SP(4)]
    story += [P('本课题使用多个响应变量，全面评估切割策略的效果：')]
    resp_data = [
        ['响应变量', '测量内容', '对切割参数的敏感性'],
        [pc('整体 mIoU（%）\n（主要指标）'),
         pc('S3DIS Area_5 上所有 13 个类别的平均 IoU'),
         pc('对 chunk_range 最敏感：过小的切块使大型物体（天花板、地板）语义不连贯')],
        [pc('边界 mIoU（%）\n（补偿专项指标）'),
         pc('仅统计距切块边界 < 0.5m 区域内点的平均 IoU'),
         pc('对 chunk_stride 最敏感：步长越小重叠越多，'
            'Logit 平均的效果越显著，边界点预测越稳定')],
        [pc('峰值显存（GB）\n（硬件约束）'),
         pc('推理过程中的 GPU 显存峰值使用量'),
         pc('随 chunk_range 增大而增加（更大切块 → 更多点 → 更多显存）；chunk_stride 影响较小')],
        [pc('推理时间（s/场景）\n（效率指标）'),
         pc('处理一个完整大场景的总耗时（含切块、推理、Alignment）'),
         pc('随 chunk_stride 减小而急剧增加（步长减半 → 切块数约翻倍）')],
    ]
    story += [tbl(resp_data, [3.0*cm, 4.5*cm, 7.0*cm], fontsize=8,
                  row_colors=[ROW_A, ROW_G, ROW_B, ROW_G, ROW_A])]
    story += [CAP('表 7.4　响应变量的选择与预期效应分析')]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 第8章 Spatial Alignment
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('第 8 章　Spatial Alignment 的统计分析理论'), SP()]

    story += [H2('8.1　问题背景：大场景滑窗推理'), SP(4)]
    story += [P('当处理超出显存限制的大场景时，必须将场景切分为重叠的小块分别推理，再合并结果。'
                '重叠区域（每个点被多个块覆盖）的处理方式直接影响分割质量。')]

    story += [H3('两种处理策略'), SP(4)]
    sa_strat = [
        ['策略', '描述', '优势', '劣势'],
        [pc('条件 A：有 Alignment\n（Logit Averaging）'),
         pc('重叠区域的每个点，收集所有覆盖该点的块的\n原始输出（logits），取加权平均后再 argmax'),
         pc('边界点的预测更稳定；\n两个块的信息互补，\n错误被平均掉'),
         pc('需要存储每个点的所有 logits，\n内存和时间开销更大')],
        [pc('条件 B：无 Alignment\n（Last-Write Wins）'),
         pc('每块独立推理，重叠区域简单地\n保留最后一个覆盖该点的块的预测结果'),
         pc('实现简单，无额外开销'),
         pc('边界点受块处理顺序影响，\n相邻块对同一点可能给出不同标签，\n导致边界伪影')],
    ]
    story += [tbl(sa_strat, [3.5*cm, 5.0*cm, 3.0*cm, 3.5*cm])]

    story += [SP(6), H2('8.2　为什么 Logit 平均比 Label 投票更好'), SP(4)]
    story += [P('你的实验采用对 logits（softmax 之前的原始输出）取平均，而非对最终标签进行投票。'
                '这是有严格理论依据的。')]
    story += [P('设某点被两个块覆盖，两个块的 softmax 输出为：')]
    story += [MATH('块1的输出（已做softmax）：[wall: 0.70, floor: 0.25, ceiling: 0.05]\n'
                   '块2的输出（已做softmax）：[wall: 0.45, floor: 0.50, ceiling: 0.05]\n\n'
                   '标签投票结果：块1预测 wall，块2预测 floor → 投票平局，需要额外规则\n\n'
                   'Logit 平均（设 logits 分别为 L₁=[2.0, 0.5, −2.0]，L₂=[0.5, 1.8, −2.0]）：\n'
                   '  平均 logits = [1.25, 1.15, −2.0]\n'
                   '  softmax → wall: 0.53, floor: 0.47, ceiling: 0.00\n'
                   '  预测结果：wall（两块的信息都有贡献）')]
    story += [P('Logit 平均的理论优势：')]
    story += [
        B('保留了每个块对每个类别的<b>置信度信息</b>，不只是二值化的标签'),
        B('可以证明，如果两个块的预测来自于同一个模型对同一个点的不同上下文观测，'
          'Logit 平均在最大似然意义下是最优的融合方式'),
        B('对于置信度高的块（logits 分布陡峭），其贡献自然更大；对于不确定的块（logits 平坦），'
          '其贡献自然被稀释——无需人工调权重'),
    ]

    story += [SP(6), H2('8.3　评估指标的设计'), SP(4)]
    story += [P('Spatial Alignment 实验使用了三类评估指标：')]
    story += [
        B('<b>全局 mIoU 差值（ΔmIoU）</b>：条件A − 条件B，衡量 alignment 对整体精度的贡献。'
          '预期为正值，但由于大多数点不在边界，ΔmIoU 可能不大（0.5~2%）'),
        B('<b>边界点专项 IoU（Boundary IoU）</b>：只统计距离块边界 < 0.5m 的点的 IoU。'
          '这是 alignment 直接发挥作用的区域，预期该指标的改善比全局 mIoU 更显著（可能 2~5%）'),
        B('<b>推理时间差值（ΔTime）</b>：衡量 alignment 的计算开销。这是直接的 trade-off 分析。'),
    ]
    story += [NOTE('使用边界点专项 IoU 是一个重要的实验设计决策。如果只看全局 mIoU，alignment 的效果会被'
                   '大量非边界点"稀释"，可能显得微不足道。边界专项指标能更准确地揭示 alignment 的真实价值。')]

    story += [SP(6), H2('8.4　统计检验：配对 t 检验'), SP(4)]
    story += [P('你在5个大房间上分别比较条件 A 和条件 B，得到5对数据：'
                '(ΔmIoU₁, ΔmIoU₂, ΔmIoU₃, ΔmIoU₄, ΔmIoU₅)。')]
    story += [P('用<b>配对 t 检验</b>判断 alignment 的平均改善是否显著不为零：')]
    story += [MATH('H₀: μ_Δ = 0（alignment 没有效果）\n'
                   'H₁: μ_Δ > 0（alignment 能提升精度）\n\n'
                   't = (ΔmIoU_mean) / (S_Δ / √5)\n\n'
                   '其中 ΔmIoU_mean 是5个差值的平均，S_Δ 是标准差。\n'
                   '自由度 = 4，α = 0.05 时 t 临界值 = 2.132。\n'
                   '若 t > 2.132，则 alignment 的改善效果在统计上显著。')]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 附录A
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('附录 A　最小二乘估计的数学推导'), SP()]
    story += [P('本附录提供 OLS 正规方程解的完整推导，供深入理解使用。')]

    story += [H2('A.1　目标函数的矩阵形式'), SP(4)]
    story += [MATH('SSE = (y − Xβ)ᵀ(y − Xβ)\n'
                   '    = yᵀy − yᵀXβ − βᵀXᵀy + βᵀXᵀXβ\n'
                   '    = yᵀy − 2βᵀXᵀy + βᵀXᵀXβ   （因为 yᵀXβ 是标量，等于其转置 βᵀXᵀy）')]

    story += [H2('A.2　对 β 求导并令其为零'), SP(4)]
    story += [MATH('∂SSE/∂β = −2Xᵀy + 2XᵀXβ = 0\n\n'
                   '⟹ XᵀXβ = Xᵀy    （正规方程）\n\n'
                   '⟹ β̂ = (XᵀX)⁻¹Xᵀy    （当 XᵀX 可逆时）')]

    story += [H2('A.3　为什么 BBD 的 XᵀX 一定可逆'), SP(4)]
    story += [P('XᵀX 可逆当且仅当设计矩阵 X 的列满秩，即 p 列线性无关。')]
    story += [P('BBD 保证了这一点：')]
    story += [
        B('15 次实验 > 10 个系数，方程组有充分约束（超定方程组）'),
        B('BBD 的设计点覆盖了参数空间的不同"角落"，确保各参数效应能被独立估计'),
        B('中心点重复不会引入线性相关（因为其他实验点同样包含中心点参数，'
          '但还有其他参数的变化），不影响 XᵀX 的可逆性'),
    ]

    story += [H2('A.4　系数的方差（不确定性）'), SP(4)]
    story += [MATH('Var(β̂) = σ² · (XᵀX)⁻¹\n\n'
                   '其中 σ² 用 MSE 估计：σ̂² = SSE / (N − p) = SSE / 5\n\n'
                   '第 i 个系数的标准误差：SE(β̂ᵢ) = σ̂ · √[(XᵀX)⁻¹ᵢᵢ]\n\n'
                   '这就是 t 检验的分母：tᵢ = β̂ᵢ / SE(β̂ᵢ)')]

    story += [PageBreak()]

    # ══════════════════════════════════════════════════════════════════════════
    # 附录B
    # ══════════════════════════════════════════════════════════════════════════
    story += [H1('附录 B　本课题完整实验矩阵对照表'), SP()]
    story += [P('以下提供所有实验的完整参数对照，供实验执行时参考。')]
    story += [P('固定参数（所有实验相同）：')]
    story += [
        B('grid_size = 0.02m（传感器本征分辨率，固定不变）'),
        B('训练 epoch = 500（与基线一致）'),
        B('batch_size = 6（PTv3，受显存限制）'),
        B('SphereCrop.sample_rate = 0.6，point_max = 204800（与基线 PTv3 配置一致）'),
    ]

    story += [SP(4), H2('B.1　完整实验矩阵（3² 全因子 + 3 次中心点重复，共 12 runs）'), SP(4)]
    exp_matrix = [
        ['Run', 'x₁\n(chunk_range)', 'x₂\n(chunk_stride)', 'chunk_range\n(m×m)', 'chunk_stride\n(m)', '重叠比例', '备注'],
        ['01', '−1', '−1', '4×4', '2', '50%', '小块高重叠'],
        ['02', '0', '−1', '6×6', '2', '67%', '中块高重叠'],
        ['03', '+1', '−1', '8×8', '2', '75%', '大块高重叠'],
        ['04', '−1', '0', '4×4', '3', '25%', '小块中重叠'],
        ['05', '0', '0', '6×6', '3', '50%', pc('中心点\n（基线参数）')],
        ['06', '+1', '0', '8×8', '3', '62%', '大块中重叠'],
        ['07', '−1', '+1', '4×4', '4', '0%', pc('无重叠（步长=块宽）\n无边界补偿效果')],
        ['08', '0', '+1', '6×6', '4', '33%', '中块低重叠'],
        ['09', '+1', '+1', '8×8', '4', '50%', '大块低重叠'],
        ['10', '0', '0', '6×6', '3', '50%', '中心点重复 ×1'],
        ['11', '0', '0', '6×6', '3', '50%', '中心点重复 ×2'],
        ['12', '0', '0', '6×6', '3', '50%', '中心点重复 ×3'],
    ]
    story += [tbl(exp_matrix,
                  [1.0*cm, 1.5*cm, 1.5*cm, 2.2*cm, 2.2*cm, 2.0*cm, 4.1*cm],
                  fontsize=8,
                  extra_style=[
                      ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#C8E6C9')),
                      ('BACKGROUND', (0,7), (-1,7), colors.HexColor('#FFECB3')),
                      ('BACKGROUND', (0,10), (-1,12), colors.HexColor('#E8EAF6')),
                  ])]
    story += [CAP('表 B.1　3² 全因子实验矩阵（绿色=基线中心点，橙色=无重叠边界情况，蓝色=中心点重复）')]

    story += [SP(8), H2('B.2　实验结果记录表（待填写）'), SP(4)]
    results_table = [
        ['Run', 'chunk_range', 'chunk_stride', '整体\nmIoU (%)', '边界\nmIoU (%)', '峰值显存\n(GB)', '推理时间\n(s)', '备注'],
        ['01', '4m×4m', '2m', '', '', '', '', ''],
        ['02', '6m×6m', '2m', '', '', '', '', ''],
        ['03', '8m×8m', '2m', '', '', '', '', ''],
        ['04', '4m×4m', '3m', '', '', '', '', ''],
        ['05', '6m×6m', '3m', '', '', '', '', pc('基线对照\n(67.01%)')],
        ['06', '8m×8m', '3m', '', '', '', '', ''],
        ['07', '4m×4m', '4m', '', '', '', '', pc('无重叠\n（边界补偿下限）')],
        ['08', '6m×6m', '4m', '', '', '', '', ''],
        ['09', '8m×8m', '4m', '', '', '', '', ''],
        ['10', '6m×6m (重复)', '3m', '', '', '', '', '中心点重复'],
        ['11', '6m×6m (重复)', '3m', '', '', '', '', '中心点重复'],
        ['12', '6m×6m (重复)', '3m', '', '', '', '', '中心点重复'],
    ]
    story += [tbl(results_table,
                  [1.0*cm, 2.0*cm, 2.0*cm, 1.8*cm, 1.8*cm, 1.8*cm, 2.0*cm, 2.6*cm],
                  fontsize=7.5,
                  extra_style=[
                      ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#C8E6C9')),
                      ('BACKGROUND', (0,10), (-1,12), colors.HexColor('#E8EAF6')),
                  ])]
    story += [CAP('表 B.2　实验结果记录表（PTv3 + S3DIS Area_5，每次实验完成后填写数据）')]

    story += [SP(8), H2('B.3　Spatial Alignment 补偿效果对比实验'), SP(4)]
    story += [P('在最优切割参数（模型推荐的最优 chunk_range 和 chunk_stride 组合）的基础上，'
                '额外进行有/无 Alignment 的配对对比实验：')]
    align_table = [
        ['条件', 'chunk_range', 'chunk_stride', 'Alignment 策略', '整体\nmIoU (%)', '边界\nmIoU (%)', '推理时间\n(s)'],
        ['A（有补偿）', '最优值', '最优值', pc('✓ Logit 平均\n（所有重叠点取 logit 均值再 argmax）'), '', '', ''],
        ['B（无补偿）', '最优值', '最优值', pc('✗ Last-Write Wins\n（重叠点保留最后覆盖块的预测）'), '', '', ''],
        ['差值 A−B', '—', '—', '—', '', '', ''],
    ]
    story += [tbl(align_table,
                  [2.0*cm, 2.0*cm, 2.0*cm, 4.0*cm, 1.8*cm, 1.8*cm, 1.9*cm],
                  fontsize=7.5,
                  extra_style=[
                      ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFF9C4')),
                  ])]
    story += [CAP('表 B.3　Spatial Alignment 补偿效果对比实验（黄色行=差值，正值说明 Logit 平均有效）')]

    # ── 页脚 ─────────────────────────────────────────────────────────────────
    story += [
        SP(16),
        HRFlowable(width='100%', thickness=1, color=TU_RED, spaceAfter=6),
        Paragraph('实验设计方法论完全指南  ·  TU Berlin · MDT · Yucan Luo · 2026  ·  '
                  '本文档由 Python ReportLab 自动生成',
                  ST['footer']),
    ]
    return story


def main():
    out = '/workspace/docs/DoE理论详解.pdf'
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    doc.build(build())
    print(f'PDF generated: {out}')


if __name__ == '__main__':
    main()
