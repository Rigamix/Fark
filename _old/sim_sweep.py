"""Parameter sweeps for the Tells that look off-target in the basic sim."""
import sys
sys.path.insert(0, '.')
from sim_tells import run_batch
import random

random.seed(123)

print("=" * 90)
print("CUTPURSE chance sweep — Finnick T3, target 7500, NPC=350, threshold=350")
print("=" * 90)
print(f"{'CHANCE':<8} {'WIN%':>6} {'BASE':>6} {'dWIN':>7} {'PALMED/MATCH':>14}")
base = run_batch(None, {}, n=2000, target=7500, npc_bank_avg=350, bank_threshold=350)
for chance in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]:
    r = run_batch('cutpurse', {'chance': chance}, n=2000, target=7500, npc_bank_avg=350, bank_threshold=350)
    delta = (r['win_rate'] - base['win_rate']) * 100
    print(f"{chance:<8.2f} {r['win_rate']*100:>5.1f}% {base['win_rate']*100:>5.1f}% {delta:>+6.1f}% {r['avg_palmed']:>13.1f}")

print()
print("=" * 90)
print("STEEPED perRoll sweep — Mabel T2, target 5500, NPC=300, threshold=350")
print("=" * 90)
print(f"{'PER':<6} {'WIN%':>6} {'BASE':>6} {'dWIN':>7} {'BANK':>6} {'BUSTS':>6}")
base = run_batch(None, {}, n=2000, target=5500, npc_bank_avg=300, bank_threshold=350)
for perRoll in [10, 25, 35, 50, 75, 100]:
    r = run_batch('steeped', {'perRoll': perRoll}, n=2000, target=5500, npc_bank_avg=300, bank_threshold=350)
    delta = (r['win_rate'] - base['win_rate']) * 100
    print(f"{perRoll:<6} {r['win_rate']*100:>5.1f}% {base['win_rate']*100:>5.1f}% {delta:>+6.1f}% {r['avg_bank']:>5.0f} {r['avg_busts']:>5.1f}")

print()
print("=" * 90)
print("IN ARREARS perRoll sweep — Corvus T4, target 10000, NPC=400, threshold=350")
print("=" * 90)
print(f"{'PER':<6} {'WIN%':>6} {'GOLD LOST/MATCH':>18}")
for perRoll in [1, 2, 3, 4, 5, 7]:
    r = run_batch('in_arrears', {'perRoll': perRoll}, n=2000, target=10000, npc_bank_avg=400, bank_threshold=350)
    print(f"{perRoll:<6} {r['win_rate']*100:>5.1f}% {-r['avg_gold_lost']:>14.0f}g")

print()
print("=" * 90)
print("LAST CALL threshold sweep — Grog T1, target 4000, NPC=280, threshold=350")
print("=" * 90)
print(f"{'THR':<6} {'WIN%':>6} {'BASE':>6} {'dWIN':>7} {'BANK-ZERO/MATCH':>18}")
base = run_batch(None, {}, n=2000, target=4000, npc_bank_avg=280, bank_threshold=350)
for thr in [150, 250, 300, 350, 400]:
    r = run_batch('last_call', {'threshold': thr}, n=2000, target=4000, npc_bank_avg=280, bank_threshold=350)
    delta = (r['win_rate'] - base['win_rate']) * 100
    print(f"{thr:<6} {r['win_rate']*100:>5.1f}% {base['win_rate']*100:>5.1f}% {delta:>+6.1f}% {r['avg_lc_zeroes']:>17.1f}")

print()
print("=" * 90)
print("STRATEGY sweep — Steeped @ +50 — banks player at varying thresholds (Mabel T2)")
print("=" * 90)
print(f"{'STRAT':<10} {'WIN%':>6} {'BASE':>6} {'dWIN':>7} {'BANK':>6} {'BUSTS':>6}")
for thr in [200, 300, 400, 500, 700]:
    base_t = run_batch(None, {}, n=2000, target=5500, npc_bank_avg=300, bank_threshold=thr)
    tell_t = run_batch('steeped', {'perRoll': 50}, n=2000, target=5500, npc_bank_avg=300, bank_threshold=thr)
    delta = (tell_t['win_rate'] - base_t['win_rate']) * 100
    print(f"{thr:<10} {tell_t['win_rate']*100:>5.1f}% {base_t['win_rate']*100:>5.1f}% {delta:>+6.1f}% {tell_t['avg_bank']:>5.0f} {tell_t['avg_busts']:>5.1f}")

print()
print("=" * 90)
print("DRILL ORDER maxRolls sweep — Brutus T5, target 13000, NPC=450")
print("=" * 90)
print(f"{'MAX':<5} {'WIN%':>6} {'BASE':>6} {'dWIN':>7} {'DRILL-BUSTS/MATCH':>20}")
base = run_batch(None, {}, n=2000, target=13000, npc_bank_avg=450, bank_threshold=400)
for maxR in [2, 3, 4, 5]:
    r = run_batch('drill_order', {'maxRolls': maxR}, n=2000, target=13000, npc_bank_avg=450, bank_threshold=400)
    delta = (r['win_rate'] - base['win_rate']) * 100
    print(f"{maxR:<5} {r['win_rate']*100:>5.1f}% {base['win_rate']*100:>5.1f}% {delta:>+6.1f}% {r['avg_drill_busts']:>19.1f}")

print()
print("Notes:")
print("  - Real game has player cards/premium dice that change scoring rates substantially")
print("  - Sim uses greedy threshold-bank strategy, no card synergies")
print("  - 'BASE' = same conditions, no Tell active")
