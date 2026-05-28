"""High-tier patrons need an aggressive strategy to even win baseline.
Tune per-tier strategy and re-test Whisper / Ambrose / Aldric Tells."""
import sys
sys.path.insert(0, '.')
from sim_tells import run_batch
import random

random.seed(456)

print("=" * 100)
print("HIGH-TIER SIM with aggressive strategy (threshold=600 to model premium-dice play)")
print("=" * 100)
print(f"{'PATRON':<18} {'WIN%':>5}  {'BASE%':>5}  {'dWIN':>6}  {'BANK':>5}  {'BUSTS':>5}  {'TURNS':>5}  {'EXTRA'}")
print("-" * 100)

high_tier = [
    ('FINNICK (T3) c=0.20', 'cutpurse',   {'chance': 0.20},                    7500,  350, 500, 'avg_palmed'),
    ('FINNICK (T3) c=0.15', 'cutpurse',   {'chance': 0.15},                    7500,  350, 500, 'avg_palmed'),
    ('FINNICK (T3) c=0.30', 'cutpurse',   {'chance': 0.30},                    7500,  350, 500, 'avg_palmed'),
    ('CORVUS (T4) -3g',     'in_arrears', {'perRoll': 3},                      10000, 400, 550, 'avg_gold_lost'),
    ('CORVUS (T4) -2g',     'in_arrears', {'perRoll': 2},                      10000, 400, 550, 'avg_gold_lost'),
    ('BRUTUS (T5) max3',    'drill_order',{'maxRolls': 3},                     13000, 450, 600, 'avg_drill_busts'),
    ('BRUTUS (T5) max4',    'drill_order',{'maxRolls': 4},                     13000, 450, 600, 'avg_drill_busts'),
    ('ALDRIC (T6) seal',    'confession', {},                                  17000, 500, 650, 'avg_cards_sealed'),
    ('WHISPER (T7) cf 1+1/3','counterfeit',{'startCount': 1, 'addEvery': 3},   22000, 550, 700, None),
    ('WHISPER (T7) cf 1+1/4','counterfeit',{'startCount': 1, 'addEvery': 4},   22000, 550, 700, None),
    ('AMBROSE (T8) reck',   'reckoning',  {},                                  28000, 600, 800, 'avg_rk_zeroes'),
    ('AMBROSE (T8) reck +', 'reckoning',  {},                                  28000, 600, 1000, 'avg_rk_zeroes'),
]

for name, tell_id, params, target, npc_avg, threshold, extra_key in high_tier:
    base = run_batch(None, {}, n=2000, target=target, npc_bank_avg=npc_avg, bank_threshold=threshold)
    tell = run_batch(tell_id, params, n=2000, target=target, npc_bank_avg=npc_avg, bank_threshold=threshold)
    delta = (tell['win_rate'] - base['win_rate']) * 100
    extra = ''
    if extra_key:
        v = tell[extra_key]
        if 'gold' in extra_key:
            extra = f"-{v:.0f}g/match"
        elif 'palmed' in extra_key:
            extra = f"{v:.1f} dice palmed/match"
        elif 'drill' in extra_key:
            extra = f"{v:.1f} drill-busts/match"
        elif 'sealed' in extra_key:
            extra = f"{v:.0f} card-seals/match"
        elif 'rk' in extra_key:
            extra = f"{v:.1f} reckoning-zeros"
    print(f"{name:<18} {tell['win_rate']*100:>4.1f}%  {base['win_rate']*100:>4.1f}%  {delta:>+5.1f}%  {tell['avg_bank']:>5.0f}  {tell['avg_busts']:>4.1f}  {tell['avg_turns']:>4.1f}   {extra}")

print()
print("=" * 100)
print("STEEPED variants — bait-vs-buff comparison (Mabel T2, threshold=400)")
print("=" * 100)
print(f"{'VARIANT':<28} {'WIN%':>6} {'BASE':>6} {'dWIN':>7} {'BANK':>6} {'BUSTS':>6}")
base = run_batch(None, {}, n=2000, target=5500, npc_bank_avg=300, bank_threshold=400)
for perRoll in [10, 25, 35, 50]:
    r = run_batch('steeped', {'perRoll': perRoll}, n=2000, target=5500, npc_bank_avg=300, bank_threshold=400)
    delta = (r['win_rate'] - base['win_rate']) * 100
    print(f"Steeped +{perRoll:<3} per roll{'':<11} {r['win_rate']*100:>5.1f}% {base['win_rate']*100:>5.1f}% {delta:>+6.1f}% {r['avg_bank']:>5.0f} {r['avg_busts']:>5.1f}")
