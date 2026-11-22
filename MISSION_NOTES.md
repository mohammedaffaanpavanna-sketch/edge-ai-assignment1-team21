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


---

# Mission 4: Would it fit inside the doorbell?

## 1. Current Model Memory

The trained model architecture is 5 -> 16 -> 16 -> 1.

Parameters are calculated using:

Parameters = (input features * output features) + output biases

| Layer | Parameters | Float32 bytes | MACs |
|---|---:|---:|---:|
| 5 -> 16 | 96 | 384 | 80 |
| 16 -> 16 | 272 | 1088 | 256 |
| 16 -> 1 | 17 | 68 | 16 |
| Total | 385 | 1540 | 352 |

Float32 weight and bias memory = 1540 bytes.
Int8 weight and bias memory = 385 bytes.

The largest individual hidden activation contains 16 values.
Float32 activation memory = 16 * 4 = 64 bytes.
Int8 activation memory = 16 * 1 = 16 bytes.

These activation figures exclude additional runtime buffers and framework memory.

## 2. Model Width Comparison

For architecture 5 -> w -> w -> 1:

Parameters = w^2 + 8w + 1
Float32 bytes = Parameters * 4
Int8 bytes = Parameters
MACs = w^2 + 6w

| Width | Parameters | Float32 bytes | Int8 bytes | Fits 300 KB SRAM (f32) | Fits 300 KB SRAM (int8) | Fits 8 MB PSRAM (f32/int8) | MACs |
|---:|---:|---:|---:|---|---|---|---:|
| 32 | 1281 | 5124 | 1281 | Yes | Yes | Yes / Yes | 1216 |
| 128 | 17409 | 69636 | 17409 | Yes | Yes | Yes / Yes | 17152 |
| 256 | 67585 | 270340 | 67585 | Yes | Yes | Yes / Yes | 67072 |
| 512 | 266241 | 1064964 | 266241 | No | Yes | Yes / Yes | 265216 |
| 2048 | 4210689 | 16842756 | 4210689 | No | No | No / Yes | 4202496 |

Memory assumptions:
300 KB = 307200 bytes.
8 MB = 8388608 bytes.
The PSRAM comparison considers weights and biases only.

## 3. Exact SRAM Width Limits

For float32, the maximum width that fits within 300 KB is 273.
At width 274, the model exceeds the limit.

For int8, the maximum width that fits within 300 KB is 550.
At width 551, the model exceeds the limit.

These calculations consider weights and biases only, not the complete runtime memory requirement.

## 4. ESP32-S3 Prediction Time Estimate

The ESP32-S3 operates at up to 240 MHz.

Espressif's ESP-NN performance benchmark reports 1543 CPU cycles for an optimized fully connected operation with 271 inputs and 3 outputs, using internal memory.

Our model requires 352 MACs per prediction.

Using the benchmark's approximate rate:

1543 / (271 * 3) = 1.90 cycles per MAC

352 * 1.90 = approximately 669 cycles.

669 / 240000000 = approximately 0.0028 ms.

This is a scaled arithmetic estimate, not a direct measurement of our model. Assuming approximately 10 times this time to account for multiple layer calls and additional runtime overhead gives a rough prediction-time estimate of 0.03 ms.

Source: https://github.com/espressif/esp-nn/blob/master/docs/performance.md

## 5. Server vs Local Inference

Running the model locally on the ESP32-S3 is the preferred approach.

Latency: Local inference avoids the additional network delay involved in sending readings to a remote server.

Privacy: Sensor readings can remain on the device instead of being transmitted over the internet.

Cost: Local inference avoids continuous server hosting and request-processing costs.

Power: Local inference avoids the extra communication energy required for every prediction, although actual power consumption depends on the implementation and Wi-Fi usage.

Wi-Fi failure: Local inference continues working even when the Wi-Fi connection is unavailable. Server-based inference would become unavailable without a connection.

The current model is small enough to fit comfortably within the stated memory budget. However, it would need conversion and testing with an embedded inference framework before deployment on the ESP32-S3.

## 6. Mission 4 Conclusion

The current model contains only 385 parameters and requires 1540 bytes in float32 or 385 bytes in int8 for weights and biases.

Even the width-256 model fits within the 300 KB SRAM weight budget in float32. Larger models may require int8 quantization or external PSRAM.

For the current small model, local inference is preferable because it reduces network dependence, improves privacy and avoids server communication costs.
