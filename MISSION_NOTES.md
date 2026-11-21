# Mission 1 — Meet the Data and Set the Bar

## 1. Initial prediction

**My estimated mean-baseline MAE: 45 days.**

Reasoning: Different doorbells have different battery conditions and usage patterns. Predicting one constant average for every doorbell would likely produce considerable errors.

*Note: This estimate was recorded retrospectively, after measuring the actual MAE.*

## 2. Actual results

| Model | Validation MAE |
|---|---:|
| Mean baseline | 55.14 days |
| Linear regression | 23.61 days |
| Neural network (32, 32) | 12.86 days |

Difference between my estimate and actual mean-baseline MAE: 10.14 days.

## 3. Data cleaning

- Original rows: 2,000
- Invalid battery readings removed: 12
- Invalid temperature readings removed: 4
- Total removed: 16
- Remaining rows: 1,984
- Wi-Fi RSSI zero readings: retained for further investigation.

## 4. GitHub

- Branch: mission-1
- Latest commit: 63c6b74
- Model files and plots committed and pushed.

## Mission 2: Final Model Selection

Selected architecture: 5 → 16 → 16 → 1

Parameters: 385
Training MAE: 4.30 days
Validation MAE: 4.98 days

Expected MAE on 400 unseen readings: approximately 5 days.

This is an estimate based on validation performance, not a
measured result on the company's hidden dataset.

Reason for selection:
The 16,16 architecture offers a good balance between accuracy
and model size. It uses 385 parameters compared with 4,609
parameters in the 64,64 architecture, while achieving a
validation MAE of only 0.46 days higher.