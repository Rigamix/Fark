# -*- coding: utf-8 -*-
"""Per-night gear, v2 - now simulating the real shop instead of assuming it.

WHAT v1 GOT WRONG, caught by reading _shopRollNight rather than trusting the
price table:
  - it bought crystal and brass. The shop stocks SEVEN families only:
    amber, jade, jade2, silver, obsidian, starstone, vagabond.
  - it assumed everything is always in stock. Each family is SOLD OUT with
    p=0.55 every night, independently.
  - it ignored the pity rule: the shop always stocks at least one family the
    player does not already own.

MEASURED (fark_proto.html):
  shop families  amber jade jade2 silver obsidian starstone vagabond
  sold-out       Math.random()<0.55 per family per night
  pity rule      always at least one unowned family available
  prices         amber 180, obsidian 500, silver 580, starstone 700,
                 vagabond 700, jade 750, jade2 1800
  NIGHT_BUYINS   [10,15,25,35,50,65,80,100]
  pointsNeeded   [2,2,2,3,3,3,3,4], seats = +2
  boss gold      [100,175,250,350,500,700,950,1300]
  patron win     net 20 + t*12       spoils purse  500 + t*60
  fresh run      six bone

ASSUMPTIONS (challenge these - they are the only unmeasured inputs):
  A1  patron win rate 65%          (brief targets 60-70%)
  A2  beats each boss first try
  A3  spoils = PURSE every night   (gear-maximising; taking a relic instead
                                    trades gold for a die - not modelled)
  A4  buys the most expensive die IN STOCK it can afford, once per night
  A5  no enchant spending, no tavern-card gold, never sells
"""
import random

FAMS = [('jade2', 1800), ('jade', 750), ('starstone', 700), ('vagabond', 700),
        ('silver', 580), ('obsidian', 500), ('amber', 180)]
BUYIN   = [10, 15, 25, 35, 50, 65, 80, 100]
NEEDED  = [2, 2, 2, 3, 3, 3, 3, 4]
BOSSGLD = [100, 175, 250, 350, 500, 700, 950, 1300]
WINRATE = 0.65
RUNS    = 4000

# loadout held when FACING each night's boss, counted across runs
held = [dict() for _ in range(8)]

for r in range(RUNS):
    rng = random.Random(20260806 + r)
    gold = 0.0
    dice = ['bone'] * 6
    for t in range(8):
        # the loadout you FACE this boss with is what you own before shopping
        key = ','.join(sorted(dice))
        held[t][key] = held[t].get(key, 0) + 1

        seats = NEEDED[t] + 2
        attempts = min(seats, NEEDED[t] / WINRATE)
        wins = attempts * WINRATE
        gold += wins * (20 + t * 12)
        gold -= (attempts - wins) * BUYIN[t]
        gold += BOSSGLD[t]
        gold += 500 + t * 60

        # shop rotation
        avail = [f for f in FAMS if rng.random() >= 0.55]
        owned = set(dice)
        if not any(f[0] not in owned for f in avail):        # pity rule
            unowned = [f for f in FAMS if f[0] not in owned]
            if unowned:
                avail.append(rng.choice(unowned))
        buyable = [f for f in avail if f[1] <= gold]
        if buyable:
            name, cost = max(buyable, key=lambda f: f[1])
            gold -= cost
            for i in range(len(dice)):
                if dice[i] == 'bone':
                    dice[i] = name
                    break

print('MODAL loadout held when facing each boss (%d simulated runs)' % RUNS)
print('%-6s %-9s %6s   %s' % ('night', 'boss', 'freq', 'loadout'))
BOSSES = ['GROG', 'MABEL', 'FINNICK', 'CORVUS', 'BRUTUS', 'ALDRIC', 'WHISPER', 'AMBROSE']
for t in range(8):
    best = max(held[t].items(), key=lambda kv: kv[1])
    pct = 100.0 * best[1] / RUNS
    print('%-6s %-9s %5.1f%%   %s' % (t + 1, BOSSES[t], pct, best[0]))
print()
print('spread - how many DISTINCT loadouts appear at each night:')
print('  ' + ', '.join('n%d:%d' % (t + 1, len(held[t])) for t in range(8)))
