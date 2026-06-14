"""
Generate Day 1 experiment guide PDF in Chinese.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('CJK', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'))
pdfmetrics.registerFont(TTFont('CJKb', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'))

MARGIN = 2.0 * cm
NAVY   = colors.HexColor('#1a3a5c')
GREEN  = colors.HexColor('#1e7a48')
RED    = colors.HexColor('#c0392b')
ORANGE = colors.HexColor('#d35400')
LGRAY  = colors.HexColor('#f5f5f5')
LGREEN = colors.HexColor('#eaf7ee')
LBLUE  = colors.HexColor('#eaf0fb')
LYELL  = colors.HexColor('#fffbe6')
WHITE  = colors.white

# ── Styles ───────────────────────────────────────────────────────────────────
def S(name, **kw):
    defaults = dict(fontName='CJK', leading=17, wordWrap='CJK', spaceAfter=3)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

STYLES = {
    'title':   S('title',  fontName='CJKb', fontSize=17, leading=24, alignment=1,
                 textColor=NAVY, spaceAfter=4),
    'meta':    S('meta',   fontSize=9, alignment=1, textColor=colors.HexColor('#666'),
                 spaceAfter=12),
    'phase':   S('phase',  fontName='CJKb', fontSize=12, leading=20, textColor=WHITE,
                 backColor=NAVY, borderPad=5, spaceAfter=5, spaceBefore=12,
                 leftIndent=-0.1*cm, rightIndent=-0.1*cm),
    'step':    S('step',   fontName='CJKb', fontSize=10.5, leading=17, textColor=NAVY,
                 spaceAfter=3, spaceBefore=8),
    'body':    S('body',   fontSize=9.5, leading=16, spaceAfter=3),
    'bullet':  S('bullet', fontSize=9.5, leading=16, leftIndent=14, spaceAfter=2),
    'sub':     S('sub',    fontSize=9,   leading=15, leftIndent=26, spaceAfter=2,
                 textColor=colors.HexColor('#444')),
    'code':    S('code',   fontName='Courier', fontSize=8.5, leading=13,
                 backColor=colors.HexColor('#1e1e1e'), textColor=colors.HexColor('#d4d4d4'),
                 borderPad=7, leftIndent=0, spaceAfter=5, spaceBefore=2),
    'warn':    S('warn',   fontSize=9, leading=15, textColor=colors.HexColor('#7d4e00'),
                 backColor=LYELL, borderColor=colors.HexColor('#f0c040'),
                 borderWidth=0.8, borderPad=5, leftIndent=6, spaceAfter=6),
    'tip':     S('tip',    fontSize=9, leading=15, textColor=colors.HexColor('#155724'),
                 backColor=LGREEN, borderColor=colors.HexColor('#28a745'),
                 borderWidth=0.8, borderPad=5, leftIndent=6, spaceAfter=6),
    'small':   S('small',  fontSize=8.5, leading=13, textColor=colors.HexColor('#888'),
                 spaceAfter=2),
}

def ph(text):  return Paragraph(f'  {text}', STYLES['phase'])
def st(n, t):  return Paragraph(f'Step {n}　{t}', STYLES['step'])
def p(text):   return Paragraph(text, STYLES['body'])
def b(text):   return Paragraph(f'▸  {text}', STYLES['bullet'])
def sub(text): return Paragraph(f'　　·  {text}', STYLES['sub'])
def cmd(text): return Paragraph(text.replace('\n', '<br/>').replace(' ', '&nbsp;'), STYLES['code'])
def warn(t):   return Paragraph(f'⚠  {t}', STYLES['warn'])
def tip(t):    return Paragraph(f'✓  {t}', STYLES['tip'])
def sp(h=5):   return Spacer(1, h)
def hr(c=colors.HexColor('#cccccc')):
    return HRFlowable(width='100%', thickness=0.5, color=c, spaceAfter=3)

# ── Time badge table ──────────────────────────────────────────────────────────
def time_badge(label, est):
    t = Table([[label, est]], colWidths=[10*cm, 5.4*cm])
    t.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,-1), 'CJKb'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (0,0),   NAVY),
        ('BACKGROUND', (1,0), (1,0),   ORANGE),
        ('TEXTCOLOR',  (0,0), (-1,-1), WHITE),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROUNDEDCORNERS', [4]),
    ]))
    return t

# ── Checklist table ───────────────────────────────────────────────────────────
def checklist(rows):
    data = [['', '检查项', '预期结果']] + [['☐', r[0], r[1]] for r in rows]
    cw = [0.6*cm, 8.5*cm, 6.3*cm]
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,0),  'CJKb'),
        ('FONTNAME',   (0,1), (-1,-1), 'CJK'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,0),  GREEN),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGREEN, WHITE]),
        ('ALIGN',      (0,0), (0,-1),  'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#bbbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (1,0), (1,-1), 6),
    ]))
    return t

# ── Result record table ───────────────────────────────────────────────────────
def result_table():
    data = [
        ['模型', 'mIoU (%)', 'Peak VRAM (GB)', '训练时长', '备注'],
        ['SpUNet\n(500 epoch)', '', '', '', '默认参数基线'],
        ['PTv3\n(500 epoch)', '', '', '', '默认参数基线'],
    ]
    cw = [2.8*cm, 2.5*cm, 3.2*cm, 2.5*cm, 4.4*cm]
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,0),  'CJKb'),
        ('FONTNAME',   (0,1), (-1,-1), 'CJK'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0),  RED),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#fff0ee'), WHITE]),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#ddbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

# ── Overview table ────────────────────────────────────────────────────────────
def overview_table():
    data = [
        ['阶段', '任务', '预计时间', '是否阻塞后续'],
        ['阶段一', '安装缺失依赖（mmengine / SharedArray / flash-attn / Pointcept）', '20 分钟', '是'],
        ['阶段二', '从 HuggingFace 下载 S3DIS 预处理数据（2 GB）并解压', '30 分钟', '是'],
        ['阶段三', '先做 Smoke Test（2 epoch），再后台跑 SpUNet + PTv3 基线（500 epoch）', '5–8 小时\n（GPU 跑，可离开）', '否'],
        ['阶段四', '训练结束后提取 mIoU / VRAM 数据，填写基线结果表', '15 分钟', '—'],
    ]
    cw = [1.8*cm, 7.5*cm, 3.0*cm, 3.1*cm]
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,0),  'CJKb'),
        ('FONTNAME',   (0,1), (-1,-1), 'CJK'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0),  NAVY),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LBLUE, WHITE]),
        ('ALIGN',      (0,0), (0,-1),  'CENTER'),
        ('ALIGN',      (2,0), (3,-1),  'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#aabbcc')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (1,0), (1,-1), 6),
    ]))
    return t

# ── FAQ table ─────────────────────────────────────────────────────────────────
def faq_table():
    data = [
        ['错误信息', '原因', '解决方法'],
        ['ModuleNotFoundError: pointcept',
         'Pointcept 未安装到 conda 环境',
         'pip install -e /workspace/Pointcept'],
        ['CUDA out of memory',
         'batch_size 过大',
         '加 --options batch_size=4'],
        ['ImportError: flash_attn',
         'flash-attn 未安装完成',
         'PTv3 config 中设 enable_flash=False'],
        ['FileNotFoundError: data/s3dis',
         '软链接未建立',
         'ln -s /workspace/data/s3dis\n   /workspace/Pointcept/data/s3dis'],
        ['TypeError in collate_fn',
         'SharedArray 版本不兼容',
         'pip install SharedArray==3.2.1'],
        ['huggingface_hub 下载卡住',
         '网络超时',
         '加 HF_ENDPOINT=https://hf-mirror.com\n环境变量重试'],
    ]
    cw = [4.0*cm, 4.0*cm, 7.4*cm]
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,0),  'CJKb'),
        ('FONTNAME',   (0,1), (-1,-1), 'CJK'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,0),  RED),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#fff5f5'), WHITE]),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#ddbbbb')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t


# ═══════════════════════════════════════════════════════════════════════════════
def build():
    out = '/workspace/Day1_实验指南.pdf'
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # ── 封面区域 ──────────────────────────────────────────────────────────────
    story += [
        sp(8),
        Paragraph('第一天实验指南', STYLES['title']),
        Paragraph('大规模点云语义分割 · 基线环境搭建与首次训练', STYLES['meta']),
        Paragraph('TU Berlin · MDT · Yucan Luo · 2026-06-09', STYLES['meta']),
        hr(NAVY), sp(4),
    ]

    # ── 总览 ──────────────────────────────────────────────────────────────────
    story += [
        p('<b>今日目标：</b>完成环境依赖安装、S3DIS 数据下载，并跑通 SpUNet 和 PTv3 两个基线模型，'
          '获取默认参数下的 mIoU 与显存数据，作为后续 DoE 实验的参考基准。'),
        sp(6),
        overview_table(),
        sp(10),
    ]

    # ══════════════════════════════════════════════════════════════════════════
    # 阶段一
    # ══════════════════════════════════════════════════════════════════════════
    story += [
        KeepTogether([
            ph('阶段一　补装缺失的 4 个包'),
            time_badge('预计时间：15–25 分钟', '⚡ 只需装一次，永久保留'),
            sp(6),
            p('conda env <b>thesis</b> 位于 <b>/workspace/miniconda3/envs/thesis/</b>，'
              '存放在持久化网络盘上，<b>换 pod 后完全保留</b>，不需要重装。'
              'PyTorch、spconv、open3d 等大包都已就位，今天只需补装以下 4 个：'),
            sp(4),
        ])
    ]

    # 缺包说明小表
    missing_data = [
        ['包名', '用途', '是否影响 SpUNet', '是否影响 PTv3'],
        ['mmengine',    'Pointcept 读取 .py 配置文件', '✗ 必须', '✗ 必须'],
        ['SharedArray', '共享内存加速数据加载',         '✗ 必须', '✗ 必须'],
        ['pointcept',   'Pointcept 本体（pip install -e）', '✗ 必须', '✗ 必须'],
        ['flash_attn',  'PTv3 高效注意力算子',           '○ 不需要', '✗ 必须'],
    ]
    mt = Table(missing_data, colWidths=[3.0*cm, 5.5*cm, 2.8*cm, 2.8*cm], repeatRows=1)
    mt.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,0),  'CJKb'),
        ('FONTNAME',   (0,1), (-1,-1), 'CJK'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,0),  ORANGE),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LYELL, WHITE]),
        ('ALIGN',      (2,0), (3,-1),  'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (1,-1), 5),
    ]))
    story += [missing_data and mt, sp(8)]

    story += [
        st('1.1', '激活环境'),
        cmd('conda activate thesis\ncd /workspace/Pointcept'),
        sp(2),
        st('1.2', '安装 mmengine 和 SharedArray（1 分钟）'),
        cmd('pip install mmengine SharedArray'),
        tip('mmengine 是 Pointcept 读取 .py 配置文件的核心依赖，缺少它训练脚本会立即崩溃。'),
        sp(2),
        st('1.3', '以开发模式安装 Pointcept（1 分钟）'),
        cmd('pip install -e /workspace/Pointcept'),
        p('开发模式（-e）意味着直接引用 /workspace/Pointcept 的源码，'
          '以后修改代码不需要重新安装。'),
        sp(2),
        st('1.4', '后台安装 flash-attn（PTv3 需要，编译约 15 分钟）'),
        cmd('mkdir -p /workspace/logs\n'
            'pip install flash-attn --no-build-isolation \\\n'
            '    > /workspace/logs/flash_attn_install.log 2>&1 &\n'
            'echo "flash-attn 安装中，PID=$!"\n'
            'echo "可用 tail -f /workspace/logs/flash_attn_install.log 查看进度"'),
        warn('flash-attn 在后台编译，不要等它。先继续做阶段二（下载数据）。'
             'SpUNet 不需要 flash-attn，今天先跑 SpUNet，等它装完再跑 PTv3。'),
        sp(2),
        st('1.5', '验证前三个包已安装'),
        cmd('python -c "import pointcept;  print(\'pointcept  OK\')"\n'
            'python -c "import mmengine;   print(\'mmengine   OK\')"\n'
            'python -c "import SharedArray; print(\'SharedArray OK\')"'),
        tip('三行都输出 OK 才继续。flash-attn 后台装，暂时不用验证。'),
        sp(8),
    ]

    # ══════════════════════════════════════════════════════════════════════════
    # 阶段二
    # ══════════════════════════════════════════════════════════════════════════
    story += [
        KeepTogether([
            ph('阶段二　下载并准备 S3DIS 数据集'),
            time_badge('预计时间：30 分钟（含下载）', '📦 2 GB 数据'),
            sp(6),
            p('Pointcept 官方在 HuggingFace 提供了预处理好的 S3DIS 压缩包（2 GB），'
              '无需填写 Google 申请表，可直接下载。数据格式已符合 Pointcept 要求，'
              '解压后只需建立软链接即可使用。'),
            sp(6),
        ])
    ]

    story += [
        st('2.1', '下载预处理数据'),
        cmd('python -c "\nfrom huggingface_hub import hf_hub_download\npath = hf_hub_download(\n'
            '    repo_id=\'Pointcept/s3dis-compressed\',\n'
            '    filename=\'s3dis.tar.gz\',\n'
            '    repo_type=\'dataset\',\n'
            '    local_dir=\'/workspace/data\'\n'
            ')\nprint(\'Downloaded:\', path)\n"'),
        warn('如果下载很慢或超时，在命令前加：\n'
             'export HF_ENDPOINT=https://hf-mirror.com\n'
             '（使用国内镜像站）'),
        sp(2),
        st('2.2', '解压数据'),
        cmd('mkdir -p /workspace/data\n'
            'cd /workspace/data\n'
            'tar -xzf s3dis.tar.gz\n'
            'echo "解压完成，目录内容："\n'
            'ls s3dis/'),
        p('解压后应看到 <b>Area_1 到 Area_6</b> 六个文件夹，每个 Area 下是各个房间子目录。'),
        sp(2),
        st('2.3', '建立软链接（让 Pointcept 找到数据）'),
        cmd('mkdir -p /workspace/Pointcept/data\n'
            'ln -s /workspace/data/s3dis /workspace/Pointcept/data/s3dis\n'
            'ls /workspace/Pointcept/data/s3dis/ | head -6  # 验证'),
        sp(2),
        st('2.4', '验证数据格式'),
        cmd('python -c "\nimport numpy as np, os\n'
            'room = \'/workspace/data/s3dis/Area_1/conferenceRoom_1\'\n'
            'for f in os.listdir(room):\n'
            '    d = np.load(os.path.join(room, f))\n'
            '    print(f\'{f}: shape={d.shape}, dtype={d.dtype}\')\n"'),
        tip('应看到 coord.npy（坐标）、color.npy（颜色）、segment.npy（标签）三个文件，'
            'coord 的 shape 类似 (N, 3)。'),
        sp(8),
    ]

    # ══════════════════════════════════════════════════════════════════════════
    # 阶段三
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story += [
        KeepTogether([
            ph('阶段三　运行基线训练'),
            time_badge('预计时间：5–8 小时（GPU 自动运行）', '🖥  挂后台即可'),
            sp(6),
            p('训练分两步：先用 <b>Smoke Test</b>（仅跑 2 个 epoch）验证整条流水线正常，'
              '再后台运行完整 500 epoch 的基线。SpUNet 和 PTv3 不能同时训练（共用一块 GPU），'
              '先跑 SpUNet，完成后再起 PTv3。'),
            sp(6),
        ])
    ]

    story += [
        st('3.1', 'Smoke Test：验证流水线（~5 分钟）'),
        p('修改 epoch=2，batch_size=4，快速确认数据读取、模型前向、损失计算都没有问题：'),
        cmd('cd /workspace/Pointcept\n\n'
            'python tools/train.py \\\n'
            '    --config-file configs/s3dis/semseg-spunet-v1m1-0-base.py \\\n'
            '    --num-gpus 1 \\\n'
            '    --options save_path=exp/smoke_test \\\n'
            '              epoch=2 \\\n'
            '              batch_size=4'),
        p('正常输出示例（看到 Loss 下降即成功）：'),
        cmd('[Epoch 1/2]  Loss: 2.45  LR: 0.0512\n'
            '[Epoch 2/2]  Loss: 2.18  LR: 0.0498\n'
            'Eval mIoU: 0.042'),
        warn('如果 Smoke Test 报错，不要继续跑后续步骤，先排查原因。'
             '常见错误见文末"常见问题"表格。'),
        sp(4),

        st('3.2', 'SpUNet 完整基线（500 epoch，后台运行）'),
        p('Smoke Test 通过后，挂后台跑完整训练：'),
        cmd('nohup python tools/train.py \\\n'
            '    --config-file configs/s3dis/semseg-spunet-v1m1-0-base.py \\\n'
            '    --num-gpus 1 \\\n'
            '    --options save_path=exp/baseline_spunet \\\n'
            '              epoch=500 \\\n'
            '              batch_size=12 \\\n'
            '    > /workspace/logs/spunet_baseline.log 2>&1 &\n\n'
            'echo "SpUNet PID=$!"\n'
            'echo "实时查看日志：tail -f /workspace/logs/spunet_baseline.log"'),
        tip('nohup 确保关闭终端后训练继续。PID 记下来，用 kill <PID> 可随时停止。'),
        sp(4),

        st('3.3', '确认 flash-attn 安装完成'),
        cmd('# 查看安装日志最后几行\ntail -5 /workspace/logs/flash_attn_install.log\n\n'
            '# 验证可以 import\npython -c "import flash_attn; print(\'flash_attn:\', flash_attn.__version__)"'),
        p('如果 flash-attn 安装失败，用以下命令临时禁用（PTv3 会慢一些但仍能运行）：'),
        cmd('sed -i \'s/enable_flash=True/enable_flash=False/\' \\\n'
            '    /workspace/Pointcept/configs/s3dis/semseg-pt-v3m1-0-base.py'),
        sp(4),

        st('3.4', 'PTv3 基线（SpUNet 跑完后再起）'),
        cmd('# 先确认 SpUNet 已完成\njobs   # 没有后台任务说明跑完了\n# 或\ncat /workspace/logs/spunet_baseline.log | grep -i "finish\\|done\\|mIoU" | tail -3\n\n'
            '# 启动 PTv3\nnohup python tools/train.py \\\n'
            '    --config-file configs/s3dis/semseg-pt-v3m1-0-base.py \\\n'
            '    --num-gpus 1 \\\n'
            '    --options save_path=exp/baseline_ptv3 \\\n'
            '              epoch=500 \\\n'
            '              batch_size=6 \\\n'
            '    > /workspace/logs/ptv3_baseline.log 2>&1 &\n\n'
            'echo "PTv3 PID=$!"'),
        warn('PTv3 batch_size 设 6（比 SpUNet 小），因为 PTv3 显存占用更大。'
             '如果仍 OOM，改为 batch_size=4。'),
        sp(4),

        st('3.5', '实时监控训练状态'),
        cmd('# 方法1：实时查看日志\ntail -f /workspace/logs/spunet_baseline.log\n\n'
            '# 方法2：查看 GPU 占用（每2秒刷新）\nwatch -n 2 nvidia-smi\n\n'
            '# 方法3：用 TensorBoard 可视化（新开终端）\ntensorboard --logdir /workspace/Pointcept/exp \\\n'
            '    --host 0.0.0.0 --port 6006'),
        sp(8),
    ]

    # ══════════════════════════════════════════════════════════════════════════
    # 阶段四
    # ══════════════════════════════════════════════════════════════════════════
    story += [
        KeepTogether([
            ph('阶段四　提取结果，填写基线记录'),
            time_badge('预计时间：15 分钟', '📊 完成后填表'),
            sp(6),
        ])
    ]

    story += [
        st('4.1', '从日志中提取 mIoU'),
        cmd('# SpUNet 最终验证 mIoU\ngrep -E "val.*mIoU|mIoU.*val|miou" \\\n'
            '    /workspace/logs/spunet_baseline.log | tail -5\n\n'
            '# PTv3 最终验证 mIoU\ngrep -E "val.*mIoU|mIoU.*val|miou" \\\n'
            '    /workspace/logs/ptv3_baseline.log | tail -5'),
        sp(2),
        st('4.2', '记录 Peak VRAM'),
        cmd('# 在训练快结束时用 nvidia-smi 查看显存占用峰值\nnvidia-smi --query-gpu=memory.used \\\n'
            '    --format=csv,noheader,nounits\n\n'
            '# 或从代码中记录（在 Python 中）\npython -c "\nimport torch\nprint(f\'Peak VRAM: {torch.cuda.max_memory_allocated()/1e9:.2f} GB\')\n"'),
        sp(4),
        st('4.3', '填写基线结果表（下表手动填写）'),
        sp(4),
        result_table(),
        sp(8),

        p('<b>完成今天所有步骤后，你应该拥有：</b>'),
        b('SpUNet 500 epoch 的 checkpoint（保存在 exp/baseline_spunet/）'),
        b('PTv3 500 epoch 的 checkpoint（保存在 exp/baseline_ptv3/）'),
        b('两个模型在 S3DIS Area_5 上的 mIoU 基线数值'),
        b('两个模型的峰值显存占用数据'),
        p('这四项数据是 <b>明天开始 DoE 实验的起点</b>，所有实验结果都会与这里的基线对比。'),
        sp(10),
    ]

    # ══════════════════════════════════════════════════════════════════════════
    # 常见问题
    # ══════════════════════════════════════════════════════════════════════════
    story += [
        ph('常见问题与解决方案'),
        sp(6),
        faq_table(),
        sp(10),
    ]

    # ── 验证清单 ──────────────────────────────────────────────────────────────
    story += [
        ph('今日完成验证清单'),
        sp(6),
        checklist([
            ('conda activate thesis && python -c "import pointcept"', '输出 Pointcept OK'),
            ('ls /workspace/Pointcept/data/s3dis/Area_1/', '看到多个房间目录'),
            ('Smoke Test（epoch=2）无报错完成', '打印 Eval mIoU: xxx'),
            ('SpUNet 500 epoch 训练结束', '日志末尾有 mIoU 数值'),
            ('PTv3 500 epoch 训练结束', '日志末尾有 mIoU 数值'),
            ('基线结果表已填写', 'SpUNet + PTv3 的 mIoU / VRAM'),
        ]),
        sp(10),
        hr(NAVY),
        Paragraph('Day 1 / 14　·　TU Berlin MDT　·　Yucan Luo　·　生成时间：2026-06-09',
                  STYLES['small']),
    ]

    doc.build(story)
    print(f'PDF 已生成：{out}')


if __name__ == '__main__':
    build()
