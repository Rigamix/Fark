"""PHASE 4 SIM — measures the impact of new archetype enabler/scaler cards.

Models a simplified Farkle match where the player banks until they hit the target.
For each card configuration, runs N matches and reports avg banks needed, avg score,
and bust rate. Goal: verify that committing to an archetype meaningfully outpaces
a random/un-themed loadout, without breaking the core economy.
"""
import random, sys, statistics

# ---- DICE BIAS (matches sim_balance.py BONE6 baseline) ----
def roll_face_bone():
    # bone bias: [1,2,2,2,1,1] — face indices 1..6 with weights
    bias = [1,2,2,2,1,1]
    total = sum(bias)
    r = random.random() * total
    for i,b in enumerate(bias):
        r -= b
        if r < 0: return i+1
    return 6

# ---- CORE SCORING (Farkle rules — singles, triples, straights, ladders) ----
def score_roll(vals, cards=None):
    cards = cards or set()
    n = len(vals)
    used = [False]*n
    pts = 0
    cnt = lambda f: sum(1 for i in range(n) if not used[i] and vals[i]==f)
    mark = lambda f,k: [used.__setitem__(i,True) for i in range(n)
                        if not used[i] and vals[i]==f and (k:=k-1)>=0]

    # straights
    counts = [vals.count(f) for f in range(1,7)]
    if all(c>=1 for c in counts):
        pts += 1500  # full straight
        for i in range(n): used[i]=True
        return pts, used
    if all(counts[f-1]>=1 for f in [2,3,4,5,6]):
        pts += 750
        for f in [2,3,4,5,6]:
            for i in range(n):
                if not used[i] and vals[i]==f: used[i]=True; break
    elif all(counts[f-1]>=1 for f in [1,2,3,4,5]):
        pts += 500
        for f in [1,2,3,4,5]:
            for i in range(n):
                if not used[i] and vals[i]==f: used[i]=True; break
    # triples
    for f in range(1,7):
        c = cnt(f)
        if c >= 3:
            base = 1000 if f==1 else f*100
            for _ in range(c-3): base*=2
            pts += base
            for i in range(n):
                if not used[i] and vals[i]==f and c>0: used[i]=True; c-=1
    # singles
    for i in range(n):
        if not used[i]:
            v = vals[i]
            if v==1: pts+=100; used[i]=True
            elif v==5: pts+=50; used[i]=True
    return pts, used

def any_scoring(vals):
    return score_roll(vals)[0] > 0

# ---- ARCHETYPE-AWARE BANK MODIFIERS ----
# Each card identified by id; we know its archetype and its bank-side effect.
# This intentionally mirrors the wired effects in index.html.
ARCH = {
    'beggars_bowl':'safeBanker','half_measure':'safeBanker','the_hearth':'safeBanker',
    'greedy_hands':'safeBanker','copper_pincher':'safeBanker','flintlock':'safeBanker',
    'slow_burn':'safeBanker','tab_at_bar':'safeBanker','last_orders':'safeBanker',
    'martyr':'brinksman','thick_skin':'brinksman','high_roller':'brinksman',
    'blood_tithe':'brinksman','last_stand':'brinksman','iron_stomach':'brinksman',
    'stakes_rising':'brinksman','the_whetstone':'brinksman',
    'tavern_cheer':'collector','twin_dice':'collector','twin_flames':'collector',
    'the_ladder':'collector','the_collector':'collector','iron_crown':'collector',
    'tavern_tales':'collector',
    'sawdust':'saboteur','short_pour':'saboteur','crows_luck':'saboteur',
    'snake_oil':'saboteur','bad_reputation':'saboteur','bar_brawl':'saboteur','the_fence':'saboteur',
    'gamblers_thumb':'sharp','loaded_die':'sharp','hot_streak':'sharp',
    'lucky_seven':'sharp','warm_hands':'sharp','rusty_spur':'sharp','loaded_deck':'sharp',
    'the_echo':'sharp',
    'fortunes_wheel':'hoarder','chain_lightning':'hoarder','kings_ransom':'hoarder',
    'last_call':'hoarder','the_grudge':'hoarder',
    'coin_jar':'hoarder','the_estate':'hoarder','compound_interest':'hoarder','the_ledger':'hoarder',
}

def arch_count(cards, arch):
    return sum(1 for c in cards if ARCH.get(c)==arch)

def apply_bank_modifiers(total, cards, state):
    """Apply all bank-side card effects in roughly the same order as index.html."""
    # Beggar's Bowl (first bank +150)
    if 'beggars_bowl' in cards and not state.get('bb_used'):
        state['bb_used']=True; total += 150
    # Half measure (3-dice bank +200)
    if 'half_measure' in cards and state.get('dice_committed')==3:
        total += 200
    # Hearth (first-roll bank +100)
    if 'the_hearth' in cards and state.get('roll_count')==1:
        total += 100
    # Greedy hands (banks <250 doubled)
    if 'greedy_hands' in cards and total < 250:
        total *= 2
    # Tab at the Bar (+25 per Safe-Banker)
    if 'tab_at_bar' in cards:
        total += arch_count(cards,'safeBanker') * 25
    # Last Orders (3+ Safe-Banker → every 3rd bank x2)
    if 'last_orders' in cards and arch_count(cards,'safeBanker')>=3:
        state['lo_count'] = state.get('lo_count',0)+1
        if state['lo_count'] % 3 == 0: total *= 2
    # Stakes Rising (arm flag)
    if 'stakes_rising' in cards and total >= 500:
        state['sr_arm']=True
    # The Ledger (stack)
    if 'the_ledger' in cards:
        st = state.get('ledger',0)
        if st > 0: total += st
        state['ledger'] = st + 25
    # Compound Interest
    if 'compound_interest' in cards:
        m = state.get('ci_mult',0)
        if m > 0: total += int(total * m)
        state['ci_mult'] = min(0.5, m + 0.05)
    # Estate
    if 'the_estate' in cards:
        state['estate'] = state.get('estate',0)+1
        total += state['estate'] * 50
    # Coin Jar
    if 'coin_jar' in cards:
        state['cj'] = state.get('cj',0)+1
        if state['cj'] % 3 == 0:
            total += 200 * (state['cj']//3)
    # Slow burn (every 3rd safe streak +300)
    if 'slow_burn' in cards and state.get('safe_streak',0) % 3 == 0 and state.get('safe_streak',0) > 0:
        total += 300
    # Twin flames (2 different triples in turn → +750)
    if 'twin_flames' in cards and state.get('triples_this_turn',0) >= 2:
        total += 750
    # Collector (3+ score types)
    if 'the_collector' in cards and state.get('score_types_this_turn',0) >= 3:
        total += 100
    # High Roller (bank 800+)
    if 'high_roller' in cards and total >= 800:
        total += 200
    # King's Ransom (ahead by 3000+)
    if 'kings_ransom' in cards and state.get('lead',0) >= 3000:
        total += 1000
    # Fortune's Wheel (every 5th bank doubled)
    if "fortunes_wheel" in cards:
        state['fw'] = state.get('fw',0)+1
        if state['fw'] % 5 == 0: total *= 2
    return total

# ---- MATCH SIMULATOR ----
def sim_match(cards, target=2500, max_turns=30):
    """Simulate the player playing solo to a target score. Returns dict of stats."""
    cards = set(cards)
    score = 0
    turn = 0
    busts = 0
    banks = 0
    state = {}
    while score < target and turn < max_turns:
        turn += 1
        state['safe_streak'] = state.get('safe_streak', 0)
        # Stakes Rising consume
        turn_pts = 100 if state.pop('sr_arm', False) else 0
        roll_count = 0
        dice = 6
        triples_this_turn = 0
        score_types = set()
        committed_count = 0
        busted = False
        while True:
            roll_count += 1
            # Apply Sharp dice manipulation crudely (just bumps avg roll quality)
            vals = [roll_face_bone() for _ in range(dice)]
            if 'gamblers_thumb' in cards and roll_count == 1:
                # 75% chance to flip one blank to 5 (×2 with loaded_deck+3 sharp)
                hits = 2 if 'loaded_deck' in cards and arch_count(cards,'sharp')>=3 else 1
                for _ in range(hits):
                    blanks = [i for i,v in enumerate(vals) if v not in (1,5)]
                    if blanks and random.random() < 0.75:
                        vals[blanks[0]] = 5
            if 'loaded_die' in cards and roll_count == 1:
                hits = 2 if 'loaded_deck' in cards and arch_count(cards,'sharp')>=3 else 1
                for _ in range(hits):
                    nonones = [i for i,v in enumerate(vals) if v != 1]
                    if nonones and random.random() < 0.4:
                        vals[nonones[0]] = 1
            pts, used = score_roll(vals, cards)
            if pts == 0:
                # bust — try saves
                martyr_used = state.get('martyr_used', False)
                if 'martyr' in cards and not martyr_used:
                    state['martyr_used']=True
                    continue
                # Iron Stomach charges
                if 'iron_stomach' in cards:
                    is_used = state.get('is_used',0)
                    is_max = arch_count(cards,'brinksman')
                    if is_used < is_max:
                        state['is_used'] = is_used+1
                        continue
                turn_pts = 0
                busted = True
                busts += 1
                state['safe_streak'] = 0
                break
            # Track combos
            counts = [vals.count(f) for f in range(1,7)]
            for c in counts:
                if c >= 3: triples_this_turn += 1
            if 1 in vals: score_types.add('s1')
            if 5 in vals: score_types.add('s5')
            if any(c>=3 for c in counts): score_types.add('triple')
            if all(counts[f-1]>=1 for f in range(1,7)): score_types.add('straight')
            committed_count += sum(used)
            turn_pts += pts
            dice -= sum(used)
            if dice == 0: dice = 6  # hot dice
            # Decide to bank or roll on
            # Simple policy: bank if turn_pts >= 300 or dice <= 2
            should_bank = turn_pts >= 300 or dice <= 2
            if should_bank:
                state['dice_committed'] = committed_count
                state['roll_count'] = roll_count
                state['triples_this_turn'] = triples_this_turn
                state['score_types_this_turn'] = len(score_types)
                state['lead'] = score - 2000  # rough proxy for "ahead"
                bank = apply_bank_modifiers(turn_pts, cards, state)
                score += bank
                banks += 1
                state['safe_streak'] = state.get('safe_streak', 0) + 1
                break
        # End turn
    return dict(score=score, turn=turn, banks=banks, busts=busts, won=score>=target)

# ---- HARNESS ----
def benchmark(label, cards, n=2000, target=2500):
    results = [sim_match(cards, target=target) for _ in range(n)]
    wins = sum(1 for r in results if r['won'])
    avg_turn = statistics.mean(r['turn'] for r in results)
    avg_banks = statistics.mean(r['banks'] for r in results)
    avg_busts = statistics.mean(r['busts'] for r in results)
    avg_score = statistics.mean(r['score'] for r in results)
    print(f"  {label:35s} winrate={wins/n*100:5.1f}%  turns={avg_turn:5.1f}  banks={avg_banks:4.1f}  busts={avg_busts:4.2f}  score={avg_score:6.0f}")

print('='*100)
print(f'  PHASE 4 SIM — 2000 games per config, target=2500 (Tier 3 difficulty)')
print('='*100)
print()
print('  BASELINE (no cards)')
benchmark('  empty loadout', [], n=2000)

print()
print('  SAFE-BANKER ARCHETYPE')
benchmark('  beggars_bowl + hearth', ['beggars_bowl','the_hearth'])
benchmark('  + tab_at_bar', ['beggars_bowl','the_hearth','tab_at_bar'])
benchmark('  4x Safe-Banker (no enablers)', ['beggars_bowl','the_hearth','greedy_hands','copper_pincher'])
benchmark('  4x Safe-Banker + tab + last_orders', ['beggars_bowl','the_hearth','tab_at_bar','last_orders'])

print()
print('  BRINKSMAN ARCHETYPE')
benchmark('  martyr alone', ['martyr'])
benchmark('  martyr + thick_skin', ['martyr','thick_skin'])
benchmark('  3x Brinksman + iron_stomach', ['martyr','thick_skin','high_roller','iron_stomach'])
benchmark('  4x Brinksman + iron_stomach + stakes', ['martyr','thick_skin','high_roller','iron_stomach','stakes_rising'])

print()
print('  HOARDER ARCHETYPE')
benchmark('  fortunes_wheel alone', ['fortunes_wheel'])
benchmark('  the_ledger alone', ['the_ledger'])
benchmark('  the_estate alone', ['the_estate'])
benchmark('  Estate + Ledger + Coin Jar', ['the_estate','the_ledger','coin_jar'])
benchmark('  Estate + Ledger + Compound + Coin Jar', ['the_estate','the_ledger','compound_interest','coin_jar'])

print()
print('  COLLECTOR ARCHETYPE')
benchmark('  tavern_cheer alone', ['tavern_cheer'])
benchmark('  tavern_cheer + twin_flames + the_collector', ['tavern_cheer','twin_flames','the_collector'])
benchmark('  + tavern_tales (3+ Collector trigger)', ['tavern_cheer','twin_flames','the_collector','tavern_tales'])

print()
print('  SHARP ARCHETYPE')
benchmark('  loaded_die alone', ['loaded_die'])
benchmark('  gamblers_thumb + loaded_die', ['gamblers_thumb','loaded_die'])
benchmark('  3x Sharp + loaded_deck', ['gamblers_thumb','loaded_die','hot_streak','loaded_deck'])

print()
print('  CROSS-ARCHETYPE (no archetype commitment)')
benchmark('  random mix 4 cards', ['beggars_bowl','martyr','tavern_cheer','loaded_die'])

print()
print('='*100)
