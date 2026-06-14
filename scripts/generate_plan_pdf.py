"""
Generate the 2-week experimental plan PDF in Chinese.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Chinese TTF fonts (WenQuanYi)
pdfmetrics.registerFont(TTFont('CJK-Regular', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'))
pdfmetrics.registerFont(TTFont('CJK-Bold',    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'))

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm

def make_styles():
    styles = getSampleStyleSheet()

    title = ParagraphStyle('MyTitle',
        fontName='CJK-Bold', fontSize=16, leading=22,
        textColor=colors.HexColor('#1a3a5c'), spaceAfter=6,
        alignment=1, wordWrap='CJK')

    subtitle = ParagraphStyle('MySubtitle',
        fontName='CJK-Regular', fontSize=11, leading=16,
        textColor=colors.HexColor('#444444'), spaceAfter=14,
        alignment=1, wordWrap='CJK')

    h1 = ParagraphStyle('H1',
        fontName='CJK-Bold', fontSize=13, leading=20,
        textColor=colors.white,
        backColor=colors.HexColor('#1a3a5c'),
        spaceBefore=14, spaceAfter=6,
        leftIndent=-0.2*cm, rightIndent=-0.2*cm,
        borderPad=4, wordWrap='CJK')

    h2 = ParagraphStyle('H2',
        fontName='CJK-Bold', fontSize=11, leading=18,
        textColor=colors.HexColor('#1a3a5c'),
        spaceBefore=10, spaceAfter=4,
        borderPad=2, wordWrap='CJK')

    h3 = ParagraphStyle('H3',
        fontName='CJK-Bold', fontSize=10, leading=16,
        textColor=colors.HexColor('#c0392b'),
        spaceBefore=8, spaceAfter=3, wordWrap='CJK')

    body = ParagraphStyle('Body', fontName='CJK-Regular', fontSize=9.5,
        leading=16, spaceAfter=4, wordWrap='CJK')

    bullet = ParagraphStyle('Bullet', fontName='CJK-Regular', fontSize=9.5,
        leading=16, leftIndent=14, bulletIndent=4, spaceAfter=3, wordWrap='CJK')

    bullet2 = ParagraphStyle('Bullet2', fontName='CJK-Regular', fontSize=9,
        leading=15, leftIndent=28, bulletIndent=18, spaceAfter=2, wordWrap='CJK')

    code = ParagraphStyle('Code',
        fontName='Courier', fontSize=8.5, leading=13,
        backColor=colors.HexColor('#f4f4f4'),
        textColor=colors.HexColor('#2c3e50'),
        leftIndent=14, spaceAfter=4, spaceBefore=2,
        borderColor=colors.HexColor('#cccccc'), borderWidth=0.5,
        borderPad=4, wordWrap='CJK')

    note = ParagraphStyle('Note', fontName='CJK-Regular', fontSize=9,
        leading=14, textColor=colors.HexColor('#666666'),
        backColor=colors.HexColor('#fffbea'),
        borderColor=colors.HexColor('#f0c040'), borderWidth=0.8,
        borderPad=5, leftIndent=8, spaceAfter=6, wordWrap='CJK')

    return dict(title=title, subtitle=subtitle, h1=h1, h2=h2, h3=h3,
                body=body, bullet=bullet, bullet2=bullet2, code=code, note=note)

S = make_styles()

def h1(text): return Paragraph(f'  {text}', S['h1'])
def h2(text): return Paragraph(text, S['h2'])
def h3(text): return Paragraph(text, S['h3'])
def p(text):  return Paragraph(text, S['body'])
def b(text):  return Paragraph(f'• {text}', S['bullet'])
def b2(text): return Paragraph(f'◦ {text}', S['bullet2'])
def code(text): return Paragraph(text, S['code'])
def note(text): return Paragraph(f'💡 {text}', S['note'])
def sp(h=6):  return Spacer(1, h)
def hr():     return HRFlowable(width='100%', thickness=0.5,
                                color=colors.HexColor('#cccccc'), spaceAfter=4)


def param_table():
    data = [
        ['enhanced.py 参数', '取值范围', 'Pointcept 对应字段', '物理含义'],
        ['scale', '20 – 100', 'GridSample.grid_size = 1/scale\n(0.01 – 0.05 m)', '坐标量化精度\n越大体素越细'],
        ['spatial_shape', '[256³] – [1024³]', 'SphereCrop.point_max\n(40k – 120k)', '空间裁剪块大小\n决定每次处理的区域'],
        ['step', '16 – 128', '推理滑窗步长\n= spatial_shape × overlap_ratio', '相邻块重叠比例\n影响边界精度'],
        ['jitter_range', '0 – 5 m', 'RandomJitter.sigma\n(0.005 – 0.2 m)', '平移抖动幅度\n训练数据增强'],
        ['voxel_size', '0.005 – 0.05 m', 'GridSample.grid_size', '下采样分辨率\n影响点云密度'],
        ['drop_prob', '0 – 0.3', 'RandomDropout.dropout_ratio', '实例随机丢弃率\n防止过拟合'],
    ]
    col_w = [3.2*cm, 3.0*cm, 5.0*cm, 4.2*cm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'CJK-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'CJK-Regular'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#f0f4fa'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#bbbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t


def pb_table():
    # Plackett-Burman 12-run design (4 factors)
    runs = [
        ['Run', 'grid_size', 'point_max', 'jitter', 'dropout', '说明'],
        ['1',  '+1(0.04)', '-1(40k)', '+1(0.2)', '-1(0.0)', ''],
        ['2',  '-1(0.01)', '+1(120k)', '+1(0.2)', '+1(0.2)', ''],
        ['3',  '+1(0.04)', '+1(120k)', '-1(0.005)', '+1(0.2)', ''],
        ['4',  '-1(0.01)', '+1(120k)', '+1(0.2)', '-1(0.0)', ''],
        ['5',  '+1(0.04)', '-1(40k)', '-1(0.005)', '+1(0.2)', ''],
        ['6',  '-1(0.01)', '-1(40k)', '+1(0.2)', '+1(0.2)', ''],
        ['7',  '+1(0.04)', '+1(120k)', '-1(0.005)', '-1(0.0)', ''],
        ['8',  '-1(0.01)', '-1(40k)', '-1(0.005)', '-1(0.0)', ''],
        ['9',  '0(0.02)',  '0(80k)',  '0(0.05)', '0(0.1)', '中心点 ×3'],
        ['10', '0(0.02)',  '0(80k)',  '0(0.05)', '0(0.1)', '中心点 ×3'],
        ['11', '0(0.02)',  '0(80k)',  '0(0.05)', '0(0.1)', '中心点 ×3'],
        ['12', '-1(0.01)', '+1(120k)', '-1(0.005)', '+1(0.2)', ''],
    ]
    col_w = [1.1*cm, 2.5*cm, 2.3*cm, 2.5*cm, 2.3*cm, 2.5*cm]
    t = Table(runs, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'CJK-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'CJK-Regular'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c7a4b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#f0faf4'), colors.white]),
        ('BACKGROUND', (0,9), (-1,11), colors.HexColor('#fffbea')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#bbbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    return t


def bbd_table():
    runs = [
        ['Run', 'grid_size', 'point_max', 'jitter', '实验目的'],
        ['1',  '-1', '-1', '0', '边角点'],
        ['2',  '+1', '-1', '0', '边角点'],
        ['3',  '-1', '+1', '0', '边角点'],
        ['4',  '+1', '+1', '0', '边角点'],
        ['5',  '-1', '0', '-1', '边角点'],
        ['6',  '+1', '0', '-1', '边角点'],
        ['7',  '-1', '0', '+1', '边角点'],
        ['8',  '+1', '0', '+1', '边角点'],
        ['9',  '0', '-1', '-1', '边角点'],
        ['10', '0', '+1', '-1', '边角点'],
        ['11', '0', '-1', '+1', '边角点'],
        ['12', '0', '+1', '+1', '边角点'],
        ['13-15', '0', '0', '0', '中心点 ×3（估计实验误差）'],
    ]
    col_w = [1.8*cm, 2.5*cm, 2.5*cm, 2.5*cm, 5.8*cm]
    t = Table(runs, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'CJK-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'CJK-Regular'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7b3fa0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#f8f0fc'), colors.white]),
        ('BACKGROUND', (0,13), (-1,13), colors.HexColor('#fffbea')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#bbbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    return t


def timeline_table():
    data = [
        ['时间', '任务', '预期产出', 'GPU 占用'],
        ['第1天\n(周一)', 'S3DIS数据下载+预处理\n跑通PTv3和SpUNet基线', '基线mIoU\n(默认参数)', '~6小时'],
        ['第2天\n(周二)', '参数映射配置\n编写DoE自动化实验脚本\n生成PB实验矩阵', '实验脚本\nPB矩阵12组config文件', '0小时\n(代码工作)'],
        ['第3-4天\n(周三四)', 'PB筛选实验：SpUNet\n12 runs × 500 epoch', 'SpUNet\n12组mIoU+显存数据', '~12小时\n(连续跑)'],
        ['第5-6天\n(周五六)', 'PB筛选实验：PTv3\n6组关键配置 × 500 epoch', 'PTv3\n6组mIoU数据', '~15小时\n(连续跑)'],
        ['第7天\n(周日)', '统计分析PB结果\n主效应图+方差分析\n确定显著参数', '显著参数列表\nBBD实验设计矩阵', '0小时\n(分析工作)'],
        ['第8-10天\n(周一三)', 'BBD精细实验\n15 runs on SpUNet+PTv3', '二阶响应面数据', '~25小时\n(连续跑)'],
        ['第11-12天\n(周四五)', '拟合回归模型\nmIoU=f(...) Memory=g(...)\nSpatial alignment对比实验', '回归公式\n参数选择规则表', '~4小时\n(alignment实验)'],
        ['第13-14天\n(周六日)', 'SemanticKITTI验证实验\n自适应参数 vs 默认参数对比\n整理实验数据+图表', '验证结果\n最终实验报告数据', '~8小时'],
    ]
    col_w = [2.0*cm, 5.5*cm, 4.5*cm, 2.5*cm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'CJK-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'CJK-Regular'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#c0392b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (3,0), (3,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#fdf0ee'), colors.white]),
        ('BACKGROUND', (0,1), (-1,2), colors.HexColor('#fdf0ee')),
        ('BACKGROUND', (0,3), (-1,4), colors.HexColor('#fff8f7')),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#fdf0ee')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#ddbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t


def issues_table():
    data = [
        ['问题', '位置', '影响', '修复方案'],
        ['crop()被注释掉',
         'transform_train()\n第155-167行',
         'spatial_shape和step\n对训练完全无效',
         '取消注释并接入\nvoxel_cfg.step参数'],
        ['jitter_range硬编码±2m',
         'dataAugment()\n第67行',
         '无法通过配置\n控制抖动幅度',
         '改为self.voxel_cfg.jitter_range\n或作为构造参数传入'],
        ['drop_prob硬编码0.1',
         'transform_train()\n第169行',
         '无法实验不同\ndrop_prob对mIoU影响',
         '改为self.voxel_cfg.drop_prob'],
        ['min/max_voxel硬编码\n0.01/0.03',
         'transform_train()\n第169行',
         '无法实验不同\nvoxel_size范围',
         '改为self.voxel_cfg.min_voxel\n和max_voxel'],
        ['缺少大规模场景\n推理滑窗逻辑',
         '整个文件',
         '无法处理超大\n点云(ArCH/DALES)',
         '实现sliding window\ninference pipeline'],
    ]
    col_w = [3.0*cm, 3.0*cm, 3.5*cm, 5.0*cm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'CJK-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'CJK-Regular'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#c0392b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#fff5f5'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#ddbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t


def build():
    out = '/workspace/实验计划_两周DoE.pdf'
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=2.2*cm, bottomMargin=2*cm)
    story = []

    # ── Title ────────────────────────────────────────────────────
    story += [
        sp(10),
        Paragraph('大规模点云语义分割参数优化', S['title']),
        Paragraph('两周实验计划（DoE 方法论）', S['subtitle']),
        Paragraph('TU Berlin · MDT 研究组 · Yucan Luo', S['subtitle']),
        hr(), sp(4),
    ]

    # ── 0. 论文核心目标 ───────────────────────────────────────────
    story += [
        h1('0  论文核心目标与实验逻辑'),
        sp(4),
        p('本论文旨在通过<b>实验设计方法（Design of Experiments, DoE）</b>，系统建立处理参数与分割精度之间的定量关系，'
          '最终实现一个<b>自适应参数选择模块</b>：给定场景统计特征（点密度、场景范围）和硬件约束（显存），'
          '自动推荐最优的 scale、spatial_shape、step、voxel_size 等参数组合。'),
        sp(4),
        p('实验需要回答两个核心问题：'),
        b('哪些参数对 mIoU 影响最显著？（筛选阶段，Plackett-Burman 设计）'),
        b('显著参数与 mIoU / 显存之间的精确函数关系是什么？（建模阶段，Box-Behnken 设计）'),
        sp(6),
    ]

    # ── 1. 代码现状分析 ──────────────────────────────────────────
    story += [
        h1('1  enhanced.py 代码现状与问题分析'),
        sp(4),
        p('通过分析 /workspace/enhanced.py（Fan Qinyuan 的增强策略代码），发现以下<b>需要修复的关键问题</b>（必须解决后才能进行DoE实验）：'),
        sp(6),
        issues_table(),
        sp(8),
        note('由于 enhanced.py 缺少原始框架（voxelization_idx 所在的模块不在本机），'
             '建议使用 Pointcept 作为实验平台，将 enhanced.py 参数映射到 Pointcept 的 transform 配置体系中。'),
        sp(6),
    ]

    # ── 2. 参数映射 ──────────────────────────────────────────────
    story += [
        h1('2  参数映射：enhanced.py → Pointcept'),
        sp(4),
        p('下表列出了 enhanced.py 中每个可调参数与 Pointcept transform 流水线的对应关系，'
          '以及在实验中使用的取值范围：'),
        sp(6),
        param_table(),
        sp(8),
        p('<b>参数间的约束关系（重要）：</b>'),
        b('grid_size 与 voxel_size 在物理含义上等价，实验中可合并为一个因子（grid_size = 1/scale）'),
        b('spatial_shape × grid_size = 实际空间块尺寸（单位：米）。'
          'S3DIS 房间约 5-10m，建议 point_max=80k 对应约 5m 的感受野'),
        b('step/spatial_shape = 滑窗重叠率，影响推理时的边界处理质量'),
        sp(6),
    ]

    # ── 3. 实验设计 ──────────────────────────────────────────────
    story.append(PageBreak())
    story += [
        h1('3  实验设计（DoE 方案）'),
        sp(6),
    ]

    # 3.1 筛选
    story += [
        h2('3.1  第一阶段：Plackett-Burman 筛选实验（12 runs）'),
        sp(4),
        p('<b>目标</b>：用最少的实验次数（12次）识别出对 mIoU 影响显著的参数。每个参数取高低两个水平。'),
        p('<b>模型</b>：SpUNet（快，约 50 min/run @ 500 epoch on A6000）+ PTv3（6个关键点，约 2.5h/run）'),
        sp(6),
        pb_table(),
        sp(8),
        p('<b>分析方法</b>：计算每个参数的主效应（高水平均值 − 低水平均值），'
          '绘制 Main Effects Plot，用 t 检验或 ANOVA 判断显著性（p < 0.05）。'),
        p('<b>预期输出</b>：筛选出2-3个显著参数，进入下一阶段精细建模。'),
        sp(6),
    ]

    # 3.2 BBD
    story += [
        h2('3.2  第二阶段：Box-Behnken Design 精细实验（15 runs）'),
        sp(4),
        p('<b>目标</b>：对筛选出的显著参数（假设为 grid_size、point_max、jitter）建立二阶响应面模型，'
          '捕捉参数间的交互效应和非线性关系。'),
        sp(6),
        bbd_table(),
        sp(8),
        p('<b>拟合模型</b>：'),
        code('mIoU = β₀ + β₁·x₁ + β₂·x₂ + β₃·x₃\n'
             '     + β₁₂·x₁x₂ + β₁₃·x₁x₃ + β₂₃·x₂x₃\n'
             '     + β₁₁·x₁² + β₂₂·x₂² + β₃₃·x₃²'),
        code('Memory = γ₀ + γ₁·point_max + γ₂·grid_size + γ₁₂·point_max·grid_size + ...'),
        sp(4),
        p('使用 Python statsmodels 或 sklearn 拟合，评估 R²、RMSE，绘制等高线图（Contour Plot）。'),
        sp(6),
    ]

    # 3.3 Spatial alignment
    story += [
        h2('3.3  附加实验：Spatial Alignment 对比'),
        sp(4),
        p('任务书明确要求量化 spatial alignment（重叠区域一致性合并）的效果：'),
        b('条件A：有 alignment（重叠区域取多次预测的平均 logits）'),
        b('条件B：无 alignment（每个块独立预测，边界不处理）'),
        b('评估指标：mIoU 差值、处理时间差值、边界点的 IoU 专项分析'),
        sp(4),
        note('Spatial alignment 只影响推理流程，不影响训练。'
             '需要先实现滑窗推理 pipeline（enhanced.py 中 crop() 的推理版本），'
             '建议在第11-12天完成这个实现。'),
        sp(6),
    ]

    # ── 4. 两周详细日程 ──────────────────────────────────────────
    story.append(PageBreak())
    story += [
        h1('4  两周详细日程表'),
        sp(6),
        timeline_table(),
        sp(8),
        p('<b>GPU 占用统计</b>：'),
        b('第1周：~33 小时 GPU 时间（基线 + PB 筛选），可连续排队跑，人工干预少'),
        b('第2周：~37 小时 GPU 时间（BBD + alignment实验 + 验证），A6000 可应对'),
        b('总计：~70 小时 GPU 时间 / 14天 = 平均 5h/天，可行'),
        sp(6),
    ]

    # ── 5. 代码操作步骤 ──────────────────────────────────────────
    story += [
        h1('5  具体代码操作步骤'),
        sp(4),
    ]

    story += [
        h2('Step 1：激活环境并下载 S3DIS'),
        code('conda activate thesis\ncd /workspace/Pointcept'),
        code('# 方法1：从 Hugging Face 下载预处理版本\npip install huggingface_hub\npython -c "\nfrom huggingface_hub import snapshot_download\nsnapshot_download(repo_id=\'OpenGVLab/S3DIS\',\n    repo_type=\'dataset\',\n    local_dir=\'/workspace/data/s3dis_raw\')\n"'),
        code('# 方法2：手动下载后按官方脚本预处理\n# https://github.com/Pointcept/Pointcept 的 README 有详细说明'),
        sp(4),
    ]

    story += [
        h2('Step 2：跑通基线'),
        code('# SpUNet 基线（速度快，约1h）\npython tools/train.py \\\n  --config-file configs/s3dis/semseg-spunet-v1m1-0-base.py \\\n  --options save_path=exp/baseline_spunet\n\n# PTv3 基线（确认能跑起来即可，可后台进行）\npython tools/train.py \\\n  --config-file configs/s3dis/semseg-pt-v3m1-0-base.py \\\n  --options save_path=exp/baseline_ptv3'),
        sp(4),
    ]

    story += [
        h2('Step 3：生成 DoE 实验 Config 文件'),
        p('编写 Python 脚本，基于 PB 矩阵自动生成 12 个 .py 配置文件，每个文件修改对应的 '
          'grid_size / point_max / jitter.sigma / dropout.ratio 参数值：'),
        code('# generate_doe_configs.py 核心逻辑\nimport copy, os\nfrom mmengine.config import Config\n\nbase = Config.fromfile("configs/s3dis/semseg-spunet-v1m1-0-base.py")\n\nPB_MATRIX = [\n    # [grid_size, point_max, jitter_sigma, dropout_ratio]\n    [0.04, 40000,  0.200, 0.0],\n    [0.01, 120000, 0.200, 0.2],\n    [0.04, 120000, 0.005, 0.2],\n    # ... 其余9组\n]\n\nfor i, (gs, pm, js, dr) in enumerate(PB_MATRIX):\n    cfg = copy.deepcopy(base)\n    # 修改 GridSample.grid_size\n    # 修改 SphereCrop.point_max\n    # 修改 RandomJitter.sigma\n    # 修改 RandomDropout.dropout_ratio\n    cfg.dump(f"configs/doe/pb_run_{i+1:02d}.py")'),
        sp(4),
    ]

    story += [
        h2('Step 4：批量提交实验'),
        code('# 串行跑所有 PB 实验（在后台 nohup 执行）\nfor i in $(seq 1 12); do\n    python tools/train.py \\\n      --config-file configs/doe/pb_run_$(printf "%02d" $i).py \\\n      --options save_path=exp/doe/pb_run_$(printf "%02d" $i) \\\n                epoch=500\ndone'),
        code('# 或用 nohup 放后台，关闭终端也继续跑\nnohup bash run_all_pb.sh > logs/pb_all.log 2>&1 &'),
        sp(4),
    ]

    story += [
        h2('Step 5：提取结果并分析'),
        code('# collect_results.py\nimport json, os, pandas as pd\n\nresults = []\nfor run_dir in sorted(os.listdir("exp/doe")):\n    log = json.load(open(f"exp/doe/{run_dir}/eval.json"))\n    results.append({"run": run_dir, "mIoU": log["mIoU"],\n                    "peak_mem_GB": log.get("peak_mem", 0)})\n\ndf = pd.DataFrame(results)\ndf.to_csv("doe_results.csv", index=False)\nprint(df.sort_values("mIoU", ascending=False))'),
        code('# 主效应分析\nimport statsmodels.api as sm\nfrom statsmodels.formula.api import ols\n\nmodel = ols("mIoU ~ grid_size + point_max + jitter + dropout", data=df).fit()\nprint(sm.stats.anova_lm(model, typ=2))  # 看 F 统计量和 p 值'),
        sp(6),
    ]

    # ── 6. 最终产出 ───────────────────────────────────────────────
    story += [
        h1('6  预期最终产出'),
        sp(4),
        h2('6.1  DoE 实验产出（写入论文第3-4章）'),
        b('Plackett-Burman 主效应图：显示每个参数对 mIoU 的独立贡献'),
        b('Box-Behnken 响应面图：显示参数交互效应和最优区域'),
        b('回归方程：mIoU = f(scale, spatial_shape, step, ...)，附 R² 和 RMSE'),
        b('显存预测模型：M = g(point_max, grid_size)，可用于资源约束下的参数选择'),
        b('Spatial alignment 增益分析：mIoU 提升幅度 vs 时间开销'),
        sp(4),
        h2('6.2  自适应参数选择模块'),
        b('输入：scene_extent（m）, point_density（pts/m³）, available_VRAM（GB）'),
        b('输出：推荐的 grid_size, point_max, step, jitter_range'),
        b('形式：回归公式 + 查找表（两种形式，分别满足"可解释"和"实用"的要求）'),
        sp(4),
        h2('6.3  跨数据集验证（论文第5章）'),
        b('训练集（DoE）：S3DIS（室内，~10⁶ points/area）'),
        b('验证集1：SemanticKITTI（室外驾驶场景，Pointcept 原生支持，容易获取）'),
        b('验证集2：如有条件，在 ArCH 或 DALES 上进行大规模推理测试'),
        sp(8),
    ]

    # ── 7. 重要提醒 ──────────────────────────────────────────────
    story += [
        h1('7  重要提醒与风险点'),
        sp(4),
        note('⚠ 首要行动：联系 Fan Qinyuan 获取 enhanced.py 所属的完整项目代码。'
             '如有完整框架，可直接在原框架中做DoE，无需迁移到Pointcept，更贴近任务书要求。'),
        sp(4),
        h3('时间风险'),
        b('S3DIS 申请可能需要1-2天等待。建议同时准备 SemanticKITTI（公开下载，无需申请）作为备用起点。'),
        b('PTv3 训练时间比 SpUNet 慢约 3-4 倍。如时间紧张，第一周以 SpUNet 为主，PTv3 做代表性验证即可。'),
        b('500 epoch 与 3000 epoch 的 mIoU 可能有差异，但参数间的<b>相对排名</b>在早期就趋于稳定（文献支持）。'),
        sp(4),
        h3('实验设计注意事项'),
        b('每次修改配置参数时，保持<b>随机种子固定</b>（seed=42），确保结果可复现。'),
        b('记录每次实验的<b>peak GPU memory</b>（可在训练脚本里加 torch.cuda.max_memory_allocated() 记录）。'),
        b('PB 实验完成后先做初步分析，再决定 BBD 的参数范围，不要直接用预设范围。'),
        sp(4),
        h3('本机硬件说明'),
        b('RTX A6000 有 46GB VRAM，远超任务书要求的 8/12/24GB 场景。'),
        b('DoE 主体实验在 A6000 上全速跑，最后做受限场景验证时可用 torch.cuda.set_per_process_memory_fraction() 模拟。'),
        sp(8),
        hr(),
        Paragraph('生成时间：2026-06-09 | TU Berlin MDT | Yucan Luo', S['note']),
    ]

    doc.build(story)
    print(f'PDF 已生成：{out}')
    return out


if __name__ == '__main__':
    build()
