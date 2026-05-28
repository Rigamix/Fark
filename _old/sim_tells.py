"""
Farkle/Fark Tells balance simulator.

Goal: estimate per-Tell impact on player win rate / banking efficiency
across batches per patron, holding strategy constant.

Strategy model: greedy-but-cautious player who banks at threshold.
"""
import random
import statistics
from collections import defaultdict


def score_dice(dice):
    if not dice:
        return 0, []
    counts = defaultdict(list)
    for i, v in enumerate(dice):
        counts[v].append(i)
    score = 0
    used = []
    for face, idxs in counts.items():
        n = len(idxs)
        if n >= 3:
            base = 1000 if face == 1 else face * 100
            mult = 1 if n == 3 else (n - 2)
            score += base * mult
            used.extend(idxs)
        else:
            if face == 1:
                score += 100 * n
                used.extend(idxs)
            elif face == 5:
                score += 50 * n
                used.extend(idxs)
    return score, used


def roll(n):
    return [random.randint(1, 6) for _ in range(n)]


def has_scoring(dice):
    s, _ = score_dice(dice)
    return s > 0


DEFAULT_BANK_THRESHOLD = 350


class TellState:
    def __init__(self, tell_id=None, params=None):
        self.id = tell_id
        self.params = params or {}
        self.steeped_bonus = 0
        self.cursed_idx = []
        self.last_npc_bank = 0
        self.gold_lost = 0
        self.cards_sealed = 0
        self.palmed_count = 0
        self.last_call_zeroes = 0
        self.reckoning_zeroes = 0
        self.drill_busts = 0


def simulate_player_turn(tell=None, bank_threshold=DEFAULT_BANK_THRESHOLD,
                          turn_num=1, num_dice=6):
    free = num_dice
    kept_pts = 0
    roll_count = 0

    cursed_positions = set()
    if tell and tell.id == 'counterfeit':
        start = tell.params.get('startCount', 1)
        add_every = tell.params.get('addEvery', 3)
        target_count = min(num_dice - 1, start + (turn_num - 1) // add_every)
        cursed_positions = set(random.sample(range(num_dice), target_count))

    while True:
        if tell and tell.id == 'drill_order' and roll_count >= tell.params.get('maxRolls', 3):
            tell.drill_busts += 1
            return 0, True, roll_count

        roll_count += 1

        if tell and tell.id == 'in_arrears':
            tell.gold_lost += tell.params.get('perRoll', 3)

        if tell and tell.id == 'steeped' and roll_count > 1:
            tell.steeped_bonus += tell.params.get('perRoll', 50)

        dice = roll(free)

        if tell and tell.id == 'cutpurse' and len(dice) > 1:
            if random.random() < tell.params.get('chance', 0.30):
                rm = random.randrange(len(dice))
                dice.pop(rm)
                tell.palmed_count += 1
                free -= 1

        if not has_scoring(dice):
            if tell and tell.id == 'steeped':
                tell.steeped_bonus = 0
            return 0, True, roll_count

        s, used = score_dice(dice)

        if tell and tell.id == 'counterfeit' and cursed_positions:
            curse_ratio = len(cursed_positions) / num_dice
            p_cursed_in_used = 1 - (1 - curse_ratio) ** len(used)
            if random.random() < p_cursed_in_used:
                s = s // 2

        kept_pts += s
        free -= len(used)
        if free == 0:
            free = num_dice

        effective_pts = kept_pts
        if tell and tell.id == 'steeped':
            effective_pts += tell.steeped_bonus

        if effective_pts >= bank_threshold:
            total = kept_pts
            if tell and tell.id == 'steeped':
                total += tell.steeped_bonus
                tell.steeped_bonus = 0
            if tell and tell.id == 'last_call' and total < tell.params.get('threshold', 250):
                tell.last_call_zeroes += 1
                return 0, False, roll_count
            if tell and tell.id == 'reckoning' and tell.last_npc_bank > 0 and total < tell.last_npc_bank:
                tell.reckoning_zeroes += 1
                return 0, False, roll_count
            return total, False, roll_count


def simulate_npc_bank(tell, target_bank=400):
    bank = max(0, int(random.gauss(target_bank, target_bank * 0.3)))
    if tell and tell.id == 'reckoning' and bank > 0:
        tell.last_npc_bank = bank
    return bank


def simulate_match(tell_id, params, target=10000, npc_bank_avg=400,
                   bank_threshold=DEFAULT_BANK_THRESHOLD, max_turns=80):
    tell = TellState(tell_id, params)
    p_pts = 0
    o_pts = 0
    p_banks = []
    p_busts = 0
    turn = 0
    while p_pts < target and o_pts < target and turn < max_turns:
        turn += 1
        eff_threshold = bank_threshold
        if tell.id == 'confession':
            tell.cards_sealed += 1
            eff_threshold = int(bank_threshold * 0.95)

        banked, busted, rolls = simulate_player_turn(tell, eff_threshold, turn)
        if busted:
            p_busts += 1
        else:
            p_banks.append(banked)
            p_pts += banked
            if p_pts >= target:
                break

        npc_bank = simulate_npc_bank(tell, npc_bank_avg)
        o_pts += npc_bank

    return {
        'won': p_pts >= target,
        'p_pts': p_pts,
        'o_pts': o_pts,
        'turns': turn,
        'banks': p_banks,
        'busts': p_busts,
        'avg_bank': statistics.mean(p_banks) if p_banks else 0,
        'gold_lost': tell.gold_lost,
        'last_call_zeroes': tell.last_call_zeroes,
        'reckoning_zeroes': tell.reckoning_zeroes,
        'drill_busts': tell.drill_busts,
        'palmed_count': tell.palmed_count,
        'cards_sealed': tell.cards_sealed,
    }


def run_batch(tell_id, params, n=2000, target=10000, npc_bank_avg=400, bank_threshold=350):
    results = [simulate_match(tell_id, params, target, npc_bank_avg, bank_threshold)
               for _ in range(n)]
    won = sum(1 for r in results if r['won'])
    return {
        'win_rate': won / n,
        'avg_bank': statistics.mean(r['avg_bank'] for r in results),
        'avg_busts': statistics.mean(r['busts'] for r in results),
        'avg_turns': statistics.mean(r['turns'] for r in results),
        'avg_gold_lost': statistics.mean(r['gold_lost'] for r in results),
        'avg_lc_zeroes': statistics.mean(r['last_call_zeroes'] for r in results),
        'avg_rk_zeroes': statistics.mean(r['reckoning_zeroes'] for r in results),
        'avg_drill_busts': statistics.mean(r['drill_busts'] for r in results),
        'avg_palmed': statistics.mean(r['palmed_count'] for r in results),
        'avg_cards_sealed': statistics.mean(r['cards_sealed'] for r in results),
    }


PATRONS = [
    ('GROG (T1)',     'last_call',  {'threshold': 250},                  4000,  280, 350),
    ('MABEL (T2)',    'steeped',    {'perRoll': 50},                     5500,  300, 350),
    ('FINNICK (T3)',  'cutpurse',   {'chance': 0.30},                    7500,  350, 350),
    ('CORVUS (T4)',   'in_arrears', {'perRoll': 3},                      10000, 400, 350),
    ('BRUTUS (T5)',   'drill_order',{'maxRolls': 3},                     13000, 450, 350),
    ('ALDRIC (T6)',   'confession', {},                                  17000, 500, 350),
    ('WHISPER (T7)',  'counterfeit',{'startCount': 1, 'addEvery': 3},    22000, 550, 350),
    ('AMBROSE (T8)',  'reckoning',  {},                                  28000, 600, 350),
]

random.seed(42)

print("=" * 102)
print(f"{'PATRON':<16} {'WIN%':>5}  {'BASE%':>5}  {'dWIN':>6}  {'BANK':>5}  {'BUSTS':>5}  {'TURNS':>5}  {'EXTRA':<32}")
print("-" * 102)

for name, tell_id, params, target, npc_avg, threshold in PATRONS:
    base = run_batch(None, {}, n=2000, target=target, npc_bank_avg=npc_avg, bank_threshold=threshold)
    tell = run_batch(tell_id, params, n=2000, target=target, npc_bank_avg=npc_avg, bank_threshold=threshold)
    delta = (tell['win_rate'] - base['win_rate']) * 100
    extra = ''
    if tell_id == 'in_arrears':
        extra = f"-{tell['avg_gold_lost']:.0f}g/match"
    elif tell_id == 'last_call':
        extra = f"{tell['avg_lc_zeroes']:.1f} bank-zeros/match"
    elif tell_id == 'reckoning':
        extra = f"{tell['avg_rk_zeroes']:.1f} reckoning-zeros"
    elif tell_id == 'drill_order':
        extra = f"{tell['avg_drill_busts']:.1f} drill-busts/match"
    elif tell_id == 'cutpurse':
        extra = f"{tell['avg_palmed']:.1f} dice palmed/match"
    elif tell_id == 'confession':
        extra = f"{tell['avg_cards_sealed']:.0f} card-seals/match"
    print(f"{name:<16} {tell['win_rate']*100:>4.1f}%  {base['win_rate']*100:>4.1f}%  {delta:>+5.1f}%  {tell['avg_bank']:>5.0f}  {tell['avg_busts']:>4.1f}  {tell['avg_turns']:>4.1f}   {extra:<32}")

print("=" * 102)
print("\nNotes:")
print("  - Baseline = no Tell, same patron target & NPC bank rate")
print("  - Strategy: greedy bank at 350; doesn't model player cards/dice/active-card use")
print("  - Each row = 4000 matches (2000 baseline + 2000 with Tell)")
