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
## Mission 3 – Benchmark Results

### 1. Localhost Benchmark (200 Requests)

First request: 3.3 ms

| Stage | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|
| Round trip | 1.796 | 3.557 | 5.519 |
| Parse | 0.054 | 0.157 | 0.378 |
| Normalise | 0.021 | 0.028 | 0.047 |
| Inference | 0.126 | 0.171 | 0.345 |
| Build | 0.016 | 0.040 | 0.050 |
| Server total | 0.220 | 0.399 | 0.967 |
| Network and framework | 1.566 | 3.002 | 4.005 |

### 2. Localhost Benchmark Without Keep-Alive (200 Requests)

First request: 2.5 ms

| Stage | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|
| Round trip | 2.216 | 3.093 | 3.633 |
| Parse | 0.024 | 0.119 | 0.187 |
| Normalise | 0.020 | 0.028 | 0.047 |
| Inference | 0.119 | 0.184 | 0.230 |
| Build | 0.013 | 0.019 | 0.052 |
| Server total | 0.193 | 0.339 | 0.416 |
| Network and framework | 2.039 | 2.841 | 3.434 |

**Observation:** Disabling keep-alive increased median round-trip time from 1.796 ms to 2.216 ms because establishing new connections adds overhead.

### 3. Individual Requests vs Batch Request

| Method | Time |
|---|---:|
| 400 individual requests | 877.832 ms |
| 1 batch request (400 readings) | 10.899 ms |

Speed improvement: **80.54×**

**Observation:** Batch processing is faster because it reduces repeated HTTP request and connection-handling overhead.

### 4. Laptop-to-Codespace Benchmark

Pending.

### 5. Laptop-to-Codespace Benchmark (200 Requests)

**Keep-alive enabled**

First request: 957.1 ms

| Stage | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|
| Round trip | 126.142 | 386.558 | 1037.048 |
| Parse | 0.049 | 0.073 | 0.081 |
| Normalise | 0.051 | 0.071 | 0.083 |
| Inference | 0.235 | 0.284 | 0.316 |
| Build | 0.019 | 0.027 | 0.049 |
| Server total | 0.376 | 0.434 | 0.479 |
| Network and framework | 125.811 | 386.182 | 1036.677 |

**Keep-alive disabled**

First request: 403.6 ms

| Stage | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|
| Round trip | 412.613 | 882.945 | 1438.510 |
| Parse | 0.043 | 0.073 | 0.078 |
| Normalise | 0.045 | 0.059 | 0.075 |
| Inference | 0.222 | 0.282 | 0.305 |
| Build | 0.018 | 0.025 | 0.041 |
| Server total | 0.361 | 0.433 | 0.484 |
| Network and framework | 412.129 | 882.614 | 1438.179 |

**Observation:** Disabling keep-alive increased median round-trip time from 126.142 ms to 412.613 ms. Server processing remained almost unchanged, showing that connection setup and network overhead contribute significantly to latency.

### 6. Time Breakdown

Laptop-to-Codespace median round trip:

- Parse: 0.049 ms
- Normalise: 0.051 ms
- Inference: 0.235 ms
- Build: 0.019 ms
- Network and framework: 125.811 ms

The largest contributor is network and framework overhead. Model inference takes only a small fraction of the total time.

### 7. Prediction vs Actual

The expected result was that network and framework overhead would be the slowest stage, while model inference would be very fast.

The measured results support this expectation. The median laptop round trip was 126.142 ms, while server processing took only 0.376 ms.

### 8. Final Conclusion

Batch processing was significantly faster than sending individual requests. Processing 400 readings in one batch took 10.899 ms compared with 877.832 ms for 400 individual requests, giving an 80.54× speed improvement.

Keep-alive also reduced network overhead. Overall, the experiments show that communication overhead is much greater than neural network inference time for this application.

