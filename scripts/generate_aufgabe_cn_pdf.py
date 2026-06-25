"""
Aufgabenstellung_Luo.pdf 中文翻译 PDF 生成脚本
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

TU_BLUE   = colors.HexColor("#1a3a5c")
TU_RED    = colors.HexColor("#C40D1E")
DARK_BG   = colors.HexColor("#1A1A2E")
LIGHT_BLU = colors.HexColor("#E3F2FD")
LIGHT_GRN = colors.HexColor("#E8F5E9")
GRAY_LT   = colors.HexColor("#F4F4F4")
GRAY_BD   = colors.HexColor("#cccccc")

def s(name, **kw):
    defaults = dict(fontName=F, fontSize=10, leading=16, wordWrap='CJK')
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

ST = dict(
    title  = s('title', fontSize=16, leading=24, alignment=TA_CENTER,
                textColor=DARK_BG, spaceAfter=4),
    sub    = s('sub',   fontSize=10, leading=15, alignment=TA_CENTER,
                textColor=colors.HexColor('#555555'), spaceAfter=12),
    h1     = s('h1',    fontSize=13, leading=20, textColor=colors.white,
                backColor=DARK_BG, spaceBefore=14, spaceAfter=6,
                leftIndent=4, borderPad=5),
    h2     = s('h2',    fontSize=11, leading=18, textColor=colors.white,
                backColor=TU_BLUE, spaceBefore=10, spaceAfter=4,
                leftIndent=4, borderPad=4),
    body   = s('body',  fontSize=10, leading=16, spaceAfter=6, alignment=TA_JUSTIFY),
    bullet = s('bullet',fontSize=10, leading=16, leftIndent=16, spaceAfter=4,
                bulletIndent=6),
    bullet2= s('bullet2',fontSize=10, leading=15, leftIndent=32, spaceAfter=3,
                bulletIndent=20),
    bullet3= s('bullet3',fontSize=9,  leading=14, leftIndent=48, spaceAfter=3,
                bulletIndent=36),
    note   = s('note',  fontSize=9,   leading=14, textColor=colors.HexColor('#555555'),
                spaceAfter=4),
    label  = s('label', fontSize=10,  leading=16, textColor=TU_BLUE, spaceAfter=4),
    sign   = s('sign',  fontSize=10,  leading=16, alignment=TA_LEFT, spaceAfter=4),
    footer = s('footer',fontSize=8,   leading=12, alignment=TA_CENTER,
                textColor=colors.HexColor('#888888')),
)

def B(text, style='body'): return Paragraph(text, ST[style])
def SP(h=0.15): return Spacer(1, h*cm)
def HR(): return HRFlowable(width='100%', thickness=0.5, color=GRAY_BD, spaceAfter=6)

def build():
    out = '/workspace/docs/Aufgabenstellung_Luo_中文.pdf'
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )

    story = []

    # ── 页眉信息 ──────────────────────────────────────────────────────────────
    story.append(B('柏林工业大学 | Einsteinufer 17 | 10587 Berlin', 'note'))
    story.append(B('柏林，2025年12月15日', 'note'))
    story.append(SP(0.3))
    story.append(B('致：Yucan Luo 先生（学号 408454）的硕士论文任务书', 'sub'))
    story.append(SP(0.2))

    # 右侧部门信息以表格展示
    info = Table([[
        B('第四学院 电气工程与计算机科学\n'
          '能源与自动化技术研究所\n'
          '电子测量与诊断技术专业\n\n'
          'Prof. Dr.-Ing. Clemens Gühmann\n\n'
          '秘书处 EN 13，房间 EN 538\n'
          'Einsteinufer 17，10587 Berlin', 'note'),
        B('电话：+49 (0)30 314-29393\n'
          '传真：+49 (0)30 314-22120\n'
          'clemens.guehmann@tu-berlin.de\n\n'
          '负责人：Ewa Heinze\n'
          '电话：+49 (0)30 314-22280\n'
          '传真：+49 (0)30 314-22120\n'
          'ewa.heinze@tu-berlin.de', 'note'),
    ]], colWidths=['55%','45%'])
    info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GRAY_LT),
        ('BOX',        (0,0), (-1,-1), 0.5, GRAY_BD),
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(info)
    story.append(SP(0.4))
    story.append(HR())

    # ── 题目 ──────────────────────────────────────────────────────────────────
    story.append(B('面向资源受限设备的大规模点云语义分割增强方法研究', 'title'))
    story.append(HR())
    story.append(SP(0.2))

    # ── 问题背景 ──────────────────────────────────────────────────────────────
    story.append(B('一、问题背景', 'h1'))

    story.append(B(
        '点云语义分割是三维场景理解的核心任务。目前最先进的方法在基准数据集上取得了较高精度，'
        '但在大规模场景下面临关键瓶颈。', 'body'))

    story.append(B('<b>规模与资源的矛盾：</b>标准基准场景（如 ScanNet，约 10⁵ 个点/场景）'
                   '可在现代 GPU 上处理；而大规模场景则面临显著挑战：', 'body'))
    story.append(B('• 建筑遗产数据集（ArCH）：每个场景超过 1000 万至 1 亿个点', 'bullet'))
    story.append(B('• 城市测绘数据集（SensatUrban、DALES）：数亿个点', 'bullet'))
    story.append(B('• 室外基准数据集（Semantic3D）：总点数达数十亿', 'bullet'))

    story.append(SP(0.1))
    story.append(B(
        '当前主流方法（基于点的 PTv3、基于体素的 MinkowskiNet 等）针对标准规模场景进行了优化，'
        '应用于大规模场景时，往往出现显存溢出（OOM）或需要自行实现空间分块策略。', 'body'))

    story.append(B('<b>现有方法的局限性：</b>', 'label'))
    story.append(B('• 架构级效率改进（稀疏卷积、序列化注意力机制）虽提升了内存效率，'
                   '但未从根本上解决大规模处理问题', 'bullet'))
    story.append(B('• 用户需自行实现空间分块策略', 'bullet'))
    story.append(B('• 目前尚无关于处理参数（块大小、重叠率）对不同场景和算法分割性能影响的系统性研究', 'bullet'))
    story.append(B('• 参数选择依赖试错，缺乏原则性指导', 'bullet'))

    story.append(SP(0.1))
    story.append(B('<b>研究机遇：</b>需要一种系统的、实验驱动的方法，以：', 'body'))
    story.append(B('1. 通过实验设计（DoE）建立处理参数、场景特征与分割性能之间的定量关系', 'bullet'))
    story.append(B('2. 推导出可泛化的规律/公式，用于预测给定场景下的最优参数', 'bullet'))
    story.append(B('3. 在不同数据集和算法上验证所推导的模型', 'bullet'))

    story.append(SP(0.2))

    # ── 增强策略背景 ──────────────────────────────────────────────────────────
    story.append(B('增强策略背景', 'h2'))
    story.append(B(
        'Fan Qinyuan 先生已开发了一套大规模点云语义分割增强策略，主要包含以下核心模块：', 'body'))
    story.append(B('• <b>坐标缩放与空间裁剪：</b>对点坐标进行缩放，并通过滑动窗口将场景裁剪为固定大小的空间块', 'bullet'))
    story.append(B('• <b>数据增强：</b>平移抖动、随机翻转、缩放和旋转等几何变换，提升训练鲁棒性', 'bullet'))
    story.append(B('• <b>自适应降采样：</b>基于体素密度的概率点丢弃，均衡计算负载', 'bullet'))

    story.append(SP(0.1))
    story.append(B('该策略涉及多个可配置参数：', 'body'))

    param_data = [
        ['参数', '说明', '示例值'],
        ['scale', '坐标缩放因子', '50'],
        ['spatial_shape', '空间裁剪尺寸', '[512, 512, 512]'],
        ['step', '滑动窗口步长（控制块重叠）', '32'],
        ['jitter_range', '平移扰动范围', '±2m'],
        ['voxel_size', '体素降采样尺寸范围', '0.01–0.03m'],
        ['drop_prob', '实例丢弃概率', '0.1'],
    ]
    pt = Table(param_data, colWidths=['28%','52%','20%'])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TU_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,-1), F),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('LEADING',    (0,0), (-1,-1), 14),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BLU, colors.white]),
        ('BOX',        (0,0), (-1,-1), 0.5, GRAY_BD),
        ('GRID',       (0,0), (-1,-1), 0.3, GRAY_BD),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(pt)
    story.append(SP(0.2))

    story.append(B(
        '目前，这些参数依赖人工经验调整。一种系统的自适应参数选择方法，将显著提升该策略在'
        '多样化场景和硬件配置下的适用性。', 'body'))

    story.append(B(
        'Fan Qinyuan 先生还开发了 PoLaAll 平台，集成了点云标注的语义分割功能。'
        '一种有原则的参数选择方法将大幅拓展该平台对大规模场景的适用范围。', 'body'))

    story.append(SP(0.1))
    story.append(B('<b>两个核心技术问题：</b>', 'label'))
    story.append(B(
        '1. 处理参数（块大小、重叠率）、增强策略参数（scale、spatial_shape、step、'
        'voxel_size、drop_prob）、场景特征与分割精度之间的定量关系是什么？', 'bullet'))
    story.append(B(
        '2. 能否从系统实验中推导出可泛化的规律，以指导不同场景下的参数选择？', 'bullet'))

    # ── 研究目标 ──────────────────────────────────────────────────────────────
    story.append(B('二、研究目标', 'h1'))
    story.append(B(
        '本论文旨在开发一种面向大规模点云语义分割的<b>自适应增强策略</b>，'
        '能够根据场景特征和硬件约束自动选择最优处理参数。', 'body'))
    story.append(B('具体目标如下：', 'body'))
    story.append(B(
        '• 开展系统性实验设计（DoE），分析处理参数、场景特征与分割性能在多种'
        '主流架构上的关系', 'bullet'))
    story.append(B(
        '• 从实验数据中推导可泛化的规律或预测模型，作为自适应策略的基础', 'bullet'))
    story.append(B(
        '• 在从标准规模到超大规模的多样化基准数据集上验证自适应策略的实际有效性', 'bullet'))

    # ── 工作内容 ──────────────────────────────────────────────────────────────
    story.append(B('三、工作内容', 'h1'))

    # 目标1
    story.append(B('目标一：增强方法研究', 'h2'))

    story.append(B('第一阶段：文献调研与基线分析', 'label'))
    story.append(B('• 调研大规模点云分割方法及其资源需求', 'bullet'))
    story.append(B('• 分析基于点的主流方法（如 Point Transformer、PTv3）', 'bullet'))
    story.append(B('• 分析基于体素的主流方法（如 MinkowskiNet、SPVCNN）', 'bullet'))
    story.append(B('• 识别计算瓶颈与显存消耗规律', 'bullet'))
    story.append(SP(0.1))

    story.append(B('第二阶段：实验设计（DoE）', 'label'))
    story.append(B('根据增强策略定义实验因子：', 'body'))

    story.append(B('缩放与裁剪参数：', 'bullet'))
    story.append(B('◦ scale：坐标缩放因子（范围：20–100）', 'bullet2'))
    story.append(B('◦ spatial_shape：空间裁剪尺寸（[256,256,256] 至 [1024,1024,1024]）', 'bullet2'))
    story.append(B('◦ step：滑动窗口步长，控制块重叠（范围：16–128）', 'bullet2'))
    story.append(B('数据增强参数：', 'bullet'))
    story.append(B('◦ jitter_range：平移扰动范围（范围：0–5m）', 'bullet2'))
    story.append(B('降采样参数：', 'bullet'))
    story.append(B('◦ voxel_size_range：体素降采样尺寸范围（范围：0.005–0.05m）', 'bullet2'))
    story.append(B('◦ drop_prob：实例丢弃概率（范围：0–0.3）', 'bullet2'))
    story.append(B('处理模式：空间对齐（重叠区域一致性合并）与无对齐（独立块处理）', 'bullet'))
    story.append(B('场景特征：点密度（点/m³）、场景范围、几何复杂度', 'bullet'))
    story.append(B('算法类型：基于点（PTv3、Point Transformer）与基于体素（MinkowskiNet、Cylinder3D）', 'bullet'))
    story.append(B('硬件约束：可用显存（8GB、12GB、24GB）', 'bullet'))

    story.append(SP(0.1))
    story.append(B('响应变量：', 'body'))
    story.append(B('• 分割质量：mIoU、AP 等', 'bullet'))
    story.append(B('• 资源消耗：峰值显存、处理时间', 'bullet'))

    story.append(SP(0.1))
    story.append(B('DoE 设计方案：', 'body'))
    story.append(B('• 全因子或部分因子设计，探索参数空间', 'bullet'))
    story.append(B('• 多数据集以覆盖场景多样性', 'bullet'))
    story.append(B('• 多次重复运行以保证统计显著性', 'bullet'))
    story.append(B('• 系统执行实验并收集数据', 'bullet'))
    story.append(SP(0.1))

    story.append(B('第三阶段：规律提取与模型推导', 'label'))
    story.append(B('实验数据分析：', 'body'))
    story.append(B('• 因子与响应变量的相关性分析', 'bullet'))
    story.append(B('• 识别显著因子及交互效应', 'bullet'))
    story.append(B('• 可视化参数–性能关系', 'bullet'))

    story.append(SP(0.05))
    story.append(B('推导预测模型/规律：', 'body'))
    story.append(B('• 回归模型：mIoU = f(scale, spatial_shape, step, voxel_size, drop_prob, 点密度, 算法类型, …)', 'bullet'))
    story.append(B('• 显存模型：M = g(块大小, voxel_size_range, 点数, 算法类型, …)', 'bullet'))
    story.append(B('• 实用决策规则或查找表', 'bullet'))

    story.append(SP(0.05))
    story.append(B('模型要求：可解释性、可泛化性、实用性', 'body'))
    story.append(SP(0.1))

    story.append(B('第四阶段：实现', 'label'))
    story.append(B('• 基于所推导模型，实现自适应参数选择模块（自动估算最优 scale、spatial_shape、step 等）', 'bullet'))
    story.append(B('• 扩展现有增强策略，支持自适应参数配置', 'bullet'))
    story.append(B('• 实现可配置块大小和重叠率的场景分块流水线', 'bullet'))
    story.append(B('• 与基于点和基于体素的主流方法集成', 'bullet'))
    story.append(B('• 实现分块处理的边界处理与结果合并', 'bullet'))

    # 目标2
    story.append(B('目标二：验证与评估', 'h2'))

    story.append(B('第五阶段：实验设置', 'label'))
    story.append(B('准备覆盖不同规模的评估数据集：', 'body'))
    story.append(B('• 大规模室内：S3DIS（每区域约 10⁶ 点）、ArCH（每场景 500–1500 万点）', 'bullet'))
    story.append(B('• 大规模室外：SensatUrban（30 亿点）、DALES（5 亿点，航空 LiDAR）', 'bullet'))
    story.append(B('• 大规模驾驶：KITTI-360（覆盖 73.7km）', 'bullet'))
    story.append(B('• 定义资源受限测试环境（如 8GB、12GB 显存限制）', 'bullet'))
    story.append(B('• 在资源约束下建立主流方法基线性能', 'bullet'))
    story.append(SP(0.1))

    story.append(B('第六阶段：模型验证', 'label'))
    story.append(B('• 在未参与 DoE 的数据集与不同硬件配置上验证推导模型', 'bullet'))
    story.append(B('• 对比模型预测参数与经验最优参数', 'bullet'))
    story.append(B('• 量化预测精度', 'bullet'))
    story.append(SP(0.1))

    story.append(B('第七阶段：性能评估', 'label'))
    story.append(B('• 对比模型引导参数选择与任意固定参数的效果（精度、OOM 规避）', 'bullet'))
    story.append(B('• 跨场景规模评估：大规模室内（S3DIS）、大规模室外（ArCH、DALES）、大规模驾驶（KITTI-360）', 'bullet'))
    story.append(B('• 评估指标：mIoU、per-class IoU、AP（分割质量）；峰值显存、总处理时间（资源消耗）', 'bullet'))
    story.append(SP(0.1))

    story.append(B('第八阶段：分析', 'label'))
    story.append(B('实验规律分析：哪些因子对性能影响最大？参数间是否存在交互效应？点方法与体素方法规律是否不同？', 'bullet'))
    story.append(B('空间对齐分析：量化对齐与非对齐的精度差异、对齐的时间/显存开销与精度收益、对齐关键场景识别', 'bullet'))
    story.append(B('泛化分析：规律是否跨室内/室外场景和不同算法迁移？记录局限性与适用范围', 'bullet'))

    # ── 工作步骤 ──────────────────────────────────────────────────────────────
    story.append(B('四、工作步骤', 'h1'))

    steps = [
        ('1. 文献调研',
         '调研大规模点云分割方法；学习实验设计（DoE）方法论与实验设计原则'),
        ('2. 渐进式开发',
         '第一阶段：文献调研与基线分析\n'
         '第二至三阶段：DoE 执行与规律推导\n'
         '第四阶段：实现\n'
         '第五至八阶段：验证与分析'),
        ('3. 实验',
         '跨数据集和算法的系统性 DoE 实验；在保留场景上验证模型；性能对比研究'),
        ('4. 文档撰写',
         '推导模型/规律的技术文档；实验结果与统计分析；录制演示视频'),
    ]
    for title, desc in steps:
        row_data = [[B(title, 'label'), B(desc.replace('\n','<br/>'), 'body')]]
        t = Table(row_data, colWidths=['30%', '70%'])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), LIGHT_BLU),
            ('BACKGROUND', (1,0), (1,0), colors.white),
            ('BOX',        (0,0), (-1,-1), 0.5, GRAY_BD),
            ('GRID',       (0,0), (-1,-1), 0.3, GRAY_BD),
            ('VALIGN',     (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(SP(0.08))

    # ── 预期成果 ──────────────────────────────────────────────────────────────
    story.append(B('五、预期成果', 'h1'))

    outcomes = [
        ('自适应增强策略',
         '一种基于场景特征和硬件约束，自动选择大规模点云分割处理参数的有原则方法'),
        ('DoE 推导规律',
         '经实验验证的公式或规则，描述参数–性能定量关系'),
        ('主流架构集成',
         '与基于点和基于体素的两类架构兼容的实现'),
        ('基准测试结果',
         '在大规模数据集（S3DIS、ArCH、DALES、KITTI-360）上的评估，'
         '验证策略有效性和可泛化性'),
    ]

    out_data = [['序号', '成果名称', '描述']] + [
        [str(i+1), B(n, 'label'), B(d, 'body')]
        for i, (n, d) in enumerate(outcomes)
    ]
    ot = Table(out_data, colWidths=['8%', '28%', '64%'])
    ot.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), TU_BLUE),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,-1), F),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('LEADING',       (0,0), (-1,-1), 14),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [LIGHT_BLU, colors.white]),
        ('BOX',           (0,0), (-1,-1), 0.5, GRAY_BD),
        ('GRID',          (0,0), (-1,-1), 0.3, GRAY_BD),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('ALIGN',         (0,0), (0,-1), 'CENTER'),
    ]))
    story.append(ot)
    story.append(SP(0.3))

    # ── 组织说明 ──────────────────────────────────────────────────────────────
    story.append(B('六、组织说明', 'h1'))
    story.append(B(
        '本研究致力于为大规模点云开发资源高效的语义分割方法，推动感知算法在受限硬件上的实际部署。'
        '文献调研、方法设计和实验研究的成果将以清晰的形式（表格、图表）呈现，并从科学角度进行讨论。'
        '研究成果将在最终测量工程研讨会上公开展示。', 'body'))
    story.append(SP(0.1))
    story.append(B('研究内容方面的联系人为 MDT 专业的 Fan Qinyuan 先生。', 'body'))
    story.append(SP(0.5))

    # ── 签名 ──────────────────────────────────────────────────────────────────
    story.append(HR())
    story.append(B('此致', 'sign'))
    story.append(SP(0.8))
    story.append(B('Prof. Dr.-Ing. Clemens Gühmann', 'sign'))
    story.append(SP(0.3))

    # footer
    story.append(SP(0.5))
    story.append(HR())
    story.append(B('柏林工业大学 | 电子测量与诊断技术专业 | www.mdt.tu-berlin.de', 'footer'))
    story.append(B('原文件：Aufgabenstellung_Luo.pdf（2025年12月15日）| 翻译版本', 'footer'))

    doc.build(story)
    print(f'PDF 已生成：{out}')

if __name__ == '__main__':
    build()
