import matplotlib.pyplot as plt

architectures = [
    "4", "8", "16", "32", "64",
    "4,4", "8,8", "16,16", "32,32", "64,64"
]

params = [29, 57, 113, 225, 449, 49, 129, 385, 1281, 4609]

val_mae = [
    14.99, 16.16, 9.70, 11.13, 16.16,
    7.80, 5.85, 4.98, 5.09, 4.52
]

plt.figure(figsize=(10, 6))
plt.scatter(params, val_mae)

for i, name in enumerate(architectures):
    plt.annotate(name, (params[i], val_mae[i]))

plt.xlabel("Number of parameters")
plt.ylabel("Validation MAE (days)")
plt.title("Architecture Comparison")
plt.xscale("log")
plt.grid(True)
plt.savefig("mission2_results/architecture_comparison.png")
plt.show()
