# S3DIS Area_5 基线结果

**数据集**: S3DIS · 测试集 Area_5 · 500 epoch · 默认参数

## 汇总

| 模型 | mIoU (%) | mAcc (%) | allAcc (%) | 训练 Best mIoU (%) |
|------|----------|----------|------------|--------------------|
| SpUNet (500ep) | 64.87 | 71.29 | 89.05 | 62.75 |
| PTv3   (500ep) | 67.01 | 73.28 | 90.10 | 65.44 |

## 各类别 IoU (%)

| 类别 | SpUNet IoU | SpUNet Acc | PTv3 IoU | PTv3 Acc |
|------|-----------|-----------|---------|----------|
| ceiling | 92.2 | 96.5 | 94.1 | 96.6 |
| floor | 97.2 | 99.5 | 98.1 | 99.2 |
| wall | 82.6 | 96.6 | 83.6 | 97.1 |
| beam | 0.0 | 0.0 | 0.0 | 0.0 |
| column | 25.6 | 27.6 | 32.8 | 35.6 |
| window | 58.1 | 60.8 | 57.4 | 59.0 |
| door | 70.9 | 84.7 | 61.1 | 68.2 |
| table | 80.7 | 89.3 | 81.8 | 92.7 |
| chair | 88.1 | 94.5 | 90.5 | 96.6 |
| sofa | 47.1 | 48.8 | 59.2 | 64.2 |
| bookcase | 75.2 | 83.3 | 75.3 | 84.1 |
| board | 68.2 | 76.9 | 75.8 | 86.7 |
| clutter | 57.5 | 68.1 | 61.3 | 72.5 |

## 原始日志

- SpUNet 训练+测评: `/workspace/logs/spunet_baseline.log`
- PTv3   训练:       `/workspace/logs/ptv3_baseline.log`
- PTv3   测评:       `/workspace/logs/ptv3_baseline_test.log`
- SpUNet checkpoint: `/workspace/Pointcept/exp/baseline_spunet/model/model_best.pth`
- PTv3   checkpoint: `/workspace/Pointcept/exp/baseline_ptv3/model/model_best.pth`
