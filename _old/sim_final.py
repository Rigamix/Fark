"""Final balance check after tunings: Cutpurse 0.20, Steeped +25, Last Call 300."""
import sys
sys.path.insert(0, '.')
from sim_tells import run_batch
import random

random.seed(789)

print("=" * 100)
print("FINAL TUNED VALUES — 4000 matches per row")
print("=" * 100)
print(f"{'PATRON':<20} {'WIN%':>5}  {'BASE%':>5}  {'dWIN':>6}  {'BANK':>5}  {'BUSTS':>5}  {'EXTRA'}")
print("-" * 100)

# Sweep two strategies per patron — naive (350) + aggressive (matches premium-dice play)
configs = [
    # name, tell_id, params, target, npc_avg, threshold, extra_key
    ('GROG (T1) lc=300',     'last_call',  {'threshold': 300},                  4000,  280, 350, 'avg_lc_zeroes'),
    ('GROG aggressive',      'last_call',  {'threshold': 300},                  4000,  280, 450, 'avg_lc_zeroes'),
    ('MABEL (T2) +25',       'steeped',    {'perRoll': 25},                     5500,  300, 350, None),
    ('MABEL aggressive',     'steeped',    {'perRoll': 25},                     5500,  300, 500, None),
    ('FINNICK (T3) c=0.20',  'cutpurse',   {'chance': 0.20},                    7500,  350, 350, 'avg_palmed'),
    ('FINNICK aggressive',   'cutpurse',   {'chance': 0.20},                    7500,  350, 550, 'avg_palmed'),
    ('CORVUS (T4) -3g',      'in_arrears', {'perRoll': 3},                     10000,  400, 350, 'avg_gold_lost'),
    ('BRUTUS (T5) max3',     'drill_order',{'maxRolls': 3},                    13000,  450, 400, 'avg_drill_busts'),
]

for name, tell_id, params, target, npc_avg, threshold, extra_key in configs:
    base = run_batch(None, {}, n=2000, target=target, npc_bank_avg=npc_avg, bank_threshold=threshold)
    tell = run_batch(tell_id, params, n=2000, target=target, npc_bank_avg=npc_avg, bank_threshold=threshold)
    delta = (tell['win_rate'] - base['win_rate']) * 100
    extra = ''
    if extra_key:
        v = tell[extra_key]
        if 'gold' in extra_key:
            extra = f"-{v:.0f}g/match"
        elif 'palmed' in extra_key:
            extra = f"{v:.1f} palmed/match"
        elif 'drill' in extra_key:
            extra = f"{v:.1f} drill-busts/match"
        elif 'lc' in extra_key:
            extra = f"{v:.1f} bank-zeros/match"
    print(f"{name:<20} {tell['win_rate']*100:>4.1f}%  {base['win_rate']*100:>4.1f}%  {delta:>+5.1f}%  {tell['avg_bank']:>5.0f}  {tell['avg_busts']:>4.1f}   {extra}")

print()
print("Targets: -5% to -25% win rate impact = healthy Tell.")
print("  +X% means Tell helps player (broken, needs more downside)")
print("  -50%+ means Tell is brutal, drop the param")
