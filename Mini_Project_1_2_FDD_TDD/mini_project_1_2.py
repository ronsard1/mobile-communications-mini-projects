"""Mini Project 1.2 - FDD vs TDD utilization under traffic asymmetry."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)
import numpy as np
import matplotlib.pyplot as plt

# ---------- Fixed parameters (Step 1) ----------
TOTAL_CAP = 100.0          # normalized total capacity (e.g. Mbps), same for both schemes
FDD_CAP_DIR = TOTAL_CAP / 2  # FDD: fixed, equal capacity per direction
SLOTS = 20                 # slots per TDD frame
OFFERED = TOTAL_CAP        # offered load = 100% of total capacity (saturated network)


def demand(dl_share, offered=OFFERED):
    return offered * dl_share, offered * (1 - dl_share)


# ---------- FDD model (Step 2) ----------
def fdd(dl_share, offered=OFFERED):
    dl_d, ul_d = demand(dl_share, offered)
    dl = min(dl_d, FDD_CAP_DIR)      # spare capacity in the other direction is wasted
    ul = min(ul_d, FDD_CAP_DIR)
    return dl, ul, (dl + ul) / TOTAL_CAP


# ---------- TDD model (Step 3) ----------
def tdd(dl_share, guard_slots=1, offered=OFFERED):
    """Pick the DL/UL slot split (from usable slots) that maximizes served traffic."""
    dl_d, ul_d = demand(dl_share, offered)
    usable = SLOTS - guard_slots
    best = None
    for n_dl in range(1, usable):                # keep at least 1 slot each way
        n_ul = usable - n_dl
        dl = min(dl_d, TOTAL_CAP * n_dl / SLOTS)
        ul = min(ul_d, TOTAL_CAP * n_ul / SLOTS)
        if best is None or dl + ul > best[0] + 1e-9:
            best = (dl + ul, dl, ul, n_dl, n_ul)
    total, dl, ul, n_dl, n_ul = best
    return dl, ul, total / TOTAL_CAP, n_dl, n_ul


# ---------- Required scenarios (Step 4) ----------
SCENARIOS = [(50, 50), (70, 30), (90, 10)]
GUARDS = [1, 2, 4]   # guard slots per 20 -> 5%, 10%, 20% overhead

print(f"{'DL:UL':<7}{'Scheme':<14}{'DL thr':>8}{'UL thr':>8}{'Util %':>8}{'Slots DL/UL/G':>16}")
print("-" * 61)
for dl_pct, ul_pct in SCENARIOS:
    p = dl_pct / 100
    dl, ul, u = fdd(p)
    print(f"{dl_pct}:{ul_pct:<4}{'FDD':<14}{dl:8.1f}{ul:8.1f}{u * 100:8.1f}{'-':>16}")
    for g in GUARDS:
        dl, ul, u, n_dl, n_ul = tdd(p, g)
        print(f"{'':<7}{f'TDD (g={g}/20)':<14}{dl:8.1f}{ul:8.1f}{u * 100:8.1f}"
              f"{f'{n_dl}/{n_ul}/{g}':>16}")
    print()

# ---------- Crossover analysis (Steps 5-6) ----------
sweep = np.arange(50, 99.5, 1) / 100
fdd_u = np.array([fdd(p)[2] for p in sweep]) * 100
tdd_u = {g: np.array([tdd(p, g)[2] for p in sweep]) * 100 for g in GUARDS}

print("Crossover (first DL share where TDD utilization exceeds FDD):")
for g in GUARDS:
    idx = np.where(tdd_u[g] > fdd_u + 1e-9)[0]
    if idx.size:
        print(f"  guard {g}/20 ({g / SLOTS * 100:.0f}% overhead): "
              f"TDD wins from ~{sweep[idx[0]] * 100:.0f}:{100 - sweep[idx[0]] * 100:.0f} DL:UL")
    else:
        print(f"  guard {g}/20: TDD never wins in the sweep")

# ---------- Charts ----------
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# (a) grouped bars for required scenarios
ax = axes[0]
labels = [f"{d}:{u}" for d, u in SCENARIOS]
x = np.arange(len(SCENARIOS))
w = 0.2
bars = [("FDD", [fdd(d / 100)[2] * 100 for d, _ in SCENARIOS])]
for g in GUARDS:
    bars.append((f"TDD g={g}/20", [tdd(d / 100, g)[2] * 100 for d, _ in SCENARIOS]))
for i, (name, vals) in enumerate(bars):
    ax.bar(x + (i - 1.5) * w, vals, w, label=name)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlabel("Traffic demand (DL:UL)")
ax.set_ylabel("Utilization (%)")
ax.set_title("Utilization by scenario")
ax.set_ylim(0, 110)
ax.legend()
ax.grid(axis="y", alpha=0.3)

# (b) full asymmetry sweep
ax = axes[1]
ax.plot(sweep * 100, fdd_u, "k-", lw=2, label="FDD")
for g in GUARDS:
    ax.plot(sweep * 100, tdd_u[g], label=f"TDD g={g}/20 ({g / SLOTS * 100:.0f}% guard)")
ax.set_xlabel("Downlink share of demand (%)")
ax.set_ylabel("Utilization (%)")
ax.set_title("Utilization vs traffic asymmetry")
ax.grid(alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fdd_tdd_comparison.png"), dpi=200)

# ---------- Optional Step 7: multi-frame slot allocation view ----------
frame_dl_share = [0.5, 0.5, 0.7, 0.7, 0.9, 0.9]   # demand shifts frame by frame
fig2, ax2 = plt.subplots(figsize=(11, 3.5))
for f_idx, p in enumerate(frame_dl_share):
    _, _, _, n_dl, n_ul = tdd(p, guard_slots=1)
    pattern = ["DL"] * n_dl + ["UL"] * n_ul + ["G"]
    for s, kind in enumerate(pattern):
        color = {"DL": "tab:blue", "UL": "tab:orange", "G": "lightgray"}[kind]
        ax2.barh(0, 1, left=f_idx * SLOTS + s, color=color, edgecolor="white")
    ax2.axvline(f_idx * SLOTS, color="k", lw=0.8)
ax2.barh(1, len(frame_dl_share) * SLOTS, color="tab:blue", alpha=0.5)
ax2.barh(2, len(frame_dl_share) * SLOTS, color="tab:orange", alpha=0.5)
ax2.set_yticks([0, 1, 2])
ax2.set_yticklabels(["TDD (one channel)", "FDD downlink", "FDD uplink"])
ax2.set_xlabel("Slot index (blue=DL, orange=UL, gray=guard)")
ax2.set_title("TDD re-slotting per frame vs FDD's fixed parallel channels")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "tdd_frames_timeline.png"), dpi=200)
# ---------- Guard-overhead study ----------
gs = np.arange(0, 9)
cross, u5050, u9010 = [], [], []
for g in gs:
    tu = np.array([tdd(p, g)[2] for p in sweep]) * 100
    idx = np.where(tu > fdd_u + 1e-9)[0]
    cross.append(sweep[idx[0]] * 100 if idx.size else np.nan)
    u5050.append(tdd(0.5, g)[2] * 100)
    u9010.append(tdd(0.9, g)[2] * 100)
gpct = gs / SLOTS * 100
figg, axg = plt.subplots(1, 2, figsize=(12, 4.6))
axg[0].plot(gpct, cross, "o-")
axg[0].set_xlabel("Guard overhead (% of frame)")
axg[0].set_ylabel("DL share where TDD first beats FDD (%)")
axg[0].set_title("Crossover point vs guard overhead")
axg[0].grid(alpha=0.3)
axg[1].plot(gpct, u5050, "o-", label="TDD at 50:50")
axg[1].plot(gpct, u9010, "s-", label="TDD at 90:10")
axg[1].axhline(fdd(0.5)[2] * 100, ls="--", color="tab:blue", alpha=0.6, label="FDD at 50:50")
axg[1].axhline(fdd(0.9)[2] * 100, ls="--", color="tab:orange", alpha=0.6, label="FDD at 90:10")
axg[1].set_xlabel("Guard overhead (% of frame)")
axg[1].set_ylabel("Utilization (%)")
axg[1].set_title("Utilization vs guard overhead")
axg[1].grid(alpha=0.3)
axg[1].legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "guard_overhead.png"), dpi=200)
plt.show()
