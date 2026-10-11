#!/usr/bin/env python3
"""
Emoji AutoBattler v5 - 3 EMOJI VARIANTS PER TIER!

v5.1 changes:
  - Procedural tiers start at T1 (only T0 Blob is hand-crafted!)
  - Every game has unique units — names, colors, stats all generated
  - 3 unique emoji variants per tier (A/B/C) with distinct colors & styles
  - Shop offers procedural tiers that scale with round progression
  - Fusion recipes still work for any tier pair that matches
  - Visual style differences: glow variants have aura, dark variants no highlight

v5 changes (kept):
  - 3 unique emoji variants per tier (A/B/C)
  - INFINITE evolution chain: merge 3 of any tier -> next tier, forever
  - No more max tier cap — the grind never ends!

Merge Types:
  - Same tier x3 = Evolve (next tier — INFINITE)
  - Same tier x2 = Star Up (+25% stats)
  - Fusion Recipe = Specific base-tier pair -> unique hybrid

Controls:
  Drag units | Right-click/S: Sell | Space: Battle
  R: Reroll (2g) | A: Auto-merge bench | F: Full auto-merge (board+bench)
  TAB: Speed toggle | ESC: Quit

Requires: pygame (pip install pygame)
"""

import pygame, sys, math, random, time, colorsys

pygame.init()

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
SW, SH = 1400, 800
FPS = 60

# Colors
BG         = (22, 22, 35)
PANEL      = (32, 34, 52)
PANEL_BD   = (55, 58, 80)
SLOT       = (42, 44, 65)
SLOT_HL    = (62, 65, 95)
SLOT_MERGE = (40, 75, 40)
SLOT_MERGE2= (55, 90, 30)
SLOT_FUSION= (80, 50, 90)
SLOT_BAD   = (80, 50, 50)
GOLD       = (255, 215, 0)
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
RED        = (220, 50, 50)
GREEN      = (50, 200, 80)
BLUE       = (60, 120, 220)
PURPLE     = (160, 80, 220)
CYAN       = (60, 200, 220)
ORANGE     = (255, 160, 40)
DIM        = (140, 140, 160)
TXT        = (220, 220, 230)
HP_BG      = (60, 20, 20)
HP_FG      = (50, 200, 80)
HP_LOW     = (220, 50, 50)
BTN_GO     = (60, 160, 60)
BTN_GO_H   = (80, 200, 80)
TOOLTIP_BG = (20, 20, 32)
MAGENTA    = (220, 60, 220)

# Layout
BCOLS, BROWS = 7, 4
BENCH_N = 7
SHOP_N  = 5
CS = 72; CP = 4; CT = CS + CP
BX, BY = 40, 160
BNX, BNY = 40, 690
SX, SY = 600, 670
SCS = 64
IX, IY = 800, 160

# ─── ITEMS ───────────────────────────────────────────────────────────────────
ITEMS = [
    {"name": "Sword",   "stat": "atk",  "val": 0.25, "desc": "+25% ATK",  "color": RED},
    {"name": "Shield",  "stat": "max_hp","val": 0.30, "desc": "+30% HP",   "color": BLUE},
    {"name": "Boots",   "stat": "spd",  "val": 0.20, "desc": "+20% SPD",  "color": GREEN},
    {"name": "Lens",    "stat": "rng",  "val": 1,     "desc": "+1 RNG",    "color": CYAN},
    {"name": "Crystal", "stat": "atk",  "val": 0.40, "desc": "+40% ATK",  "color": PURPLE},
    {"name": "Heart",   "stat": "max_hp","val": 0.50, "desc": "+50% HP",   "color": (255, 100, 150)},
    {"name": "Scroll",  "stat": "xp_mult","val":0.5, "desc": "+50% XP",   "color": GOLD},
    {"name": "Fury",    "stat": "crit",  "val": 0.20, "desc": "+20% Crit", "color": ORANGE},
]

# ─── SYNERGY GROUPS ─────────────────────────────────────────────────────────
SYNERGIES = {
    "Elemental": {"tiers": {0, 2, 4}, "bonus": "+15% ATK", "stat": "atk", "val": 0.15,
                  "color": (255, 180, 60), "desc": "Elemental (Blob/Spark/Frost)"},
    "Nature":    {"tiers": {1, 4, 8}, "bonus": "+20% HP",  "stat": "max_hp", "val": 0.20,
                  "color": (80, 220, 120), "desc": "Nature (Slime/Frost/Cosmic)"},
    "Demon":     {"tiers": {3, 5, 7}, "bonus": "+20% SPD", "stat": "spd", "val": 0.20,
                  "color": (200, 60, 60),  "desc": "Demon (Flame/Shadow/Dragon)"},
    "Celestial": {"tiers": {6, 8}, "bonus": "+2 RNG",  "stat": "rng", "val": 2,
                  "color": (255, 220, 100),"desc": "Celestial (Star/Cosmic)"},
}

def unit_family(tier):
    for fam, info in SYNERGIES.items():
        if tier in info["tiers"]:
            return fam
    return None

# ─── FUSION RECIPES ──────────────────────────────────────────────────────────
FUSION_RECIPES = {
    (0, 1): {"name": "Ooze",    "body": (90, 190, 180), "eye": WHITE,       "feature": "bubbles",
             "hp": 50, "atk": 9,  "spd": 1.1, "rng": 2, "cost": 3,
             "desc": "Blob + Slime"},
    (2, 3): {"name": "Plasma",  "body": (255, 180, 30), "eye": (200, 50, 50), "feature": "lightning",
             "hp": 120, "atk": 22, "spd": 1.4, "rng": 3, "cost": 7,
             "desc": "Spark + Flame"},
    (5, 6): {"name": "Eclipse", "body": (40, 30, 80),   "eye": (255, 200, 50), "feature": "rings",
             "hp": 350, "atk": 55, "spd": 1.5, "rng": 4, "cost": 13,
             "desc": "Shadow + Star"},
    (7, 8): {"name": "Nova",    "body": (180, 60, 180), "eye": WHITE,       "feature": "explosion",
             "hp": 800, "atk": 100, "spd": 1.8, "rng": 5, "cost": 17,
             "desc": "Dragon + Cosmic"},
}

# ─── EMOJI VARIANTS (3 per tier) ──────────────────────────────────────────
# Each tier has 3 visual variants: A (original), B (alternate glow), C (alternate dark)
# Format: [(name, body_color, eye_color, style), ...]
# Only T0 Blob is hand-crafted; T1+ all use procedural generation
TIER_EMOJIS = {
    0: [("Blue Blob",    (100,140,255), WHITE,          "normal"),
        ("Teal Blob",    (80,200,210),  (210,240,255),  "glow"),
        ("Indigo Blob",  (80,70,180),   (180,150,255),  "dark")],
}

# Fusion unit emoji variants
FUSION_EMOJI_NAMES = {
    10000: [("Teal Ooze",     (90,190,180),  WHITE,          "normal"),
            ("Dark Ooze",     (40,110,90),   (180,255,220),  "glow"),
            ("Red Ooze",      (180,80,90),   (255,200,180),  "dark")],
    10001: [("Orange Plasma", (255,180,30),  (200,50,50),    "normal"),
            ("Blue Plasma",   (30,120,255),  (200,220,255),  "glow"),
            ("Green Plasma",  (80,200,80),   (255,255,200),  "dark")],
    10002: [("Dark Eclipse", (40,30,80),    (255,200,50),   "normal"),
            ("Red Eclipse",  (120,40,50),   (255,200,150),  "glow"),
            ("Green Eclipse",(30,80,40),    (200,255,200),  "dark")],
    10003: [("Purple Nova",  (180,60,180),  WHITE,          "normal"),
            ("Blue Nova",    (60,80,200),   (200,220,255),  "glow"),
            ("Red Nova",     (200,60,60),   (255,200,200),  "dark")],
}

_emoji_variant_cache = {}

def get_emoji_variant(tier, variant_index=0):
    """Get emoji variant data (name, body, eye, style) for a tier + variant."""
    variant_index = variant_index % 3
    cache_key = (tier, variant_index)
    if cache_key in _emoji_variant_cache:
        return _emoji_variant_cache[cache_key]
    if tier in TIER_EMOJIS:
        result = TIER_EMOJIS[tier][variant_index]
    elif tier in FUSION_EMOJI_NAMES:
        result = FUSION_EMOJI_NAMES[tier][variant_index]
    else:
        # Procedural: generate 3 variants with hue shifts
        d = get_tier_def(tier)
        base_body = d["body"]
        base_eye = d["eye"]
        r_, g_, b_ = [c/255.0 for c in base_body]
        h, s, v = colorsys.rgb_to_hsv(r_, g_, b_)
        shifts = [0.0, 0.15, -0.12]
        new_h = (h + shifts[variant_index]) % 1.0
        styles = ["normal", "glow", "dark"]
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, s, v)
        new_body = (int(nr*255), int(ng*255), int(nb*255))
        er, eg, eb = [c/255.0 for c in base_eye]
        eh, es_, ev = colorsys.rgb_to_hsv(er, eg, eb)
        new_eh = (eh + shifts[variant_index] * 0.5) % 1.0
        ner, neg, neb = colorsys.hsv_to_rgb(new_eh, es_, ev)
        new_eye = (int(ner*255), int(neg*255), int(neb*255))
        prefixes = ["", "Shimmer ", "Shadow "]
        vname = f"{prefixes[variant_index]}{d['name']}"
        result = (vname, new_body, new_eye, styles[variant_index])
    _emoji_variant_cache[cache_key] = result
    return result

def get_fusion(tier_a, tier_b):
    key = (min(tier_a, tier_b), max(tier_a, tier_b))
    return FUSION_RECIPES.get(key)

# ─── PROCEDURAL TIER GENERATOR ──────────────────────────────────────────────
# Only T0 Blob is hand-crafted; T1+ are all procedurally generated!
HAND_CRAFTED = [
    {"name": "Blob",      "body": (100, 140, 255), "eye": WHITE,         "feature": "none",    "hp": 18,   "atk": 4,   "spd": 1.0, "rng": 2, "cost": 1},
]

NUM_HANDCRAFTED = 1  # Only T0 Blob is hand-crafted; T1+ are all procedural!

# Name generation for infinite tiers
PREFIXES = [
    "Ultra", "Mega", "Hyper", "Supreme", "Eternal", "Omega", "Alpha", "Neo",
    "Prime", "Grand", "Ancient", "Divine", "Infinite", "Cosmic", "Void",
    "Quantum", "Chaos", "Sacred", "Radiant", "Astral", "Eldritch", "Mythic",
    "Legendary", "Celestial", "Primordial", "Apex", "Zenith", "Pinnacle",
    "Titan", "Archon", "Seraph", "Olympian", "Chromatic", "Prismatic",
    "Stellar", "Galactic", "Universal", "Dimensional", "Rift", "Ethereal",
]
SUFFIXES = [
    "Lord", "King", "God", "Beast", "Titan", "Warden", "Guardian", "Sage",
    "Entity", "Construct", "Archon", "Seraph", "Colossus", "Leviathan",
    "Phoenix", "Dragon", "Golem", "Spirit", "Wraith", "Champion",
    "Sovereign", "Emperor", "Oracle", "Prophet", "Mystic", "Elemental",
    "Daemon", "Archangel", "Behemoth", "Hydra", "Kraken", "Sphinx",
]
ERA_NAMES = {
    10: "Era I", 20: "Era II", 30: "Era III", 50: "Era IV",
    75: "Era V", 100: "Era VI",
}
ERA_SUFFIX = {10: "I", 20: "II", 30: "III", 50: "IV", 75: "V", 100: "VI"}

ALL_FEATURES = ["none", "antenna", "spiky", "flame", "crystal", "horns",
                "crown", "wings", "aura", "void", "phoenix", "celestial_wings",
                "transcend"]

# Cache for generated tier defs
_tier_cache = {}

def get_tier_def(tier):
    """Get unit definition for any tier (infinite)."""
    if tier in _tier_cache:
        return _tier_cache[tier]
    # Check fusion IDs first
    if tier in _FUSION_DEFS_BY_ID:
        d = dict(_FUSION_DEFS_BY_ID[tier])
    elif tier < NUM_HANDCRAFTED:
        d = dict(HAND_CRAFTED[tier])
    else:
        d = _generate_tier(tier)
    _tier_cache[tier] = d
    return d

def _generate_tier(t):
    """Procedurally generate a tier definition for t >= 1."""
    # Stats scale exponentially
    hp  = int(18 * (1.52 ** t))
    atk = int(4 * (1.48 ** t))
    spd = min(4.0, 1.0 + t * 0.12)
    rng = min(10, 2 + t // 3)
    cost = t + 1

    # Name generation
    era = ""
    era_num = 0
    for threshold in sorted(ERA_NAMES.keys()):
        if t >= threshold:
            era = ERA_NAMES[threshold]
            era_num = threshold
    # Use deterministic random from tier
    rng_state = random.getstate()
    random.seed(t * 7919 + 1337)
    prefix = PREFIXES[t % len(PREFIXES)]
    suffix = SUFFIXES[(t * 3 + 7) % len(SUFFIXES)]
    if era:
        name = f"{prefix}{suffix} {era}"
    else:
        name = f"{prefix}{suffix}"
    # Make it unique by appending tier number for very high tiers
    if t >= 30:
        name += f" T{t}"

    # Color: HSV rotation for body
    hue = (t * 0.083 + 0.6) % 1.0  # slow rotation
    sat = 0.5 + 0.3 * math.sin(t * 0.5)  # varying saturation
    val = 0.6 + 0.3 * math.cos(t * 0.3)  # varying brightness
    sat = max(0.3, min(1.0, sat))
    val = max(0.4, min(1.0, val))
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    body = (int(r * 255), int(g * 255), int(b * 255))

    # Eye color: complementary
    eye_hue = (hue + 0.5) % 1.0
    er, eg, eb = colorsys.hsv_to_rgb(eye_hue, 0.8, 0.95)
    eye = (int(er * 255), int(eg * 255), int(eb * 255))

    # Feature: cycle through features, combining at higher tiers
    base_feat_idx = t % len(ALL_FEATURES)
    feature = ALL_FEATURES[base_feat_idx]
    # Higher tiers get combo features stored as tuple
    if t >= 20:
        second_feat = ALL_FEATURES[(t + 5) % len(ALL_FEATURES)]
        feature = (feature, second_feat)
    if t >= 50:
        third_feat = ALL_FEATURES[(t + 11) % len(ALL_FEATURES)]
        feature = (feature[0], feature[1], third_feat)

    random.setstate(rng_state)

    d = {
        "name": name, "body": body, "eye": eye, "feature": feature,
        "hp": hp, "atk": atk, "spd": round(spd, 2), "rng": rng, "cost": cost,
        "procedural": True,
    }
    return d

def is_fusion_tier(tier):
    """Check if this tier index corresponds to a fusion result."""
    for key, fusion in FUSION_RECIPES.items():
        if fusion.get("_idx") == tier:
            return True, fusion
    return False, None

# Build fusion tier indices after hand-crafted
# Fusion units use high tier IDs to avoid collision with procedural tiers
FUSION_ID_BASE = 10000
for i, (key, fusion) in enumerate(FUSION_RECIPES.items()):
    fusion["_idx"] = FUSION_ID_BASE + i

# Fusion lookup by tier ID
_FUSION_DEFS_BY_ID = {}
for key, fusion in FUSION_RECIPES.items():
    _FUSION_DEFS_BY_ID[fusion["_idx"]] = {
        "name": fusion["name"], "body": fusion["body"], "eye": fusion["eye"],
        "feature": fusion["feature"], "hp": fusion["hp"], "atk": fusion["atk"],
        "spd": fusion["spd"], "rng": fusion["rng"], "cost": fusion["cost"],
        "is_fusion": True, "fusion_desc": fusion["desc"],
    }

# Unit defs accessor — always use get_tier_def() now
# We keep a flat list only for fusion lookups
FUSION_UNIT_DEFS = []
for key, fusion in FUSION_RECIPES.items():
    FUSION_UNIT_DEFS.append({
        "name": fusion["name"], "body": fusion["body"], "eye": fusion["eye"],
        "feature": fusion["feature"], "hp": fusion["hp"], "atk": fusion["atk"],
        "spd": fusion["spd"], "rng": fusion["rng"], "cost": fusion["cost"],
        "is_fusion": True, "fusion_desc": fusion["desc"], "_fusion_idx": fusion["_idx"],
    })

# Reverse lookup: (tierA, tierB) -> FUSION_UNIT_DEFS entry
_FUSION_BY_PAIR = {}
for (ta, tb), fusion in FUSION_RECIPES.items():
    _FUSION_BY_PAIR[(ta, tb)] = FUSION_UNIT_DEFS[fusion["_idx"] - FUSION_ID_BASE]

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))

def rrect(surf, color, rect, rad=8, bw=0, bc=None):
    r = pygame.Rect(rect)
    if bw > 0 and bc:
        pygame.draw.rect(surf, bc, r, border_radius=rad)
        pygame.draw.rect(surf, color, r.inflate(-bw*2, -bw*2), border_radius=max(0, rad-bw))
    else:
        pygame.draw.rect(surf, color, r, border_radius=rad)

def draw_feature(surf, feat, cx, cy, r, bc, oc, t_time):
    """Draw a single feature on a creature. Handles both string and tuple features."""
    if isinstance(feat, tuple):
        for f in feat:
            draw_feature(surf, f, cx, cy, r, bc, oc, t_time)
        return
    # Single string feature
    if feat == "antenna":
        pygame.draw.line(surf, bc, (cx, cy-r), (cx, cy-r-10), 2)
        pygame.draw.circle(surf, lerp(bc, WHITE, 0.5), (cx, cy-r-12), 4)
    elif feat == "spiky":
        for ad in [0, 60, 120, 180, 240, 300]:
            a = math.radians(ad)
            pygame.draw.circle(surf, lerp(bc, (255,255,100), 0.5),
                               (int(cx+math.cos(a)*(r+6)), int(cy+math.sin(a)*(r+6))), 4)
    elif feat == "flame":
        for dx in [-8, 0, 8]:
            pygame.draw.polygon(surf, (255,160,30), [(cx+dx,cy-r),(cx+dx-5,cy-r-14),(cx+dx+5,cy-r-14)])
            pygame.draw.polygon(surf, (255,240,100), [(cx+dx,cy-r-2),(cx+dx-3,cy-r-10),(cx+dx+3,cy-r-10)])
    elif feat == "crystal":
        for dx in [-12, 0, 12]:
            pygame.draw.polygon(surf, (180,230,255), [(cx+dx,cy-r-2),(cx+dx-4,cy-r-12),(cx+dx+4,cy-r-12)])
    elif feat == "horns":
        for s in [-1, 1]:
            pygame.draw.polygon(surf, (60,30,80), [(cx+s*(r//2),cy-r+4),(cx+s*(r//2+8),cy-r-14),(cx+s*(r//2-4),cy-r+2)])
    elif feat == "crown":
        ccy = cy-r-2
        pygame.draw.polygon(surf, GOLD, [(cx-10,ccy),(cx-12,ccy-14),(cx-5,ccy-8),(cx,ccy-16),(cx+5,ccy-8),(cx+12,ccy-14),(cx+10,ccy)])
        pygame.draw.polygon(surf, (200,170,0), [(cx-10,ccy),(cx-12,ccy-14),(cx-5,ccy-8),(cx,ccy-16),(cx+5,ccy-8),(cx+12,ccy-14),(cx+10,ccy)], 2)
    elif feat == "wings":
        for s in [-1, 1]:
            wx = cx + s*(r+8)
            pts = [(cx+s*r,cy-5),(wx,cy-20),(wx,cy+5),(cx+s*r,cy+5)]
            pygame.draw.polygon(surf, lerp(bc,(255,100,50),0.3), pts)
            pygame.draw.polygon(surf, oc, pts, 2)
    elif feat == "aura":
        for i in range(3):
            ar = r+6+i*4
            if ar > 0:
                as_ = pygame.Surface((ar*2, ar*2), pygame.SRCALPHA)
                pygame.draw.circle(as_, (*bc, max(0, 40-i*12)), (ar, ar), ar)
                surf.blit(as_, (cx-ar, cy-ar))
    elif feat == "void":
        for i in range(5):
            a = math.radians(i * 72 + t_time * 60)
            x1 = cx + math.cos(a) * (r+4)
            y1 = cy + math.sin(a) * (r+4)
            x2 = cx + math.cos(a + 0.5) * (r+14)
            y2 = cy + math.sin(a + 0.5) * (r+14)
            pygame.draw.line(surf, (80, 30, 150), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        pygame.draw.circle(surf, (10, 5, 20), (cx, cy), max(1, r//3))
    elif feat == "phoenix":
        for s in [-1, 1]:
            wx = cx + s * (r + 12)
            pts = [(cx + s*r, cy-5), (wx, cy-25), (int(wx + s*5*math.sin(t_time*4)), cy+5), (cx+s*r, cy+5)]
            pygame.draw.polygon(surf, (255, 140, 20), pts)
            pygame.draw.polygon(surf, (255, 220, 80), pts, 2)
        for i in range(3):
            fr = r - 6 + i * 2
            if fr > 0:
                fs_ = pygame.Surface((fr*2, fr*2), pygame.SRCALPHA)
                pygame.draw.circle(fs_, (255, 200, 50, max(0, 30 - i*8)), (fr, fr), fr)
                surf.blit(fs_, (cx-fr, cy-fr))
    elif feat == "celestial_wings":
        for s in [-1, 1]:
            wx = cx + s * (r + 16)
            pts = [(cx + s*r, cy-8), (wx, cy-28), (int(wx + s*3), cy-10),
                   (int(wx + s*5), cy+8), (cx+s*r, cy+8)]
            pygame.draw.polygon(surf, lerp(bc, (200, 180, 255), 0.3), pts)
            pygame.draw.polygon(surf, (180, 160, 220), pts, 2)
            pygame.draw.circle(surf, GOLD, (int(wx), cy-28), 3)
        for s in [-1, 1]:
            wx = cx + s * (r + 8)
            pts = [(cx + s*(r-2), cy), (wx, cy-15), (wx, cy+5), (cx+s*(r-2), cy+5)]
            pygame.draw.polygon(surf, lerp(bc, WHITE, 0.2), pts)
    elif feat == "transcend":
        for i in range(8):
            a = math.radians(i * 45 + t_time * 45)
            rx = cx + math.cos(a) * (r + 10)
            ry = cy + math.sin(a) * (r + 10)
            pygame.draw.circle(surf, GOLD, (int(rx), int(ry)), 3)
            pygame.draw.circle(surf, (255, 255, 255), (int(rx), int(ry)), 1)
        for i in range(4):
            a1 = math.radians(i * 90 + t_time * 30)
            a2 = math.radians(i * 90 + 30 + t_time * 30)
            x1 = cx + math.cos(a1) * (r + 5)
            y1 = cy + math.sin(a1) * (r + 5)
            x2 = cx + math.cos(a2) * (r + 5)
            y2 = cy + math.sin(a2) * (r + 5)
            pygame.draw.line(surf, (255, 255, 200), (int(x1), int(y1)), (int(x2), int(y2)), 2)
    elif feat == "bubbles":
        for i in range(4):
            bx_ = cx + random.randint(-max(1,r//2), max(1,r//2))
            by_ = cy - max(1,r//2) - random.randint(0, 8)
            br_ = random.randint(2, 4)
            pygame.draw.circle(surf, lerp(bc, WHITE, 0.5), (bx_, by_), br_, 1)
    elif feat == "lightning":
        for s in [-1, 1]:
            x1 = cx + s * r
            y1 = cy - max(1, r//2)
            for j in range(3):
                x2 = x1 + s * random.randint(3, 8)
                y2 = y1 + random.randint(-6, 6)
                pygame.draw.line(surf, (255, 255, 100), (int(x1), int(y1)), (int(x2), int(y2)), 2)
                x1, y1 = x2, y2
    elif feat == "rings":
        for i in range(2):
            rw = r + 8 + i * 5
            rh = max(1, (r + 8 + i * 5) // 2)
            rect = (cx - rw, cy - rh, rw * 2, rh * 2)
            pygame.draw.ellipse(surf, (*lerp(bc, (200, 180, 255), 0.5),), rect, 1)
        a = t_time * 2
        ox = cx + math.cos(a) * (r + 10)
        oy = cy + math.sin(a) * (r + 10) // 2
        pygame.draw.circle(surf, GOLD, (int(ox), int(oy)), 3)
    elif feat == "explosion":
        for i in range(6):
            a = math.radians(i * 60 + t_time * 20)
            x1 = cx + math.cos(a) * r
            y1 = cy + math.sin(a) * r
            x2 = cx + math.cos(a) * (r + 12 + 3 * math.sin(t_time * 5 + i))
            y2 = cy + math.sin(a) * (r + 12 + 3 * math.sin(t_time * 5 + i))
            pygame.draw.line(surf, lerp(bc, WHITE, 0.5), (int(x1), int(y1)), (int(x2), int(y2)), 2)
    elif feat == "halo":
        hw = r + 6
        rect = (cx - hw, cy - r - 12, hw * 2, 8)
        pygame.draw.ellipse(surf, GOLD, rect, 2)
        a = t_time * 3
        sx_ = cx + math.cos(a) * hw
        sy_ = cy - r - 8 + math.sin(a * 2) * 3
        pygame.draw.circle(surf, WHITE, (int(sx_), int(sy_)), 2)

def draw_creature(surf, cx, cy, sz, tier, hp_ratio=1.0, is_enemy=False, flash=0, stars=0, variant_index=0):
    d = get_tier_def(tier)
    vname, vbody, veye, vstyle = get_emoji_variant(tier, variant_index)
    bc = vbody
    ec = veye
    _emoji_style = vstyle
    if is_enemy: bc = lerp(bc, (180, 40, 40), 0.4)
    if flash > 0: bc = lerp(bc, (255, 255, 200), flash)
    r = sz // 2 - 4
    if r < 2: r = 2
    t_time = time.time()

    # Procedural glow for high tiers (T12+)
    if tier >= 12:
        n_rings = min(1 + (tier - 12) // 8, 5)
        pulse = (math.sin(t_time * 2.5 + tier) + 1) * 0.5
        for i in range(n_rings):
            ar = r + 4 + i * 5
            if ar > 0:
                as_ = pygame.Surface((ar*2, ar*2), pygame.SRCALPHA)
                alpha = int((20 + 10 * pulse) * (1 - i / (n_rings + 1)))
                pygame.draw.circle(as_, (*bc, alpha), (ar, ar), ar)
                surf.blit(as_, (cx-ar, cy-ar))

    # Variant glow style aura
    if _emoji_style == "glow" and r > 3:
        gs = pygame.Surface((r*2+16, r*2+16), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*bc, 50), (r+8, r+8), r+6)
        surf.blit(gs, (cx-r-8, cy-r-8))
    # Shadow
    pygame.draw.ellipse(surf, (15, 15, 20), (cx-r, cy+r-4, r*2, 8))
    # Body
    pygame.draw.circle(surf, bc, (cx, cy), r)
    # Highlight (skip for dark style)
    if r > 4 and _emoji_style != "dark":
        hl_str = 0.6 if _emoji_style == "glow" else 0.45
        pygame.draw.circle(surf, lerp(bc, WHITE, hl_str), (cx - r//3, cy - r//3), r//3)
    oc = lerp(bc, BLACK, 0.4)
    pygame.draw.circle(surf, oc, (cx, cy), r, 2)
    # Eyes
    er = max(2, r//4); ey = cy - r//6; es = max(2, r//2)
    for ex in [cx-es, cx+es]:
        pygame.draw.circle(surf, ec, (ex, ey), er)
        pr = max(1, er//2)
        pygame.draw.circle(surf, BLACK, (ex+1, ey+1), pr)
        if pr > 1:
            pygame.draw.circle(surf, WHITE, (ex-1, ey-1), 1)
    # Mouth
    if r > 4:
        my = cy + r//3; mw = r//2
        pygame.draw.arc(surf, BLACK, (cx-mw, my-mw//2, mw*2, mw), 3.14, 6.28, 2)
    # Feature(s) - handles single string or tuple of strings
    feat = d["feature"]
    draw_feature(surf, feat, cx, cy, r, bc, oc, t_time)
    # Tier dots (show up to 6)
    sy = cy + r + 2
    ndots = min(tier + 1, 6) if tier < 12 else 6
    for i in range(ndots):
        sx_ = cx - (ndots-1)*3 + i*6
        pygame.draw.circle(surf, GOLD, (sx_, sy), 2)
    # Procedural tier indicator for high tiers
    if tier >= 12:
        tier_label = f"T{tier}"
        if tier >= 100: tier_label = f"{tier}"
        ft = pygame.font.SysFont("DejaVu Sans", max(8, min(14, 10 + (tier - 12) // 5)))
        t_surf = ft.render(tier_label, True, GOLD)
        surf.blit(t_surf, (cx - t_surf.get_width()//2, cy - r - 14))
    # Fusion indicator
    if d.get("is_fusion") and r > 6:
        pygame.draw.circle(surf, MAGENTA, (cx, cy - r - 6), 5)
        pygame.draw.circle(surf, WHITE, (cx, cy - r - 6), 5, 1)
    # Extra stars
    for i in range(stars):
        sx_ = cx - stars*4 + i*8
        pygame.draw.circle(surf, CYAN, (sx_, cy + r + 2 + (5 if tier <= 5 else -10)), 3)
    # HP bar
    if hp_ratio < 1.0 and r > 3:
        bw_ = r*2; bh_ = 5; bx_ = cx-r; by_ = cy-r-8
        pygame.draw.rect(surf, HP_BG, (bx_, by_, bw_, bh_), border_radius=2)
        fw = max(0, int(bw_ * hp_ratio))
        if fw > 0:
            pygame.draw.rect(surf, HP_FG if hp_ratio > 0.3 else HP_LOW, (bx_, by_, fw, bh_), border_radius=2)

# ─── UNIT CLASS ───────────────────────────────────────────────────────────────
class Unit:
    _nid = 0
    def __init__(self, tier, count=1, variant_index=None):
        Unit._nid += 1
        self.uid = Unit._nid
        self.tier = tier
        self.count = count
        self.star_ups = 0
        d = get_tier_def(tier)
        self.name = d["name"]
        self.base_hp = d["hp"]; self.base_atk = d["atk"]
        self.base_spd = d["spd"]; self.base_rng = d["rng"]
        self.cost = d["cost"]
        self.is_fusion = d.get("is_fusion", False)
        self.fusion_desc = d.get("fusion_desc", "")
        self.variant_index = variant_index if variant_index is not None else random.randint(0, 2)
        self._apply_star_bonuses()
        self.max_hp = self.base_hp; self.hp = self.max_hp
        self.atk = self.base_atk; self.spd = self.base_spd; self.rng = self.base_rng
        self.x = 0.0; self.y = 0.0; self.target_x = 0.0; self.target_y = 0.0
        self.atk_timer = 0.0; self.alive = True; self.flash = 0.0
        self.is_player = True
        self.xp = 0; self.level = 1; self.xp_to_next = 10
        self.xp_mult = 1.0
        self.items = []
        self.kills = 0; self.dmg_dealt = 0
        self.crit_chance = 0.0

    def _apply_star_bonuses(self):
        mult = 1.0 + self.star_ups * 0.25
        d = get_tier_def(self.tier)
        self.base_hp = int(d["hp"] * mult)
        self.base_atk = int(d["atk"] * mult)

    def recalc_stats(self, synergy_mults=None):
        self.max_hp = self.base_hp; self.atk = self.base_atk
        self.spd = self.base_spd; self.rng = self.base_rng
        self.crit_chance = 0.0
        lvl_mult = 1.0 + (self.level - 1) * 0.10
        self.max_hp = int(self.max_hp * lvl_mult)
        self.atk = int(self.atk * lvl_mult)
        for item in self.items:
            s = item["stat"]; v = item["val"]
            if s == "atk": self.atk = int(self.atk * (1 + v))
            elif s == "max_hp": self.max_hp = int(self.max_hp * (1 + v))
            elif s == "spd": self.spd *= (1 + v)
            elif s == "rng": self.rng += int(v)
            elif s == "xp_mult": self.xp_mult += v
            elif s == "crit": self.crit_chance += v
        if synergy_mults:
            for stat, val in synergy_mults.items():
                if stat == "atk": self.atk = int(self.atk * (1 + val))
                elif stat == "max_hp": self.max_hp = int(self.max_hp * (1 + val))
                elif stat == "spd": self.spd *= (1 + val)
                elif stat == "rng": self.rng += int(val)
        if self.hp > self.max_hp: self.hp = self.max_hp

    def gain_xp(self, amount):
        self.xp += int(amount * self.xp_mult)
        leveled = False
        while self.xp >= self.xp_to_next and self.level < 10:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.5)
            leveled = True
        return leveled

    def can_merge_with(self, other):
        if other is None or self is other:
            return False
        # Same tier merge (any tier!)
        if self.tier == other.tier:
            return self.count + other.count <= 3
        # Fusion recipe check (any tier)
        fusion = get_fusion(self.tier, other.tier)
        if fusion:
            return True
        return False

    def can_evolve_merge(self, other):
        return (other is not None and self.tier == other.tier
                and self is not other
                and self.count + other.count <= 3)

    def can_fusion_merge(self, other):
        if other is None or self is other: return False
        return get_fusion(self.tier, other.tier) is not None

    def merge(self, other):
        # Check fusion first (any tier pair)
        fusion = get_fusion(self.tier, other.tier)
        if fusion:
            ftier = fusion["_idx"]
            nu = Unit(ftier)
            nu.is_player = self.is_player
            all_items = self.items + other.items
            if all_items: nu.items = all_items[:3]
            return ("fusion", nu)

        # Same-tier merge — INFINITE EVOLUTION
        total = self.count + other.count
        if total >= 3:
            # Always evolve to next tier (no cap!)
            nu = Unit(self.tier + 1)
            nu.is_player = self.is_player
            nu.star_ups = (self.star_ups + other.star_ups) // 2
            nu._apply_star_bonuses()
            nu.items = list(self.items)
            return ("evolve", nu)
        elif total == 2:
            self.count = 2
            self.star_ups += 1
            self._apply_star_bonuses()
            return ("star", None)
        else:
            self.count = min(total, 3)
            return ("stack", None)

    def take_damage(self, dmg):
        self.hp -= dmg; self.flash = 0.15
        if self.hp <= 0: self.hp = 0; self.alive = False

    def copy_stats(self):
        self.max_hp = self.base_hp; self.hp = self.max_hp
        self.atk = self.base_atk; self.spd = self.base_spd; self.rng = self.base_rng
        self.alive = True; self.atk_timer = 0; self.flash = 0
        self.kills = 0; self.dmg_dealt = 0

    def update(self, dt):
        if self.flash > 0: self.flash -= dt
        dx = self.target_x - self.x; dy = self.target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 2:
            spd = 200 * dt
            if dist < spd: self.x = self.target_x; self.y = self.target_y
            else: self.x += (dx/dist)*spd; self.y += (dy/dist)*spd

    def sell_value(self):
        base = self.cost + self.star_ups * 1 + len(self.items) * 2
        if self.is_fusion: base += 3
        return base

# ─── PARTICLES / PROJECTILES ────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=0.5, sz=4):
        self.x=x; self.y=y; self.color=color; self.vx=vx; self.vy=vy
        self.life=life; self.ml=life; self.sz=sz
    def update(self, dt):
        self.x+=self.vx*dt; self.y+=self.vy*dt; self.vy+=200*dt; self.life-=dt
        return self.life > 0
    def draw(self, surf):
        a = max(0, self.life/self.ml)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), max(1, int(self.sz*a)))

class Projectile:
    def __init__(self, sx, sy, tx, ty, color, spd=500, sz=5):
        self.x=sx; self.y=sy; self.tx=tx; self.ty=ty; self.color=color
        self.spd=spd; self.sz=sz; self.alive=True
        dx=tx-sx; dy=ty-sy; d=math.sqrt(dx*dx+dy*dy)
        if d > 0: self.vx=(dx/d)*spd; self.vy=(dy/d)*spd
        else: self.alive = False
    def update(self, dt):
        self.x+=self.vx*dt; self.y+=self.vy*dt
        if math.sqrt((self.tx-self.x)**2+(self.ty-self.y)**2) < 10: self.alive = False
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.sz)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.sz//2)

class FloatText:
    def __init__(self, x, y, text, color, life=1.0, font=None):
        self.x=x; self.y=y; self.text=text; self.color=color
        self.life=life; self.ml=life; self.font=font
    def update(self, dt):
        self.y -= 40 * dt; self.life -= dt
        return self.life > 0
    def draw(self, surf):
        a = max(0, min(255, int(255 * self.life / self.ml)))
        t = self.font.render(self.text, True, self.color)
        t.set_alpha(a)
        surf.blit(t, (int(self.x) - t.get_width()//2, int(self.y)))

# ─── GAME ────────────────────────────────────────────────────────────────────
class Game:
    HS_FILE = ".emoji_autobattler_hs"

    def __init__(self):
        self.scr = pygame.display.set_mode((SW, SH))
        pygame.display.set_caption("Emoji AutoBattler v5.1 - Procedural T1+!")
        self.clk = pygame.time.Clock()
        self.fb = pygame.font.SysFont("DejaVu Sans", 28, bold=True)
        self.fm = pygame.font.SysFont("DejaVu Sans", 20)
        self.fs = pygame.font.SysFont("DejaVu Sans", 15)
        self.fx = pygame.font.SysFont("DejaVu Sans", 12)
        self.ft = pygame.font.SysFont("DejaVu Sans", 36, bold=True)
        self.fxs = pygame.font.SysFont("DejaVu Sans", 11)
        self.highscore = self._load_hs()
        self.speed_mult = 1
        self.highest_tier_seen = 0
        self.reset()

    def reset(self):
        self.gold = 10; self.rnd = 0; self.phase = "prep"
        self.score = 0; self.lives = 3; self.max_lives = 5
        self.board = [[None]*BCOLS for _ in range(BROWS)]
        self.bench = [None]*BENCH_N; self.shop = []
        self.enemies = []; self.particles = []; self.projs = []; self.floats = []
        self.drag = None; self.drag_src = None; self.drag_xy = (0,0)
        self.hover = None; self.tooltip_unit = None
        self.bt = 0.0; self.bt_max = 30.0; self.bres = None; self.rt = 0.0
        self.wins=0; self.losses=0; self.streak=0; self.best_streak=0
        self.reroll_cost = 2; self.last_reward = 0
        self.free_reroll = False
        self.active_synergies = {}
        self.merge_highlights = []
        self._gen_shop()

    # ── SHOP ────────────────────────────────────────────────────────────────
    def _gen_shop(self):
        self.shop = []
        # Shop offers tiers 0 through a max based on round progression
        # T0 is hand-crafted, T1+ are procedural — more variety each round!
        mt = min(self.rnd // 3 + 1, 15)
        w = [max(1, 10 - t*2) for t in range(mt+1)]
        s = sum(w); w = [x/s for x in w]
        for _ in range(SHOP_N):
            roll = random.random(); cum = 0; tier = 0
            for t, wt in enumerate(w):
                cum += wt
                if roll <= cum: tier = t; break
            self.shop.append(Unit(tier))

    def _buy(self, si):
        if si >= len(self.shop) or not self.shop[si]: return False
        u = self.shop[si]
        if self.gold < u.cost: return False
        for i in range(BENCH_N):
            if self.bench[i] is None:
                self.gold -= u.cost; self.bench[i] = u; self.shop[si] = None
                self._particles(SX+si*(SCS+6)+SCS//2, SY+SCS//2, GOLD, 8)
                return True
        return False

    def _sell(self, pt, idx, row=None):
        u = self.bench[idx] if pt == "bench" else (self.board[row][idx] if pt == "board" else None)
        if not u: return
        val = u.sell_value()
        px = (BNX if pt=="bench" else BX) + idx*CT + CS//2
        py = (BNY if pt=="bench" else BY+row*CT) + CS//2
        self.gold += val; self.floats.append(FloatText(px, py-10, f"+{val}g", GOLD, 1.2, self.fm))
        self._particles(px, py, GOLD, 10)
        if pt == "bench": self.bench[idx] = None
        else: self.board[row][idx] = None

    # ── PLACEMENT / MERGE ──────────────────────────────────────────────────
    def _slot_at(self, mx, my):
        for i in range(BENCH_N):
            rx, ry = BNX+i*CT, BNY
            if rx <= mx < rx+CS and ry <= my < ry+CS: return ("bench", i, None)
        for r in range(BROWS):
            for c in range(BCOLS):
                rx, ry = BX+c*CT, BY+r*CT
                if rx <= mx < rx+CS and ry <= my < ry+CS: return ("board", c, r)
        return None

    def _shop_at(self, mx, my):
        for i in range(SHOP_N):
            rx, ry = SX+i*(SCS+6), SY
            if rx <= mx < rx+SCS and ry <= my < ry+SCS: return i
        return None

    def _try_place(self, unit, pt, idx, row=None):
        tgt = self.bench[idx] if pt == "bench" else self.board[row][idx]
        if tgt is None:
            if pt == "bench": self.bench[idx] = unit
            else: self.board[row][idx] = unit
            return True
        elif unit.can_merge_with(tgt):
            result, new_u = tgt.merge(unit)
            px = (BNX if pt=="bench" else BX) + idx*CT + CS//2
            py = (BNY if pt=="bench" else BY+row*CT) + CS//2
            if result == "evolve":
                if pt == "bench": self.bench[idx] = new_u
                else: self.board[row][idx] = new_u
                self._track_tier(new_u.tier)
                self._particles(px, py, get_tier_def(new_u.tier)["body"], 30)
                self._particles(px, py, GOLD, 20)
                self.floats.append(FloatText(px, py-20, f"EVOLVE -> {new_u.name}!", GOLD, 1.5, self.fm))
                if new_u.tier >= 12:
                    self.floats.append(FloatText(px, py-40, f"TIER {new_u.tier}!", (255,200,100), 1.5, self.fs))
                self._check_cascade_merge(pt, idx, row)
            elif result == "fusion":
                if pt == "bench": self.bench[idx] = new_u
                else: self.board[row][idx] = new_u
                self._particles(px, py, MAGENTA, 25)
                self._particles(px, py, get_tier_def(new_u.tier)["body"], 20)
                self.floats.append(FloatText(px, py-20, f"FUSION -> {new_u.name}!", MAGENTA, 1.5, self.fm))
            elif result == "star":
                self.floats.append(FloatText(px, py-20, f"Star Up! (+{tgt.star_ups})", CYAN, 1.2, self.fm))
                self._particles(px, py, CYAN, 15)
            else:
                self._particles(px, py, get_tier_def(tgt.tier)["body"], 8)
            return True
        return False

    def _track_tier(self, tier):
        if tier > self.highest_tier_seen:
            self.highest_tier_seen = tier
            self.score += tier * 10  # bonus score for reaching new tiers

    def _check_cascade_merge(self, pt, idx, row):
        u = self.bench[idx] if pt == "bench" else self.board[row][idx]
        if not u: return
        candidates = []
        for bi in range(BENCH_N):
            if self.bench[bi] and self.bench[bi] is not u:
                if u.can_evolve_merge(self.bench[bi]):
                    candidates.append(("bench", bi, None))
        for br in range(BROWS):
            for bc in range(BCOLS):
                if self.board[br][bc] and self.board[br][bc] is not u:
                    if u.can_evolve_merge(self.board[br][bc]):
                        candidates.append(("board", bc, br))
        if not candidates: return
        cpt, cidx, crow = candidates[0]
        src_u = self.bench[cidx] if cpt == "bench" else self.board[crow][cidx]
        if src_u is None: return
        result, new_u = u.merge(src_u)
        if result in ("evolve", "star"):
            px = (BNX if pt=="bench" else BX) + idx*CT + CS//2
            py = (BNY if pt=="bench" else BY+row*CT) + CS//2
            if result == "evolve":
                if pt == "bench": self.bench[idx] = new_u
                else: self.board[row][idx] = new_u
                self._track_tier(new_u.tier)
                self._particles(px, py, GOLD, 25)
                self.floats.append(FloatText(px, py-20, f"CHAIN -> T{new_u.tier} {new_u.name}!", GOLD, 1.5, self.fs))
                if cpt == "bench": self.bench[cidx] = None
                else: self.board[crow][cidx] = None
                self._check_cascade_merge(pt, idx, row)
            elif result == "star":
                if cpt == "bench": self.bench[cidx] = None
                else: self.board[crow][cidx] = None

    def _auto_merge(self, full=False):
        merged = 0
        changed = True
        iterations = 0
        while changed and iterations < 50:
            changed = False; iterations += 1
            positions = []
            for i in range(BENCH_N):
                if self.bench[i]: positions.append(("bench", i, None, self.bench[i]))
            if full:
                for r in range(BROWS):
                    for c in range(BCOLS):
                        if self.board[r][c]: positions.append(("board", c, r, self.board[r][c]))
            # 3-count same-tier -> evolve
            for i in range(len(positions)):
                if changed: break
                for j in range(i+1, len(positions)):
                    pti, idxi, ri, ui = positions[i]
                    ptj, idxj, rj, uj = positions[j]
                    if ui is None or uj is None: continue
                    if ui.can_evolve_merge(uj) and ui.count + uj.count >= 3:
                        result, new_u = ui.merge(uj)
                        px = (BNX if pti=="bench" else BX) + idxi*CT + CS//2
                        py = (BNY if pti=="bench" else BY+ri*CT) + CS//2
                        if pti == "bench": self.bench[idxi] = new_u
                        else: self.board[ri][idxi] = new_u
                        if ptj == "bench": self.bench[idxj] = None
                        else: self.board[rj][idxj] = None
                        self._track_tier(new_u.tier)
                        self._particles(px, py, GOLD, 15)
                        lbl = f"Auto -> T{new_u.tier}!" if new_u.tier >= 12 else f"Auto -> {new_u.name}!"
                        self.floats.append(FloatText(px, py-20, lbl, GOLD, 1.2, self.fs))
                        changed = True; merged += 1; break
            if changed: continue
            # Fusion
            for i in range(len(positions)):
                if changed: break
                for j in range(i+1, len(positions)):
                    pti, idxi, ri, ui = positions[i]
                    ptj, idxj, rj, uj = positions[j]
                    if ui is None or uj is None: continue
                    if ui.can_fusion_merge(uj):
                        result, new_u = ui.merge(uj)
                        px = (BNX if pti=="bench" else BX) + idxi*CT + CS//2
                        py = (BNY if pti=="bench" else BY+ri*CT) + CS//2
                        if pti == "bench": self.bench[idxi] = new_u
                        else: self.board[ri][idxi] = new_u
                        if ptj == "bench": self.bench[idxj] = None
                        else: self.board[rj][idxj] = None
                        self._particles(px, py, MAGENTA, 20)
                        self.floats.append(FloatText(px, py-20, f"Auto Fusion!", MAGENTA, 1.2, self.fs))
                        changed = True; merged += 1; break
            if changed: continue
            # 2-count star-ups
            for i in range(len(positions)):
                if changed: break
                for j in range(i+1, len(positions)):
                    pti, idxi, ri, ui = positions[i]
                    ptj, idxj, rj, uj = positions[j]
                    if ui is None or uj is None: continue
                    if ui.can_evolve_merge(uj):
                        result, _ = ui.merge(uj)
                        if ptj == "bench": self.bench[idxj] = None
                        else: self.board[rj][idxj] = None
                        px = (BNX if pti=="bench" else BX) + idxi*CT + CS//2
                        py = (BNY if pti=="bench" else BY+ri*CT) + CS//2
                        self._particles(px, py, CYAN, 10)
                        changed = True; merged += 1; break
        return merged

    def _update_merge_highlights(self):
        self.merge_highlights = []
        if self.phase != "prep": return
        all_units = []
        for i in range(BENCH_N):
            if self.bench[i]: all_units.append(("bench", i, None, self.bench[i]))
        for r in range(BROWS):
            for c in range(BCOLS):
                if self.board[r][c]: all_units.append(("board", c, r, self.board[r][c]))
        for i in range(len(all_units)):
            for j in range(i+1, len(all_units)):
                if all_units[i][3].can_merge_with(all_units[j][3]):
                    self.merge_highlights.append((all_units[i][0], all_units[i][1], all_units[i][2]))
                    self.merge_highlights.append((all_units[j][0], all_units[j][1], all_units[j][2]))

    # ── SYNERGIES ──────────────────────────────────────────────────────────
    def _calc_synergies(self):
        board_units = self._board_units()
        families = {}
        for u in board_units:
            fam = unit_family(u.tier)
            if fam: families[fam] = families.get(fam, 0) + 1
        self.active_synergies = {}
        for fam, count in families.items():
            if count >= 3:
                info = SYNERGIES[fam]
                self.active_synergies[fam] = {
                    "count": count, "stat": info["stat"],
                    "val": info["val"], "color": info["color"],
                    "desc": info["desc"], "bonus": info["bonus"]
                }

    def _synergy_mults(self):
        m = {}
        for fam, info in self.active_synergies.items():
            m[info["stat"]] = m.get(info["stat"], 0) + info["val"]
        return m

    # ── BATTLE ─────────────────────────────────────────────────────────────
    def _start_battle(self):
        if self.phase != "prep": return
        interest = min(self.gold // 10, 5)
        if interest > 0:
            self.gold += interest
            self.floats.append(FloatText(120, 55, f"+{interest}g interest", GOLD, 1.5, self.fs))
        if self.free_reroll: self.free_reroll = False
        self.phase = "battle"; self.bt = 0; self.bres = None; self.rt = 0
        self.rnd += 1; self.projs.clear(); self.particles.clear(); self.floats.clear()
        self._calc_synergies()
        sm = self._synergy_mults()
        for r in range(BROWS):
            for c in range(BCOLS):
                u = self.board[r][c]
                if u:
                    u.copy_stats(); u.is_player = True
                    u.recalc_stats(sm)
                    u.x = BX+c*CT+CS//2; u.y = BY+r*CT+CS//2
                    u.target_x = u.x; u.target_y = u.y
        self.enemies = self._gen_enemies()

    def _gen_enemies(self):
        ne = min(3 + self.rnd // 2, 12)
        met = min(self.rnd // 3, 15)
        enemies = []
        for i in range(ne):
            tier = 0
            if met > 0:
                if random.random() < 0.3: tier = min(random.randint(0, met), 15)
                else: tier = random.randint(0, max(0, met-1))
            e = Unit(tier); e.is_player = False; e.copy_stats()
            scale = 1.0 + (self.rnd - 1) * 0.12
            e.max_hp = int(e.max_hp * scale); e.hp = e.max_hp
            e.atk = int(e.atk * scale)
            eax = BX + BCOLS*CT + 40; eaw = IX - eax - 20
            cpr = max(1, eaw // (CS + 8))
            er = i % BROWS; ec = i // BROWS
            e.x = float(eax + (ec % cpr)*(CS+8) + CS//2)
            e.y = float(BY + er*CT + CS//2)
            e.target_x = e.x; e.target_y = e.y
            enemies.append(e)
        return enemies

    def _board_units(self):
        return [self.board[r][c] for r in range(BROWS) for c in range(BCOLS) if self.board[r][c]]

    def _update_battle(self, dt):
        if self.phase != "battle": return
        dt *= self.speed_mult
        self.bt += dt
        pa = [u for u in self._board_units() if u.alive]
        ea = [e for e in self.enemies if e.alive]
        if not ea: self._end_battle("win"); return
        if not pa: self._end_battle("lose"); return
        if self.bt >= self.bt_max:
            self._end_battle("win" if sum(u.hp for u in pa) >= sum(e.hp for e in ea) else "lose")
            return
        for u in pa:
            u.update(dt); u.atk_timer -= dt
            if u.atk_timer <= 0:
                cl = self._closest(u, ea)
                if cl:
                    rng_px = u.rng * CT
                    dx=cl.x-u.x; dy=cl.y-u.y; dist=math.sqrt(dx*dx+dy*dy)
                    if dist <= rng_px:
                        dmg = u.atk
                        crit = random.random() < u.crit_chance
                        if crit:
                            dmg = int(dmg * 2.0)
                            self.floats.append(FloatText(cl.x, cl.y-20, "CRIT!", ORANGE, 0.6, self.fs))
                        if not crit:
                            for it in u.items:
                                if it["stat"] == "atk" and random.random() < 0.15:
                                    dmg = int(dmg * 1.5)
                                    self.floats.append(FloatText(cl.x, cl.y-20, "CRIT!", ORANGE, 0.6, self.fs))
                                    break
                        cl.take_damage(dmg); u.atk_timer = 1.0 / u.spd
                        u.dmg_dealt += dmg
                        d = get_tier_def(u.tier)
                        self.projs.append(Projectile(u.x, u.y, cl.x, cl.y, d["body"], 400, 4))
                        if not cl.alive:
                            u.kills += 1
                            u.gain_xp(3 + cl.tier * 2)
                            self._particles(cl.x, cl.y, get_tier_def(cl.tier)["body"], 15)
                    else:
                        if dist > 0:
                            mv = 150*dt; ma = min(mv, max(0, dist-rng_px+20))
                            u.target_x = u.x + (dx/dist)*ma; u.target_y = u.y + (dy/dist)*ma
        for e in ea:
            e.update(dt); e.atk_timer -= dt
            if e.atk_timer <= 0:
                cl = self._closest(e, pa)
                if cl:
                    rng_px = e.rng * CT
                    dx=cl.x-e.x; dy=cl.y-e.y; dist=math.sqrt(dx*dx+dy*dy)
                    if dist <= rng_px:
                        cl.take_damage(e.atk); e.atk_timer = 1.0 / e.spd
                        self.projs.append(Projectile(e.x, e.y, cl.x, cl.y, RED, 400, 4))
                        if not cl.alive:
                            self._particles(cl.x, cl.y, get_tier_def(cl.tier)["body"], 15)
                    else:
                        if dist > 0:
                            mv=120*dt; ma=min(mv, max(0, dist-rng_px+20))
                            e.target_x=e.x+(dx/dist)*ma; e.target_y=e.y+(dy/dist)*ma
        for p in self.projs: p.update(dt)
        self.projs = [p for p in self.projs if p.alive]

    @staticmethod
    def _closest(unit, targets):
        cl=None; cd=float('inf')
        for t in targets:
            d = math.sqrt((t.x-unit.x)**2+(t.y-unit.y)**2)
            if d < cd: cd=d; cl=t
        return cl

    def _end_battle(self, result):
        self.phase = "prep"; self.bres = result; self.rt = 2.0
        if result == "win":
            self.wins += 1; self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            reward = 3 + self.streak + self.rnd
            self.gold += reward; self.last_reward = reward
            self.score += 10 + self.rnd*2 + self.streak*5
            if random.random() < 0.35 + self.rnd * 0.02:
                self._give_item()
            xp_gain = 2 + self.rnd
            for u in self._board_units():
                if u.alive:
                    if u.gain_xp(xp_gain):
                        px = u.x if u.x > 0 else BX + 100
                        self.floats.append(FloatText(px, (u.y if u.y > 0 else 200) - 30,
                                                      f"Lv.{u.level}!", GREEN, 1.5, self.fs))
        else:
            self.losses += 1; self.streak = 0; self.last_reward = 0
            self.score += max(1, self.rnd)
            self.lives -= 1; self.free_reroll = True
            if self.lives <= 0:
                self._upd_hs(); self.phase = "gameover"; return
            if self.rnd > 0 and self.rnd % 10 == 0 and self.lives < self.max_lives:
                self.lives = min(self.lives + 1, self.max_lives)
        for u in self._board_units(): u.copy_stats()
        self.enemies.clear(); self.projs.clear()
        self._gen_shop(); self._upd_hs()

    def _give_item(self):
        bu = self._board_units()
        if not bu: return
        target = random.choice(bu)
        if len(target.items) >= 3:
            target = random.choice([u for u in bu if len(u.items) < 3] or [bu[0]])
        item = random.choice(ITEMS).copy()
        target.items.append(item)
        px = target.x if target.x > 0 else BX + 200
        py = target.y if target.y > 0 else 250
        self.floats.append(FloatText(px, py - 30, f"+{item['name']}!", item["color"], 1.8, self.fm))

    # ── HIGHSCORE ──────────────────────────────────────────────────────────
    def _load_hs(self):
        try:
            import os
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.HS_FILE)) as f:
                return int(f.read().strip())
        except: return 0
    def _save_hs(self):
        try:
            import os
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.HS_FILE), 'w') as f:
                f.write(str(self.highscore))
        except: pass
    def _upd_hs(self):
        if self.score > self.highscore: self.highscore = self.score; self._save_hs()

    # ── PARTICLES ──────────────────────────────────────────────────────────
    def _particles(self, x, y, color, n=10):
        for _ in range(n):
            a=random.uniform(0,6.28); s=random.uniform(50,200)
            self.particles.append(Particle(x,y,color,math.cos(a)*s,math.sin(a)*s-100,
                                           random.uniform(0.3,0.8),random.randint(2,6)))

    # ── EVENTS ─────────────────────────────────────────────────────────────
    def handle(self, ev):
        if ev.type == pygame.QUIT: return False
        if self.phase == "gameover":
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN: self.reset()
            elif ev.type == pygame.MOUSEBUTTONDOWN: self.reset()
            return True
        mx, my = pygame.mouse.get_pos()
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 1:
                if self.phase == "prep":
                    br = pygame.Rect(IX+10, IY+10, 140, 36)
                    if br.collidepoint(mx, my): self._start_battle(); return True
                    rr = pygame.Rect(IX+160, IY+10, 110, 36)
                    if rr.collidepoint(mx, my):
                        cost = 0 if self.free_reroll else self.reroll_cost
                        if self.gold >= cost:
                            self.gold -= cost; self._gen_shop(); self.free_reroll = False
                        return True
                    amr = pygame.Rect(IX+280, IY+10, 110, 36)
                    if amr.collidepoint(mx, my):
                        c = self._auto_merge(full=False)
                        if c > 0: self.floats.append(FloatText(IX+335, IY+52, f"{c} merges!", CYAN, 1.0, self.fs))
                        return True
                    famr = pygame.Rect(IX+400, IY+10, 130, 36)
                    if famr.collidepoint(mx, my):
                        c = self._auto_merge(full=True)
                        if c > 0: self.floats.append(FloatText(IX+465, IY+52, f"{c} full merges!", MAGENTA, 1.0, self.fs))
                        return True
                    si = self._shop_at(mx, my)
                    if si is not None and self.shop[si]: self._buy(si); return True
                slot = self._slot_at(mx, my)
                if slot and self.phase == "prep":
                    pt, idx, row = slot
                    u = self.bench[idx] if pt == "bench" else self.board[row][idx]
                    if u:
                        self.drag = u; self.drag_src = slot; self.drag_xy = (mx, my)
                        if pt == "bench": self.bench[idx] = None
                        else: self.board[row][idx] = None
                        return True
            elif ev.button == 3:
                if self.phase == "prep":
                    slot = self._slot_at(mx, my)
                    if slot: self._sell(*slot)
        elif ev.type == pygame.MOUSEBUTTONUP:
            if ev.button == 1 and self.drag:
                slot = self._slot_at(mx, my)
                placed = False
                if slot and self.phase == "prep":
                    placed = self._try_place(self.drag, *slot)
                if not placed:
                    pt, idx, row = self.drag_src
                    if pt == "bench": self.bench[idx] = self.drag
                    else: self.board[row][idx] = self.drag
                self.drag = None; self.drag_src = None
        elif ev.type == pygame.MOUSEMOTION:
            if self.drag: self.drag_xy = (mx, my)
            self.hover = self._slot_at(mx, my)
            self.tooltip_unit = None
            if self.phase == "prep" and not self.drag:
                slot = self._slot_at(mx, my)
                if slot:
                    pt, idx, row = slot
                    u = self.bench[idx] if pt == "bench" else (self.board[row][idx] if pt == "board" else None)
                    if u: self.tooltip_unit = u
                si = self._shop_at(mx, my)
                if si is not None and self.shop and self.shop[si]:
                    self.tooltip_unit = self.shop[si]
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE and self.phase == "prep": self._start_battle()
            elif ev.key == pygame.K_r and self.phase == "prep":
                cost = 0 if self.free_reroll else self.reroll_cost
                if self.gold >= cost: self.gold -= cost; self._gen_shop(); self.free_reroll = False
            elif ev.key == pygame.K_s and self.phase == "prep":
                slot = self._slot_at(mx, my)
                if slot: self._sell(*slot)
            elif ev.key == pygame.K_a and self.phase == "prep":
                c = self._auto_merge(full=False)
                if c > 0: self.floats.append(FloatText(400, 650, f"{c} auto-merges!", CYAN, 1.2, self.fm))
            elif ev.key == pygame.K_f and self.phase == "prep":
                c = self._auto_merge(full=True)
                if c > 0: self.floats.append(FloatText(400, 650, f"{c} full merges!", MAGENTA, 1.2, self.fm))
            elif ev.key == pygame.K_TAB and self.phase in ("prep", "battle"):
                self.speed_mult = self.speed_mult % 3 + 1
                self.floats.append(FloatText(SW//2, SH//2, f"Speed: {self.speed_mult}x", WHITE, 1.0, self.fb))
        return True

    # ── UPDATE ─────────────────────────────────────────────────────────────
    def update(self, dt):
        if self.phase == "battle": self._update_battle(dt)
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floats = [f for f in self.floats if f.update(dt)]
        if self.rt > 0: self.rt -= dt
        if self.phase == "prep":
            self._calc_synergies()
            self._update_merge_highlights()

    # ── DRAWING ────────────────────────────────────────────────────────────
    def draw(self):
        self.scr.fill(BG)
        self._draw_header()
        self._draw_board()
        self._draw_bench()
        self._draw_shop()
        self._draw_info()
        if self.phase == "battle": self._draw_battle()
        elif self.phase == "gameover": self._draw_go()
        if self.bres and self.rt > 0: self._draw_result()
        for p in self.particles: p.draw(self.scr)
        for f in self.floats: f.draw(self.scr)
        if self.tooltip_unit and not self.drag: self._draw_tooltip()
        if self.drag:
            draw_creature(self.scr, int(self.drag_xy[0]), int(self.drag_xy[1]),
                         CS-8, self.drag.tier, 1.0, False, 0.3, self.drag.star_ups, self.drag.variant_index)
            self._draw_merge_preview()
        pygame.display.flip()

    def _draw_merge_preview(self):
        if not self.hover: return
        pt, idx, row = self.hover
        tgt = self.bench[idx] if pt == "bench" else (self.board[row][idx] if pt == "board" else None)
        if not tgt or not self.drag.can_merge_with(tgt): return
        hx = (BNX if pt=="bench" else BX) + idx*CT
        hy = (BNY if pt=="bench" else BY+row*CT)
        if self.drag.can_fusion_merge(tgt):
            fusion = get_fusion(self.drag.tier, tgt.tier)
            if fusion:
                s = pygame.Surface((CS, CS), pygame.SRCALPHA); s.fill((*SLOT_FUSION, 140))
                self.scr.blit(s, (hx, hy))
                ft = self.fx.render(f"FUSION: {fusion['name']}!", True, MAGENTA)
                self.scr.blit(ft, (hx+CS//2-ft.get_width()//2, hy+CS+2))
                return
        total = self.drag.count + tgt.count
        if total >= 3:
            next_tier = tgt.tier + 1
            nd = get_tier_def(next_tier)
            s = pygame.Surface((CS, CS), pygame.SRCALPHA); s.fill((*SLOT_MERGE2, 120))
            self.scr.blit(s, (hx, hy))
            label = f"-> {nd['name']}"
            if next_tier >= 12: label = f"-> T{next_tier} {nd['name']}"
            nt_text = self.fx.render(label, True, GOLD)
            self.scr.blit(nt_text, (hx+CS//2-nt_text.get_width()//2, hy+CS+2))
        elif total == 2:
            s = pygame.Surface((CS, CS), pygame.SRCALPHA); s.fill((*SLOT_MERGE, 120))
            self.scr.blit(s, (hx, hy))
            st = self.fx.render(f"Star Up! {total}/3", True, CYAN)
            self.scr.blit(st, (hx+CS//2-st.get_width()//2, hy+CS+2))
        else:
            ct_text = self.fx.render(f"{total}/3", True, GOLD)
            self.scr.blit(ct_text, (hx+CS//2-ct_text.get_width()//2, hy+CS//2-ct_text.get_height()//2))

    def _draw_header(self):
        t = self.ft.render("Emoji AutoBattler v5.1 - Procedural T1+!", True, TXT)
        self.scr.blit(t, (20, 8))
        self.scr.blit(self.fb.render(f"Gold: {self.gold}", True, GOLD), (20, 52))
        self.scr.blit(self.fm.render(f"Round: {self.rnd}", True, TXT), (20, 85))
        self.scr.blit(self.fm.render(f"Score: {self.score}", True, (180, 140, 255)), (20, 110))
        hsc = GOLD if self.score >= self.highscore and self.score > 0 else DIM
        self.scr.blit(self.fs.render(f"Best: {self.highscore}", True, hsc), (180, 113))
        if self.phase == "prep":
            ints = min(self.gold // 10, 5)
            if ints > 0:
                self.scr.blit(self.fxs.render(f"(+{ints}g interest)", True, (120, 180, 120)), (310, 113))
        sc = [GREEN, GOLD, RED][self.speed_mult - 1]
        self.scr.blit(self.fs.render(f"Speed: {self.speed_mult}x [TAB]", True, sc), (20, 133))
        # Highest tier
        if self.highest_tier_seen > 0:
            ht_color = GOLD if self.highest_tier_seen >= 12 else DIM
            ht_name = get_tier_def(self.highest_tier_seen)["name"]
            ht_label = f"Max Tier: T{self.highest_tier_seen} {ht_name}"
            self.scr.blit(self.fs.render(ht_label, True, ht_color), (200, 133))
        # Lives
        lx, ly = 200, 85
        for i in range(self.max_lives):
            hx = lx + i * 22
            if i < self.lives:
                pygame.draw.circle(self.scr, RED, (hx, ly+6), 7)
                pygame.draw.circle(self.scr, RED, (hx+9, ly+6), 7)
                pygame.draw.polygon(self.scr, RED, [(hx-7,ly+8),(hx+16,ly+8),(hx+4,ly+18)])
            else:
                pygame.draw.circle(self.scr, (60,30,30), (hx, ly+6), 7, 2)
                pygame.draw.circle(self.scr, (60,30,30), (hx+9, ly+6), 7, 2)
                pygame.draw.polygon(self.scr, (60,30,30), [(hx-7,ly+8),(hx+16,ly+8),(hx+4,ly+18)], 2)
        if self.phase == "battle":
            self.scr.blit(self.fb.render("BATTLE!", True, RED), (400, 52))
            self.scr.blit(self.fm.render(f"Time: {self.bt:.1f}s", True, DIM), (400, 82))
            pa = sum(1 for u in self._board_units() if u.alive)
            ea = sum(1 for e in self.enemies if e.alive)
            self.scr.blit(self.fs.render(f"Allies: {pa}  Enemies: {ea}", True, DIM), (400, 110))
        elif self.phase == "gameover":
            self.scr.blit(self.fb.render("GAME OVER", True, GOLD), (400, 52))
        else:
            self.scr.blit(self.fm.render("PREP - Place & Merge!", True, GREEN), (400, 52))
            ne = min(3 + (self.rnd+1)//2, 12)
            diff = "Easy" if self.rnd < 5 else ("Medium" if self.rnd < 12 else ("Hard" if self.rnd < 20 else "INSANE"))
            dc = GREEN if self.rnd < 5 else (GOLD if self.rnd < 12 else (ORANGE if self.rnd < 20 else RED))
            self.scr.blit(self.fs.render(f"Next: ~{ne} enemies [{diff}]", True, dc), (400, 78))
            if self.free_reroll:
                self.scr.blit(self.fs.render("FREE REROLL!", True, CYAN), (400, 98))
            if self.merge_highlights:
                self.scr.blit(self.fxs.render(f"{len(self.merge_highlights)//2} merge pairs available", True, (120,180,120)), (400, 116))
        self.scr.blit(self.fs.render(f"W:{self.wins} L:{self.losses} Streak:{self.best_streak}", True, DIM), (620, 133))

    def _draw_unit_slot(self, x, y, unit, show_count=True, glow=False):
        if unit is None or unit is self.drag: return
        if glow:
            t = time.time()
            pulse = (math.sin(t * 3) + 1) * 0.5
            gs = pygame.Surface((CS, CS), pygame.SRCALPHA)
            c = (160, 60, 160, int(20 + 15 * pulse)) if unit.is_fusion else (60, 100, 60, int(15 + 10 * pulse))
            gs.fill(c)
            self.scr.blit(gs, (x, y))
        cx, cy = x + CS//2, y + CS//2
        draw_creature(self.scr, cx, cy, CS-8, unit.tier, 1.0, False, 0, unit.star_ups, unit.variant_index)
        if show_count and unit.count > 1:
            bx_, by_ = x+CS-12, y+4
            pygame.draw.circle(self.scr, (50,50,200), (bx_, by_), 10)
            self.scr.blit(self.fx.render(str(unit.count), True, WHITE),
                         (bx_ - self.fx.size(str(unit.count))[0]//2, by_ - self.fx.size(str(unit.count))[1]//2))
        if unit.count < 3:
            bw = CS - 8; bh = 3; bx_ = x + 4; by_ = y + CS - 6
            pygame.draw.rect(self.scr, (30,30,40), (bx_, by_, bw, bh), border_radius=1)
            fw = int(bw * unit.count / 3)
            if fw > 0:
                c = CYAN if unit.count == 2 else (80,80,100)
                pygame.draw.rect(self.scr, c, (bx_, by_, fw, bh), border_radius=1)
        if unit.level > 1:
            lt = self.fxs.render(f"Lv{unit.level}", True, GREEN)
            self.scr.blit(lt, (x+2, y+CS-16))
        if unit.items:
            for i, it in enumerate(unit.items):
                ix_ = x + 3 + i * 8
                iy_ = y + CS - 18 if unit.level <= 1 else y + CS - 30
                pygame.draw.circle(self.scr, it["color"], (ix_, iy_), 3)
        if unit.is_fusion:
            self.scr.blit(self.fxs.render("F", True, MAGENTA), (x+2, y+2))
        # Variant indicator (A/B/C)
        vlabel = ["A", "B", "C"][unit.variant_index % 3]
        vcolor = [WHITE, (150, 220, 255), (200, 150, 255)][unit.variant_index % 3]
        self.scr.blit(self.fxs.render(vlabel, True, vcolor), (x+CS-14, y+CS-14))

    def _draw_board(self):
        bw = BCOLS*CT; bh = BROWS*CT
        rrect(self.scr, PANEL, (BX-8, BY-8, bw+16, bh+16), 10, 2, PANEL_BD)
        self.scr.blit(self.fs.render("BATTLE BOARD", True, DIM), (BX, BY-20))
        for r in range(BROWS):
            for c in range(BCOLS):
                rx, ry = BX+c*CT, BY+r*CT
                col = SLOT
                if self.drag and self.hover:
                    pt, idx, row = self.hover
                    if pt == "board" and idx == c and row == r:
                        tgt = self.board[r][c]
                        if tgt is None: col = SLOT_HL
                        elif self.drag.can_merge_with(tgt):
                            col = SLOT_FUSION if self.drag.can_fusion_merge(tgt) else SLOT_MERGE
                        elif tgt.tier == self.drag.tier and tgt.count + self.drag.count > 3: col = SLOT_BAD
                rrect(self.scr, col, (rx, ry, CS, CS), 6)
                u = self.board[r][c]
                is_glow = any(h[0]=="board" and h[1]==c and h[2]==r for h in self.merge_highlights) and not self.drag
                if u and self.phase == "battle" and u.alive:
                    fl = u.flash / 0.15 if u.flash > 0 else 0
                    draw_creature(self.scr, int(u.x), int(u.y), CS-8, u.tier,
                                 u.hp/u.max_hp if u.max_hp > 0 else 0, False, fl, u.star_ups, u.variant_index)
                    if u.level > 1:
                        lt = self.fxs.render(f"Lv{u.level}", True, GREEN)
                        self.scr.blit(lt, (int(u.x)-lt.get_width()//2, int(u.y)+CS//2-14))
                    ht = self.fx.render(f"{u.hp}", True, WHITE)
                    self.scr.blit(ht, (int(u.x)-ht.get_width()//2, int(u.y)+CS//2-2))
                elif u:
                    self._draw_unit_slot(rx, ry, u, glow=is_glow)

    def _draw_bench(self):
        bw = BENCH_N * CT
        rrect(self.scr, PANEL, (BNX-8, BNY-8, bw+16, CS+16), 10, 2, PANEL_BD)
        self.scr.blit(self.fs.render("BENCH | A:Auto F:Full", True, DIM), (BNX, BNY-20))
        for i in range(BENCH_N):
            rx, ry = BNX+i*CT, BNY
            col = SLOT
            if self.drag and self.hover:
                pt, idx, row = self.hover
                if pt == "bench" and idx == i:
                    tgt = self.bench[i]
                    if tgt is None: col = SLOT_HL
                    elif self.drag.can_merge_with(tgt):
                        col = SLOT_FUSION if self.drag.can_fusion_merge(tgt) else SLOT_MERGE
            rrect(self.scr, col, (rx, ry, CS, CS), 6)
            is_glow = any(h[0]=="bench" and h[1]==i for h in self.merge_highlights) and not self.drag
            self._draw_unit_slot(rx, ry, self.bench[i], glow=is_glow)

    def _draw_shop(self):
        sw = SHOP_N * (SCS + 6)
        rrect(self.scr, (38,40,58), (SX-8, SY-30, sw+16, SCS+50), 10, 2, PANEL_BD)
        self.scr.blit(self.fm.render("SHOP", True, GOLD), (SX, SY-26))
        if self.free_reroll:
            self.scr.blit(self.fx.render("FREE REROLL!", True, CYAN), (SX+60, SY-24))
        mx, my = pygame.mouse.get_pos()
        for i in range(SHOP_N):
            rx, ry = SX+i*(SCS+6), SY; col = SLOT
            u = self.shop[i] if i < len(self.shop) else None
            if not u:
                rrect(self.scr, (30,30,40), (rx, ry, SCS, SCS), 6)
                self.scr.blit(self.fx.render("SOLD", True, (60,60,70)),
                             (rx+SCS//2-self.fx.size("SOLD")[0]//2, ry+SCS//2-6))
                continue
            hov = rx <= mx < rx+SCS and ry <= my < ry+SCS
            if hov and self.phase == "prep" and self.gold >= u.cost: col = SLOT_HL
            rrect(self.scr, col, (rx, ry, SCS, SCS), 6)
            draw_creature(self.scr, rx+SCS//2, ry+SCS//2-6, SCS-16, u.tier, variant_index=u.variant_index)
            cc = GOLD if self.gold >= u.cost else RED
            self.scr.blit(self.fs.render(f"{u.cost}g", True, cc),
                         (rx+SCS//2-self.fs.size(f"{u.cost}g")[0]//2, ry+SCS-18))
            vname_shop = get_emoji_variant(u.tier, u.variant_index)[0]
            self.scr.blit(self.fxs.render(vname_shop, True, DIM),
                         (rx+SCS//2-self.fxs.size(vname_shop)[0]//2, ry+2))

    def _draw_info(self):
        pw = SW - IX - 20; ph = 510
        rrect(self.scr, PANEL, (IX, IY, pw, ph), 10, 2, PANEL_BD)
        mx, my = pygame.mouse.get_pos()
        if self.phase == "battle":
            self.scr.blit(self.fm.render("Unit Guide", True, TXT), (IX+15, IY+8))
            y = IY + 32
            # Show base tiers
            for tier in range(NUM_HANDCRAFTED):
                if y > IY + ph - 20: break
                d = get_tier_def(tier)
                draw_creature(self.scr, IX+18, y+10, 18, tier)
                self.scr.blit(self.fxs.render(f"T{tier} {d['name']}", True, d["body"]), (IX+34, y))
                self.scr.blit(self.fxs.render(f"HP:{d['hp']} ATK:{d['atk']} SPD:{d['spd']}", True, DIM), (IX+34, y+12))
                y += 26
            # Show fusion units
            for fd in FUSION_UNIT_DEFS:
                if y > IY + ph - 20: break
                draw_creature(self.scr, IX+18, y+10, 18, fd["_fusion_idx"])
                self.scr.blit(self.fxs.render(f"F {fd['name']}", True, fd["body"]), (IX+34, y))
                self.scr.blit(self.fxs.render(f"HP:{fd['hp']} ATK:{fd['atk']} {fd['cost']}g", True, DIM), (IX+34, y+12))
                y += 26
            # Note about infinite tiers
            if y < IY + ph - 30:
                self.scr.blit(self.fxs.render("T1+ = Procedural (infinite!)", True, GOLD), (IX+15, y+5))
            return

        # Buttons
        btn_y = IY + 10
        br = pygame.Rect(IX+10, btn_y, 140, 36)
        bh = br.collidepoint(mx, my)
        rrect(self.scr, BTN_GO_H if bh else BTN_GO, br, 8)
        self.scr.blit(self.fm.render("BATTLE!", True, WHITE),
                     (br.centerx-self.fm.size("BATTLE!")[0]//2, br.centery-self.fm.size("BATTLE!")[1]//2))
        rc = 0 if self.free_reroll else self.reroll_cost
        rr = pygame.Rect(IX+160, btn_y, 110, 36)
        can = self.gold >= rc
        rh = rr.collidepoint(mx, my) and can
        rrect(self.scr, SLOT_HL if rh else ((40,40,50) if not can else PANEL_BD), rr, 8)
        rt = f"Reroll {rc}g"
        if self.free_reroll: rt = "FREE Reroll!"
        self.scr.blit(self.fs.render(rt, True, TXT if can else (80,80,90)),
                     (rr.centerx-self.fs.size(rt)[0]//2, rr.centery-self.fs.size(rt)[1]//2))
        amr = pygame.Rect(IX+280, btn_y, 110, 36)
        ah = amr.collidepoint(mx, my)
        rrect(self.scr, SLOT_HL if ah else PANEL_BD, amr, 8)
        self.scr.blit(self.fs.render("Auto-Merge", True, CYAN if ah else TXT),
                     (amr.centerx-self.fs.size("Auto-Merge")[0]//2, amr.centery-self.fs.size("Auto-Merge")[1]//2))
        famr = pygame.Rect(IX+400, btn_y, 130, 36)
        fah = famr.collidepoint(mx, my)
        rrect(self.scr, SLOT_HL if fah else (80, 40, 80), famr, 8)
        self.scr.blit(self.fs.render("Full-Merge", True, MAGENTA if fah else (180, 120, 180)),
                     (famr.centerx-self.fs.size("Full-Merge")[0]//2, famr.centery-self.fs.size("Full-Merge")[1]//2))

        # Evolution chain: show T0 (hand-crafted) + sample procedural tiers
        y_start = btn_y + 46
        self.scr.blit(self.fm.render("Evolution Chain (T0 fixed, T1+ procedural)", True, TXT), (IX+15, y_start))
        y = y_start + 22
        # Show T0
        d = get_tier_def(0)
        draw_creature(self.scr, IX+18, y+10, 18, 0)
        self.scr.blit(self.fxs.render(f"T0 {d['name']} (HAND-CRAFTED)", True, d["body"]), (IX+34, y))
        self.scr.blit(self.fxs.render(f"HP:{d['hp']} ATK:{d['atk']} {d['cost']}g", True, DIM), (IX+34, y+12))
        self.scr.blit(self.fxs.render("v", True, GOLD), (IX+14, y+24))
        y += 34
        # Show a few procedural tiers as examples
        for ptier in [1, 2, 3, 5, 8, 12]:
            if y > IY + ph - 150: break
            pd = get_tier_def(ptier)
            draw_creature(self.scr, IX+18, y+10, 18, ptier)
            self.scr.blit(self.fxs.render(f"T{ptier} {pd['name']}", True, pd["body"]), (IX+34, y))
            self.scr.blit(self.fxs.render(f"HP:{pd['hp']} ATK:{pd['atk']} {pd['cost']}g", True, DIM), (IX+34, y+12))
            self.scr.blit(self.fxs.render("v", True, GOLD), (IX+14, y+24))
            y += 34

        # Infinite tier info
        fy = y + 4
        rrect(self.scr, (30, 25, 45), (IX+5, fy, pw-10, 32), 6, 1, (70, 50, 100))
        self.scr.blit(self.fs.render("T1+ ALL PROCEDURAL: Unique names, stats, colors every game!", True, GOLD), (IX+10, fy+3))
        self.scr.blit(self.fxs.render("3 emoji variants (A/B/C) per tier. Shop scales with rounds!", True, DIM), (IX+10, fy+19))

        # Fusion Recipes
        fy += 38
        rrect(self.scr, (35, 25, 45), (IX+5, fy-4, pw-10, 90), 6, 1, (70, 50, 80))
        self.scr.blit(self.fs.render("Fusion Recipes:", True, MAGENTA), (IX+10, fy))
        fy += 16
        for (ta, tb), fusion in FUSION_RECIPES.items():
            da, db = get_tier_def(ta), get_tier_def(tb)
            draw_creature(self.scr, IX+16, fy+6, 14, ta)
            self.scr.blit(self.fxs.render("+", True, TXT), (IX+28, fy+1))
            draw_creature(self.scr, IX+38, fy+6, 14, tb)
            self.scr.blit(self.fxs.render("=", True, TXT), (IX+50, fy+1))
            fd = _FUSION_BY_PAIR.get((ta, tb), FUSION_UNIT_DEFS[0])
            draw_creature(self.scr, IX+62, fy+6, 14, fd["_fusion_idx"])
            self.scr.blit(self.fxs.render(f"{fd['name']} HP:{fd['hp']} ATK:{fd['atk']}", True, fd["body"]), (IX+78, fy+1))
            fy += 17

        # Active synergies
        if self.active_synergies:
            sy = fy + 2
            for fam, info in self.active_synergies.items():
                if sy > IY + ph - 30: break
                st = self.fxs.render(f"{info['desc']} x{info['count']} ({info['bonus']})", True, info["color"])
                self.scr.blit(st, (IX+10, sy)); sy += 14

        # Controls
        hy = IY + ph - 20
        self.scr.blit(self.fxs.render("Drag:Move | Right-click:Sell | A:Bench F:Full | TAB:Speed | A/B/C=Variant", True, DIM), (IX+5, hy))

    def _draw_battle(self):
        eax = BX + BCOLS*CT + 20; eaw = IX - eax - 10
        if eaw > 0:
            rrect(self.scr, (40,25,25), (eax, BY-28, eaw, BROWS*CT+16), 8, 1, (100,40,40))
            el = self.fs.render("ENEMIES", True, (200,80,80))
            self.scr.blit(el, (eax+eaw//2-el.get_width()//2, BY-24))
        for e in self.enemies:
            if e.alive:
                fl = e.flash / 0.15 if e.flash > 0 else 0
                draw_creature(self.scr, int(e.x), int(e.y), CS-8, e.tier,
                             e.hp/e.max_hp if e.max_hp > 0 else 0, True, fl)
                ht = self.fx.render(f"{e.hp}", True, WHITE)
                self.scr.blit(ht, (int(e.x)-ht.get_width()//2, int(e.y)+CS//2-2))
        for p in self.projs: p.draw(self.scr)

    def _draw_result(self):
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((0,0,0, min(150, int(self.rt*200)))); self.scr.blit(ov, (0,0))
        if self.bres == "win":
            t = self.ft.render("VICTORY!", True, GOLD)
            s = self.fb.render(f"+{self.last_reward} Gold  (Streak: {self.streak})", True, GREEN)
        else:
            t = self.ft.render("DEFEAT!", True, RED)
            if self.phase == "gameover": s = self.fb.render("No lives remaining...", True, (200,100,100))
            else: s = self.fb.render(f"Lives: {self.lives} | Free Reroll next round!", True, (255,180,100))
        self.scr.blit(t, (SW//2-t.get_width()//2, SH//2-40))
        self.scr.blit(s, (SW//2-s.get_width()//2, SH//2+10))

    def _draw_go(self):
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA); ov.fill((0,0,0,180)); self.scr.blit(ov, (0,0))
        new_hs = self.score >= self.highscore and self.score > 0
        self.scr.blit(self.ft.render("GAME OVER", True, GOLD), (SW//2-self.ft.size("GAME OVER")[0]//2, SH//2-100))
        sl = self.ft.render(f"Score: {self.score}", True, GOLD if new_hs else WHITE)
        self.scr.blit(sl, (SW//2-sl.get_width()//2, SH//2-50))
        if new_hs:
            nt = self.fb.render("NEW HIGHSCORE!", True, (255,200,50))
            self.scr.blit(nt, (SW//2-nt.get_width()//2, SH//2-10))
        mt_name = "None"
        if self.highest_tier_seen > 0:
            mt_name = f"T{self.highest_tier_seen} {get_tier_def(self.highest_tier_seen)['name']}"
        stats = [f"Rounds: {self.rnd}", f"W: {self.wins}  L: {self.losses}",
                 f"Best Streak: {self.best_streak}", f"Highest: {mt_name}",
                 f"Final Gold: {self.gold}"]
        sy = SH//2 + 20 if new_hs else SH//2
        for i, s in enumerate(stats):
            st = self.fb.render(s, True, TXT)
            self.scr.blit(st, (SW//2-st.get_width()//2, sy+i*32))
        ht = self.fm.render(f"Highscore: {self.highscore}", True, GOLD)
        self.scr.blit(ht, (SW//2-ht.get_width()//2, sy+len(stats)*32+8))
        rt = self.fm.render("Press ENTER or click to retry", True, DIM)
        self.scr.blit(rt, (SW//2-rt.get_width()//2, SH//2+200))

    def _draw_tooltip(self):
        u = self.tooltip_unit
        if not u: return
        mx, my = pygame.mouse.get_pos()
        d = get_tier_def(u.tier)
        vname = get_emoji_variant(u.tier, u.variant_index)[0]
        lines = [f"{vname} (T{u.tier})"]
        if u.is_fusion: lines[0] += f" [FUSION: {u.fusion_desc}]"
        if d.get("procedural"): lines[0] += " [Procedural]"
        lines.append(f"HP: {u.max_hp}  ATK: {u.atk}  SPD: {u.spd:.1f}  RNG: {u.rng}")
        if u.star_ups > 0: lines.append(f"Star-Ups: {u.star_ups} (+{u.star_ups*25}% stats)")
        if u.level > 1: lines.append(f"Level: {u.level} (XP: {u.xp}/{u.xp_to_next})")
        if u.crit_chance > 0: lines.append(f"Crit: {u.crit_chance*100:.0f}%")
        if u.items:
            for it in u.items: lines.append(f"Item: {it['name']} ({it['desc']})")
        lines.append(f"Merge: {u.count}/3  |  Sell: {u.sell_value()}g")
        if u.tier >= NUM_HANDCRAFTED:
            nd = get_tier_def(u.tier + 1)
            lines.append(f"Next: T{u.tier+1} {nd['name']} (HP:{nd['hp']} ATK:{nd['atk']})")
        for other_tier in range(NUM_HANDCRAFTED):
            fusion = get_fusion(u.tier, other_tier)
            if fusion:
                pair = (min(u.tier, other_tier), max(u.tier, other_tier))
                fd = _FUSION_BY_PAIR.get(pair, {})
                fname = fd.get("name", "?")
                lines.append(f"Fusion: +T{other_tier} {get_tier_def(other_tier)['name']} -> {fname}")
        tw = max(self.fxs.size(l)[0] for l in lines) + 16
        th = len(lines) * 16 + 10
        tx = min(mx + 15, SW - tw - 5)
        ty = max(my - th - 5, 5)
        rrect(self.scr, TOOLTIP_BG, (tx, ty, tw, th), 6, 1, PANEL_BD)
        for i, l in enumerate(lines):
            c = get_tier_def(u.tier)["body"] if i == 0 else TXT
            if "Item:" in l:
                for it in u.items:
                    if it["name"] in l: c = it["color"]; break
            if "Fusion:" in l: c = MAGENTA
            if "Next:" in l: c = GOLD
            self.scr.blit(self.fxs.render(l, True, c), (tx+8, ty+6+i*16))

    # ── MAIN LOOP ──────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = min(self.clk.tick(FPS) / 1000.0, 0.05)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: running = False
                else:
                    if not self.handle(ev): running = False
            self.update(dt)
            self.draw()
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    Game().run()