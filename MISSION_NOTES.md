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
