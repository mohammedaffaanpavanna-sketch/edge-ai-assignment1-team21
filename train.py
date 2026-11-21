"""
train.py -- STARTER. Clean the data, fit baselines, train the network, save it for the server.

    python train.py --team 7 --hidden 32,32
Writes model/model.pt and model/config.json, which app/main.py loads.

Look for TODO. The training loop is given; the decisions are yours.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import torch

from app.model import FEATURES, BatteryNet

ap = argparse.ArgumentParser()
ap.add_argument("--team", type=int, required=True)
ap.add_argument("--hidden", default="32,32")
ap.add_argument("--epochs", type=int, default=1500)
a = ap.parse_args()
hidden = tuple(int(h) for h in a.hidden.split(","))

df = pd.read_csv(f"data/team_{a.team:02d}_train.csv")
# Mission 1: identify and remove impossible sensor readings
bad_battery = df["battery_v"] <= 0
bad_temperature = df["temp_c"] == -127

# Combine conditions so each row is counted only once
bad = bad_battery | bad_temperature

print(f"Total rows before cleaning: {len(df)}")
print(f"Invalid battery readings: {bad_battery.sum()}")
print(f"Invalid temperature readings: {bad_temperature.sum()}")
print(f"Total glitch rows removed: {bad.sum()}")

df = df[~bad].copy()
print(f"Rows remaining after cleaning: {len(df)}")

rng = np.random.default_rng(0)
idx = rng.permutation(len(df)); n_val = len(df) // 5
val, tr = df.iloc[idx[:n_val]], df.iloc[idx[n_val:]]
X, y = tr[FEATURES].to_numpy(np.float32), tr.days_left.to_numpy(np.float32)
Xv, yv = val[FEATURES].to_numpy(np.float32), val.days_left.to_numpy(np.float32)
# Mission 2: calculate normalization statistics using training data only
mu = X.mean(axis=0)
sd = X.std(axis=0)

# Avoid division by zero if any feature has zero standard deviation
sd[sd == 0] = 1.0
mae = lambda p, t: float(np.mean(np.abs(p - t)))
print(f"baseline (predict the mean): {mae(np.full_like(yv, y.mean()), yv):.2f} days")
# Mission 1: linear regression baseline using least squares
X_train_lr = np.column_stack([X, np.ones(len(X))])
X_val_lr = np.column_stack([Xv, np.ones(len(Xv))])

weights, residuals, rank, singular_values = np.linalg.lstsq(
    X_train_lr, y, rcond=None
)

linear_predictions = X_val_lr @ weights
linear_mae = mae(linear_predictions, yv)

print(f"baseline (linear regression): {linear_mae:.2f} days")
# Mission 1: identify the largest linear regression errors
absolute_errors = np.abs(linear_predictions - yv)

largest_error_indices = np.argsort(absolute_errors)[-10:][::-1]

print("\nTop 10 largest linear regression errors:")
for i in largest_error_indices:
    print(
        f"Actual: {yv[i]:.2f}, "
        f"Predicted: {linear_predictions[i]:.2f}, "
        f"Error: {absolute_errors[i]:.2f} days"
    )
# Mission 1: plot predicted vs actual values
import matplotlib.pyplot as plt

plt.figure(figsize=(7, 5))
plt.scatter(yv, linear_predictions, alpha=0.6)

# Ideal prediction line
plt.plot(
    [yv.min(), yv.max()],
    [yv.min(), yv.max()],
    "r--"
)

plt.xlabel("Actual days left")
plt.ylabel("Predicted days left")
plt.title("Linear Regression: Predicted vs Actual")
plt.savefig("linear_regression_plot.png")
plt.show()
torch.manual_seed(0)
net = BatteryNet(hidden)
opt = torch.optim.Adam(net.parameters(), lr=3e-3)
Xt, yt = torch.tensor((X - mu) / sd), torch.tensor(y)
Xvt = torch.tensor((Xv - mu) / sd)
for ep in range(a.epochs):
    perm = torch.randperm(len(Xt))
    for i in range(0, len(Xt), 128):
        b = perm[i:i + 128]
        loss = torch.nn.functional.mse_loss(net(Xt[b]), yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
    if ep % 300 == 0 or ep == a.epochs - 1:
        with torch.no_grad():
            print(f"  epoch {ep:4d}  val MAE {mae(net(Xvt).numpy(), yv):.2f} days")
with torch.no_grad():
    train_mae = mae(net(Xt).numpy(), y)
    val_mae = mae(net(Xvt).numpy(), yv)

print(f"Training MAE:   {train_mae:.2f} days")
print(f"Validation MAE: {val_mae:.2f} days")

os.makedirs("model", exist_ok=True)
torch.save(net.state_dict(), "model/model.pt")
json.dump(dict(team=a.team, hidden=list(hidden), mu=mu.tolist(), sd=sd.tolist(),
               features=FEATURES, val_mae=round(val_mae, 2)), open("model/config.json", "w"), indent=2)
print("saved model/model.pt and model/config.json")
