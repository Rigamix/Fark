"""COMPREHENSIVE PLAYTEST SIM
Runs ~50 representative builds across all 8 tier opponents to measure:
- Per-archetype win rates vs each tier
- Outlier cards (broken or dead)
- Build cohesion (committed builds beating mixed builds)
- Boss signature impact on boss-tier matches

Models the Phase 4-6 card effects (enablers, scalers, boss passives, actives)
against the same opponent AI as sim_balance.py.
"""
import random, statistics, sys

# ─────────── DICE & SCORING ───────────
DICE_BIAS = {
    'bone':    [1,2,2,2,1,1],
    'iron':    [1,1,1,1,1,1],
    'flint':   [1,1,2,3,2,2],
    'lead':    [2,2,2,2,1,1],
    'amber':   [1,2,2,2,2,1],
    'jade':    [1,1,3,3,1,2],
    'brass':   [2,2,2,2,1,2],
    'silver':  [2,2,2,2,2,2],
    'crystal': [1,3,3,3,1,3],
}

def roll_face(mat='bone'):
    bias = DICE_BIAS.get(mat, DICE_BIAS['bone'])
    total = sum(bias)
    r = random.random() * total
    for i,b in enumerate(bias):
        r -= b
        if r < 0: return i+1
    return 6

def score_roll(vals, cards=None, ctx=None):
    """Returns (pts, used_mask, combo_types_set)."""
    cards = cards or set()
    ctx = ctx or {}
    n = len(vals)
    used = [False]*n
    pts = 0
    combo_types = set()

    counts = [vals.count(f) for f in range(1,7)]

    # Straights (consume all dice if full)
    if all(c>=1 for c in counts):
        base = 1500
        if 'tavern_cheer' in cards: base += 750
        if 'tavern_tales' in cards:
            cn = arch_count_in(cards,'collector')
            if cn >= 3: base = int(base*1.5)
            elif cn == 2: base = int(base*1.2)
        pts += base
        for i in range(n): used[i]=True
        combo_types.add('straight')
        combo_types.add('hotdice')  # full straight triggers hot dice
        return pts, used, combo_types
    if all(counts[f-1]>=1 for f in [2,3,4,5,6]):
        base = 750
        if 'tavern_tales' in cards:
            cn = arch_count_in(cards,'collector')
            if cn >= 3: base = int(base*1.5)
            elif cn == 2: base = int(base*1.2)
        pts += base
        for f in [2,3,4,5,6]:
            for i in range(n):
                if not used[i] and vals[i]==f: used[i]=True; break
        combo_types.add('straight')
    elif all(counts[f-1]>=1 for f in [1,2,3,4,5]):
        base = 500
        if 'tavern_tales' in cards:
            cn = arch_count_in(cards,'collector')
            if cn >= 3: base = int(base*1.5)
            elif cn == 2: base = int(base*1.2)
        pts += base
        for f in [1,2,3,4,5]:
            for i in range(n):
                if not used[i] and vals[i]==f: used[i]=True; break
        combo_types.add('straight')

    # Triples (only count unused dice)
    for f in range(1,7):
        c = sum(1 for i in range(n) if not used[i] and vals[i]==f)
        if c >= 3:
            base = 1000 if f==1 else f*100
            for _ in range(c-3): base*=2
            if 'tavern_tales' in cards:
                cn = arch_count_in(cards,'collector')
                if cn >= 3: base = int(base*1.25)
                elif cn == 2: base = int(base*1.10)
            pts += base
            cnt = c
            for i in range(n):
                if not used[i] and vals[i]==f and cnt>0: used[i]=True; cnt-=1
            combo_types.add('triple')

    # Singles
    n_ones = 0
    for i in range(n):
        if not used[i]:
            v = vals[i]
            if v==1:
                pts += 150 if 'blood_tithe' in cards else (125 if 'copper_pincher' in cards else 100)
                used[i]=True
                n_ones += 1
            elif v==5:
                pts += 75 if 'copper_pincher' in cards else 50
                used[i]=True
    # Twin Dice
    if 'twin_dice' in cards and n_ones>=2:
        pts += 100

    return pts, used, combo_types

def any_scoring(vals, cards=None):
    return score_roll(vals, cards)[0] > 0

# ─────────── ARCHETYPE TABLE ───────────
ARCH = {
    # Safe-Banker
    'beggars_bowl':'safeBanker','half_measure':'safeBanker','the_hearth':'safeBanker',
    'greedy_hands':'safeBanker','copper_pincher':'safeBanker','flintlock':'safeBanker',
    'slow_burn':'safeBanker','tab_at_bar':'safeBanker','last_orders':'safeBanker',
    'mabels_ward':'safeBanker','bakers_dozen':'safeBanker',
    # Brinksman
    'martyr':'brinksman','thick_skin':'brinksman','high_roller':'brinksman',
    'blood_tithe':'brinksman','last_stand':'brinksman','iron_stomach':'brinksman',
    'stakes_rising':'brinksman','the_whetstone':'brinksman','double_down':'brinksman',
    'all_in':'brinksman','the_pyre':'brinksman','second_wind':'brinksman',
    'mabels_stitch':'brinksman','aldrics_vow':'brinksman','brutus_grit':'brinksman',
    # Collector
    'tavern_cheer':'collector','twin_dice':'collector','twin_flames':'collector',
    'the_ladder':'collector','the_collector':'collector','iron_crown':'collector',
    'tavern_tales':'collector','aldrics_banner':'collector',
    # Saboteur
    'sawdust':'saboteur','short_pour':'saboteur','crows_luck':'saboteur',
    'snake_oil':'saboteur','bad_reputation':'saboteur','bar_brawl':'saboteur',
    'the_fence':'saboteur','rats_in_cellar':'saboteur','whispers_hex':'saboteur',
    'whispers_veil':'saboteur','taxing_breath':'saboteur','leaky_cup':'saboteur',
    'cold_shoulder':'saboteur','cowards_bell':'saboteur','sooty_table':'saboteur',
    'slippery_table':'saboteur',
    # Sharp
    'gamblers_thumb':'sharp','loaded_die':'sharp','hot_streak':'sharp',
    'lucky_seven':'sharp','warm_hands':'sharp','rusty_spur':'sharp',
    'loaded_deck':'sharp','the_echo':'sharp','wild_die':'sharp','frozen_die':'sharp',
    'gamblers_eye':'sharp','grogs_flask':'sharp','finnicks_palm':'sharp',
    'brutus_fist':'sharp','ambrose_grace':'sharp','seven_dice':'sharp',
    'finnicks_trick':'sharp',
    # Hoarder
    'fortunes_wheel':'hoarder','chain_lightning':'hoarder','kings_ransom':'hoarder',
    'last_call':'hoarder','the_grudge':'hoarder','the_alchemist':'hoarder',
    'coin_jar':'hoarder','the_estate':'hoarder','compound_interest':'hoarder',
    'the_ledger':'hoarder','corvus_ledger':'hoarder','the_brewer':'hoarder',
    'dead_mans_hand':'hoarder','the_heir':'hoarder','corvus_book':'hoarder',
    'loan':'hoarder',
    # Utility
    'keen_eyes':'utility','iron_grip':'utility','ambrose_chalice':'utility',
}

def arch_count_in(cards, arch):
    return sum(1 for c in cards if ARCH.get(c)==arch)

# ─────────── BANK MODIFIERS (mirror index.html) ───────────
def apply_bank(total, cards, state, kept_dice_count, roll_count, combo_types_in_turn, lead, score, target):
    cards = set(cards)
    # Beggar's Bowl
    if 'beggars_bowl' in cards and not state.get('bb_used'):
        state['bb_used']=True; total += 150
    # Half Measure
    if 'half_measure' in cards and kept_dice_count == 3:
        total += 200
    # Hearth
    if 'the_hearth' in cards and roll_count == 1:
        total += 100
    # Greedy Hands
    if 'greedy_hands' in cards and total < 250:
        total *= 2
    # Tab at the Bar
    if 'tab_at_bar' in cards:
        total += arch_count_in(cards,'safeBanker') * 25
    # Last Orders
    if 'last_orders' in cards and arch_count_in(cards,'safeBanker') >= 3:
        state['lo_count'] = state.get('lo_count',0)+1
        if state['lo_count'] % 3 == 0: total *= 2
    # Stakes Rising arm
    if 'stakes_rising' in cards and total >= 500:
        state['sr_arm']=True
    # The Ledger
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
    # Slow Burn
    streak = state.get('safe_streak', 0)
    if 'slow_burn' in cards and streak > 0 and streak % 3 == 0:
        total += 300
    # Twin Flames
    triples = combo_types_in_turn.get('triples', 0)
    if 'twin_flames' in cards and triples >= 2:
        total += 750
    # Collector
    if 'the_collector' in cards and len(combo_types_in_turn.get('types', set())) >= 3:
        total += 100
    # High Roller
    if 'high_roller' in cards and total >= 800:
        total += 200
    # King's Ransom
    if 'kings_ransom' in cards and lead >= 3000:
        total += 1000
    # Fortune's Wheel
    if 'fortunes_wheel' in cards:
        state['fw'] = state.get('fw',0)+1
        if state['fw'] % 5 == 0: total *= 2
    # Mabel's Ward
    if 'mabels_ward' in cards:
        state['mw'] = state.get('mw',0)+1
        total += 400 if state['mw'] % 5 == 0 else 75
    # Corvus's Book
    if 'corvus_book' in cards:
        i = state.get('cb',0)
        if i > 0: total += i
        state['cb'] = i + (50 if total >= 1000 else 25)
    # Aldric's Banner
    if 'aldrics_banner' in cards:
        match_combos = state.setdefault('ab_types', set())
        for t in combo_types_in_turn.get('types', set()):
            match_combos.add(t)
        n = len(match_combos)
        if n > 0: total += n * 150
    # Brutus's Grit (bank bonus, +15%)
    if 'brutus_grit' in cards and total >= 500:
        total += int(total * 0.15)
    # NOTE: Grit bust-save is in match loop (capped at 1 per tuning)
    # Baker's Dozen
    if 'bakers_dozen' in cards:
        state['bd'] = state.get('bd',0)+1
        if state['bd'] == 13: total += 1300
    # The Heir
    if 'the_heir' in cards and state.get('turn',0) > 6:
        total += (state['turn']-6) * 50
    # Ambrose's Chalice (3 regular slots same arch)
    if 'ambrose_chalice' in cards:
        regular = [c for c in cards if c != 'ambrose_chalice'][:3]
        if len(regular) >= 3:
            archs = [ARCH.get(c) for c in regular[:3] if ARCH.get(c)]
            if len(archs) == 3 and archs[0] == archs[1] == archs[2]:
                total += 250
    # Last Call (winning bank)
    if 'last_call' in cards and (score+total) >= target:
        total += int(total * 0.5)
    # Blood Tithe
    if 'blood_tithe' in cards:
        total -= 50
    return total

# ─────────── PLAYER POLICY ───────────
def player_should_bank(turn_pts, dice_left, my_pts, opp_pts, target, cards):
    """A reasonably skilled banking policy."""
    # Always bank if it wins
    if my_pts + turn_pts >= target: return True
    # Stakes Rising bonus → push for 500+ if close
    if 'stakes_rising' in cards and turn_pts < 500 and dice_left >= 3:
        return False
    # Brutus's Grit makes <500 risk-free
    if 'brutus_grit' in cards and turn_pts < 500: return False
    # Few dice left → bank
    if dice_left <= 2 and turn_pts >= 300: return True
    # High Roller threshold push
    if 'high_roller' in cards and turn_pts < 800 and dice_left >= 3: return False
    # Generally bank ~300 when behind, ~500 when ahead
    behind = opp_pts > my_pts
    floor = 300 if behind else 500
    if turn_pts >= floor: return True
    return False

# ─────────── MATCH SIMULATOR ───────────
def sim_match(rung, p_cards):
    """Returns dict with win, p_score, o_score, turns."""
    p_score = 0
    o_score = 0
    turn = 0
    state = {'turn': 0}
    p_cards = set(p_cards)
    p_active = True  # alternate
    target = rung['target']
    max_turns = 30

    # Turn loop
    while p_score < target and o_score < target and turn < max_turns*2:
        turn += 1
        if p_active:
            state['turn'] = (turn+1)//2
            state['safe_streak'] = state.get('safe_streak', 0)
            # Stakes Rising consume
            turn_pts = 100 if state.pop('sr_arm', False) else 0
            # Loan repayment (unused since we don't have actives in this sim)
            roll_count = 0
            dice = 6
            if 'whispers_veil' in p_cards: pass  # affects opp not us
            committed_count = 0
            combo_in_turn = {'triples': 0, 'types': set()}
            grit_uses = 0
            martyr_used = False
            is_used = 0
            busted = False
            while True:
                roll_count += 1
                vals = [roll_face('bone') for _ in range(dice)]
                # Sharp dice manipulation
                if 'gamblers_thumb' in p_cards and roll_count == 1:
                    hits = 2 if 'loaded_deck' in p_cards and arch_count_in(p_cards,'sharp')>=3 else 1
                    for _ in range(hits):
                        if random.random() < 0.75:
                            blanks = [i for i,v in enumerate(vals) if v not in (1,5)]
                            if blanks: vals[blanks[0]] = 5
                if 'loaded_die' in p_cards and roll_count == 1:
                    hits = 2 if 'loaded_deck' in p_cards and arch_count_in(p_cards,'sharp')>=3 else 1
                    for _ in range(hits):
                        if random.random() < 0.4:
                            non1 = [i for i,v in enumerate(vals) if v != 1]
                            if non1: vals[non1[0]] = 1
                if 'finnicks_trick' in p_cards and roll_count == 1:
                    blanks = [i for i,v in enumerate(vals) if v not in (1,5)]
                    if blanks: vals[blanks[0]] = 5
                pts, used, combo_types = score_roll(vals, p_cards)
                if pts == 0:
                    # Bust — try saves in priority order
                    if 'brutus_grit' in p_cards and turn_pts < 500 and grit_uses < 1:
                        grit_uses += 1; continue
                    if 'martyr' in p_cards and not martyr_used:
                        martyr_used = True; continue
                    if 'iron_stomach' in p_cards:
                        is_max = min(2, arch_count_in(p_cards,'brinksman'))
                        if is_used < is_max: is_used += 1; continue
                    # Real bust
                    if 'thick_skin' in p_cards and not state.get('ts_used'):
                        state['ts_used'] = True
                        turn_pts = turn_pts // 2
                    else:
                        turn_pts = 0
                    busted = True
                    state['safe_streak'] = 0
                    if 'loose_thread' in p_cards and state.get('busts_in_a_row',0) >= 1:
                        p_score += 400
                    state['busts_in_a_row'] = state.get('busts_in_a_row',0) + 1
                    break
                # Track combos
                counts = [vals.count(f) for f in range(1,7)]
                for c in counts:
                    if c >= 3: combo_in_turn['triples'] += 1
                if any(c>=3 for c in counts): combo_in_turn['types'].add('triple')
                if all(counts[f-1]>=1 for f in range(1,7)):
                    combo_in_turn['types'].add('straight')
                    combo_in_turn['types'].add('hotdice')
                if 'straight' in combo_types: combo_in_turn['types'].add('straight')
                committed_count += sum(used)
                turn_pts += pts
                dice -= sum(used)
                if dice == 0:
                    # Hot dice
                    combo_in_turn['types'].add('hotdice')
                    if 'iron_crown' in p_cards:
                        state['ic_hits'] = state.get('ic_hits', 0) + 1
                        bonus = 500 + (state['ic_hits']-1) * 250
                        p_score += bonus
                    dice = 6
                # Decide to bank or roll on
                if player_should_bank(turn_pts, dice, p_score, o_score, target, p_cards):
                    bank = apply_bank(
                        turn_pts, p_cards, state,
                        kept_dice_count=committed_count,
                        roll_count=roll_count,
                        combo_types_in_turn=combo_in_turn,
                        lead=p_score - o_score,
                        score=p_score,
                        target=target
                    )
                    p_score += bank
                    state['safe_streak'] = state.get('safe_streak', 0) + 1
                    state['busts_in_a_row'] = 0
                    break
        else:
            # Opponent turn — simple model
            opp_dice = 6
            opp_turn_idx = state.get('opp_turn_idx', 0) + 1
            state['opp_turn_idx'] = opp_turn_idx
            if 'whispers_veil' in p_cards and opp_turn_idx % 2 == 1: opp_dice = 5
            if 'whispers_hex' in p_cards: opp_dice = max(3, opp_dice-1)
            o_turn_pts = 0
            o_committed = 0
            o_busted = False
            roll_n = 0
            while True:
                roll_n += 1
                vals = [roll_face(rung.get('dice',['bone']*6)[(o_committed+roll_n)%6]) for _ in range(opp_dice)]
                pts, used, _ = score_roll(vals)
                if pts == 0:
                    o_busted = True
                    # Bar Brawl
                    if 'bar_brawl' in p_cards:
                        state['bb_hits'] = state.get('bb_hits',0)+1
                        p_score += 250 + (state['bb_hits']-1) * 50
                    # Rats in the Cellar
                    if 'rats_in_cellar' in p_cards:
                        o_score = max(0, o_score - 200)
                    break
                o_turn_pts += pts
                o_committed += sum(used)
                opp_dice -= sum(used)
                if opp_dice == 0: opp_dice = 6
                # Opp bank policy: bank if turn_pts >= rung's minBank, more aggressive with agg
                if o_turn_pts >= rung.get('minBank', 200) and (random.random() > rung.get('agg', 0.5) or opp_dice <= 2):
                    o_score += o_turn_pts
                    # Saboteur first-bank effects
                    if 'bad_reputation' in p_cards and not state.get('br_used') and arch_count_in(p_cards,'saboteur')>=3:
                        state['br_used'] = True
                        o_score -= o_turn_pts // 2
                    if 'short_pour' in p_cards:
                        o_score -= int(o_turn_pts * 0.10)
                    if 'taxing_breath' in p_cards and o_turn_pts >= 100:
                        o_score -= 100
                        p_score += 100
                    break
                if o_turn_pts > 1500: break  # safety cap
        p_active = not p_active

    won = p_score >= target and (p_score >= o_score or o_score < target)
    return dict(win=won, p_score=p_score, o_score=o_score, turns=turn)

# ─────────── RUNGS ───────────
RUNGS = [
    dict(name='GROG',    target=1500, agg=0.22, minBank=0,   chaotic=True,  dice=['bone']*6),
    dict(name='MABEL',   target=2000, agg=0.30, minBank=150, dice=['bone']*5+['iron']),
    dict(name='FINNICK', target=2500, agg=0.40, minBank=200, dice=['bone','bone','bone','iron','iron','flint']),
    dict(name='CORVUS',  target=3000, agg=0.50, minBank=350, dice=['bone','iron','iron','flint','lead','lead']),
    dict(name='BRUTUS',  target=3500, agg=0.55, minBank=250, dice=['iron','iron','flint','lead','amber','amber']),
    dict(name='ALDRIC',  target=4000, agg=0.58, minBank=300, dice=['iron','flint','lead','amber','jade','jade']),
    dict(name='WHISPER', target=4500, agg=0.58, minBank=300, dice=['flint','lead','amber','jade','brass','brass']),
    dict(name='AMBROSE', target=5000, agg=0.62, minBank=200, dice=['lead','amber','jade','brass','silver','crystal']),
]

# ─────────── BUILDS TO TEST ───────────
BUILDS = [
    # Baseline
    ('EMPTY', []),
    # Pure archetype builds
    ('SAFE-BANKER pure 4', ['beggars_bowl','the_hearth','greedy_hands','tab_at_bar']),
    ('SAFE-BANKER + LAST ORDERS', ['beggars_bowl','the_hearth','greedy_hands','last_orders']),
    ('SAFE-BANKER + MABELS WARD', ['beggars_bowl','the_hearth','tab_at_bar','mabels_ward']),
    ('SAFE-BANKER + BAKER', ['beggars_bowl','the_hearth','tab_at_bar','bakers_dozen']),
    ('BRINKSMAN pure 4', ['martyr','thick_skin','high_roller','iron_stomach']),
    ('BRINKSMAN + STAKES', ['martyr','thick_skin','iron_stomach','stakes_rising']),
    ('BRINKSMAN + GRIT', ['martyr','thick_skin','iron_stomach','brutus_grit']),
    ('COLLECTOR pure 4', ['tavern_cheer','twin_flames','the_collector','tavern_tales']),
    ('COLLECTOR + BANNER', ['tavern_cheer','twin_flames','the_collector','aldrics_banner']),
    ('COLLECTOR + IRON CROWN', ['tavern_cheer','twin_flames','iron_crown','tavern_tales']),
    ('SABOTEUR pure 4', ['sawdust','short_pour','crows_luck','bad_reputation']),
    ('SABOTEUR + BAR BRAWL', ['sawdust','short_pour','rats_in_cellar','bar_brawl']),
    ('SABOTEUR + WHISPERS VEIL', ['sawdust','short_pour','crows_luck','whispers_veil']),
    ('SHARP pure 4', ['gamblers_thumb','loaded_die','warm_hands','loaded_deck']),
    ('SHARP + FINNICKS TRICK', ['gamblers_thumb','loaded_die','hot_streak','finnicks_trick']),
    ('SHARP + LOADED DECK + WARM', ['gamblers_thumb','loaded_die','warm_hands','loaded_deck']),
    ('HOARDER ledger build', ['the_estate','the_ledger','coin_jar','compound_interest']),
    ('HOARDER + CORVUS BOOK', ['the_estate','the_ledger','coin_jar','corvus_book']),
    ('HOARDER + HEIR', ['the_estate','the_ledger','the_heir','coin_jar']),
    ('HOARDER + LEDGER + RANSOM', ['the_estate','the_ledger','kings_ransom','last_call']),
    # Mixed (no enabler triggers)
    ('MIXED random 4', ['beggars_bowl','martyr','tavern_cheer','loaded_die']),
    ('MIXED 2 archs', ['the_estate','the_ledger','tavern_cheer','twin_flames']),
    ('MIXED 4 archs', ['beggars_bowl','high_roller','tavern_cheer','rats_in_cellar']),
    # Boss-card showcase (one signature with archetype support)
    ('CHALICE pure', ['beggars_bowl','the_hearth','greedy_hands','ambrose_chalice']),
    ('CHALICE mixed (no proc)', ['beggars_bowl','high_roller','tavern_cheer','ambrose_chalice']),
]

N = 400  # matches per build per opponent

print('='*108)
print(f'  PLAYTEST SIM — {N} matches per build × opponent — {N*len(BUILDS)*len(RUNGS):,} total matches')
print('='*108)

# Quick header
header = f"  {'BUILD':35s}"
for r in RUNGS: header += f" {r['name'][:5]:>6s}"
header += '   AVG'
print()
print(header)
print('  ' + '-'*100)

results = {}
for label, cards in BUILDS:
    row = f"  {label:35s}"
    wins_per_rung = []
    for rung in RUNGS:
        wins = sum(1 for _ in range(N) if sim_match(rung, cards)['win'])
        wr = wins/N*100
        wins_per_rung.append(wr)
        row += f" {wr:5.1f}%"
    avg = statistics.mean(wins_per_rung)
    row += f"  {avg:5.1f}%"
    results[label] = (wins_per_rung, avg)
    print(row, flush=True)

print('  ' + '-'*100)
print()

# Summary: which builds are strongest, which are dead?
sorted_by_avg = sorted(results.items(), key=lambda x: -x[1][1])
print('  TOP 5 BUILDS (by avg win rate across all tiers):')
for label, (rates, avg) in sorted_by_avg[:5]:
    print(f"    {avg:5.1f}%  {label}")
print()
print('  BOTTOM 5 BUILDS:')
for label, (rates, avg) in sorted_by_avg[-5:]:
    print(f"    {avg:5.1f}%  {label}")
print()

# Archetype committed vs mixed
committed = [r for k,(r,a) in results.items() if 'pure' in k.lower() or '+' in k and 'MIXED' not in k]
mixed = [r for k,(r,a) in results.items() if 'MIXED' in k]
if committed and mixed:
    flat_c = [v for sub in committed for v in sub]
    flat_m = [v for sub in mixed for v in sub]
    print(f'  Committed builds avg: {statistics.mean(flat_c):.1f}%')
    print(f'  Mixed builds avg:     {statistics.mean(flat_m):.1f}%')
    print(f'  Commitment delta:     +{statistics.mean(flat_c)-statistics.mean(flat_m):.1f}%')

print()
print('='*108)
