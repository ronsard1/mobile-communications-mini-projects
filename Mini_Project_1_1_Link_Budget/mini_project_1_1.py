"""Mini Project 1.1 - Link budgets and coverage range (free-space model)."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)
import numpy as np
import matplotlib.pyplot as plt


# ---------- Core functions (Steps 2 and 3) ----------
def fspl_db(d_km, f_mhz):
    return 20 * np.log10(d_km) + 20 * np.log10(f_mhz) + 32.44


def link_budget_dbm(p_tx_dbm, g_tx_db, l_path_db, g_rx_db, l_other_db):
    return p_tx_dbm + g_tx_db - l_path_db + g_rx_db - l_other_db


def max_range_km(f_mhz, p_tx, g_tx, g_rx, l_other, sens):
    """Closed-form range: solve P_RX = sensitivity for d."""
    max_path_loss = p_tx + g_tx + g_rx - l_other - sens
    return 10 ** ((max_path_loss - 20 * np.log10(f_mhz) - 32.44) / 20)


def noise_dbm(bw_hz, nf_db=0):
    """Thermal noise floor: -174 dBm/Hz + 10log10(B). -104 dBm for 10 MHz."""
    return -174 + 10 * np.log10(bw_hz) + nf_db


def capacity_bps(prx_dbm, bw_hz):
    snr_lin = 10 ** ((prx_dbm - noise_dbm(bw_hz)) / 10)
    return bw_hz * np.log2(1 + snr_lin)


# ---------- Fixed parameters (Steps 4-8) ----------
P_TX, G_TX, G_RX, L_OTHER = 40, 15, 0, 3      # dBm, dBi, dBi, dB
SENS = -100                                   # dBm
D_REF = 0.5                                   # km reference distance
BANDS = {"700 MHz (low-band)": 700, "28 GHz (mmWave)": 28000}

# Extended to 10,000 km so the 700 MHz range is not clipped by the array edge
distances = np.logspace(-2, 4, 800)


def prx_curve(f_mhz, g_tx=G_TX, l_other=L_OTHER):
    return link_budget_dbm(P_TX, g_tx, fspl_db(distances, f_mhz), G_RX, l_other)


def max_range_from_curve(prx):
    ok = distances[prx > SENS]                # Step 10: boolean indexing
    return ok.max() if ok.size else 0.0


def summarize(label, f_mhz, g_tx=G_TX, l_other=L_OTHER):
    pl_ref = fspl_db(D_REF, f_mhz)
    prx_ref = link_budget_dbm(P_TX, g_tx, pl_ref, G_RX, l_other)
    rng = max_range_km(f_mhz, P_TX, g_tx, G_RX, l_other, SENS)
    print(f"{label:<28} f={f_mhz:>6} MHz | PL@{D_REF}km={pl_ref:6.1f} dB | "
          f"PRX={prx_ref:7.1f} dBm | margin={prx_ref - SENS:6.1f} dB | "
          f"max range={rng:10.2f} km")
    return rng


# ---------- Baseline (Steps 7-12) ----------
print("=== BASELINE ===")
plt.figure(figsize=(8, 5))
ranges = {}
for label, f in BANDS.items():
    prx = prx_curve(f)
    ranges[label] = summarize(label, f)
    # sanity check against array-based method
    assert abs(max_range_from_curve(prx) - ranges[label]) / ranges[label] < 0.02
    plt.plot(distances, prx, label=label)
plt.xscale("log")
plt.axhline(SENS, linestyle="--", color="k", label=f"Sensitivity ({SENS} dBm)")
plt.xlabel("Distance (km, log scale)")
plt.ylabel("Received power (dBm)")
plt.title("P_RX vs distance: 700 MHz vs 28 GHz (free space)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "link_budget_comparison.png"), dpi=200)

r_low, r_mm = ranges.values()
print(f"\nRange ratio (700 MHz / 28 GHz) = {r_low / r_mm:.1f}x "
      f"(= 28000/700 = {28000 / 700:.0f}x in frequency)")

# ---------- Task 1: 24 dBi phased array at 28 GHz ----------
print("\n=== TASK 1: 28 GHz with 24 dBi TX gain ===")
r_new = summarize("28 GHz, 24 dBi", 28000, g_tx=24)
print(f"Range recovered: {r_mm:.2f} -> {r_new:.2f} km (x{r_new / r_mm:.2f}); "
      f"+9 dB gives 10^(9/20) = {10 ** (9 / 20):.2f}x")

# ---------- Task 2: add 3.5 GHz ----------
print("\n=== TASK 2: add 3.5 GHz mid-band ===")
r_mid = summarize("3.5 GHz (mid-band)", 3500)
plt.figure(figsize=(8, 5))
for label, f, g in [("700 MHz", 700, G_TX), ("3.5 GHz", 3500, G_TX),
                    ("28 GHz (15 dBi)", 28000, G_TX),
                    ("28 GHz (24 dBi)", 28000, 24)]:
    plt.plot(distances, prx_curve(f, g_tx=g), label=label)
plt.xscale("log")
plt.axhline(SENS, linestyle="--", color="k", label="Sensitivity")
plt.xlabel("Distance (km, log scale)")
plt.ylabel("Received power (dBm)")
plt.title("Three bands + 28 GHz phased-array gain")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "task_1_2_bands_and_gain.png"), dpi=200)

# ---------- Task 3: 8 dB shadowing margin ----------
print("\n=== TASK 3: extra 8 dB shadowing/fading margin ===")
for label, f in [("700 MHz", 700), ("3.5 GHz", 3500), ("28 GHz", 28000)]:
    before = max_range_km(f, P_TX, G_TX, G_RX, L_OTHER, SENS)
    after = max_range_km(f, P_TX, G_TX, G_RX, L_OTHER + 8, SENS)
    print(f"{label:<8}: {before:10.2f} km -> {after:10.2f} km "
          f"(shrinks to {after / before * 100:.0f}% of original)")

# Task 3 chart: range before/after the shadowing margin
freqs3 = [700, 3500, 28000]
before3 = [max_range_km(f, P_TX, G_TX, G_RX, L_OTHER, SENS) for f in freqs3]
after3 = [max_range_km(f, P_TX, G_TX, G_RX, L_OTHER + 8, SENS) for f in freqs3]
x3 = np.arange(3)
plt.figure(figsize=(7.5, 5))
plt.bar(x3 - 0.2, before3, 0.4, label="L_other = 3 dB")
plt.bar(x3 + 0.2, after3, 0.4, label="L_other = 11 dB (+8 dB shadowing)")
plt.yscale("log")
plt.xticks(x3, ["700 MHz", "3.5 GHz", "28 GHz"])
plt.ylabel("Maximum range (km, log scale)")
plt.title("Effect of an 8 dB shadowing margin on range")
plt.legend()
plt.grid(axis="y", which="both", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "task_3_shadowing.png"), dpi=200)

# ---------- Task 4: SNR and capacity vs distance ----------
print("\n=== TASK 4: SNR and capacity (B = 10 MHz, noise = "
      f"{noise_dbm(10e6):.0f} dBm) ===")
BW = 10e6
plt.figure(figsize=(8, 5))
for label, f in BANDS.items():
    prx = prx_curve(f)
    cap_mbps = capacity_bps(prx, BW) / 1e6
    plt.semilogx(distances, cap_mbps, label=label)
    for d in (0.1, 1, 10):
        p = link_budget_dbm(P_TX, G_TX, fspl_db(d, f), G_RX, L_OTHER)
        print(f"{label:<20} d={d:>5} km: PRX={p:7.1f} dBm, "
              f"SNR={p - noise_dbm(BW):6.1f} dB, "
              f"C={capacity_bps(p, BW) / 1e6:8.1f} Mbps")
plt.xlabel("Distance (km, log scale)")
plt.ylabel("Capacity ceiling (Mbps)")
plt.title("Shannon capacity vs distance (10 MHz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "task_4_capacity.png"), dpi=200)

# ---------- Task 5: double power vs double bandwidth ----------
print("\n=== TASK 5: double TX power vs double bandwidth ===")
for label, f, d in [("700 MHz", 700, 0.5), ("28 GHz", 28000, 0.5),
                    ("28 GHz", 28000, 10)]:
    prx = link_budget_dbm(P_TX, G_TX, fspl_db(d, f), G_RX, L_OTHER)
    base = capacity_bps(prx, BW) / 1e6
    dbl_p = capacity_bps(prx + 3.01, BW) / 1e6       # +3 dB
    dbl_b = capacity_bps(prx, 2 * BW) / 1e6          # noise also doubles
    print(f"{label:<8} d={d:>4} km: base={base:7.1f} | 2x power={dbl_p:7.1f} "
          f"(x{dbl_p / base:.2f}) | 2x bandwidth={dbl_b:7.1f} (x{dbl_b / base:.2f})")

plt.show()
