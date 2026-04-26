import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import random
import asyncio
import json
import os
import string
import time
import base64
import tempfile
from urllib.parse import quote_plus, urlparse
from functools import partial
import yt_dlp
from decimal import Decimal, InvalidOperation
from html import unescape as html_unescape
from difflib import SequenceMatcher

DATA_FILE = "/app/data/data.json"

music_queue = {}
music_now = {}
music_locks = {}
recent_play_requests = {}
music_starting = set()
music_idle_tasks = {}
music_text_channels = {}
music_control_messages = {}
music_autoplay = {}
private_bal = {}
payment_blocked = {}
jail_troll_tasks = {}
jail_guard_active = {}
guard_cooldown = {}
jail = {}
player_health = {}
player_lives = {}
player_points = {}
farm_xp = {}
farm_level = {}
wallet = {}
bank = {}
economy_claims = {}
afk_users = {}
jerk_cooldown = {}
jerk_active = set()
entity_cooldown = {}
blackjack_games = {}
fishing_xp = {}
fishing_level = {}
fishing_rods_owned = {}
fishing_equipped_rod = {}
fishing_active = set()

# ── General player level (XP from all activities) ────────────────────────────
player_general_xp: dict[int, int]    = {}
player_general_level: dict[int, int] = {}

# ── Fishing hooks & bait ─────────────────────────────────────────────────────
hooks_owned: dict[int, list]     = {}
hooks_equipped: dict[int, str]   = {}
bait_inventory: dict[int, dict]  = {}   # {user_id: {"Worm": n, "Shrimp": n, ...}}
bait_equipped: dict[int, str]    = {}

# ── Delivery system ──────────────────────────────────────────────────────────
delivery_active = set()
delivery_vehicles_owned: dict[int, list] = {}
delivery_equipped_vehicle: dict[int, str] = {}
pet_data: dict[int, dict] = {}
company_data: dict[int, dict] = {}
custom_rod_data: dict[int, dict] = {}

OWNER_ID = 756539405463978024
PET_MAX_LEVEL = 50
PET_RENAME_COST = 50_000
CUSTOM_ROD_UNLOCK_COST = 5_000_000
CUSTOM_ROD_RENAME_COST = 500_000
COMPANY_NAME_MAX_LENGTH = 24

FISHING_RODS = {
    "Basic Rod": {
        "price": 0,
        "reward_multiplier": 1.0,
        "reaction_time": 3.0,
        "rare_bonus": 0,
        "shark_bonus": 0,
    },
    "Good Rod": {
        "price": 10_000,
        "reward_multiplier": 1.1,
        "reaction_time": 3.5,
        "rare_bonus": 3,
        "shark_bonus": 1,
    },
    "Pro Rod": {
        "price": 100_000,
        "reward_multiplier": 1.25,
        "reaction_time": 4.0,
        "rare_bonus": 6,
        "shark_bonus": 2,
    },
    "Mythic Rod": {
        "price": 1_000_000,
        "reward_multiplier": 1.5,
        "reaction_time": 5.0,
        "rare_bonus": 10,
        "shark_bonus": 4,
    },
    "OP Rod": {
        "price": 10_000_000,
        "reward_multiplier": 2.0,
        "reaction_time": 6.0,
        "rare_bonus": 18,
        "shark_bonus": 8,
    },
    "Unbelievable Rod": {
        "price": 100_000_000,
        "reward_multiplier": 3.0,
        "reaction_time": 7.0,
        "rare_bonus": 30,
        "shark_bonus": 15,
    },
}

FISHING_CATCHES = {
    "small":  {"emoji": "🐟",  "name": "Small Fish",  "reward": 500},
    "rare":   {"emoji": "🐠",  "name": "Rare Fish",   "reward": 2_000},
    "shark":  {"emoji": "🦈",  "name": "Shark",       "reward": 100_000},
    "boot":   {"emoji": "👢",  "name": "Old Boot",    "reward": 100},
    # ── Legendary fish ──────────────────────────────────────────────────
    "kraken":   {"emoji": "🦑", "name": "Kraken",    "base_reward": 1_000_000,  "base_chance": 0.001,   "scales_level": False},
    "bloop":    {"emoji": "🌊", "name": "Bloop",     "base_reward": 3_000_000,  "base_chance": 0.0005,  "scales_level": False},
    "mobydick": {"emoji": "🐋", "name": "Moby Dick", "base_reward": 10_000_000, "base_chance": 0.00012, "scales_level": False},
    "spongebob":{"emoji": "🧽", "name": "SpongeBob", "base_reward": 1_000_000,  "base_chance": 0.0015,  "scales_level": False, "fixed_reward": True},
}

# ── Fishing hooks ────────────────────────────────────────────────────────────
FISHING_HOOKS = {
    "Basic Hook":   {"price": 0,       "level_req": 0,  "emoji": "🪝", "rare_bonus": 0,  "shark_bonus": 0,  "legendary_bonus": 0.0},
    "Iron Hook":    {"price": 5_000,   "level_req": 3,  "emoji": "⚙️", "rare_bonus": 5,  "shark_bonus": 1,  "legendary_bonus": 0.0},
    "Golden Hook":  {"price": 50_000,  "level_req": 10, "emoji": "🥇", "rare_bonus": 12, "shark_bonus": 3,  "legendary_bonus": 0.25},
    "Diamond Hook": {"price": 500_000, "level_req": 25, "emoji": "💎", "rare_bonus": 20, "shark_bonus": 6,  "legendary_bonus": 0.75},
    "Abyssal Hook": {"price": 25_000_000, "level_req": 45, "emoji": "🌌", "rare_bonus": 42, "shark_bonus": 18, "legendary_bonus": 3.6},
}

# ── Fishing bait ─────────────────────────────────────────────────────────────
FISHING_BAITS = {
    "Worm":       {"price": 0,      "level_req": 0,  "emoji": "🪱", "reward_bonus": 0.00, "consumed": False},
    "Shrimp":     {"price": 500,    "level_req": 2,  "emoji": "🦐", "reward_bonus": 0.25, "consumed": True},
    "Squid":      {"price": 2_000,  "level_req": 8,  "emoji": "🦑", "reward_bonus": 0.60, "consumed": True},
    "Magic Bait": {"price": 10_000, "level_req": 20, "emoji": "✨", "reward_bonus": 1.50, "consumed": True},
}

# ── Delivery vehicles ────────────────────────────────────────────────────────
DELIVERY_VEHICLES = {
    "Scooter":   {"price": 0,         "level_req": 0,  "time_bonus": 0,  "reward_multiplier": 1.00, "emoji": "🛵", "steps_normal": 5, "steps_vip": 7},
    "Bike":      {"price": 25_000,    "level_req": 5,  "time_bonus": 5,  "reward_multiplier": 1.10, "emoji": "🚲", "steps_normal": 5, "steps_vip": 6},
    "Car":       {"price": 200_000,   "level_req": 15, "time_bonus": 10, "reward_multiplier": 1.25, "emoji": "🚗", "steps_normal": 4, "steps_vip": 5},
    "Super Van": {"price": 2_000_000, "level_req": 30, "time_bonus": 20, "reward_multiplier": 1.50, "emoji": "🚀", "steps_normal": 3, "steps_vip": 4},
}

DELIVERY_BASE_TIME      = 20          # seconds before vehicle bonus
DELIVERY_DIRECTIONS     = ["LEFT", "RIGHT", "FORWARD", "BACK"]
DELIVERY_DIR_EMOJI      = {"LEFT": "⬅️", "RIGHT": "➡️", "FORWARD": "⬆️", "BACK": "⬇️"}
DELIVERY_VIP_CHANCE     = 0.05        # 5 % chance of VIP customer
DELIVERY_BASE_REWARD_NORMAL = (800,  2_500)
DELIVERY_BASE_REWARD_VIP    = (100_000, 100_000)

PET_SHOP = {
    "Cat": {
        "price": 250_000,
        "emoji": "🐈",
        "bonus_type": "company",
        "bonus_value": 0.08,
        "bonus_label": "+8% company income",
    },
    "Dog": {
        "price": 250_000,
        "emoji": "🐕",
        "bonus_type": "fishing",
        "bonus_value": 0.10,
        "bonus_label": "+10% fishing rewards",
    },
    "Fox": {
        "price": 500_000,
        "emoji": "🦊",
        "bonus_type": "delivery",
        "bonus_value": 0.12,
        "bonus_label": "+12% delivery rewards",
    },
    "Dragon": {
        "price": 2_500_000,
        "emoji": "🐉",
        "bonus_type": "all",
        "bonus_value": 0.15,
        "bonus_label": "+15% company, fishing, and delivery rewards",
    },
}


def load_data():
    global farm_xp, farm_level, player_health, player_lives, player_points, wallet, bank, economy_claims, jail
    global fishing_xp, fishing_level, fishing_rods_owned, fishing_equipped_rod, private_bal, payment_blocked
    global delivery_vehicles_owned, delivery_equipped_vehicle
    global player_general_xp, player_general_level
    global hooks_owned, hooks_equipped, bait_inventory, bait_equipped
    global pet_data, company_data, custom_rod_data

    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    farm_xp = {int(k): v for k, v in data.get("xp", {}).items()}
    farm_level = {int(k): v for k, v in data.get("level", {}).items()}
    player_health = {int(k): v for k, v in data.get("player_health", {}).items()}
    player_lives = {int(k): v for k, v in data.get("player_lives", {}).items()}
    player_points = {int(k): v for k, v in data.get("player_points", {}).items()}
    wallet = {int(k): v for k, v in data.get("wallet", {}).items()}
    bank = {int(k): v for k, v in data.get("bank", {}).items()}
    economy_claims = {int(k): v for k, v in data.get("economy_claims", {}).items()}
    jail = {int(k): v for k, v in data.get("jail", {}).items()}
    private_bal = {int(k): v for k, v in data.get("private_bal", {}).items()}
    payment_blocked = {int(k): v for k, v in data.get("payment_blocked", {}).items()}
    fishing_level = {int(k): v for k, v in data.get("fishing_level", {}).items()}
    fishing_xp = {int(k): v for k, v in data.get("fishing_xp", {}).items()}
    fishing_rods_owned = {int(k): v for k, v in data.get("fishing_rods_owned", {}).items()}
    fishing_equipped_rod = {int(k): v for k, v in data.get("fishing_equipped_rod", {}).items()}
    delivery_vehicles_owned = {int(k): v for k, v in data.get("delivery_vehicles_owned", {}).items()}
    delivery_equipped_vehicle = {int(k): v for k, v in data.get("delivery_equipped_vehicle", {}).items()}
    player_general_xp    = {int(k): v for k, v in data.get("player_general_xp", {}).items()}
    player_general_level = {int(k): v for k, v in data.get("player_general_level", {}).items()}
    hooks_owned    = {int(k): v for k, v in data.get("hooks_owned", {}).items()}
    hooks_equipped = {int(k): v for k, v in data.get("hooks_equipped", {}).items()}
    bait_inventory = {int(k): v for k, v in data.get("bait_inventory", {}).items()}
    bait_equipped  = {int(k): v for k, v in data.get("bait_equipped", {}).items()}
    pet_data = {int(k): v for k, v in data.get("pet_data", {}).items()}
    company_data = {int(k): v for k, v in data.get("company_data", {}).items()}
    custom_rod_data = {int(k): v for k, v in data.get("custom_rod_data", {}).items()}


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "xp": {str(k): v for k, v in farm_xp.items()},
            "level": {str(k): v for k, v in farm_level.items()},
            "player_health": {str(k): v for k, v in player_health.items()},
            "player_lives": {str(k): v for k, v in player_lives.items()},
            "player_points": {str(k): v for k, v in player_points.items()},
            "wallet": {str(k): v for k, v in wallet.items()},
            "bank": {str(k): v for k, v in bank.items()},
            "economy_claims": {str(k): v for k, v in economy_claims.items()},
            "jail": {str(k): v for k, v in jail.items()},
            "fishing_xp": {str(k): v for k, v in fishing_xp.items()},
            "private_bal": {str(k): v for k, v in private_bal.items()},
            "payment_blocked": {str(k): v for k, v in payment_blocked.items()},
            "fishing_level": {str(k): v for k, v in fishing_level.items()},
            "fishing_rods_owned": {str(k): v for k, v in fishing_rods_owned.items()},
            "fishing_equipped_rod": {str(k): v for k, v in fishing_equipped_rod.items()},
            "delivery_vehicles_owned": {str(k): v for k, v in delivery_vehicles_owned.items()},
            "delivery_equipped_vehicle": {str(k): v for k, v in delivery_equipped_vehicle.items()},
            "player_general_xp":    {str(k): v for k, v in player_general_xp.items()},
            "player_general_level": {str(k): v for k, v in player_general_level.items()},
            "hooks_owned":    {str(k): v for k, v in hooks_owned.items()},
            "hooks_equipped": {str(k): v for k, v in hooks_equipped.items()},
            "bait_inventory": {str(k): v for k, v in bait_inventory.items()},
            "bait_equipped":  {str(k): v for k, v in bait_equipped.items()},
            "pet_data": {str(k): v for k, v in pet_data.items()},
            "company_data": {str(k): v for k, v in company_data.items()},
            "custom_rod_data": {str(k): v for k, v in custom_rod_data.items()},
        }, f, indent=4)


def get_wallet(user_id):
    wallet.setdefault(user_id, 0)
    return wallet[user_id]


def get_bank(user_id):
    bank.setdefault(user_id, 0)
    return bank[user_id]


def get_claims(user_id):
    economy_claims.setdefault(user_id, {"daily": 0, "weekly": 0, "monthly": 0})
    return economy_claims[user_id]


def get_level(xp):
    return xp // 100


def generate_random_word(length=5):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def format_coins(amount):
    return f"{amount:,}"


def get_fishing_xp(user_id):
    fishing_xp.setdefault(user_id, 0)
    return fishing_xp[user_id]


def get_fishing_level_value(user_id):
    fishing_level.setdefault(user_id, get_fishing_xp(user_id) // 100)
    return fishing_level[user_id]


# ── General player level helpers ─────────────────────────────────────────────
GENERAL_XP_PER_LEVEL = 500

def get_general_xp(user_id: int) -> int:
    player_general_xp.setdefault(user_id, 0)
    return player_general_xp[user_id]

def get_general_level(user_id: int) -> int:
    player_general_level.setdefault(user_id, get_general_xp(user_id) // GENERAL_XP_PER_LEVEL)
    return player_general_level[user_id]

def add_general_xp(user_id: int, amount: int) -> tuple[int, bool]:
    """Add XP and return (new_level, leveled_up)."""
    old_level = get_general_level(user_id)
    player_general_xp[user_id] = get_general_xp(user_id) + amount
    new_level = player_general_xp[user_id] // GENERAL_XP_PER_LEVEL
    player_general_level[user_id] = new_level
    return new_level, new_level > old_level


def get_pet_record(user_id: int):
    return pet_data.get(user_id)


def sync_pet_state(user_id: int):
    pet = pet_data.get(user_id)
    if not pet:
        return None

    pet.setdefault("type", "Cat")
    pet.setdefault("name", pet["type"])
    pet.setdefault("xp", 0)
    pet.setdefault("level", 1)
    pet.setdefault("hunger", 100)
    pet.setdefault("last_hunger_tick", int(time.time()))

    now = int(time.time())
    elapsed_hours = max(0, (now - pet["last_hunger_tick"]) // 3600)
    if elapsed_hours:
        pet["hunger"] = max(0, pet["hunger"] - (elapsed_hours * 8))
        pet["last_hunger_tick"] += elapsed_hours * 3600

    level = min(PET_MAX_LEVEL, 1 + (pet["xp"] // 120))
    pet["level"] = max(1, level)
    return pet


def pet_bonus_multiplier(user_id: int, bonus_type: str) -> float:
    pet = sync_pet_state(user_id)
    if not pet:
        return 1.0

    hunger = pet.get("hunger", 0)
    if hunger <= 15:
        return 1.0

    pet_info = PET_SHOP.get(pet.get("type"))
    if not pet_info:
        return 1.0

    if pet_info["bonus_type"] not in {bonus_type, "all"}:
        return 1.0

    level_scale = 1.0 + ((pet.get("level", 1) - 1) * 0.01)
    hunger_scale = 0.6 + min(hunger, 100) / 250
    return 1.0 + (pet_info["bonus_value"] * level_scale * hunger_scale)


def feed_pet(user_id: int):
    pet = sync_pet_state(user_id)
    if not pet:
        return None

    before_level = pet["level"]
    pet["hunger"] = min(100, pet.get("hunger", 0) + 30)
    pet["last_hunger_tick"] = int(time.time())
    pet["xp"] += 20
    pet["level"] = min(PET_MAX_LEVEL, 1 + (pet["xp"] // 120))
    return pet, pet["level"] > before_level


def get_company_record(user_id: int):
    company = company_data.get(user_id)
    if not company:
        return None

    company.setdefault("name", "My Company")
    company.setdefault("concept", "Widgets")
    company.setdefault("level", 1)
    company.setdefault("resource", 0)
    company.setdefault("stored_income", 0)
    company.setdefault("last_tick", int(time.time()))
    return company


def company_resource_label(company: dict) -> str:
    concept = company.get("concept", "Widget")
    return f"{concept} Crates"


def company_hourly_income(level: int) -> int:
    return int(350 * (level ** 1.35))


def company_resource_unit_cost(level: int) -> int:
    return 60 + (level * 35)


def company_upgrade_resource_cost(level: int) -> int:
    return 20 + (level * 14)


def sync_company_income(user_id: int):
    company = get_company_record(user_id)
    if not company:
        return None

    now = int(time.time())
    elapsed = max(0, now - company.get("last_tick", now))
    if elapsed:
        per_second = company_hourly_income(company["level"]) / 3600
        company["stored_income"] += int(elapsed * per_second)
        company["last_tick"] = now
    return company


def get_custom_rod_entry(user_id: int):
    entry = custom_rod_data.setdefault(user_id, {"unlocked": False, "name": "Custom Rod"})
    entry.setdefault("unlocked", False)
    entry.setdefault("name", "Custom Rod")
    return entry


def has_custom_rod(user_id: int) -> bool:
    return bool(get_custom_rod_entry(user_id).get("unlocked"))


def get_custom_rod_display_name(user_id: int) -> str:
    entry = get_custom_rod_entry(user_id)
    return entry.get("name", "Custom Rod")[:20] or "Custom Rod"


def get_best_owned_real_rod(user_id: int) -> str:
    rods = [name for name in get_owned_rods(user_id) if name in FISHING_RODS and name != "Custom Rod"]
    if not rods:
        return "Basic Rod"
    return max(rods, key=lambda name: FISHING_RODS[name]["price"])

# ── Hook helpers ─────────────────────────────────────────────────────────────
def get_owned_hooks(user_id: int) -> list:
    hooks = hooks_owned.setdefault(user_id, ["Basic Hook"])
    if "Basic Hook" not in hooks:
        hooks.insert(0, "Basic Hook")
    return hooks

def get_equipped_hook(user_id: int) -> str:
    eq = hooks_equipped.setdefault(user_id, "Basic Hook")
    if eq not in get_owned_hooks(user_id):
        eq = "Basic Hook"
        hooks_equipped[user_id] = eq
    return eq

# ── Bait helpers ─────────────────────────────────────────────────────────────
def get_bait_inventory(user_id: int) -> dict:
    inv = bait_inventory.setdefault(user_id, {"Worm": -1})  # -1 = unlimited
    if "Worm" not in inv:
        inv["Worm"] = -1
    return inv

def get_equipped_bait(user_id: int) -> str:
    eq = bait_equipped.setdefault(user_id, "Worm")
    inv = get_bait_inventory(user_id)
    # Fall back to Worm if equipped bait is depleted
    if eq != "Worm" and inv.get(eq, 0) <= 0:
        eq = "Worm"
        bait_equipped[user_id] = eq
    return eq

def consume_bait(user_id: int) -> str:
    """Use one unit of equipped bait. Returns the bait name used."""
    bait_name = get_equipped_bait(user_id)
    inv = get_bait_inventory(user_id)
    if bait_name != "Worm" and FISHING_BAITS[bait_name]["consumed"]:
        inv[bait_name] = max(0, inv.get(bait_name, 0) - 1)
        if inv[bait_name] == 0:
            bait_equipped[user_id] = "Worm"  # auto switch back
    return bait_name


def get_owned_rods(user_id):
    rods = fishing_rods_owned.setdefault(user_id, ["Basic Rod"])
    if "Basic Rod" not in rods:
        rods.insert(0, "Basic Rod")
    if has_custom_rod(user_id) and "Custom Rod" not in rods:
        rods.append("Custom Rod")
    return rods


def get_equipped_rod(user_id):
    equipped = fishing_equipped_rod.setdefault(user_id, "Basic Rod")
    if equipped not in get_owned_rods(user_id):
        equipped = "Basic Rod"
        fishing_equipped_rod[user_id] = equipped
    return equipped


def find_rod_name(name):
    wanted = str(name).strip().lower()
    if wanted in {"custom", "custom rod"}:
        return "Custom Rod"
    for rod_name in FISHING_RODS:
        if rod_name.lower() == wanted:
            return rod_name
    return None


def resolve_rod_profile(user_id: int, equipped_name: str = None):
    equipped_name = equipped_name or get_equipped_rod(user_id)
    if equipped_name == "Custom Rod" and has_custom_rod(user_id):
        base_name = get_best_owned_real_rod(user_id)
        return base_name, get_custom_rod_display_name(user_id), FISHING_RODS[base_name]
    return equipped_name, equipped_name, FISHING_RODS[equipped_name]


def build_fishing_grid(catch_position):
    cells = ["⬜"] * 9
    cells[catch_position - 1] = "🐟"
    return "\n".join([
        " ".join(cells[0:3]),
        " ".join(cells[3:6]),
        " ".join(cells[6:9]),
    ])


def choose_fish_catch(rod_name: str, hook_name: str = "Basic Hook"):
    rod_data  = FISHING_RODS[rod_name]
    hook_data = FISHING_HOOKS[hook_name]
    boot_weight  = 8
    rare_weight  = 20 + rod_data["rare_bonus"]  + hook_data["rare_bonus"]
    shark_weight = 2  + rod_data["shark_bonus"] + hook_data["shark_bonus"]
    small_weight = max(1, 100 - boot_weight - rare_weight - shark_weight)

    return random.choices(
        ["small", "rare", "shark", "boot"],
        weights=[small_weight, rare_weight, shark_weight, boot_weight],
        k=1,
    )[0]


def _legendary_multiplier(user_id: int, rod_name: str, hook_name: str = "Basic Hook") -> float:
    """Scale legendary chance on rod + hook + general level. No fishing level."""
    rod_data  = FISHING_RODS[rod_name]
    hook_data = FISHING_HOOKS[hook_name]
    gen_level = get_general_level(user_id)

    rod_factor   = 1.0 + min(rod_data["rare_bonus"], 40) * 0.02
    hook_factor  = 1.0 + min(hook_data["legendary_bonus"], 4.0) * 0.45
    level_factor = 1.0 + min(gen_level, 50) * 0.02
    return min(rod_factor * hook_factor * level_factor, 7.5)


def legendary_reward(catch_key: str, rod_name: str, user_id: int) -> int:
    """Legendary rewards scale with rod and general level."""
    catch = FISHING_CATCHES[catch_key]
    if catch.get("fixed_reward"):
        return catch["base_reward"]
    level_factor = 1.0 + min(get_general_level(user_id), 100) * 0.005
    return int(catch["base_reward"] * FISHING_RODS[rod_name]["reward_multiplier"] * level_factor)


def parse_amount_input(raw_amount, *, balance=None, allow_all=False):
    if raw_amount is None:
        return None

    text = str(raw_amount).strip().lower().replace(",", "")
    if not text:
        return None

    if allow_all and text == "all":
        return balance if balance is not None else None

    multiplier = 1
    if text[-1:] in {"k", "m", "b"}:
        suffix = text[-1]
        text = text[:-1]
        multiplier = {
            "k": 1_000,
            "m": 1_000_000,
            "b": 1_000_000_000,
        }[suffix]

    try:
        amount = Decimal(text) * multiplier
    except (InvalidOperation, ValueError):
        return None

    if amount != amount.to_integral_value():
        return None

    amount = int(amount)
    return amount if amount > 0 else None


class AllInConfirmView(discord.ui.View):
    def __init__(self, requester, game_name):
        super().__init__(timeout=20)
        self.requester_id = requester.id if hasattr(requester, "id") else int(requester)
        self.game_name = game_name
        self.confirmed = False
        self.message = None  # we store message for timeout edit

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.requester_id:
            await interaction.response.send_message(
                "This isn't your confirmation.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @discord.ui.button(label="Yes, go all in", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content=f"{self.game_name} all-in confirmed. Starting now...",
            view=self
        )
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(view=self)
        self.stop()


async def confirm_all_in(ctx, game_name):
    view = AllInConfirmView(ctx.author, game_name)

    message = await ctx.send(
        f"{ctx.author.mention} are you sure you want to {game_name.lower()} **all** your withdrawn coins?",
        view=view
    )

    view.message = message

    await view.wait()

    if not view.confirmed:
        try:
            for item in view.children:
                item.disabled = True
            await message.edit(view=view)
        except:
            pass
        return False

    return True


# ============ AMOUNT PARSER ============
def parse_amount(amount_str, user_balance):
    amount_str = str(amount_str).lower().strip()
    if amount_str == "all":
        return user_balance
    try:
        if amount_str.endswith("k"):
            return int(float(amount_str[:-1]) * 1_000)
        elif amount_str.endswith("m"):
            return int(float(amount_str[:-1]) * 1_000_000)
        else:
            return int(amount_str)
    except:
        return None
    

# ================= BOT =================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    load_data()
    print(f"Logged as {bot.user}")


# ===== MUSIC SYSTEM CONFIG =====

YTDLP_COOKIE_FILE = None


def setup_ytdlp_cookie_file():
    global YTDLP_COOKIE_FILE

    cookie_path = os.environ.get("YTDLP_COOKIES_FILE")
    cookie_b64 = os.environ.get("YTDLP_COOKIES_B64")

    if cookie_path and os.path.exists(cookie_path):
        YTDLP_COOKIE_FILE = cookie_path
        return

    if not cookie_b64:
        return

    try:
        cookie_bytes = base64.b64decode(cookie_b64)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "targetbot_cookies.txt")

        with open(temp_path, "wb") as cookie_file:
            cookie_file.write(cookie_bytes)

        YTDLP_COOKIE_FILE = temp_path
        print("Loaded yt-dlp cookies from YTDLP_COOKIES_B64")
    except Exception as e:
        print(f"Failed to load yt-dlp cookies: {e}")


def build_ytdl_options(default_search="auto"):
    options = {
        "format": "bestaudio[protocol=m3u8_native]/bestaudio[protocol=m3u8]/bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": default_search,
        "source_address": "0.0.0.0",
        "extractor_args": {
            "youtube": {
                "player_client": ["web_safari", "web"],
            }
        },
    }

    user_agent = os.environ.get("YTDLP_USER_AGENT")
    if user_agent:
        options["http_headers"] = {"User-Agent": user_agent}

    if YTDLP_COOKIE_FILE:
        options["cookiefile"] = YTDLP_COOKIE_FILE

    return options

setup_ytdlp_cookie_file()

ytdl_format_options = build_ytdl_options()

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


def search_youtube(query):
    ydl_opts = build_ytdl_options(default_search="scsearch5")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl_search:
        info = ydl_search.extract_info(query, download=False)
        return info.get("entries", []) or []


def is_url(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def is_youtube_url(value):
    if not is_url(value):
        return False

    host = urlparse(value).netloc.lower()
    return "youtube.com" in host or "youtu.be" in host or "music.youtube.com" in host


def normalize_music_query(query):
    query = query.strip()

    if is_youtube_url(query):
        return None

    if is_url(query):
        return query

    return f"scsearch1:{query}"

# ===== MUSIC CLASS =====

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "Unknown title")
        self.webpage_url = data.get("webpage_url")
        self.artist = data.get("artist") or data.get("uploader") or "Unknown artist"
        self.track = data.get("track") or data.get("alt_title") or self.title
        self.duration = data.get("duration")
        self.thumbnail = data.get("thumbnail")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_running_loop()

        data = await loop.run_in_executor(
            None,
            partial(ytdl.extract_info, url, download=not stream)
        )

        if "entries" in data:
            entries = [entry for entry in data["entries"] if entry]
            if not entries:
                raise ValueError("No results found.")
            data = entries[0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        source = discord.FFmpegPCMAudio(
            filename,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn",
        )

        return cls(source, data=data)

    
# ===== LYRICS SYSTEM =====

import requests
import re

GENIUS_HEADERS = {"User-Agent": "TargetBot/1.0"}
GENIUS_TAG_RE = re.compile(r"<[^>]+>")
GENIUS_BLOCK_RE = re.compile(r'<div[^>]+data-lyrics-container="true"[^>]*>(.*?)</div>', re.DOTALL | re.IGNORECASE)


def clean_lyrics_title(text):
    if not text:
        return ""

    cleaned = text
    cleaned = re.sub(r"https?://\S+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bby\s+[A-Za-z0-9_.-]+\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\([^)]*(official|video|audio|lyrics?|visualizer|hd|4k)[^)]*\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[[^\]]*(official|video|audio|lyrics?|visualizer|hd|4k)[^\]]*\]", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\(([^)]*(?:prod|producer|slowed|speed up|sped up|reverb|remix|edit|nightcore|bass boosted|snippet|mashup|version|cover|live|extended|instrumental|performance)[^)]*)\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[([^\]]*(?:prod|producer|slowed|speed up|sped up|reverb|remix|edit|nightcore|bass boosted|snippet|mashup|version|cover|live|extended|instrumental|performance)[^\]]*)\]", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(official video|official audio|lyrics video|lyric video|visualizer|audio|lyrics|hd|4k|prod\.?\s+by|produced by|slowed(?:\s*\+\s*reverb)?|sped up|speed up|reverb|nightcore|bass boosted|snippet|mashup|extended|instrumental|live performance|live version)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bft\.?\b", "feat", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bfeat\.?\s+[^-|\n]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bwith\s+[^-|\n]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*[|/]\s*.*$", "", cleaned)
    cleaned = re.sub(r"\s*[-–—]\s*(?:prod.*|slowed.*|sped up.*|reverb.*|remix.*|edit.*|nightcore.*|bass boosted.*)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*[-–—]\s*$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    return cleaned.strip()


def build_lyrics_search_variants(text):
    cleaned = clean_lyrics_title(text)
    variants = []

    def add_variant(value):
        value = clean_lyrics_title(value)
        key = value.lower()
        if value and key not in seen:
            seen.add(key)
            variants.append(value)

    seen = set()
    add_variant(cleaned)

    dash_parts = [part.strip() for part in re.split(r"\s[-–—]\s", cleaned) if part.strip()]
    if len(dash_parts) >= 2:
        add_variant(f"{dash_parts[0]} - {dash_parts[1]}")
        add_variant(dash_parts[1])
        add_variant(dash_parts[0])

    no_feat = re.sub(r"\bfeat\b.*$", "", cleaned, flags=re.IGNORECASE).strip(" -")
    add_variant(no_feat)

    no_paren = re.sub(r"\([^)]*\)", "", cleaned).strip(" -")
    add_variant(no_paren)

    return variants


def split_lyrics_chunks(text, chunk_size=1800):
    lines = text.splitlines()
    chunks = []
    current = ""

    for line in lines:
        next_part = line if not current else f"{current}\n{line}"
        if len(next_part) <= chunk_size:
            current = next_part
        else:
            if current:
                chunks.append(current)
            if len(line) <= chunk_size:
                current = line
            else:
                for i in range(0, len(line), chunk_size):
                    chunks.append(line[i:i + chunk_size])
                current = ""

    if current:
        chunks.append(current)

    return chunks or [text[:chunk_size]]


def format_lyrics_for_embed(text):
    lines = [line.rstrip() for line in text.splitlines()]
    formatted_lines = []
    blank_streak = 0

    for line in lines:
        if not line.strip():
            blank_streak += 1
            if blank_streak <= 1:
                formatted_lines.append("")
            continue

        blank_streak = 0
        formatted_lines.append(line)

        if len(line) > 25:
            formatted_lines.append("")

    formatted = "\n".join(formatted_lines).strip()
    return formatted or text


def build_lyrics_embed(found_label, chunks, page_index, source_url=None):
    total_pages = len(chunks)
    embed = discord.Embed(
        title=found_label,
        description=chunks[page_index],
        color=discord.Color.magenta()
    )
    if source_url:
        embed.description += f"\n\n[Open source]({source_url})"
    embed.set_footer(text=f"Lyrics page {page_index + 1}/{total_pages}")
    return embed


def build_lyrics_queries(title, artist, track):
    title_variants = build_lyrics_search_variants(title)
    track_variants = build_lyrics_search_variants(track or title)
    cleaned_title = title_variants[0] if title_variants else clean_lyrics_title(title)
    cleaned_track = track_variants[0] if track_variants else clean_lyrics_title(track or title)
    cleaned_artist = clean_lyrics_title(artist or "")

    queries = []
    for track_variant in track_variants or [cleaned_track]:
        if cleaned_artist and track_variant:
            queries.append(f"{cleaned_artist} {track_variant}")
            queries.append(f"{track_variant} {cleaned_artist}")
            queries.append(f"{cleaned_artist} - {track_variant}")
        if track_variant:
            queries.append(track_variant)
    for title_variant in title_variants or [cleaned_title]:
        if title_variant:
            queries.append(title_variant)
    if title and title not in queries:
        queries.append(title)

    seen = set()
    ordered = []
    for query in queries:
        key = query.strip().lower()
        if key and key not in seen:
            seen.add(key)
            ordered.append(query)
    return ordered


def build_lyrics_pairs(title, artist, track):
    title_variants = build_lyrics_search_variants(title)
    track_variants = build_lyrics_search_variants(track or title)
    cleaned_title = title_variants[0] if title_variants else clean_lyrics_title(title)
    cleaned_track = track_variants[0] if track_variants else clean_lyrics_title(track or title)
    cleaned_artist = clean_lyrics_title(artist or "")

    pairs = []
    for track_variant in track_variants or [cleaned_track]:
        if cleaned_artist and track_variant:
            pairs.append((cleaned_artist, track_variant))
    if cleaned_artist and cleaned_title and cleaned_title != cleaned_track:
        pairs.append((cleaned_artist, cleaned_title))

    title_parts = [part.strip() for part in cleaned_title.split(" - ") if part.strip()]
    if len(title_parts) >= 2:
        pairs.append((title_parts[0], title_parts[-1]))

    if artist or track or title:
        pairs.append((artist or "unknown", track or cleaned_title or title))

    seen = set()
    ordered = []
    for artist_name, song_name in pairs:
        key = (artist_name.strip().lower(), song_name.strip().lower())
        if key not in seen and key[1]:
            seen.add(key)
            ordered.append((artist_name, song_name))
    return ordered


def normalize_lyrics_key(text):
    cleaned = clean_lyrics_title(text or "").lower()
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"(ft|feat|featuring|prod|with)", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def similarity_score(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def score_lyrics_candidate(result_title, result_artist, title, artist, track):
    target_title = normalize_lyrics_key(track or title)
    target_artist = normalize_lyrics_key(artist or "")
    target_combo = normalize_lyrics_key(f"{artist or ''} {track or title}")
    result_title = normalize_lyrics_key(result_title)
    result_artist = normalize_lyrics_key(result_artist)
    result_combo = normalize_lyrics_key(f"{result_artist} {result_title}")

    title_score = similarity_score(target_title, result_title)
    artist_score = similarity_score(target_artist, result_artist) if target_artist else 0.75
    combo_score = similarity_score(target_combo, result_combo)
    return (title_score * 0.5) + (artist_score * 0.2) + (combo_score * 0.3)


def choose_best_lrclib_match(results, title, artist, track):
    best_result = None
    best_score = 0.0

    for result in results:
        score = score_lyrics_candidate(
            result.get("trackName") or result.get("name") or "",
            result.get("artistName") or result.get("artist") or "",
            title,
            artist,
            track,
        )
        if score > best_score:
            best_score = score
            best_result = result

    if best_result and best_score >= 0.72:
        return best_result
    return None


def choose_best_genius_hit(hits, title, artist, track):
    best_result = None
    best_score = 0.0

    for hit in hits:
        result = hit.get("result", {})
        score = score_lyrics_candidate(
            result.get("title") or "",
            result.get("primary_artist", {}).get("name") or "",
            title,
            artist,
            track,
        )
        if score > best_score:
            best_score = score
            best_result = result

    if best_result and best_score >= 0.62:
        return best_result
    return None


def extract_genius_lyrics(page_html):
    matches = GENIUS_BLOCK_RE.findall(page_html)
    if not matches:
        return None

    parts = []
    for block in matches:
        block = re.sub(r"<br\s*/?>", "\n", block, flags=re.IGNORECASE)
        block = GENIUS_TAG_RE.sub("", block)
        block = html_unescape(block)
        cleaned = "\n".join(line.rstrip() for line in block.splitlines()).strip()
        if cleaned:
            parts.append(cleaned)

    if not parts:
        return None
    return "\n\n".join(parts).strip()


def fetch_genius_lyrics(title, artist, track):
    for search_query in build_lyrics_queries(title, artist, track):
        try:
            search_url = f"https://genius.com/api/search/multi?per_page=8&q={quote_plus(search_query)}"
            response = requests.get(search_url, timeout=10, headers=GENIUS_HEADERS)
            if not response.ok:
                continue
            payload = response.json()
        except Exception:
            continue

        sections = payload.get("response", {}).get("sections", [])
        hits = []
        for section in sections:
            hits.extend(section.get("hits", []))

        best_result = choose_best_genius_hit(hits, title, artist, track)
        if not best_result:
            continue

        song_url = best_result.get("url")
        if not song_url:
            continue

        try:
            page = requests.get(song_url, timeout=10, headers=GENIUS_HEADERS)
        except Exception:
            continue
        if not page.ok:
            continue

        lyrics_text = extract_genius_lyrics(page.text)
        if lyrics_text:
            artist_name = best_result.get("primary_artist", {}).get("name") or artist or "Unknown artist"
            song_title = best_result.get("title") or track or title
            return lyrics_text, f"{artist_name} - {song_title}", song_url
    return None


def fetch_lrclib_lyrics(title, artist, track, source_url):
    for search_query in build_lyrics_queries(title, artist, track):
        try:
            lrclib_url = f"https://lrclib.net/api/search?q={quote_plus(search_query)}"
            response = requests.get(
                lrclib_url,
                timeout=10,
                headers={"User-Agent": "TargetBot/1.0"}
            )
            if not response.ok:
                continue
            results = response.json()
        except Exception:
            continue

        if not isinstance(results, list) or not results:
            continue

        best = choose_best_lrclib_match(results, title, artist, track)
        if not best:
            continue

        lyrics_text = best.get("plainLyrics") or best.get("syncedLyrics")
        if not lyrics_text:
            continue

        best_artist = best.get("artistName") or artist or "Unknown artist"
        best_track = best.get("trackName") or track or title
        return (lyrics_text, f"{best_artist} - {best_track}", source_url), "lrclib"
    return None


def fetch_musixmatch_lyrics(title, artist, track, source_url):
    api_key = os.environ.get("MUSIXMATCH_API_KEY")
    if not api_key:
        return None

    for search_query in build_lyrics_queries(title, artist, track):
        try:
            search_url = (
                "https://api.musixmatch.com/ws/1.1/track.search"
                f"?q_track_artist={quote_plus(search_query)}"
                f"&page_size=5&s_track_rating=desc&apikey={quote_plus(api_key)}"
            )
            response = requests.get(
                search_url,
                timeout=10,
                headers={"User-Agent": "TargetBot/1.0"},
            )
            if not response.ok:
                continue
            data = response.json()
        except Exception:
            continue

        track_list = (
            data.get("message", {})
            .get("body", {})
            .get("track_list", [])
        )
        if not track_list:
            continue

        best_track_data = None
        best_score = 0.0
        for item in track_list:
            track_data = item.get("track", {})
            score = score_lyrics_candidate(
                track_data.get("track_name") or "",
                track_data.get("artist_name") or "",
                title,
                artist,
                track,
            )
            if score > best_score:
                best_score = score
                best_track_data = track_data

        if not best_track_data or best_score < 0.72:
            continue

        track_id = best_track_data.get("track_id")
        if not track_id:
            continue

        try:
            lyrics_url = (
                "https://api.musixmatch.com/ws/1.1/track.lyrics.get"
                f"?track_id={track_id}&apikey={quote_plus(api_key)}"
            )
            response = requests.get(
                lyrics_url,
                timeout=10,
                headers={"User-Agent": "TargetBot/1.0"},
            )
            if not response.ok:
                continue
            data = response.json()
        except Exception:
            continue

        lyrics_text = (
            data.get("message", {})
            .get("body", {})
            .get("lyrics", {})
            .get("lyrics_body", "")
            .strip()
        )
        if not lyrics_text:
            continue

        lines = []
        for line in lyrics_text.splitlines():
            if "******* This Lyrics is NOT for Commercial use *******" in line:
                break
            if line.strip():
                lines.append(line.rstrip())
        lyrics_text = "\n".join(lines).strip()
        if not lyrics_text:
            continue

        best_artist = best_track_data.get("artist_name") or artist or "Unknown artist"
        best_name = best_track_data.get("track_name") or track or title
        return (lyrics_text, f"{best_artist} - {best_name}", source_url), "musixmatch"

    return None


def fetch_ovh_lyrics(title, artist, track, source_url):
    for candidate_artist, candidate_track in build_lyrics_pairs(title, artist, track):
        try:
            fallback_url = (
                f"https://api.lyrics.ovh/v1/"
                f"{quote_plus(candidate_artist)}/{quote_plus(candidate_track)}"
            )
            response = requests.get(
                fallback_url,
                timeout=10,
                headers={"User-Agent": "TargetBot/1.0"}
            )
            if not response.ok:
                continue
            data = response.json()
        except Exception:
            continue

        lyrics_text = data.get("lyrics", "").strip()
        if not lyrics_text:
            continue

        score = score_lyrics_candidate(candidate_track, candidate_artist, title, artist, track)
        if score < 0.68:
            continue

        return (lyrics_text, f"{candidate_artist} - {candidate_track}", source_url), "lyrics.ovh"
    return None


def fetch_lyrics_payload(current=None, manual_query=None):
    if manual_query:
        title = manual_query
        artist = None
        track = manual_query
        source_url = getattr(current, "webpage_url", None) if current else None
    else:
        title = current.title
        artist = getattr(current, "artist", None)
        track = getattr(current, "track", None)
        source_url = getattr(current, "webpage_url", None)

    genius_result = fetch_genius_lyrics(title, artist, track)
    if genius_result:
        return genius_result, "genius"

    lrclib_result = fetch_lrclib_lyrics(title, artist, track, source_url)
    if lrclib_result:
        return lrclib_result

    musixmatch_result = fetch_musixmatch_lyrics(title, artist, track, source_url)
    if musixmatch_result:
        return musixmatch_result

    ovh_result = fetch_ovh_lyrics(title, artist, track, source_url)
    if ovh_result:
        return ovh_result

    return None, None


class LyricsPaginatorView(discord.ui.View):
    def __init__(self, requester, found_label, chunks, source_url=None):
        super().__init__(timeout=180)
        self.requester = requester
        self.found_label = found_label
        self.chunks = chunks
        self.source_url = source_url
        self.page_index = 0
        self.message = None
        self._refresh_buttons()

    def _refresh_buttons(self):
        self.prev_button.disabled = self.page_index == 0
        self.next_button.disabled = self.page_index >= len(self.chunks) - 1

    def current_embed(self):
        return build_lyrics_embed(
            self.found_label,
            self.chunks,
            self.page_index,
            self.source_url
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.requester.id:
            await interaction.response.send_message("This isn't your lyrics panel.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Previous Page", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_index -= 1
        self._refresh_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_index += 1
        self._refresh_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)


async def send_lyrics_panel(send_callable, requester, guild_id=None, manual_query=None):
    current = music_now.get(guild_id) if guild_id is not None else None
    if current is None and not manual_query:
        return None

    payload, source_name = fetch_lyrics_payload(current, manual_query=manual_query)
    if not payload:
        return False

    lyrics_text, found_label, source_url = payload
    if source_name != "genius":
        search_label = manual_query or current.title
        await send_callable(f"Genius missed it, trying **{source_name}** for: **{search_label}**")

    lyrics_text = format_lyrics_for_embed(lyrics_text)
    chunks = split_lyrics_chunks(lyrics_text, chunk_size=900)
    view = LyricsPaginatorView(requester, found_label, chunks, source_url)
    message = await send_callable(embed=view.current_embed(), view=view)
    view.message = message
    return message


@bot.command()
async def lyrics(ctx, *, song_name=None):
    guild = ctx.guild

    current = music_now.get(guild.id)
    if current is None and not song_name:
        return await ctx.send("Nothing is playing right now.")

    search_label = song_name or current.title
    await ctx.send(f"Searching lyrics for: **{search_label}**")

    try:
        message = await send_lyrics_panel(ctx.send, ctx.author, guild.id if current else None, manual_query=song_name)
        if message is None:
            await ctx.send("Nothing is playing right now.")
        elif message is False:
            if song_name:
                await ctx.send("Failed to find lyrics for that song.")
            else:
                await ctx.send("Failed to find lyrics please try to use `!lyrics <song name>`")
    except Exception as e:
        print(f"Lyrics error: {e}")
        await ctx.send("Error getting lyrics.")

# ======= ON JOIN =========
@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(
        title="👋 Hi, I'm TargetBot",
        description=(
            "Thanks for adding me to your server.\n"
            "I handle economy, fishing, delivery, pets, companies, minigames, and music.\n\n"
            "Use `!help` to browse all commands by category."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(name="💰 Economy", value="`!daily` `!balance` `!transfer` `!deposit` `!leaderboard`", inline=False)
    embed.add_field(name="🎣 Fishing", value="`!fish` `!fishshop` `!hookshop` `!baitshop`", inline=False)
    embed.add_field(name="🚦 Delivery", value="`!delivery` `!vehicleshop`", inline=False)
    embed.add_field(name="🐾 Pet", value="`!pet` `!petshop` `!feed`", inline=False)
    embed.add_field(name="🏢 Company", value="`!company` `!company buy` `!company upgrade` `!company collect`", inline=False)
    embed.add_field(name="⬆️ Progression", value="`!level` `!custom`", inline=False)
    embed.add_field(name="🚔 Crime", value="`!rob` `!escape` `!bail`", inline=False)
    embed.add_field(name="🎰 Gambling", value="`!slots` `!blackjack`", inline=False)
    embed.add_field(name="🎧 Music", value="`!play` `!skip` `!queue` `!lyrics`", inline=False)

    embed.set_footer(text="Use !help for the full interactive command panel.")

    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed)
            break


# ================ HELP ==================
HELP_CATEGORIES = {
    "economy": {
        "title": "💰 Economy",
        "description": (
            "`!daily` — Daily reward\n"
            "`!weekly` — Weekly reward\n"
            "`!monthly` — Monthly reward\n"
            "`!balance` / `!bal [@user]` — Check balance\n"
            "`!transfer @user <amount>` — Send coins\n"
            "`!deposit` / `!dep <amount>` — Deposit to bank\n"
            "`!withdraw` / `!wit <amount>` — Withdraw from bank\n"
            "`!leaderboard` / `!lb` / `!rich` — Richest players\n"
            "`!private` / `!prv` — Hide your balance\n"
            "`!unprivate` / `!unprv` — Show balance again\n"
            "`!blockpay` — Block incoming transfers\n"
            "`!unblockpay` — Allow transfers again"
        ),
        "emoji": "💰",
    },
    "gambling": {
        "title": "🎰 Gambling",
        "description": (
            "`!slots <amount>` — Spin the slot machine\n"
            "`!blackjack <amount>` / `!bj` — Play blackjack"
        ),
        "emoji": "🎰",
    },
    "jail": {
        "title": "🚔 Jail / Crime",
        "description": (
            "`!rob @user` — Attempt a robbery\n"
            "`!guard` — Jail guard event\n"
            "`!escape` — Try to escape jail\n"
            "`!bail` — Pay coins to leave jail"
        ),
        "emoji": "🚔",
    },
    "fishing": {
        "title": "🎣 Fishing",
        "description": (
            "`!fish` — Start a fishing minigame\n"
            "`!fishshop` — Browse & buy rods (button embed)\n"
            "`!rod <n>` — Equip a rod you own\n"
            "`!hookshop` / `!hshop` — Browse & buy hooks\n"
            "`!hook <n>` — Equip a hook you own\n"
            "`!baitshop` / `!bshop` — Interactive bait shop\n"
            "`!buybait <n> <amount>` — Buy bait via command\n"
            "`!bait <n>` — Equip a bait you have in stock"
        ),
        "emoji": "🎣",
    },
    "delivery": {
        "title": "🚦 Delivery",
        "description": (
            "`!delivery` — Start a delivery minigame\n"
            "Follow direction buttons before the timer runs out\n"
            "Reward depends on speed, vehicle & customer type\n\n"
            "`!vehicleshop` / `!vshop` — Browse & buy vehicles\n"
            "`!vehicle <n>` / `!veh` — Equip a vehicle"
        ),
        "emoji": "🚦",
    },
    "pet": {
        "title": "🐾 Pet",
        "description": (
            "`!pet` — View your pet name, level, XP & hunger\n"
            "`!petshop` — Buy a pet or food (button embed)\n"
            "`!feed` — Feed your pet to restore hunger\n"
            "`!rename` — Rename your pet or company (10,000 coins)\n\n"
            "**Pets & bonuses:**\n"
            "🐱 Cat — +fishing rare/legendary chance\n"
            "🐶 Dog — +delivery reward %\n"
            "🐦 Parrot — +XP from all activities\n"
            "🐢 Turtle — +passive bank interest\n"
            "🦊 Fox — +rob success & reduced jail time"
        ),
        "emoji": "🐾",
    },
    "company": {
        "title": "🏢 Company",
        "description": (
            "`!company` — View your company & hourly income\n"
            "First use: bot asks for name & one-word concept\n"
            "💡 Example: Name `KFC`, concept `Chicken`\n\n"
            "`!company buy <amount>` — Buy units of your resource\n"
            "`!company upgrade` — Spend resources to level up\n"
            "`!company collect` — Collect hourly earnings\n\n"
            "Higher level = more coins generated per hour"
        ),
        "emoji": "🏢",
    },
    "progression": {
        "title": "⬆️ Progression & Custom",
        "description": (
            "`!level [@user]` / `!rank` / `!lvl`\n"
            "View general level, XP bar, rod, hook & vehicle\n\n"
            "`!custom` — Open the customisation menu\n"
            "Currently: name your own custom rod\n"
            "Custom rod always mirrors your best owned rod stats"
        ),
        "emoji": "⬆️",
    },
    "minigames": {
        "title": "🎮 Minigames",
        "description": (
            "`!jerk` — Tap XP minigame\n"
            "`!bazooka @user` — Reaction fight minigame"
        ),
        "emoji": "🎮",
    },
    "social": {
        "title": "💘 Social / Fun",
        "description": (
            "`!ship [@user1] [@user2]` — Compatibility check\n"
            "`!date` — Random date event\n"
            "`!stalk [@user]` — Creepy stalker event\n"
            "`!gay` — Random percentage picker\n"
            "`!wanted` — Generate a wanted poster\n"
            "`!expose @user1 @user2` — Expose two people"
        ),
        "emoji": "💘",
    },
    "utility": {
        "title": "🕵️ Utility",
        "description": (
            "`!help` — Open this help panel\n"
            "`!commands` / `!cmds` — Commands website link\n"
            "`!avatar [@user]` / `!av` — Show someone's avatar\n"
            "`!afk <reason>` — Set AFK status\n"
            "`!entity [@user]` — Scan a user"
        ),
        "emoji": "🕵️",
    },
    "music": {
        "title": "🎧 Music",
        "description": (
            "`!play <song>` / `!p` — Play a song or add to queue\n"
            "`!search <query>` — Search SoundCloud\n"
            "`!pause` — Pause or resume\n"
            "`!skip` — Skip current song\n"
            "`!stop` — Stop and clear queue\n"
            "`!queue` — Show the queue\n"
            "`!np` — Now playing\n"
            "`!lyrics [song]` — Fetch lyrics (Genius first)\n"
            "`!join` / `!leave` — Voice channel controls"
        ),
        "emoji": "🎧",
    },
}


class HelpMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        # Row 0
        self._add_button("economy",     "Economy",      "💰", 0)
        self._add_button("gambling",    "Gambling",     "🎰", 0)
        self._add_button("jail",        "Jail/Crime",   "🚔", 0)
        self._add_button("fishing",     "Fishing",      "🎣", 0)
        # Row 1
        self._add_button("delivery",    "Delivery",     "🚦", 1)
        self._add_button("pet",         "Pet",          "🐾", 1)
        self._add_button("company",     "Company",      "🏢", 1)
        self._add_button("progression", "Progression",  "⬆️", 1)
        # Row 2
        self._add_button("minigames",   "Minigames",    "🎮", 2)
        self._add_button("social",      "Social/Fun",   "💘", 2)
        self._add_button("utility",     "Utility",      "🕵️", 2)
        self._add_button("music",       "Music",        "🎧", 2)

    def _add_button(self, key, label, emoji, row):
        button = discord.ui.Button(label=label, emoji=emoji, style=discord.ButtonStyle.primary, row=row)
        button.callback = self._make_callback(key)
        self.add_item(button)

    def _make_callback(self, key):
        async def callback(interaction: discord.Interaction):
            config = HELP_CATEGORIES[key]
            embed = discord.Embed(
                title=config["title"],
                description=config["description"],
                color=discord.Color.blurple(),
            )
            embed.set_footer(text="TargetBot help menu")
            try:
                await interaction.user.send(embed=embed)
                await interaction.response.send_message(
                    f"Sent the **{config['title']}** commands to your DMs.",
                    ephemeral=True,
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "I couldn't DM you. Please enable DMs from this server and try again.",
                    ephemeral=True,
                )
        return callback


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="How can we help u sir?",
        description="Choose a category below and I'll DM you the command list.",
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="TargetBot help center")
    await ctx.send(embed=embed, view=HelpMenuView())


# ======= AVATAR =========

@bot.command(aliases=["av"])
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.blurple()
    )
    embed.set_image(url=member.display_avatar.url)

    await ctx.send(embed=embed)
        

# ============ WANTED ============
@bot.command()
async def wanted(ctx):
    members = [m for m in ctx.guild.members if not m.bot]
    person = random.choice(members)

    crimes = [
        "nga dress up as an old granny and rape kids 🥷",
        "Stop stealing u blackass nga 🍗",
        "Raped 4 kids in the woods 🙀",
        "Spamming N word too loud in VCs 🎙️",
        "He likes Kids 💔",
        "Gayass 🏳️‍🌈",
        "Jorking it in VC 💦",
        "Sending moaning voice messages 🎤",
        "Sending his nudes in NFSW servers 😭 ",
        "Blaming His wifi, retarted nger",
        "He rape animals 🐵",
        "catch em simping on a 9yo",
    ]

    reward = random.randint(100, 99999)
    crime = random.choice(crimes)

    await ctx.send(f'{person.mention}')

    embed = discord.Embed(
        title="WANTED, EVEN IF DEAD, WE WILL RAPE HIS ASS",
        color=discord.Color.yellow()
    )
    embed.set_thumbnail(url=person.display_avatar.url)
    embed.add_field(name="Outlaw", value=person.mention, inline=True)
    embed.add_field(name="Reward", value=f"${reward:,}", inline=True)
    embed.add_field(name="Crime", value=crime, inline=False)
    embed.set_footer(text="Wanted by the BBC 👨🏿‍🦲")

    await ctx.send(embed=embed)


# ============ SHIP ============
@bot.command()
async def ship(ctx, member1: discord.Member = None, member2: discord.Member = None):
    members = [m for m in ctx.guild.members if not m.bot]

    if member1 is None and member2 is None:
        member1, member2 = random.sample(members, 2)
    elif member2 is None:
        member2 = random.choice([m for m in members if m != member1])

    percentage = random.randint(0, 100)

    if percentage < 20:
        comment = "Absolutely no chance 💀"
        color = discord.Color.dark_red()
        bar = "💔💔💔💔💔"
    elif percentage < 40:
        comment = "Meh, maybe as friends 🤷"
        color = discord.Color.orange()
        bar = "❤️💔💔💔💔"
    elif percentage < 60:
        comment = "There's something there... 👀"
        color = discord.Color.yellow()
        bar = "❤️❤️💔💔💔"
    elif percentage < 80:
        comment = "Cute couple fr 🥰"
        color = discord.Color.green()
        bar = "❤️❤️❤️💔💔"
    else:
        comment = "SOULMATES!! 💍🔥"
        color = discord.Color.red()
        bar = "❤️❤️❤️❤️❤️"

    ship_name = member1.display_name[:len(member1.display_name)//2] + member2.display_name[len(member2.display_name)//2:]

    await ctx.send(f'{member1.mention} {member2.mention}')

    embed = discord.Embed(
        title=f"💘 Ship: {ship_name}",
        description=f"{member1.mention} + {member2.mention}",
        color=color
    )
    embed.add_field(name="Compatibility", value=f"**{percentage}%** {bar}", inline=False)
    embed.add_field(name="Verdict", value=comment, inline=False)
    embed.set_footer(text="Powered by the LoveCalculatorXAiden 💘")

    await ctx.send(embed=embed)


# ============ STALK ============
@bot.command()
async def stalk(ctx, member: discord.Member = None):
    members = [m for m in ctx.guild.members if not m.bot]
    person = member if member else random.choice(members)

    import asyncio

    await ctx.send(f'{person.mention}')

    messages = [
        ("👁️", "Yeah… you nga.\nDon’t act confused dumbass.\nWe BEEN watching you all time u bitchass nigger.", discord.Color.dark_gray()),

        ("👁️", f"You showed up {random.randint(6,25)} times today looking for femboys.\nNo lifer ass nigga, go fuck ur self.", discord.Color.dark_red()),

        ("👁️", f"{random.randint(1,4)}:{random.randint(10,59)}AM.\nStill awake.\nNo messages.\nJust lurking like a bitchass nga.", discord.Color.from_rgb(15, 0, 0)),

        ("👁️", "You move server to server looking for kids like nobody notices.\nWe notice EVERYTHING NIGGA.", discord.Color.dark_gray()),

        ("👁️", "You type something… then delete it.\nOver and over.\nScared to speak dumbass hoe?", discord.Color.dark_red()),

        ("👁️", "Somebody here laughs at you behind your back.\nYou even call them bro.\nThat’s crazy, u meant to be raped bitch.", discord.Color.from_rgb(25, 0, 25)),

        ("👁️", "Open Discord.\nClose it.\nOpen it again.\nYou’re addicted. \ntouch some grass Nigger", discord.Color.dark_blue()),

        ("👁️", "Sleep? Nah.\nOverthinking and Watching Porn hits harder, right?", discord.Color.from_rgb(10, 0, 0)),

        ("👁️", "You thought this was a joke command.\nWe’re literally reading you right now. \nChopped ass nigga fuck ur self", discord.Color.from_rgb(5, 0, 0)),

        ("👁️", "Keep laughing.\nKeep scrolling. \nKeep Raping Kids. \nWe not going anywhere.", discord.Color.dark_red()),
    ]

    for emoji, text, color in messages:
        embed = discord.Embed(
            description=f"**{text}**",
            color=color
        )
        embed.set_author(name=f"{emoji}  {person.display_name}  {emoji}")
        embed.set_thumbnail(url=person.display_avatar.url)
        await asyncio.sleep(2)
        await ctx.send(embed=embed)

    final = discord.Embed(
        title="You Retard.",
        description=(
            f"*We got everything we needed on you, {person.mention}.*\n\n"
            "*Your habits… your late nights… the way you move quiet and jork ur meat.*\n\n"
            "**You’re predictable fucking retard.**\n\n"
            "Go ahead… pretend you don’t feel watched dumbass nigger."
        ),
        color=discord.Color.from_rgb(5, 0, 0)
    )
    final.set_image(url=person.display_avatar.url)
    final.set_footer(text="We’ll Fuck ur tiny ass.")

    await asyncio.sleep(3)
    await ctx.send(embed=final)

# ===== AFK SYSTEM =====
import json
from datetime import datetime, timezone

afk_users = {}

def save_afk():
    with open("afk.json", "w") as f:
        json.dump(afk_users, f)

def load_afk():
    global afk_users
    try:
        with open("afk.json", "r") as f:
            afk_users = json.load(f)
            afk_users = {int(k): v for k, v in afk_users.items()}
    except:
        afk_users = {}

load_afk()


@bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = {
        "reason": reason,
        "time": str(discord.utils.utcnow())
    }

    save_afk()

    embed = discord.Embed(
        description=f"{ctx.author.mention} is now AFK: **{reason}**",
        color=discord.Color.light_gray()
    )
    embed.set_footer(text="They will be notified when mentioned 💤")
    await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in afk_users:
        data = afk_users.pop(message.author.id)
        save_afk()

        try:
            afk_time = datetime.fromisoformat(data["time"])
            now = datetime.now(timezone.utc)
            diff = now - afk_time
            total_minutes = int(diff.total_seconds() // 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60

            if hours > 0:
                time_str = f"**{hours}h {minutes}m**"
            elif minutes > 0:
                time_str = f"**{minutes}m**"
            else:
                time_str = "**less than a minute**"

            await message.channel.send(f"Welcome back {message.author.mention}! You were AFK for {time_str} 👋")
        except:
            await message.channel.send(f"{message.author.mention} is no longer AFK.")

    for user in message.mentions:
        if user.id in afk_users:
            data = afk_users[user.id]
            await message.channel.send(
                f"{user.mention} is AFK: **{data['reason']}**"
            )

    await bot.process_commands(message)and nga

# ============= Bazooka ==============
@bot.command()
async def bazooka(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("💀 Tag someone to blast.")
        return

    shooter = ctx.author
    target = member

    if shooter == target:
        await ctx.send("💀 You can't bazooka yourself.")
        return

    for p in [shooter, target]:
        if p.id not in player_health:
            player_health[p.id] = 100
        if p.id not in player_lives:
            player_lives[p.id] = 3
        if p.id not in player_points:
            player_points[p.id] = 10

    correct_word = generate_random_word(random.randint(4, 8))
    await ctx.send(f"{shooter.mention} ⚠️ QUICK! Type this exact word to fire at {target.mention}:\n`{correct_word}`\nYou have 5 seconds!")

    def check(m):
        return m.author == shooter and m.content == correct_word and m.channel == ctx.channel

    try:
        await bot.wait_for("message", timeout=7.5, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"⏱️ {shooter.mention} TOO SLOW or typed wrong… attack FAILED 💀\nThe word was **{correct_word}**")
        return

    damage = random.randint(20, 60)
    player_health[target.id] -= damage

    if player_health[target.id] <= 0:
        player_health[target.id] = 100
        if player_lives[target.id] > 0:
            player_lives[target.id] -= 1
        player_points[target.id] = max(0, player_points[target.id] - 3)
        player_points[shooter.id] += 5
        player_lives[shooter.id] += 1
        desc = (
            f"💥 {shooter.mention} OBLITERATED {target.mention} (-{damage})\n\n"
            f"☠️ {target.mention} lost 1 life & 3 pts\n"
            f"🔥 {shooter.mention} gained 5 pts & stole 1 life\n\n"
            f"🔄 Respawned with 100 HP"
        )
        color = discord.Color.dark_red()
    else:
        desc = (
            f"💥 {shooter.mention} hit {target.mention} for **{damage} dmg**\n"
            f"❤️ HP left: **{player_health[target.id]}**"
        )
        color = discord.Color.orange()

    embed = discord.Embed(title="🚀 BAZOOKA", description=desc, color=color)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="📊 Target", value=f"Lives: {player_lives[target.id]} | Points: {player_points[target.id]}", inline=False)
    embed.add_field(name="📊 Shooter", value=f"Lives: {player_lives[shooter.id]} | Points: {player_points[shooter.id]}", inline=False)
    await ctx.send(embed=embed)
    save_data()
    

# ============ DATE ============
@bot.command()
async def date(ctx):
    members = [m for m in ctx.guild.members if not m.bot]
    if len(members) < 2:
        await ctx.send("Not enough members to play matchmaker!")
        return

    person1, person2 = random.sample(members, 2)
    await ctx.send(f'{person1.mention} {person2.mention}')

    embed = discord.Embed(
        title="💘 Date Request!",
        description=f"{person1.mention} do u wanna date {person2.mention}?",
        color=discord.Color.pink()
    )
    embed.set_footer(text="You have 60 seconds to respond!")
    view = DateView(person1, person2, ctx.channel)
    await ctx.send(embed=embed, view=view)

class DateView(discord.ui.View):
    def __init__(self, person1, person2, channel):
        super().__init__(timeout=60)
        self.person1 = person1
        self.person2 = person2
        self.channel = channel
        self.answered = False

    async def on_timeout(self):
        if self.answered:
            return
        for item in self.children:
            item.disabled = True
        embed = discord.Embed(
            title="💔 Timed Out...",
            description=f"{self.person1.mention} left {self.person2.mention} on read 😭",
            color=discord.Color.dark_red()
        )
        await self.channel.send(embed=embed)

    @discord.ui.button(label='Accept 💚', style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.person1:
            await interaction.response.send_message("This isn't your request!", ephemeral=True)
            return
        self.answered = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f'🎉 Congrats {self.person1.mention} and {self.person2.mention}, you are now a couple! 💑')

    @discord.ui.button(label='Decline ❌', style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.person1:
            await interaction.response.send_message("This isn't your request!", ephemeral=True)
            return
        self.answered = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f'looks like {self.person1.mention} rejected {self.person2.mention} 💔')


# ============ SPIN ============

@bot.command()
async def gay(ctx):
    members = [m for m in ctx.guild.members if not m.bot]
    person = random.choice(members)

    spinning = discord.Embed(
        title="Spinning the gayass wheel...",
        description="who's gonna be the jew retarted nigga 👀",
        color=discord.Color.yellow()
    )
    msg = await ctx.send(embed=spinning)

    await asyncio.sleep(3)

    await ctx.send(f'{person.mention}')

    result = discord.Embed(
        title="LMFAO THIS RETARTED GAYASS",
        description=f"The wheel landed on the motherfucker {person.mention}!\n\n**congrats gayass nigga**",
        color=discord.Color.purple()
    )
    result.set_thumbnail(url=person.display_avatar.url)
    result.set_footer(text="if u read this, go fuck ur self nigga lmfao gayass")
    await msg.edit(embed=result)


# ============ FARM / TAP TAP ============
class TapTapView(discord.ui.View):
    def __init__(self, user, buttons, correct):
        super().__init__(timeout=3)
        self.user = user
        self.correct = correct
        self.answered_correct = False
        self.answered_wrong = False

        for emoji in buttons:
            button = discord.ui.Button(label=emoji, style=discord.ButtonStyle.primary)
            button.callback = self.make_callback(emoji)
            self.add_item(button)

    def make_callback(self, emoji):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.user:
                await interaction.response.send_message("This isn't your game!", ephemeral=True)
                return
            if emoji == self.correct:
                self.answered_correct = True
            else:
                self.answered_wrong = True
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            self.stop()
        return callback

async def tap_tap(ctx, user):
    score = 0
    rounds = 5

    for i in range(rounds):
        buttons = ["🦴", "🍆", "🍑"]
        correct = random.choice(buttons)
        random.shuffle(buttons)

        embed = discord.Embed(
            title=f"🎯 Jerking off! Round {i+1}/{rounds}",
            description=f"Tap **{correct}** before time runs out!\n\n✅ Score: {score}/{rounds}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="You have 3 seconds! ⏱️")

        view = TapTapView(user, buttons, correct)
        msg = await ctx.send(embed=embed, view=view)

        await asyncio.sleep(3)

        if view.answered_correct:
            score += 1
            result_embed = discord.Embed(description=f"✅ Correct! +1", color=discord.Color.green())
        elif view.answered_wrong:
            result_embed = discord.Embed(description=f"❌ Wrong Hit!", color=discord.Color.red())
        else:
            result_embed = discord.Embed(description=f"⏱️ Dont Stop!", color=discord.Color.orange())

        for item in view.children:
            item.disabled = True
        await msg.edit(view=view)
        await ctx.send(embed=result_embed)
        await asyncio.sleep(1)

    goodjob = discord.Embed(
        title="🥵 Good job!",
        description=f"{user.mention} you have cummed! 💦",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=goodjob)
    await asyncio.sleep(1)

    if score == rounds:
        xp_gained = 50
        farm_xp[user.id] += xp_gained
        new_level = get_level(farm_xp[user.id])
        leveled_up = new_level > farm_level[user.id]
        farm_level[user.id] = new_level
        save_data()

        final = discord.Embed(
            title="🏆 PERFECT! 5/5!",
            description=f"🎉 {user.mention} you nailed it!\n\n+**{xp_gained} XP** earned!\n**Total XP:** {farm_xp[user.id]}\n**Level:** {farm_level[user.id]}",
            color=discord.Color.gold()
        )
        if leveled_up:
            final.add_field(name="🆙 LEVEL UP!", value=f"You are now Level **{farm_level[user.id]}**!", inline=False)
    else:
        xp_gained = score * 5
        farm_xp[user.id] += xp_gained
        farm_level[user.id] = get_level(farm_xp[user.id])
        save_data()

        final = discord.Embed(
            title=f"Result: {score}/{rounds}",
            description=f"{user.mention} you got **{score}/5**\n\n+**{xp_gained} XP** earned\n**Total XP:** {farm_xp[user.id]}\n**Level:** {farm_level[user.id]}",
            color=discord.Color.green() if score >= 3 else discord.Color.red()
        )
        final.set_footer(text="Get 5/5 for full XP! 💪")

    await ctx.send(embed=final)
    jerk_active.discard(ctx.guild.id)

@bot.command()
async def jerk(ctx):
    user = ctx.author

    if ctx.guild.id in jerk_active:
        await ctx.send(f"⏳ Someone is already playing! Wait for them to finish 💀")
        return

    last_used = jerk_cooldown.get(user.id)
    if last_used:
        elapsed = discord.utils.utcnow().timestamp() - last_used
        if elapsed < 120:
            remaining = int(120 - elapsed)
            await ctx.send(f"⏱️ Cooldown! Wait **{remaining}s** before jerking again 💀")
            return

    jerk_cooldown[user.id] = discord.utils.utcnow().timestamp()
    jerk_active.add(ctx.guild.id)

    if user.id not in farm_xp:
        farm_xp[user.id] = 0
    if user.id not in farm_level:
        farm_level[user.id] = 0

    embed = discord.Embed(
        title="Masturbate",
        description=f"Welcome {user.mention}!\n\n**XP:** {farm_xp[user.id]}\n**Level:** {farm_level[user.id]}\n\n Starting **Jerking** Minigame... get ready! 🎯",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    await asyncio.sleep(2)
    await tap_tap(ctx, user)

    # ============ EXPOSE ============
expose_evidence = [
    "Was googling 'how to be cool' at 2AM 🔍",
    "Cried during a kids movie 😭",
    "Has 847 unsent messages to their crush 💌",
    "Talked to themselves in the mirror for 20 minutes 🪞",
    "Their search history is actually criminal 🤭",
    "Practiced a handshake alone for 30 minutes 🤝",
    "Laughed at their own joke before finishing it 💀",
    "Fell asleep on the keyboard and sent gibberish to their crush ⌨️",
    "Has a folder named 'definitely not important' on their desktop 📁",
    "Googled their own name 3 times this week 🕵️",
    "Rehearsed an argument in the shower and lost 🚿",
    "Liked a 3 year old photo while stalking someone's profile 📸",
    "Set 7 alarms and ignored all of them ⏰",
    "Replied 'you too' when the waiter said enjoy your meal 🍽️",
    "Waved back at someone who wasn't waving at them 👋",
    "Spent 45 mins choosing what to watch then gave up 📺",
    "Sent a voice message then immediately regretted it 🎤",
    "Typed a paragraph then deleted it and said 'lol' 📱",
    "Has been 'about to sleep' for 3 hours 😴",
    "Googled a word they already knew just to make sure 📖",
]

class ExposeView(discord.ui.View):
    def __init__(self, requester, accomplice, victim, channel):
        super().__init__(timeout=60)
        self.requester = requester
        self.accomplice = accomplice
        self.victim = victim
        self.channel = channel
        self.answered = False

    async def on_timeout(self):
        if self.answered:
            return
        embed = discord.Embed(
            title="💨 Operation Failed",
            description=f"{self.accomplice.mention} chickened out... the mission is off 💀",
            color=discord.Color.dark_gray()
        )
        await self.channel.send(embed=embed)

    @discord.ui.button(label='Accept 🤝', style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.accomplice:
            await interaction.response.send_message("This isn't your request!", ephemeral=True)
            return
        self.answered = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        evidence = random.sample(expose_evidence, 5)

        await self.channel.send(f'{self.victim.mention}')

        embed = discord.Embed(
            title="🔍 OFFICIAL EXPOSURE REPORT",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="📋 Subject", value=self.victim.mention, inline=True)
        embed.add_field(name="🕵️ Filed by", value=f"{self.requester.mention} & {self.accomplice.mention}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        for i, ev in enumerate(evidence, 1):
            embed.add_field(name=f"📌 Exhibit {chr(64+i)}", value=ev, inline=False)

        embed.add_field(name="⚖️ Verdict", value="**Fully Exposed. No recovery possible. 💀**", inline=False)
        embed.set_thumbnail(url=self.victim.display_avatar.url)
        embed.set_footer(text="This report has been filed with the server authorities 🔏")
        await self.channel.send(embed=embed)

    @discord.ui.button(label='Decline ❌', style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.accomplice:
            await interaction.response.send_message("This isn't your request!", ephemeral=True)
            return
        self.answered = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        embed = discord.Embed(
            title="💨 Operation Cancelled",
            description=f"{self.accomplice.mention} backed out like a coward 💀",
            color=discord.Color.dark_gray()
        )
        await self.channel.send(embed=embed)

@bot.command()
async def expose(ctx, accomplice: discord.Member = None, victim: discord.Member = None):
    if accomplice is None or victim is None:
        await ctx.send("Usage: `!expose @accomplice @victim`")
        return
    if accomplice == ctx.author:
        await ctx.send("You can't be your own accomplice 💀")
        return
    if victim == ctx.author or victim == accomplice:
        await ctx.send("Nice try 💀")
        return

    await ctx.send(f'{accomplice.mention}')

    embed = discord.Embed(
        title="🕵️ Exposure Request",
        description=f"{ctx.author.mention} wants you to help expose {victim.mention}!\n\nAre you in? 👀",
        color=discord.Color.dark_red()
    )
    embed.set_footer(text="You have 60 seconds to decide!")
    view = ExposeView(ctx.author, accomplice, victim, ctx.channel)
    await ctx.send(embed=embed, view=view)


# ============ ENTITY ============
@bot.command()
async def entity(ctx, member: discord.Member = None):
    if ctx.author.id != OWNER_ID:
        last_used = entity_cooldown.get(ctx.author.id)
        if last_used:
            elapsed = discord.utils.utcnow().timestamp() - last_used
            if elapsed < 600:
                remaining = int(600 - elapsed)
                await ctx.send(f"⏱️ Cooldown! Wait **{remaining}s** before using this again.")
                return

    entity_cooldown[ctx.author.id] = discord.utils.utcnow().timestamp()

    members = [m for m in ctx.guild.members if not m.bot]
    person = member if member else random.choice(members)

    await ctx.send(f'{person.mention}')

    scanning_embed = discord.Embed(
        title="⚠️ ANOMALY DETECTED",
        description="Scanning server for supernatural activity...",
        color=discord.Color.dark_gray()
    )
    msg = await ctx.send(embed=scanning_embed)
    await asyncio.sleep(3)

    scan2 = discord.Embed(
        title="🔴 SIGNAL LOCKED",
        description=f"Entity has attached itself to **{person.display_name}**\n\nInitiating deep scan...",
        color=discord.Color.from_rgb(30, 0, 0)
    )
    scan2.set_thumbnail(url=person.display_avatar.url)
    await msg.edit(embed=scan2)
    await asyncio.sleep(3)

    messages = [
        (
            "📡 SCAN LAYER 1 — SURFACE",
            f"Username: **{person.display_name}**\nAccount Created: **{person.created_at.strftime('%B %d, %Y')}**\nJoined Server: **{person.joined_at.strftime('%B %d, %Y') if person.joined_at else 'Unknown'}**\n\n*Normal so far... digging deeper.*",
            discord.Color.from_rgb(20, 0, 0)
        ),
        (
            "📡 SCAN LAYER 2 — BEHAVIORAL",
            f"Times online past midnight: **{random.randint(47, 312)}**\nMessages deleted before sending: **{random.randint(200, 999)}**\nTimes opened Discord and closed it immediately: **{random.randint(50, 400)}**\n\n*Unusual patterns detected...*",
            discord.Color.from_rgb(30, 0, 0)
        ),
        (
            "📡 SCAN LAYER 3 — PSYCHOLOGICAL",
            f"Deepest fear detected: **Being forgotten** 🕯️\nRecurring thought at 3AM: **'{random.choice(['am i real', 'do they actually like me', 'something is watching me', 'why is it so quiet', 'i shouldnt be awake right now'])}**'\nLast nightmare was about: **{random.choice(['an empty room with one door that wouldnt open', 'everyone leaving at once', 'a figure standing at the foot of the bed', 'running but never moving'])}**\n\n*We are getting close to it...*",
            discord.Color.from_rgb(40, 0, 0)
        ),
        (
            "⚠️ SCAN LAYER 4 — ENTITY CONTACT",
            f"The entity has been with **{person.display_name}** since **{random.randint(1, 6)} years ago**\n\nIt watches when the room is dark.\nIt listens when you talk to yourself.\nIt was here before you joined this server.\n\n*It knows you noticed it.*",
            discord.Color.from_rgb(50, 0, 0)
        ),
        (
            "🔴 SCAN LAYER 5 — FINAL",
            f"Entity classification: **UNKNOWN**\nThreat level: **DO NOT ENGAGE**\nCurrent location: **Same room as {person.display_name}**\n\n*Turn around.*",
            discord.Color.from_rgb(60, 0, 0)
        ),
    ]

    for title, text, color in messages:
        embed = discord.Embed(title=title, description=text, color=color)
        embed.set_thumbnail(url=person.display_avatar.url)
        await asyncio.sleep(3)
        await ctx.send(embed=embed)

    await asyncio.sleep(3)

    final = discord.Embed(
        title="👁️ IT KNOWS YOU ARE READING THIS",
        description=(
            f"*{person.mention}.*\n\n"
            f"*It has been watching you for a long time.*\n\n"
            f"*The scan is over.*\n\n"
            f"*But it is not.*\n\n"
            f"**Don't look behind you.**"
        ),
        color=discord.Color.from_rgb(5, 0, 0)
    )
    final.set_image(url=person.display_avatar.url)
    final.set_footer(text="scan terminated. connection lost. 📡")
    await ctx.send(embed=final)

    await asyncio.sleep(120)

    scary_images = [
        "https://static.wikia.nocookie.net/villains/images/d/dc/Go_to_Sleep.png/revision/latest?cb=20241023095623",
        "https://media1.tenor.com/m/ninvfnBO1D4AAAAd/monster-scared.gif",
    ]

    try:
        await person.send(
            embed=discord.Embed(
                title="👁️",
                description="*We told you it wasn't over Dumbass nga.*\n\n*Did you really think ignoring would help?*\n\n**I always comeback.**",
                color=discord.Color.from_rgb(5, 0, 0)
            ).set_image(url=random.choice(scary_images))
        )
    except:
        pass


# ============ PING SPAM ============
@bot.command()
async def ping(ctx, member: discord.Member = None, times: int = 3):
    if ctx.author.id != OWNER_ID:
        await ctx.send("You don't have permission to use this command 💀")
        return
    if member is None:
        await ctx.send("Tag someone! `!ping @user 6`")
        return
    if times > 20:
        await ctx.send("Max is 20 💀")
        return

    await ctx.message.delete()

    messages = []
    for _ in range(times):
        msg = await ctx.send(member.mention)
        messages.append(msg)
        await asyncio.sleep(0)

    await asyncio.sleep(1)
    for msg in messages:
        await msg.delete()


# ================== LINK COMMAND ==================


@bot.command(name="commands", aliases=["cmds"])
async def commands_list(ctx):
    try:
        website_url = "https://unblended-paralyze-cursor.ngrok-free.dev"

        embed = discord.Embed(
            title="TargetBot Commands List",
            description="Click the button below to open our full commands website!",
            color=0x00ff00
        )
        embed.set_footer(text=f"Requested by {ctx.author}")

        view = discord.ui.View()
        button = discord.ui.Button(
            label="Click here to open the SITE",
            style=discord.ButtonStyle.link,
            url=website_url
        )
        view.add_item(button)

        try:
            await ctx.author.send(embed=embed, view=view)
            await ctx.send("✅ Sent you the commands link in DM!", delete_after=8)
        except discord.Forbidden:
            await ctx.send(embed=embed, view=view)

    except Exception as e:
        await ctx.send(f"Error: {e}")

def format_time(seconds_left):
    hours, remainder = divmod(seconds_left, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)

# ===== BANK SYSTEM =====

def get_bank(user_id):
    bank.setdefault(user_id, 0)
    return bank[user_id]


# === Private Balance ====
@bot.command(aliases=["prv"])
async def private(ctx):
    user = ctx.author.id
    private_bal[user] = True
    save_data()
    await ctx.send("🔒 your balance is now private")


@bot.command(aliases=["unprv"])
async def unprivate(ctx):
    user = ctx.author.id
    private_bal.pop(user, None)
    save_data()
    await ctx.send("🔓 your balance is no longer private")



# ===== CLAIM SYSTEM =====
async def claim_reward(ctx, reward_type, amount, cooldown_seconds):
    user_id = ctx.author.id
    claims = get_claims(user_id)
    now = int(time.time())
    last_claim = claims.get(reward_type, 0)

    if now - last_claim < cooldown_seconds:
        remaining = cooldown_seconds - (now - last_claim)
        await ctx.send(
            f"{ctx.author.mention} you already used `!{reward_type}`. "
            f"Try again in **{format_time(remaining)}**."
        )
        return

    claims[reward_type] = now
    wallet.setdefault(user_id, 0)
    wallet[user_id] += amount
    save_data()

    embed = discord.Embed(
        title=f"{reward_type.title()} Reward Claimed",
        description=f"{ctx.author.mention} got **{amount}** coins.\nBalance: **{wallet[user_id]}** coins",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command()
async def daily(ctx):
    await claim_reward(ctx, "daily", 500, 86400)


@bot.command()
async def weekly(ctx):
    await claim_reward(ctx, "weekly", 3500, 604800)


@bot.command()
async def monthly(ctx):
    await claim_reward(ctx, "monthly", 15000, 2592000)


class FishShopView(discord.ui.View):
    def __init__(self, requester, user_id):
        super().__init__(timeout=120)
        self.requester = requester
        self.user_id   = user_id
        self._build()

    def _build(self):
        self.clear_items()
        owned    = get_owned_rods(self.user_id)
        equipped = get_equipped_rod(self.user_id)
        row = 0
        col = 0
        for rod_name, rod_data in FISHING_RODS.items():
            is_equipped = rod_name == equipped
            is_owned    = rod_name in owned
            if is_equipped:
                label = f"✅ {rod_name}"
                style = discord.ButtonStyle.success
            elif is_owned:
                label = f"Equip {rod_name}"
                style = discord.ButtonStyle.secondary
            else:
                label = f"Buy {rod_name}"
                style = discord.ButtonStyle.primary
            btn = discord.ui.Button(label=label, style=style, row=row)
            btn.callback = self._make_cb(rod_name)
            self.add_item(btn)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _make_cb(self, rod_name):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("This isn\'t your shop.", ephemeral=True)
                return
            owned = get_owned_rods(self.user_id)
            if rod_name in owned:
                fishing_equipped_rod[self.user_id] = rod_name
                save_data()
                self._build()
                await interaction.response.edit_message(
                    embed=_build_fishshop_embed(self.user_id), view=self
                )
                return
            price = FISHING_RODS[rod_name]["price"]
            if get_wallet(self.user_id) < price:
                await interaction.response.send_message(
                    f"You need **{format_coins(price)}** coins for **{rod_name}**.", ephemeral=True
                )
                return
            wallet[self.user_id] -= price
            owned.append(rod_name)
            fishing_equipped_rod[self.user_id] = rod_name
            save_data()
            self._build()
            await interaction.response.edit_message(
                embed=_build_fishshop_embed(self.user_id), view=self
            )
        return callback


def _build_fishshop_embed(user_id):
    owned    = get_owned_rods(user_id)
    equipped = get_equipped_rod(user_id)
    embed = discord.Embed(
        title="🎣 Fishing Rod Shop",
        description=(
            f"**General Level:** {get_general_level(user_id)}\n"
            f"**Equipped:** {equipped}\n"
            f"**Wallet:** {format_coins(get_wallet(user_id))} coins"
        ),
        color=discord.Color.blurple()
    )
    for rod_name, rod_data in FISHING_RODS.items():
        if rod_name in owned:
            status = "✅ Equipped" if rod_name == equipped else "✅ Owned"
        else:
            status = f"💰 {format_coins(rod_data['price'])}"
        embed.add_field(
            name=rod_name,
            value=(
                f"{status}\n"
                f"Reward ×{rod_data['reward_multiplier']}\n"
                f"Reaction: {rod_data['reaction_time']}s"
            ),
            inline=True
        )
    embed.set_footer(text="Click Buy to purchase, click Equip or the rod name to switch.")
    return embed


@bot.command()
async def fishshop(ctx):
    user_id = ctx.author.id
    await ctx.send(embed=_build_fishshop_embed(user_id), view=FishShopView(ctx.author, user_id))



@bot.command()
async def rod(ctx, *, rod_name: str = None):
    user_id = ctx.author.id

    if not rod_name:
        equipped = get_equipped_rod(user_id)
        _, display_name, _ = resolve_rod_profile(user_id, equipped)
        await ctx.send(f"Your equipped rod is **{display_name}**.")
        return

    matched_rod = find_rod_name(rod_name)
    if not matched_rod and has_custom_rod(user_id):
        if rod_name.strip().lower() == get_custom_rod_display_name(user_id).lower():
            matched_rod = "Custom Rod"
    if not matched_rod:
        await ctx.send("Unknown rod. Use `!fishshop` to see available rods.")
        return

    if matched_rod not in get_owned_rods(user_id):
        await ctx.send(f"You don't own **{matched_rod}** yet.")
        return

    fishing_equipped_rod[user_id] = matched_rod
    save_data()
    _, display_name, _ = resolve_rod_profile(user_id, matched_rod)
    await ctx.send(f"Equipped **{display_name}**.")


@bot.command()
async def fish(ctx):
    user_id = ctx.author.id

    if user_id in fishing_active:
        await ctx.send("You're already fishing right now.")
        return

    fishing_active.add(user_id)

    try:
        owned = get_owned_rods(user_id)
        equipped = get_equipped_rod(user_id)
        if equipped not in owned:
            equipped = "Basic Rod"
            fishing_equipped_rod[user_id] = equipped

        base_rod_name, rod_display_name, rod_data = resolve_rod_profile(user_id, equipped)
        equipped_hook = get_equipped_hook(user_id)

        waiting_embed = discord.Embed(
            title="🎣 Fishing Time",
            description="You threw your bait into the water...\n\nWaiting for a fish...",
            color=discord.Color.blurple()
        )
        waiting_embed.set_footer(
            text=f"Rod: {rod_display_name} | Hook: {FISHING_HOOKS[equipped_hook]['emoji']} {equipped_hook}"
        )

        game_message = await ctx.send(embed=waiting_embed)
        await asyncio.sleep(2)

        position = random.randint(1, 9)
        grid = build_fishing_grid(position)

        prompt_embed = discord.Embed(
            title="🐟 A Fish Appeared!",
            description=(
                f"{grid}\n\n"
                "Quick! Type the position **(1-9)**!\n\n"
                "**Positions:**\n"
                "`1 2 3`\n"
                "`4 5 6`\n"
                "`7 8 9`"
            ),
            color=discord.Color.blue()
        )
        prompt_embed.set_footer(text=f"Rod: {rod_display_name} | Time: {rod_data['reaction_time']}s")
        await game_message.edit(embed=prompt_embed)

        def check(message):
            return (
                message.author.id == user_id
                and message.channel == ctx.channel
                and message.content.strip() in {str(i) for i in range(1, 10)}
            )

        try:
            reply = await bot.wait_for("message", timeout=rod_data["reaction_time"], check=check)
            guess = int(reply.content.strip())
        except asyncio.TimeoutError:
            guess = None

        if guess == position:
            used_bait = consume_bait(user_id)
            bait_data = FISHING_BAITS[used_bait]
            legendary_key = check_legendary_catch(user_id, base_rod_name, equipped_hook)

            if legendary_key:
                catch_key = legendary_key
                catch = FISHING_CATCHES[catch_key]
                reward = legendary_reward(catch_key, base_rod_name, user_id)
            else:
                catch_key = choose_fish_catch(base_rod_name, equipped_hook)
                catch = FISHING_CATCHES[catch_key]
                reward = int(catch["reward"] * rod_data["reward_multiplier"])

            reward = int(reward * (1.0 + bait_data["reward_bonus"]))
            reward = int(reward * pet_bonus_multiplier(user_id, "fishing"))

            wallet.setdefault(user_id, 0)
            wallet[user_id] += reward

            gen_xp_gain = random.randint(30, 60) if catch_key != "boot" else 5
            new_gen_level, gen_leveled = add_general_xp(user_id, gen_xp_gain)
            save_data()

            bait_line = (
                f"🪱 Bait: {bait_data['emoji']} {used_bait}"
                + (f" (+{int(bait_data['reward_bonus'] * 100)}% coins)" if bait_data["reward_bonus"] else "")
            )

            if legendary_key:
                result_embed = discord.Embed(
                    title=f"🌟 LEGENDARY CATCH! {catch['emoji']} {catch['name']}!",
                    description=(
                        f"{grid}\n\n"
                        f"⚠️ You pulled up a **{catch['name']}** from the depths!\n\n"
                        f"**+{format_coins(reward)} coins**\n"
                        f"**+{gen_xp_gain} General XP**\n"
                        f"{bait_line}"
                    ),
                    color=discord.Color.gold()
                )
            else:
                result_embed = discord.Embed(
                    title=f"{catch['emoji']} You got a {catch['name']}!",
                    description=(
                        f"{grid}\n\n"
                        f"**+{format_coins(reward)} coins**\n"
                        f"**+{gen_xp_gain} General XP**\n"
                        f"{bait_line}"
                    ),
                    color=discord.Color.green() if catch_key != "boot" else discord.Color.orange()
                )

            result_embed.add_field(name="⬆️ General Level", value=str(new_gen_level), inline=True)
            result_embed.add_field(name="🎣 Rod", value=rod_display_name, inline=True)
            result_embed.add_field(name="🪝 Hook", value=f"{FISHING_HOOKS[equipped_hook]['emoji']} {equipped_hook}", inline=True)
            if gen_leveled:
                result_embed.add_field(name="⬆️ General Level Up!", value=f"You reached **Level {new_gen_level}**!", inline=False)
        else:
            boot = FISHING_CATCHES["boot"]
            reward = int(boot["reward"] * rod_data["reward_multiplier"])
            reward = int(reward * pet_bonus_multiplier(user_id, "fishing"))
            wallet.setdefault(user_id, 0)
            wallet[user_id] += reward
            save_data()
            result_embed = discord.Embed(
                title=f"{boot['emoji']} You caught an {boot['name']}",
                description=(
                    f"{grid}\n\n"
                    "Wrong spot or too slow.\n"
                    f"**+{format_coins(reward)} coins**"
                ),
                color=discord.Color.orange()
            )
            result_embed.add_field(name="Rod", value=rod_display_name, inline=True)

        result_embed.set_footer(text=f"Wallet: {format_coins(get_wallet(user_id))} coins")
        await game_message.edit(embed=result_embed)

    finally:
        fishing_active.discard(user_id)



def sanitize_pet_name(name: str) -> str:
    cleaned = " ".join(name.strip().split())
    if not cleaned or len(cleaned) > 20:
        return ""
    return cleaned


def sanitize_company_name(name: str) -> str:
    cleaned = " ".join(name.strip().split())
    if not cleaned or len(cleaned) > COMPANY_NAME_MAX_LENGTH:
        return ""
    return cleaned


def sanitize_company_concept(concept: str) -> str:
    cleaned = concept.strip()
    if not cleaned or " " in cleaned:
        return ""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{0,15}", cleaned):
        return ""
    return cleaned.capitalize()


def sanitize_custom_rod_name(name: str) -> str:
    cleaned = " ".join(name.strip().split())
    if not cleaned or len(cleaned) > 20:
        return ""
    return cleaned


async def prompt_for_author_message(channel, author, prompt_text: str, *, timeout: float = 60.0):
    if prompt_text:
        await channel.send(prompt_text)

    def check(message):
        return message.author.id == author.id and message.channel == channel

    try:
        message = await bot.wait_for("message", timeout=timeout, check=check)
        return message.content.strip()
    except asyncio.TimeoutError:
        return None


def build_pet_embed(user_id: int, owner_name: str):
    pet = sync_pet_state(user_id)
    if not pet:
        return discord.Embed(
            title="Pet Profile",
            description="You don't have a pet yet. Use `!petshop` to adopt one.",
            color=discord.Color.orange(),
        )

    pet_info = PET_SHOP[pet["type"]]
    embed = discord.Embed(
        title=f"{pet_info['emoji']} {pet['name']}",
        description=f"{owner_name}'s loyal companion",
        color=discord.Color.teal(),
    )
    embed.add_field(name="Type", value=pet["type"], inline=True)
    embed.add_field(name="Level", value=str(pet["level"]), inline=True)
    embed.add_field(name="Hunger", value=f"{pet['hunger']}/100", inline=True)
    embed.add_field(name="Passive", value=pet_info["bonus_label"], inline=False)
    embed.add_field(name="Next Feed", value="Use `!feed` to keep bonuses active.", inline=False)
    if pet["hunger"] <= 15:
        embed.set_footer(text="Your pet is hungry, so its passive bonus is sleeping right now.")
    else:
        embed.set_footer(text=f"Passive bonus is active. Rename cost: 10,000 coins via !rename")
    return embed


class PetShopView(discord.ui.View):
    def __init__(self, requester, user_id: int):
        super().__init__(timeout=120)
        self.requester = requester
        self.user_id = user_id
        for index, (pet_name, pet_info) in enumerate(PET_SHOP.items()):
            button = discord.ui.Button(
                label=f"{pet_info['emoji']} {pet_name}",
                style=discord.ButtonStyle.primary,
                row=index // 2,
            )
            button.callback = self._make_callback(pet_name)
            self.add_item(button)

    def _make_callback(self, pet_name: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("This isn't your pet shop.", ephemeral=True)
                return
            if get_pet_record(self.user_id):
                await interaction.response.send_message("You already have a pet. One pet per user.", ephemeral=True)
                return
            price = PET_SHOP[pet_name]["price"]
            if get_wallet(self.user_id) < price:
                await interaction.response.send_message(
                    f"You need **{format_coins(price)}** coins to adopt **{pet_name}**.",
                    ephemeral=True,
                )
                return
            wallet[self.user_id] -= price
            pet_data[self.user_id] = {
                "type": pet_name,
                "name": pet_name,
                "xp": 0,
                "level": 1,
                "hunger": 100,
                "last_hunger_tick": int(time.time()),
            }
            save_data()
            await interaction.response.edit_message(
                embed=build_pet_embed(self.user_id, interaction.user.display_name),
                view=None,
            )
        return callback


@bot.command()
async def pet(ctx):
    await ctx.send(embed=build_pet_embed(ctx.author.id, ctx.author.display_name))


@bot.command()
async def petshop(ctx):
    embed = discord.Embed(
        title="Pet Shop",
        description="Adopt one pet. Pets give passive bonuses while they stay fed.",
        color=discord.Color.blurple(),
    )
    for pet_name, pet_info in PET_SHOP.items():
        embed.add_field(
            name=f"{pet_info['emoji']} {pet_name}",
            value=f"Price: {format_coins(pet_info['price'])} coins\n{pet_info['bonus_label']}",
            inline=True,
        )
    await ctx.send(embed=embed, view=PetShopView(ctx.author, ctx.author.id))


@bot.command()
async def feed(ctx):
    result = feed_pet(ctx.author.id)
    if not result:
        return await ctx.send("You don't have a pet yet. Use `!petshop` first.")
    pet, leveled_up = result
    save_data()
    embed = discord.Embed(
        title=f"Fed {pet['name']}",
        description=f"Hunger is now **{pet['hunger']}/100**.",
        color=discord.Color.green(),
    )
    embed.add_field(name="Pet Level", value=str(pet['level']), inline=True)
    embed.add_field(name="Pet XP", value=str(pet['xp']), inline=True)
    if leveled_up:
        embed.add_field(name="Level Up!", value=f"{pet['name']} reached **Level {pet['level']}**!", inline=False)
    await ctx.send(embed=embed)


RENAME_COST = 10_000


class RenameView(discord.ui.View):
    def __init__(self, requester, user_id: int):
        super().__init__(timeout=120)
        self.requester = requester
        self.user_id   = user_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.requester.id:
            await interaction.response.send_message("This isn't your rename panel.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🐾 Pet", style=discord.ButtonStyle.primary)
    async def rename_pet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pet = sync_pet_state(self.user_id)
        if not pet:
            await interaction.response.send_message("You don't have a pet yet.", ephemeral=True)
            return
        if get_wallet(self.user_id) < RENAME_COST:
            await interaction.response.send_message(
                f"You need **{format_coins(RENAME_COST)}** coins to rename your pet.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"What do you want to call your pet? (Max 20 characters) — you have 60 seconds.",
            ephemeral=True
        )
        name_input = await prompt_for_author_message(
            interaction.channel, interaction.user,
            f"💬 Type your new **pet name** now (max 20 chars):"
        )
        if name_input is None:
            await interaction.followup.send("Rename timed out.", ephemeral=True)
            return
        cleaned = sanitize_pet_name(name_input)
        if not cleaned:
            await interaction.followup.send("Pet names must be 1-20 characters.", ephemeral=True)
            return
        wallet[self.user_id] -= RENAME_COST
        pet["name"] = cleaned
        save_data()
        await interaction.followup.send(
            f"✅ Your pet is now called **{cleaned}**! (**{format_coins(RENAME_COST)}** coins deducted)",
            ephemeral=True
        )

    @discord.ui.button(label="🏢 Company", style=discord.ButtonStyle.primary)
    async def rename_company_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        company = get_company_record(self.user_id)
        if not company:
            await interaction.response.send_message("You don't have a company yet.", ephemeral=True)
            return
        if get_wallet(self.user_id) < RENAME_COST:
            await interaction.response.send_message(
                f"You need **{format_coins(RENAME_COST)}** coins to rename your company.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"What do you want to call your company? (Max 24 characters) — you have 60 seconds.",
            ephemeral=True
        )
        name_input = await prompt_for_author_message(
            interaction.channel, interaction.user,
            f"💬 Type your new **company name** now (max 24 chars):"
        )
        if name_input is None:
            await interaction.followup.send("Rename timed out.", ephemeral=True)
            return
        cleaned = sanitize_company_name(name_input)
        if not cleaned:
            await interaction.followup.send("Company names must be 1-24 characters.", ephemeral=True)
            return
        wallet[self.user_id] -= RENAME_COST
        company["name"] = cleaned
        save_data()
        await interaction.followup.send(
            f"✅ Your company is now called **{cleaned}**! (**{format_coins(RENAME_COST)}** coins deducted)",
            ephemeral=True
        )


@bot.command()
async def rename(ctx):
    """Open the rename panel — pet or company."""
    embed = discord.Embed(
        title="✏️ What do you want to rename?",
        description=(
            f"Choose a button below.\n\n"
            f"💰 Rename cost: **{format_coins(RENAME_COST)}** coins"
        ),
        color=discord.Color.blurple(),
    )
    await ctx.send(embed=embed, view=RenameView(ctx.author, ctx.author.id))


class CustomRodView(discord.ui.View):
    def __init__(self, requester, user_id: int):
        super().__init__(timeout=120)
        self.requester = requester
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.requester.id:
            await interaction.response.send_message("This isn't your custom rod menu.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🎣 Rod", style=discord.ButtonStyle.primary)
    async def custom_rod_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        entry = get_custom_rod_entry(self.user_id)

        if not entry.get("unlocked"):
            if get_wallet(self.user_id) < CUSTOM_ROD_UNLOCK_COST:
                await interaction.response.send_message(
                    f"You need **{format_coins(CUSTOM_ROD_UNLOCK_COST)}** coins to unlock your custom rod.",
                    ephemeral=True,
                )
                return
            await interaction.response.send_message(
                "Check the channel and send your custom rod name within 60 seconds. Max 20 characters.",
                ephemeral=True,
            )
            name_input = await prompt_for_author_message(
                interaction.channel,
                interaction.user,
                "Send your custom rod name now. Max 20 characters.",
            )
        else:
            await interaction.response.send_message(
                "Check the channel and send a new custom rod name, or type `skip` to just equip it.",
                ephemeral=True,
            )
            name_input = await prompt_for_author_message(
                interaction.channel,
                interaction.user,
                "Send a new custom rod name, or type `skip` to just equip it.",
            )

        if name_input is None:
            await interaction.followup.send("Custom rod setup timed out.", ephemeral=True)
            return

        if name_input.lower() == "skip" and entry.get("unlocked"):
            fishing_equipped_rod[self.user_id] = "Custom Rod"
            save_data()
            await interaction.followup.send(f"Equipped **{get_custom_rod_display_name(self.user_id)}**.", ephemeral=True)
            return

        cleaned = sanitize_custom_rod_name(name_input)
        if not cleaned:
            await interaction.followup.send("Custom rod names must be 1-20 characters.", ephemeral=True)
            return

        if not entry.get("unlocked"):
            wallet[self.user_id] -= CUSTOM_ROD_UNLOCK_COST
            entry["unlocked"] = True
        elif cleaned != entry.get("name"):
            if get_wallet(self.user_id) < CUSTOM_ROD_RENAME_COST:
                await interaction.followup.send(
                    f"You need **{format_coins(CUSTOM_ROD_RENAME_COST)}** coins to rename your custom rod.",
                    ephemeral=True,
                )
                return
            wallet[self.user_id] -= CUSTOM_ROD_RENAME_COST

        entry["name"] = cleaned
        fishing_equipped_rod[self.user_id] = "Custom Rod"
        save_data()
        await interaction.followup.send(f"Custom rod set to **{cleaned}** and equipped.", ephemeral=True)


@bot.command()
async def custom(ctx):
    entry = get_custom_rod_entry(ctx.author.id)
    unlocked = entry.get("unlocked")
    base_name = get_best_owned_real_rod(ctx.author.id)
    base_data = FISHING_RODS[base_name]
    embed = discord.Embed(
        title="Custom Rod",
        description=(
            f"**Status:** {'Unlocked' if unlocked else 'Locked'}\n"
            f"**Best rod mirrored:** {base_name}\n"
            f"**Current custom name:** {get_custom_rod_display_name(ctx.author.id)}\n\n"
            f"Unlock: **{format_coins(CUSTOM_ROD_UNLOCK_COST)}** coins\n"
            f"Rename: **{format_coins(CUSTOM_ROD_RENAME_COST)}** coins"
        ),
        color=discord.Color.purple(),
    )
    embed.add_field(
        name="Mirrored Stats",
        value=(
            f"Reward x{base_data['reward_multiplier']}\n"
            f"Reaction {base_data['reaction_time']}s"
        ),
        inline=False,
    )
    await ctx.send(embed=embed, view=CustomRodView(ctx.author, ctx.author.id))


def build_company_embed(user_id: int, owner_name: str):
    company = sync_company_income(user_id)
    if not company:
        return discord.Embed(
            title="Company",
            description="You don't own a company yet. Use `!company` to create one.",
            color=discord.Color.orange(),
        )

    hourly_income = company_hourly_income(company['level'])
    resource_name = company_resource_label(company)
    embed = discord.Embed(
        title=f"{company['name']}",
        description=f"{owner_name}'s {company['concept']} company",
        color=discord.Color.dark_teal(),
    )
    embed.add_field(name="Level", value=str(company['level']), inline=True)
    embed.add_field(name="Hourly Income", value=f"{format_coins(hourly_income)} coins", inline=True)
    embed.add_field(name="Stored Income", value=f"{format_coins(company['stored_income'])} coins", inline=True)
    embed.add_field(name="Resource", value=f"{format_coins(company['resource'])} {resource_name}", inline=False)
    embed.add_field(
        name="Upgrade Cost",
        value=f"{format_coins(company_upgrade_resource_cost(company['level']))} {resource_name}",
        inline=False,
    )
    embed.add_field(
        name="Resource Buy Cost",
        value=f"{format_coins(company_resource_unit_cost(company['level']))} coins each",
        inline=False,
    )
    embed.set_footer(text="Commands: !company buy <amount> ? !company upgrade ? !company collect")
    return embed


@bot.group(invoke_without_command=True)
async def company(ctx):
    user_id = ctx.author.id
    current = get_company_record(user_id)
    if current:
        return await ctx.send(embed=build_company_embed(user_id, ctx.author.display_name))

    name_input = await prompt_for_author_message(ctx.channel, ctx.author, "Send your company name. Max 24 characters.")
    if name_input is None:
        return await ctx.send("Company setup timed out.")
    company_name = sanitize_company_name(name_input)
    if not company_name:
        return await ctx.send("Company names must be 1-24 characters.")

    concept_input = await prompt_for_author_message(ctx.channel, ctx.author, "Now send your company concept as **one word**. Example: `Coffee`\n\n💡 *Think of KFC — their concept is `Chicken`. You'll buy more of it to grow your company!*")
    if concept_input is None:
        return await ctx.send("Company setup timed out.")
    concept = sanitize_company_concept(concept_input)
    if not concept:
        return await ctx.send("Concept must be one clean word, like `Coffee` or `Steel`.")

    COMPANY_CREATION_COST = 100_000_000
    if get_wallet(user_id) < COMPANY_CREATION_COST:
        return await ctx.send(
            f"Starting a company costs **{format_coins(COMPANY_CREATION_COST)}** coins. "
            f"You only have **{format_coins(get_wallet(user_id))}** coins."
        )

    wallet[user_id] -= COMPANY_CREATION_COST

    company_data[user_id] = {
        "name": company_name,
        "concept": concept,
        "level": 1,
        "resource": 0,
        "stored_income": 0,
        "last_tick": int(time.time()),
    }
    save_data()
    await ctx.send(embed=build_company_embed(user_id, ctx.author.display_name))


@company.command(name="buy")
async def company_buy(ctx, amount: str = None):
    company = get_company_record(ctx.author.id)
    if not company:
        return await ctx.send("Create your company first with `!company`.")
    amount_value = parse_amount_input(amount, balance=10**12, allow_all=False)
    if amount_value is None or amount_value <= 0:
        return await ctx.send("Usage: `!company buy <amount>`")
    unit_cost = company_resource_unit_cost(company['level'])
    total_cost = unit_cost * amount_value
    if get_wallet(ctx.author.id) < total_cost:
        return await ctx.send(f"You need **{format_coins(total_cost)}** coins.")
    wallet[ctx.author.id] -= total_cost
    company['resource'] += amount_value
    save_data()
    await ctx.send(f"Bought **{format_coins(amount_value)} {company_resource_label(company)}** for **{format_coins(total_cost)}** coins.")


@company.command(name="upgrade")
async def company_upgrade(ctx):
    company = get_company_record(ctx.author.id)
    if not company:
        return await ctx.send("Create your company first with `!company`.")
    cost = company_upgrade_resource_cost(company['level'])
    if company['resource'] < cost:
        return await ctx.send(f"You need **{format_coins(cost)} {company_resource_label(company)}** to upgrade.")
    company['resource'] -= cost
    company['level'] += 1
    save_data()
    await ctx.send(f"Upgraded **{company['name']}** to **Level {company['level']}**. Hourly income is now **{format_coins(company_hourly_income(company['level']))}** coins.")


@company.command(name="collect")
async def company_collect(ctx):
    company = sync_company_income(ctx.author.id)
    if not company:
        return await ctx.send("Create your company first with `!company`.")
    stored = company.get('stored_income', 0)
    if stored <= 0:
        return await ctx.send("Your company has nothing ready to collect yet.")
    payout = int(stored * pet_bonus_multiplier(ctx.author.id, 'company'))
    wallet.setdefault(ctx.author.id, 0)
    wallet[ctx.author.id] += payout
    company['stored_income'] = 0
    save_data()
    await ctx.send(f"Collected **{format_coins(payout)}** coins from **{company['name']}**.")


# ============== Owner Power =============

@bot.command()
async def wish(ctx, *args):
    if ctx.author.id != OWNER_ID:
        return

    if not args:
        await ctx.send(
            "**!wish usage:**\n"
            "`!wish [@user] <amount>` ? give coins\n"
            "`!wish [@user] remove <amount>` ? remove coins\n"
            "`!wish [@user] reset` ? reset claim timers\n"
            "`!wish [@user] rod <rod name>` ? give rod\n"
            "`!wish [@user] remove rod <rod name>` ? remove rod\n"
            "`!wish [@user] vehicle <vehicle name>` ? give vehicle\n"
            "`!wish [@user] remove vehicle <vehicle name>` ? remove vehicle\n"
            "`!wish [@user] hook <hook name>` ? give hook\n"
            "`!wish [@user] remove hook <hook name>` ? remove hook\n"
            "`!wish [@user] bait <bait name> [amount]` ? give bait\n"
            "`!wish [@user] remove bait <bait name> [amount]` ? remove bait\n"
            "`!wish [@user] level <amount>` ? add general levels\n"
            "`!wish [@user] remove level <amount>` ? remove general levels\n"
            "_Omit @user to target yourself._"
        )
        return

    # ?? Resolve optional target ???????????????????????????????????????????????
    target = ctx.author
    parts  = list(args)
    converter = commands.MemberConverter()
    try:
        possible_target = await converter.convert(ctx, parts[0])
        target = possible_target
        parts  = parts[1:]
    except commands.BadArgument:
        pass

    if not parts:
        await ctx.send("Specify what to wish for. Use `!wish` to see usage.")
        return

    uid    = target.id
    action = parts[0].strip().lower()   # first real arg

    # ── Helper ────────────────────────────────────────────────────────────────
    def name_of(target_member):
        return "You" if target_member.id == ctx.author.id else target_member.mention

    # ══════════════════════════════════════════════════════════════════════════
    # REMOVE branch
    # ══════════════════════════════════════════════════════════════════════════
    if action in {"remove", "take", "del", "delete"}:
        if len(parts) < 2:
            await ctx.send("Remove what? Specify `coins`, `rod`, `hook`, `bait`, or `level`.")
            return

        sub = parts[1].strip().lower()

        # ── remove coins ─────────────────────────────────────────────────────
        if sub not in {"rod", "vehicle", "hook", "bait", "level"}:
            # treat parts[1] as a coin amount
            amount = parse_amount_input(parts[1], balance=get_wallet(uid), allow_all=True)
            if amount is None:
                await ctx.send("Invalid coin amount.")
                return
            wallet.setdefault(uid, 0)
            wallet[uid] = max(0, wallet[uid] - amount)
            save_data()
            await ctx.send(f"Removed **{format_coins(amount)}** coins from {name_of(target)}.")
            return

        # ── remove rod ───────────────────────────────────────────────────────
        if sub == "rod":
            rod_input = " ".join(parts[2:]).strip()
            if not rod_input:
                await ctx.send("Specify a rod name. E.g. `!wish remove rod Pro Rod`")
                return
            matched = find_rod_name(rod_input)
            if not matched:
                await ctx.send(f"Unknown rod **{rod_input}**.")
                return
            if matched == "Basic Rod":
                await ctx.send("Can't remove the Basic Rod — it's the default.")
                return
            owned = get_owned_rods(uid)
            if matched not in owned:
                await ctx.send(f"{name_of(target)} doesn't own **{matched}**.")
                return
            owned.remove(matched)
            if get_equipped_rod(uid) == matched:
                fishing_equipped_rod[uid] = "Basic Rod"
            save_data()
            await ctx.send(f"Removed rod **{matched}** from {name_of(target)}.")
            return

        # ── remove vehicle ───────────────────────────────────────────────────
        if sub == "vehicle":
            vehicle_input = " ".join(parts[2:]).strip()
            if not vehicle_input:
                await ctx.send("Specify a vehicle name. E.g. `!wish remove vehicle Car`")
                return
            matched = next((n for n in DELIVERY_VEHICLES if n.lower() == vehicle_input.lower()), None)
            if not matched:
                await ctx.send(f"Unknown vehicle **{vehicle_input}**.")
                return
            if matched == "Scooter":
                await ctx.send("Can't remove the Scooter — it's the default vehicle.")
                return
            owned = get_owned_vehicles(uid)
            if matched not in owned:
                await ctx.send(f"{name_of(target)} doesn't own **{matched}**.")
                return
            owned.remove(matched)
            if get_equipped_vehicle(uid) == matched:
                delivery_equipped_vehicle[uid] = "Scooter"
            save_data()
            await ctx.send(f"Removed vehicle **{DELIVERY_VEHICLES[matched]['emoji']} {matched}** from {name_of(target)}.")
            return

        # ── remove hook ──────────────────────────────────────────────────────
        if sub == "hook":
            hook_input = " ".join(parts[2:]).strip()
            if not hook_input:
                await ctx.send("Specify a hook name. E.g. `!wish remove hook Golden Hook`")
                return
            matched = next((n for n in FISHING_HOOKS if n.lower() == hook_input.lower()), None)
            if not matched:
                await ctx.send(f"Unknown hook **{hook_input}**.")
                return
            if matched == "Basic Hook":
                await ctx.send("Can't remove the Basic Hook — it's the default.")
                return
            owned = get_owned_hooks(uid)
            if matched not in owned:
                await ctx.send(f"{name_of(target)} doesn't own **{matched}**.")
                return
            owned.remove(matched)
            if get_equipped_hook(uid) == matched:
                hooks_equipped[uid] = "Basic Hook"
            save_data()
            await ctx.send(f"Removed hook **{matched}** from {name_of(target)}.")
            return

        # ── remove bait ──────────────────────────────────────────────────────
        if sub == "bait":
            # parts: [remove, bait, ...name..., optional_qty]
            bait_parts = parts[2:]
            qty = 1
            if bait_parts and bait_parts[-1].isdigit():
                qty        = int(bait_parts[-1])
                bait_parts = bait_parts[:-1]
            bait_input = " ".join(bait_parts).strip()
            if not bait_input:
                await ctx.send("Specify a bait name. E.g. `!wish remove bait Shrimp 10`")
                return
            matched = next((n for n in FISHING_BAITS if n.lower() == bait_input.lower()), None)
            if not matched:
                await ctx.send(f"Unknown bait **{bait_input}**.")
                return
            if matched == "Worm":
                await ctx.send("Worm is unlimited — can't remove it.")
                return
            inv = get_bait_inventory(uid)
            current = inv.get(matched, 0)
            if current <= 0:
                await ctx.send(f"{name_of(target)} has no **{matched}**.")
                return
            inv[matched] = max(0, current - qty)
            if inv[matched] == 0 and get_equipped_bait(uid) == matched:
                bait_equipped[uid] = "Worm"
            save_data()
            await ctx.send(f"Removed **{qty}× {matched}** from {name_of(target)}. (Remaining: {inv[matched]})")
            return

        # ── remove level ─────────────────────────────────────────────────────
        if sub == "level":
            if len(parts) < 3 or not parts[2].isdigit():
                await ctx.send("Specify how many levels to remove. E.g. `!wish remove level 10`")
                return
            lvl_amount = int(parts[2])
            xp_to_remove = lvl_amount * GENERAL_XP_PER_LEVEL
            current_xp   = get_general_xp(uid)
            new_xp       = max(0, current_xp - xp_to_remove)
            player_general_xp[uid]    = new_xp
            player_general_level[uid] = new_xp // GENERAL_XP_PER_LEVEL
            save_data()
            await ctx.send(
                f"Removed **{lvl_amount} level(s)** from {name_of(target)}. "
                f"Now Level **{player_general_level[uid]}**."
            )
            return

    # ══════════════════════════════════════════════════════════════════════════
    # GIVE / SET branch
    # ══════════════════════════════════════════════════════════════════════════

    # ── reset claims ─────────────────────────────────────────────────────────
    if action == "reset":
        claims = get_claims(uid)
        claims["daily"] = claims["weekly"] = claims["monthly"] = 0
        save_data()
        await ctx.send(f"Reset all claim timers for {name_of(target)}.")
        return

    # ── give rod ─────────────────────────────────────────────────────────────
    if action == "rod":
        rod_input = " ".join(parts[1:]).strip()
        if not rod_input:
            await ctx.send("Specify a rod name. E.g. `!wish rod Pro Rod`")
            return
        matched = find_rod_name(rod_input)
        if not matched:
            await ctx.send(f"Unknown rod **{rod_input}**. Options: {', '.join(FISHING_RODS)}")
            return
        owned = get_owned_rods(uid)
        if matched not in owned:
            owned.append(matched)
        fishing_equipped_rod[uid] = matched
        save_data()
        await ctx.send(f"Gave rod **{matched}** to {name_of(target)} and equipped it.")
        return

    # ── give vehicle ──────────────────────────────────────────────────────────
    if action in {"vehicle", "veh"}:
        vehicle_input = " ".join(parts[1:]).strip()
        if not vehicle_input:
            await ctx.send("Specify a vehicle name. E.g. `!wish vehicle Super Van`")
            return
        matched = next((n for n in DELIVERY_VEHICLES if n.lower() == vehicle_input.lower()), None)
        if not matched:
            await ctx.send(f"Unknown vehicle **{vehicle_input}**. Options: {', '.join(DELIVERY_VEHICLES)}")
            return
        owned = get_owned_vehicles(uid)
        if matched not in owned:
            owned.append(matched)
        delivery_equipped_vehicle[uid] = matched
        save_data()
        await ctx.send(f"Gave vehicle **{DELIVERY_VEHICLES[matched]['emoji']} {matched}** to {name_of(target)} and equipped it.")
        return

    # ── give hook ─────────────────────────────────────────────────────────────
    if action == "hook":
        hook_input = " ".join(parts[1:]).strip()
        if not hook_input:
            await ctx.send("Specify a hook name. E.g. `!wish hook Diamond Hook`")
            return
        matched = next((n for n in FISHING_HOOKS if n.lower() == hook_input.lower()), None)
        if not matched:
            await ctx.send(f"Unknown hook **{hook_input}**. Options: {', '.join(FISHING_HOOKS)}")
            return
        owned = get_owned_hooks(uid)
        if matched not in owned:
            owned.append(matched)
        hooks_equipped[uid] = matched
        save_data()
        await ctx.send(f"Gave hook **{FISHING_HOOKS[matched]['emoji']} {matched}** to {name_of(target)} and equipped it.")
        return

    # ── give bait ─────────────────────────────────────────────────────────────
    if action == "bait":
        bait_parts = parts[1:]
        qty = 10   # default
        if bait_parts and bait_parts[-1].isdigit():
            qty        = int(bait_parts[-1])
            bait_parts = bait_parts[:-1]
        bait_input = " ".join(bait_parts).strip()
        if not bait_input:
            await ctx.send("Specify a bait name. E.g. `!wish bait Magic Bait 50`")
            return
        matched = next((n for n in FISHING_BAITS if n.lower() == bait_input.lower()), None)
        if not matched:
            await ctx.send(f"Unknown bait **{bait_input}**. Options: {', '.join(FISHING_BAITS)}")
            return
        inv = get_bait_inventory(uid)
        if matched == "Worm":
            await ctx.send("Worm is already unlimited for everyone.")
            return
        inv[matched] = inv.get(matched, 0) + qty
        bait_equipped[uid] = matched
        save_data()
        await ctx.send(f"Gave **{qty}× {FISHING_BAITS[matched]['emoji']} {matched}** to {name_of(target)}. (Total: {inv[matched]})")
        return

    # ── give level ────────────────────────────────────────────────────────────
    if action == "level":
        if len(parts) < 2 or not parts[1].isdigit():
            await ctx.send("Specify how many levels to give. E.g. `!wish level 10`")
            return
        lvl_amount = int(parts[1])
        xp_to_add  = lvl_amount * GENERAL_XP_PER_LEVEL
        player_general_xp[uid]    = get_general_xp(uid) + xp_to_add
        player_general_level[uid] = player_general_xp[uid] // GENERAL_XP_PER_LEVEL
        save_data()
        await ctx.send(
            f"Gave **{lvl_amount} level(s)** to {name_of(target)}. "
            f"Now Level **{player_general_level[uid]}**."
        )
        return

    # ── give coins (default) ──────────────────────────────────────────────────
    amount = parse_amount_input(parts[0])
    if amount is None:
        await ctx.send("Unknown wish action. Use `!wish` to see all options.")
        return
    wallet.setdefault(uid, 0)
    wallet[uid] += amount
    save_data()
    await ctx.send(f"Granted **{format_coins(amount)}** coins to {name_of(target)}.")


# ===== TRANSFER =====
@bot.command()
async def blockpay(ctx):
    payment_blocked[ctx.author.id] = True
    save_data()
    await ctx.send("🔒 You are no longer accepting coin transfers.")


@bot.command()
async def unblockpay(ctx):
    payment_blocked.pop(ctx.author.id, None)
    save_data()
    await ctx.send("🔓 People can send you coins again.")


@bot.command()
async def transfer(ctx, member: discord.Member, amount: str):
    sender = ctx.author.id
    target = member.id
    amount = parse_amount_input(amount, balance=get_wallet(sender), allow_all=True)

    if amount is None or amount <= 0:
        return await ctx.send("Invalid amount.")

    if sender == target:
        return await ctx.send("You can't send coins to yourself.")

    if payment_blocked.get(target):
        return await ctx.send(f"{member.mention} isn't accepting payments right now.")

    if get_wallet(sender) < amount:
        return await ctx.send("Not enough coins.")

    wallet.setdefault(sender, 0)
    wallet.setdefault(target, 0)

    wallet[sender] -= amount
    wallet[target] += amount
    save_data()

    await ctx.send(f"{ctx.author.mention} sent **{format_coins(amount)}** coins to {member.mention}.")


# ===== DEPOSIT =====
@bot.command(aliases=["dep"])
async def deposit(ctx, amount: str):
    user = ctx.author.id
    amount = parse_amount_input(amount, balance=get_wallet(user), allow_all=True)

    if amount is None or amount <= 0:
        return await ctx.send("Invalid amount.")

    if get_wallet(user) < amount:
        return await ctx.send("Not enough coins.")

    wallet.setdefault(user, 0)
    bank.setdefault(user, 0)

    wallet[user] -= amount
    bank[user] += amount
    save_data()

    await ctx.send(f"Deposited **{amount}** coins.")


# ===== WITHDRAW =====
@bot.command(aliases=["wit"])
async def withdraw(ctx, amount: str):
    user = ctx.author.id
    amount = parse_amount_input(amount, balance=get_bank(user), allow_all=True)

    if amount is None or amount <= 0:
        return await ctx.send("Invalid amount.")

    if get_bank(user) < amount:
        return await ctx.send("Not enough in bank.")

    wallet.setdefault(user, 0)
    bank.setdefault(user, 0)

    bank[user] -= amount
    wallet[user] += amount
    save_data()

    await ctx.send(f"Withdrew **{amount}** coins.")


# ===== BALANCE =====
@bot.command(aliases=["bal"])
async def balance(ctx, member: discord.Member = None):
    user = member.id if member else ctx.author.id

    # block if viewing someone else's private balance
    if member and private_bal.get(user):
        return await ctx.send("🔒 this user has a private balance")

    await ctx.send(
        f"{member.mention if member else ctx.author.mention} Wallet: **{get_wallet(user)}** | Bank: **{get_bank(user)}**"
    )


# ===== JAIL SYSTEM =====
def is_jailed(user_id):
    if user_id not in jail:
        return False

    if random.random() < 0.15:
        jail_guard_active[user_id] = True

    return jail.get(user_id, 0) > int(time.time())


def jail_time_left(user_id):
    return max(0, jail.get(user_id, 0) - int(time.time()))


# ============== ROBBERY ===============
@bot.command()
async def rob(ctx, member: discord.Member):
    robber = ctx.author.id
    target = member.id

    # 🚔 jail check (BLOCK ROB + show time left)
    if is_jailed(robber):
        left = jail_time_left(robber)

        embed = discord.Embed(
            title="🚔 YOU ARE JAILED",
            description="You can't use `rob` right now.",
            color=discord.Color.dark_red()
        )

        embed.add_field(
            name="⏱️ Time Left",
            value=f"{left//60}m {left%60}s",
            inline=False
        )

        if jail_guard_active.get(robber):
            embed.add_field(
                name="👁️ GUARD EVENT",
                value="A guard is watching you… type `!guard` fast 👀",
                inline=False
            )

        return await ctx.send(embed=embed)

    if member.bot:
        return await ctx.send("you can't rob bots 💀")

    if robber == target:
        return await ctx.send("bro rob yourself? 💀")

    if get_wallet(target) < 100:
        return await ctx.send("they too broke to rob")

    if get_wallet(robber) < 50:
        return await ctx.send("you need at least 50 coins to rob")

    wallet.setdefault(robber, 0)
    wallet.setdefault(target, 0)

    # 50% success chance
    if random.random() < 0.5:
        steal_amount = random.randint(50, min(300, get_wallet(target)))

        wallet[target] -= steal_amount
        wallet[robber] += steal_amount

        save_data()

        await ctx.send(f"🤑 you robbed **{steal_amount}** coins from {member.mention}")

    else:
        fail_amount = random.randint(20, 100)

        wallet[robber] -= fail_amount
        wallet[target] += fail_amount

        jail[robber] = int(time.time()) + 300  # 5 min jail

        save_data()

        embed = discord.Embed(
            title="💀 Robbery Failed",
            description=f"{ctx.author.mention} failed the robbery!",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Penalty",
            value=f"Paid **{fail_amount}** coins to {member.mention}",
            inline=False
        )

        embed.add_field(
            name="Jail",
            value="🚔 You got jailed for **5 minutes**",
            inline=False
        )

        await ctx.send(embed=embed)


# ============ GUARD TROLL ===============

@bot.command()
async def guard(ctx):
    user = ctx.author.id

    if user not in jail_guard_active:
        return await ctx.send("no guard watching you 💀")

    del jail_guard_active[user]

    outcome = random.choice(["help", "troll", "ignore"])

    if outcome == "help":
        jail.pop(user, None)
        return await ctx.send("🚔 guard felt bad… you got released")

    if outcome == "troll":
        jail[user] = int(time.time()) + 120
        return await ctx.send("💀 guard added MORE time (2 min extra)")

    await ctx.send("👁️ guard ignored you… still jailed")



# ============= ESCAPE/MINIGAME ============

@bot.command()
async def escape(ctx):
    user = ctx.author.id

    if not is_jailed(user):
        return await ctx.send("you're not in jail 💀")

    word = generate_random_word(6)

    embed = discord.Embed(
        title="🚔 JAIL BREAK",
        description=(
            f"Type this word correctly to escape:\n\n"
            f"**`{word}`**\n\n"
            f"You have **7 seconds** ⏱️"
        ),
        color=discord.Color.orange()
    )

    await ctx.send(embed=embed)

    def check(m):
        return m.author.id == user and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", timeout=7, check=check)

        if msg.content == word:
            del jail[user]

            embed = discord.Embed(
                title="✅ ESCAPE SUCCESSFUL",
                description="You broke out of jail 💀",
                color=discord.Color.green()
            )

            return await ctx.send(embed=embed)

        else:
            await ctx.send("❌ wrong word. stay locked 💀")

    except asyncio.TimeoutError:
        await ctx.send("⏱️ too slow. still jailed 💀")

# ============= BAIL ================
@bot.command()
async def bail(ctx):
    user = ctx.author.id

    if not is_jailed(user):
        return await ctx.send("you're not jailed")

    left = jail_time_left(user)
    cost = max(75, left // 4)

    if get_wallet(user) < cost:
        return await ctx.send(f"need **{cost}** coins to bail out")

    wallet[user] -= cost
    del jail[user]
    save_data()

    await ctx.send(f"🚔 you paid **{cost}** coins and got released")


# ================= SLOTS =====================
SLOTS_SYMBOLS = ["🍒", "🍋", "🔔", "💎", "7️⃣"]

@bot.command()
async def slots(ctx, bet: str):
    user = ctx.author.id
    raw_bet = bet
    bet = parse_amount_input(bet, balance=get_wallet(user), allow_all=True)

    if bet is None or bet <= 0:
        return await ctx.send("bet must be above 0")

    if isinstance(raw_bet, str) and raw_bet.strip().lower() == "all":
        confirmed = await confirm_all_in(ctx, "Slots")
        if not confirmed:
            return

    if get_wallet(user) < bet:
        return await ctx.send("not enough coins")

    wallet.setdefault(user, 0)
    wallet[user] -= bet

    r1 = random.choice(SLOTS_SYMBOLS)
    r2 = random.choice(SLOTS_SYMBOLS)
    r3 = random.choice(SLOTS_SYMBOLS)

    result = f"{r1} | {r2} | {r3}"

    if r1 == r2 == r3:
        win = bet * 5
        wallet[user] += win
        msg = f"🎰 JACKPOT!!\n{result}\nYou won **{win}** coins"

    elif r1 == r2 or r2 == r3 or r1 == r3:
        win = bet * 2
        wallet[user] += win
        msg = f"✨ Nice!\n{result}\nYou won **{win}** coins"

    else:
        msg = f"💀 You lost\n{result}\n-**{bet}** coins"

    save_data()

    embed = discord.Embed(
        title="🎲 SLOTS MACHINE",
        description=msg,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)



# ================= BLACKJACK =================

BLACKJACK_SUITS = ["♠", "♥", "♦", "♣"]
BLACKJACK_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

def bj_make_deck():
    deck = []
    for suit in BLACKJACK_SUITS:
        for rank in BLACKJACK_RANKS:
            deck.append((rank, suit))
    random.shuffle(deck)
    return deck

def bj_card_value(card):
    rank = card[0]
    if rank == "A":
        return 11
    if rank in ["J", "Q", "K"]:
        return 10
    return int(rank)

def bj_hand_value(hand):
    total = sum(bj_card_value(card) for card in hand)
    aces = sum(1 for card in hand if card[0] == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def bj_is_blackjack(hand):
    return len(hand) == 2 and bj_hand_value(hand) == 21

def bj_card_text(hand):
    return " ".join(f"`{rank}{suit}`" for rank, suit in hand)

def bj_split_key(card):
    rank = card[0]
    if rank in ["10", "J", "Q", "K"]:
        return "10"
    return rank

class BlackjackHand:
    def __init__(self, cards, bet, from_split=False):
        self.cards = cards
        self.bet = bet
        self.from_split = from_split
        self.finished = False
        self.acted = False
        self.outcome = ""

class BlackjackGame:
    def __init__(self, user, channel, bet):
        self.user = user
        self.channel = channel
        self.deck = bj_make_deck()
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.hands = [BlackjackHand([self.deck.pop(), self.deck.pop()], bet)]
        self.active_hand = 0
        self.finished = False
        self.original_bet = bet  # added this

    def current_hand(self):
        if self.finished or self.active_hand >= len(self.hands):
            return None
        return self.hands[self.active_hand]

    def can_split(self, hand):
        if not hand or hand.finished or hand.acted or len(hand.cards) != 2:
            return False
        if get_wallet(self.user.id) < hand.bet:
            return False
        return bj_split_key(hand.cards[0]) == bj_split_key(hand.cards[1])

    def can_double(self, hand):
        if not hand or hand.finished or hand.acted or len(hand.cards) != 2:
            return False
        return get_wallet(self.user.id) >= hand.bet

    def deal_to_hand(self, hand):
        hand.cards.append(self.deck.pop())

    def finish_if_done(self):
        while self.active_hand < len(self.hands) and self.hands[self.active_hand].finished:
            self.active_hand += 1
        if self.active_hand >= len(self.hands):
            self.resolve_game()

    def check_starting_blackjack(self):
        player_bj = bj_is_blackjack(self.hands[0].cards)
        dealer_bj = bj_is_blackjack(self.dealer_hand)

        if not player_bj and not dealer_bj:
            return False

        hand = self.hands[0]

        if player_bj and dealer_bj:
            wallet[self.user.id] += hand.bet
            hand.outcome = f"Push. Bet returned: **{hand.bet}**"
        elif player_bj:
            payout = hand.bet + (hand.bet * 3) // 2
            wallet[self.user.id] += payout
            hand.outcome = f"Blackjack. Won **{payout - hand.bet}**"
        else:
            hand.outcome = f"Dealer blackjack. Lost **{hand.bet}**"

        hand.finished = True
        self.finished = True
        save_data()
        blackjack_games.pop(self.user.id, None)
        return True

    def hit(self):
        hand = self.current_hand()
        if not hand:
            return
        hand.acted = True
        self.deal_to_hand(hand)
        if bj_hand_value(hand.cards) >= 21:
            hand.finished = True
        self.finish_if_done()

    def stand(self):
        hand = self.current_hand()
        if not hand:
            return
        hand.acted = True
        hand.finished = True
        self.finish_if_done()

    def double_down(self):
        hand = self.current_hand()
        if not self.can_double(hand):
            return False
        wallet[self.user.id] -= hand.bet
        hand.bet *= 2
        hand.acted = True
        self.deal_to_hand(hand)
        hand.finished = True
        save_data()
        self.finish_if_done()
        return True

    def split(self):
        hand = self.current_hand()
        if not self.can_split(hand):
            return False
        wallet[self.user.id] -= hand.bet
        card1 = hand.cards[0]
        card2 = hand.cards[1]
        first_hand = BlackjackHand([card1, self.deck.pop()], hand.bet, from_split=True)
        second_hand = BlackjackHand([card2, self.deck.pop()], hand.bet, from_split=True)
        self.hands[self.active_hand] = first_hand
        self.hands.insert(self.active_hand + 1, second_hand)
        save_data()
        if bj_hand_value(first_hand.cards) == 21:
            first_hand.finished = True
        self.finish_if_done()
        return True

    def resolve_game(self):
        if self.finished:
            return
        self.finished = True
        if any(bj_hand_value(hand.cards) <= 21 for hand in self.hands):
            while bj_hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())
        dealer_total = bj_hand_value(self.dealer_hand)
        dealer_blackjack = bj_is_blackjack(self.dealer_hand)
        for index, hand in enumerate(self.hands, start=1):
            total = bj_hand_value(hand.cards)
            if total > 21:
                hand.outcome = f"Hand {index}: Bust. Lost **{hand.bet}**"
                continue
            if bj_is_blackjack(hand.cards) and not hand.from_split and not dealer_blackjack:
                payout = hand.bet + (hand.bet * 3) // 2
                wallet[self.user.id] += payout
                hand.outcome = f"Hand {index}: Blackjack. Won **{payout - hand.bet}**"
            elif dealer_total > 21:
                wallet[self.user.id] += hand.bet * 2
                hand.outcome = f"Hand {index}: Dealer bust. Won **{hand.bet}**"
            elif total > dealer_total:
                wallet[self.user.id] += hand.bet * 2
                hand.outcome = f"Hand {index}: Won **{hand.bet}**"
            elif total == dealer_total:
                wallet[self.user.id] += hand.bet
                hand.outcome = f"Hand {index}: Push. Bet returned: **{hand.bet}**"
            else:
                hand.outcome = f"Hand {index}: Lost **{hand.bet}**"
        save_data()
        blackjack_games.pop(self.user.id, None)

    def build_embed(self, reveal=False):
        embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blurple())
        if reveal or self.finished:
            dealer_text = bj_card_text(self.dealer_hand)
            dealer_total = bj_hand_value(self.dealer_hand)
            embed.add_field(name=f"Dealer - {dealer_total}", value=dealer_text, inline=False)
        else:
            dealer_text = f"`{self.dealer_hand[0][0]}{self.dealer_hand[0][1]}` `??`"
            embed.add_field(
                name=f"Dealer - showing {bj_card_value(self.dealer_hand[0])}",
                value=dealer_text,
                inline=False
            )
        for i, hand in enumerate(self.hands, start=1):
            total = bj_hand_value(hand.cards)
            marker = " <-- active" if not self.finished and (i - 1) == self.active_hand else ""
            result_text = f"\n{hand.outcome}" if hand.outcome else ""
            embed.add_field(
                name=f"Your Hand {i} - {total}{marker}",
                value=f"{bj_card_text(hand.cards)}\nBet: **{hand.bet}**{result_text}",
                inline=False
            )
        embed.set_footer(text=f"Balance: {get_wallet(self.user.id)} coins")
        return embed


# ============ PLAY AGAIN VIEW ============
class PlayAgainView(discord.ui.View):
    def __init__(self, user, channel, last_bet):
        super().__init__(timeout=60)
        self.user = user
        self.channel = channel
        self.last_bet = last_bet

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("not ur game lol", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Play Again (Same Bet)", style=discord.ButtonStyle.success, custom_id="bj_replay_same")
    async def replay_same(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        if self.user.id in blackjack_games:
            await self.channel.send("you already got a game running")
            return
        if get_wallet(self.user.id) < self.last_bet:
            await self.channel.send(f"ur broke, u got **{get_wallet(self.user.id)}** coins")
            return

        wallet[self.user.id] -= self.last_bet
        save_data()
        game = BlackjackGame(self.user, self.channel, self.last_bet)
        blackjack_games[self.user.id] = game

        if game.check_starting_blackjack():
            replay = PlayAgainView(self.user, self.channel, self.last_bet)
            await self.channel.send(f"{self.user.mention}", embed=game.build_embed(reveal=True), view=replay)
            return

        view = BlackjackView(game)
        msg = await self.channel.send(f"{self.user.mention}", embed=game.build_embed(), view=view)
        view.message = msg

    @discord.ui.button(label="Play Again (New Bet)", style=discord.ButtonStyle.primary, custom_id="bj_replay_new")
    async def replay_new(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await self.channel.send(f"{self.user.mention} how much do you want to bet? type it below 👇")

        def check(m):
            return m.author == self.user and m.channel == self.channel

        try:
            msg = await bot.wait_for("message", timeout=30.0, check=check)
            new_bet = parse_amount_input(msg.content, balance=get_wallet(self.user.id), allow_all=True)
            if new_bet is None or new_bet <= 0:
                await self.channel.send("bet has to be above 0")
                return
            if self.user.id in blackjack_games:
                await self.channel.send("you already got a game running")
                return
            if get_wallet(self.user.id) < new_bet:
                await self.channel.send(f"ur broke, u got **{get_wallet(self.user.id)}** coins")
                return
            wallet[self.user.id] -= new_bet
            save_data()
            game = BlackjackGame(self.user, self.channel, new_bet)
            blackjack_games[self.user.id] = game
            if game.check_starting_blackjack():
                replay = PlayAgainView(self.user, self.channel, new_bet)
                await self.channel.send(f"{self.user.mention}", embed=game.build_embed(reveal=True), view=replay)
                return
            view = BlackjackView(game)
            msg2 = await self.channel.send(f"{self.user.mention}", embed=game.build_embed(), view=view)
            view.message = msg2
        except asyncio.TimeoutError:
            await self.channel.send(f"{self.user.mention} too slow 💀")


class BlackjackView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=60)
        self.game = game
        self.message = None
        self.update_buttons()

    def update_buttons(self):
        hand = self.game.current_hand()
        for item in self.children:
            if item.custom_id == "bj_hit":
                item.disabled = self.game.finished or hand is None or hand.finished
            elif item.custom_id == "bj_stand":
                item.disabled = self.game.finished or hand is None or hand.finished
            elif item.custom_id == "bj_double":
                item.disabled = not self.game.can_double(hand)
            elif item.custom_id == "bj_split":
                item.disabled = not self.game.can_split(hand)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("not ur game lol", ephemeral=True)
            return False
        return True

    async def finish_message(self):
        self.update_buttons()
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(embed=self.game.build_embed(reveal=True), view=self)
        replay = PlayAgainView(self.game.user, self.game.channel, self.game.original_bet)
        await self.game.channel.send(view=replay)

    async def on_timeout(self):
        if self.game.finished:
            return
        while not self.game.finished:
            hand = self.game.current_hand()
            if not hand:
                break
            hand.finished = True
            self.game.finish_if_done()
        await self.finish_message()

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary, custom_id="bj_hit")
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game.hit()
        self.update_buttons()
        if self.game.finished:
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=self.game.build_embed(reveal=True), view=self)
            replay = PlayAgainView(self.game.user, self.game.channel, self.game.original_bet)
            await self.game.channel.send(view=replay)
        else:
            await interaction.response.edit_message(embed=self.game.build_embed(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.secondary, custom_id="bj_stand")
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game.stand()
        self.update_buttons()
        if self.game.finished:
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=self.game.build_embed(reveal=True), view=self)
            replay = PlayAgainView(self.game.user, self.game.channel, self.game.original_bet)
            await self.game.channel.send(view=replay)
        else:
            await interaction.response.edit_message(embed=self.game.build_embed(), view=self)

    @discord.ui.button(label="Double", style=discord.ButtonStyle.success, custom_id="bj_double")
    async def double_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.game.double_down():
            await interaction.response.send_message("you can't double rn", ephemeral=True)
            return
        self.update_buttons()
        if self.game.finished:
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=self.game.build_embed(reveal=True), view=self)
            replay = PlayAgainView(self.game.user, self.game.channel, self.game.original_bet)
            await self.game.channel.send(view=replay)
        else:
            await interaction.response.edit_message(embed=self.game.build_embed(), view=self)

    @discord.ui.button(label="Split", style=discord.ButtonStyle.danger, custom_id="bj_split")
    async def split_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.game.split():
            await interaction.response.send_message("you can't split rn", ephemeral=True)
            return
        self.update_buttons()
        await interaction.response.edit_message(embed=self.game.build_embed(), view=self)


@bot.command(aliases=["bj"])
async def blackjack(ctx, bet: str = None):
    user = ctx.author
    if bet is None:
        await ctx.send("use `!bj <amount>`")
        return

    raw_bet = bet
    bet = parse_amount_input(bet, balance=get_wallet(user.id), allow_all=True)
    if bet is None or bet <= 0:
        await ctx.send("bet has to be above 0")
        return

    if isinstance(raw_bet, str) and raw_bet.strip().lower() == "all":
        confirmed = await confirm_all_in(ctx, "Blackjack")
        if not confirmed:
            return

    if user.id in blackjack_games:
        await ctx.send("you already got a game running")
        return
    if get_wallet(user.id) < bet:
        await ctx.send(f"ur broke, u got **{get_wallet(user.id)}** coins")
        return

    wallet[user.id] -= bet
    save_data()

    game = BlackjackGame(user, ctx.channel, bet)
    blackjack_games[user.id] = game

    if game.check_starting_blackjack():
        replay = PlayAgainView(user, ctx.channel, bet)
        await ctx.send(f"{user.mention}", embed=game.build_embed(reveal=True), view=replay)
        return

    view = BlackjackView(game)
    msg = await ctx.send(f"{user.mention}", embed=game.build_embed(), view=view)
    view.message = msg


# ============= LEADERBOARD ==============

@bot.command(aliases=["lb", "rich"])
async def leaderboard(ctx):
    all_users = set(wallet.keys()) | set(bank.keys())
    if not all_users:
        return await ctx.send("no data yet")

    totals = {uid: get_wallet(uid) + get_bank(uid) for uid in all_users}
    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:10]

    embed = discord.Embed(title="TOP RICHEST PLAYERS", color=discord.Color.gold())
    desc = ""

    for i, (user_id, total) in enumerate(top, start=1):
        member = ctx.guild.get_member(user_id)
        name = member.display_name if member else f"User {user_id}"
        medal = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        w = get_wallet(user_id)
        b = get_bank(user_id)
        desc += f"{medal} **{i}. {name}** — `{total:,}` coins (💰 {w:,} | 🏦 {b:,})\n"

    embed.description = desc
    embed.set_footer(text="based on total coins.")
    await ctx.send(embed=embed)


# ======================== DELIVERY SYSTEM ====================================

# ── Vehicle helpers ───────────────────────────────────────────────────────────
def get_owned_vehicles(user_id: int) -> list:
    vehicles = delivery_vehicles_owned.setdefault(user_id, ["Scooter"])
    if "Scooter" not in vehicles:
        vehicles.insert(0, "Scooter")
    return vehicles


def get_equipped_vehicle(user_id: int) -> str:
    equipped = delivery_equipped_vehicle.setdefault(user_id, "Scooter")
    if equipped not in get_owned_vehicles(user_id):
        equipped = "Scooter"
        delivery_equipped_vehicle[user_id] = equipped
    return equipped


# ── Vehicle shop UI ──────────────────────────────────────────────────────────
class VehicleShopView(discord.ui.View):
    def __init__(self, requester, user_id: int):
        super().__init__(timeout=120)
        self.requester = requester
        self.user_id   = user_id

        for vname, vdata in DELIVERY_VEHICLES.items():
            style  = discord.ButtonStyle.success if vdata["price"] == 0 else discord.ButtonStyle.primary
            button = discord.ui.Button(
                label=f"{vdata['emoji']} {vname}",
                style=style,
                row=0 if len(self.children) < 3 else 1,
            )
            button.callback = self._make_callback(vname)
            self.add_item(button)

    def _make_callback(self, vname: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("This isn't your shop.", ephemeral=True)
                return
            owned = get_owned_vehicles(self.user_id)
            if vname in owned:
                delivery_equipped_vehicle[self.user_id] = vname
                save_data()
                await interaction.response.send_message(
                    f"Equipped **{DELIVERY_VEHICLES[vname]['emoji']} {vname}**.", ephemeral=True
                )
                return
            price     = DELIVERY_VEHICLES[vname]["price"]
            level_req = DELIVERY_VEHICLES[vname]["level_req"]
            if get_general_level(self.user_id) < level_req:
                await interaction.response.send_message(
                    f"You need **General Level {level_req}** to buy **{vname}**. "
                    f"(You are Level {get_general_level(self.user_id)})",
                    ephemeral=True,
                )
                return
            if get_wallet(self.user_id) < price:
                await interaction.response.send_message(
                    f"You need **{format_coins(price)}** coins for **{vname}**.", ephemeral=True
                )
                return
            wallet[self.user_id] -= price
            owned.append(vname)
            delivery_equipped_vehicle[self.user_id] = vname
            save_data()
            await interaction.response.send_message(
                f"Bought & equipped **{DELIVERY_VEHICLES[vname]['emoji']} {vname}** "
                f"for **{format_coins(price)}** coins!",
                ephemeral=True,
            )
        return callback


@bot.command(aliases=["vshop"])
async def vehicleshop(ctx):
    """Browse and buy delivery vehicles."""
    user_id  = ctx.author.id
    owned    = get_owned_vehicles(user_id)
    equipped = get_equipped_vehicle(user_id)

    embed = discord.Embed(
        title="🚗 Delivery Vehicle Shop",
        description=(
            f"**Equipped:** {DELIVERY_VEHICLES[equipped]['emoji']} {equipped}\n"
            f"**Wallet:** {format_coins(get_wallet(user_id))} coins\n\n"
            "Click a button to **buy** or **equip** a vehicle."
        ),
        color=discord.Color.blurple(),
    )
    for vname, vdata in DELIVERY_VEHICLES.items():
        status = "✅ Owned" if vname in owned else f"💰 {format_coins(vdata['price'])}"
        lvl_line = f"🔒 Level {vdata['level_req']} required\n" if vdata["level_req"] > 0 else ""
        embed.add_field(
            name=f"{vdata['emoji']} {vname}",
            value=(
                f"{status}\n"
                f"{lvl_line}"
                f"⏱️ +{vdata['time_bonus']}s  |  💵 x{vdata['reward_multiplier']}"
            ),
            inline=True,
        )
    await ctx.send(embed=embed, view=VehicleShopView(ctx.author, user_id))


@bot.command(aliases=["veh"])
async def vehicle(ctx, *, vname: str = None):
    """Equip a vehicle you own."""
    user_id = ctx.author.id
    if not vname:
        eq = get_equipped_vehicle(user_id)
        return await ctx.send(
            f"Your equipped vehicle: **{DELIVERY_VEHICLES[eq]['emoji']} {eq}**"
        )
    match = next(
        (n for n in DELIVERY_VEHICLES if n.lower() == vname.strip().lower()), None
    )
    if not match:
        return await ctx.send("Unknown vehicle. Use `!vehicleshop` to see options.")
    if match not in get_owned_vehicles(user_id):
        return await ctx.send(f"You don't own **{match}** yet. Buy it from `!vehicleshop`.")
    delivery_equipped_vehicle[user_id] = match
    save_data()
    await ctx.send(f"Equipped **{DELIVERY_VEHICLES[match]['emoji']} {match}**.")


# ── Delivery minigame UI ─────────────────────────────────────────────────────
class DeliveryView(discord.ui.View):
    """One button row for a single delivery step."""
    def __init__(self, requester_id: int, correct_direction: str, timeout: float):
        super().__init__(timeout=timeout)
        self.requester_id      = requester_id
        self.correct_direction = correct_direction
        self.result            = None  # "correct" | "wrong" | None (timeout)

        for direction in DELIVERY_DIRECTIONS:
            btn = discord.ui.Button(
                label=DELIVERY_DIR_EMOJI[direction],
                style=discord.ButtonStyle.primary,
            )
            btn.callback = self._make_cb(direction)
            self.add_item(btn)

    def _make_cb(self, direction: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester_id:
                await interaction.response.send_message(
                    "This isn't your delivery!", ephemeral=True
                )
                return
            self.result = "correct" if direction == self.correct_direction else "wrong"
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            self.stop()
        return callback


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def delivery(ctx):
    """Start a timed delivery minigame."""
    user_id = ctx.author.id

    if user_id in delivery_active:
        return await ctx.send("You're already on a delivery!")

    delivery_active.add(user_id)

    try:
        equipped   = get_equipped_vehicle(user_id)
        vdata      = DELIVERY_VEHICLES[equipped]
        is_vip     = random.random() < DELIVERY_VIP_CHANCE
        step_count = vdata["steps_vip"] if is_vip else vdata["steps_normal"]
        route      = [random.choice(DELIVERY_DIRECTIONS) for _ in range(step_count)]
        time_limit = DELIVERY_BASE_TIME + vdata["time_bonus"]
        step_timeout = time_limit / step_count

        customer_label    = "⭐ **VIP Customer**" if is_vip else "👤 Normal Customer"
        base_reward_range = DELIVERY_BASE_REWARD_VIP if is_vip else DELIVERY_BASE_REWARD_NORMAL

        intro_embed = discord.Embed(
            title="🚦 Delivery Started!",
            description=(
                f"**Vehicle:** {vdata['emoji']} {equipped}\n"
                f"**Customer:** {customer_label}\n"
                f"**Route:** {step_count} steps\n"
                f"**Time per step:** {step_timeout:.1f}s\n\n"
                "Follow the directions — click the correct button fast!"
            ),
            color=discord.Color.blurple(),
        )
        msg = await ctx.send(embed=intro_embed)
        await asyncio.sleep(1.5)

        start_time  = time.monotonic()
        failed      = False
        fail_reason = ""

        for step_idx, direction in enumerate(route, start=1):
            step_embed = discord.Embed(
                title=f"🚦 Delivery — Step {step_idx}/{step_count}",
                description=(
                    f"**Direction:** {DELIVERY_DIR_EMOJI[direction]} **{direction}**\n\n"
                    f"⬅️ LEFT  |  ➡️ RIGHT  |  ⬆️ FORWARD  |  ⬇️ BACK\n\n"
                    f"⏱️ You have **{step_timeout:.1f}s** per step."
                ),
                color=discord.Color.orange(),
            )
            step_embed.set_footer(
                text=f"Vehicle: {vdata['emoji']} {equipped}  •  "
                     f"Customer: {'VIP ⭐' if is_vip else 'Normal'}"
            )
            view = DeliveryView(user_id, direction, timeout=step_timeout)
            await msg.edit(embed=step_embed, view=view)
            await view.wait()

            if view.result is None:
                failed      = True
                fail_reason = "⏱️ You ran out of time!"
                break
            if view.result == "wrong":
                failed      = True
                fail_reason = "❌ Wrong direction — package dropped!"
                break

        elapsed = time.monotonic() - start_time

        if failed:
            fail_embed = discord.Embed(
                title="📦 Delivery Failed!",
                description=(
                    f"{fail_reason}\n\n"
                    "Better luck next time. Use `!delivery` to try again."
                ),
                color=discord.Color.red(),
            )
            fail_embed.set_footer(text=f"Vehicle: {vdata['emoji']} {equipped}")
            await msg.edit(embed=fail_embed, view=None)
            return

        # ── Success — calculate reward ────────────────────────────────────
        base_reward  = random.randint(*base_reward_range)
        speed_ratio  = max(0.0, 1.0 - (elapsed / time_limit))
        speed_bonus  = 1.0 + speed_ratio * 0.5          # up to +50 %
        final_reward = int(base_reward * vdata["reward_multiplier"] * speed_bonus * pet_bonus_multiplier(user_id, "delivery"))

        wallet.setdefault(user_id, 0)
        wallet[user_id] += final_reward
        gen_xp_gain = random.randint(40, 80)
        new_gen_level, gen_leveled = add_general_xp(user_id, gen_xp_gain)
        save_data()

        speed_label = (
            "🔥 Lightning!" if speed_ratio > 0.75 else
            "✅ Fast"        if speed_ratio > 0.40 else
            "🐢 Just in time"
        )

        success_embed = discord.Embed(
            title="📦 Delivery Complete!",
            description=(
                f"You delivered the package successfully!\n\n"
                f"**Customer:** {customer_label}\n"
                f"**Route length:** {step_count} steps\n"
                f"**Completion:** {speed_label} ({elapsed:.1f}s / {time_limit}s)\n\n"
                f"💰 **+{format_coins(final_reward)} coins**\n"
                f"⬆️ **+{gen_xp_gain} General XP** (Level {new_gen_level})"
            ),
            color=discord.Color.green(),
        )
        if gen_leveled:
            success_embed.add_field(
                name="🎉 General Level Up!",
                value=f"You reached **Level {new_gen_level}**!",
                inline=False,
            )
        success_embed.add_field(
            name="Breakdown",
            value=(
                f"Base: {format_coins(base_reward)}\n"
                f"Vehicle bonus: x{vdata['reward_multiplier']}\n"
                f"Speed bonus: x{speed_bonus:.2f}"
            ),
            inline=False,
        )
        success_embed.set_footer(text=f"Wallet: {format_coins(get_wallet(user_id))} coins")
        await msg.edit(embed=success_embed, view=None)

    finally:
        delivery_active.discard(user_id)


@delivery.error
async def delivery_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"⏳ Cooldown! Start another delivery in **{error.retry_after:.1f}s**."
        )
    else:
        raise error


# ======================== HOOK & BAIT SYSTEM ==================================

class HookShopView(discord.ui.View):
    def __init__(self, requester, user_id: int):
        super().__init__(timeout=120)
        self.requester = requester
        self.user_id   = user_id
        self._build()

    def _build(self):
        self.clear_items()
        owned    = get_owned_hooks(self.user_id)
        equipped = get_equipped_hook(self.user_id)
        for hname, hdata in FISHING_HOOKS.items():
            is_equipped = hname == equipped
            is_owned    = hname in owned
            if is_equipped:
                label = f"✅ {hdata['emoji']} {hname}"
                style = discord.ButtonStyle.success
            elif is_owned:
                label = f"Equip {hdata['emoji']} {hname}"
                style = discord.ButtonStyle.secondary
            else:
                label = f"Buy {hdata['emoji']} {hname}"
                style = discord.ButtonStyle.primary
            btn = discord.ui.Button(label=label, style=style)
            btn.callback = self._make_cb(hname)
            self.add_item(btn)

    def _make_cb(self, hname: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("Not your shop.", ephemeral=True)
                return
            owned = get_owned_hooks(self.user_id)
            hdata = FISHING_HOOKS[hname]
            if hname in owned:
                hooks_equipped[self.user_id] = hname
                save_data()
                self._build()
                await interaction.response.edit_message(embed=_build_hookshop_embed(self.user_id), view=self)
                return
            level_req = hdata["level_req"]
            if get_general_level(self.user_id) < level_req:
                await interaction.response.send_message(
                    f"You need **General Level {level_req}** to buy **{hname}**. "
                    f"(You are Level {get_general_level(self.user_id)})", ephemeral=True)
                return
            if get_wallet(self.user_id) < hdata["price"]:
                await interaction.response.send_message(
                    f"You need **{format_coins(hdata['price'])}** coins.", ephemeral=True)
                return
            wallet[self.user_id] -= hdata["price"]
            owned.append(hname)
            hooks_equipped[self.user_id] = hname
            save_data()
            self._build()
            await interaction.response.edit_message(embed=_build_hookshop_embed(self.user_id), view=self)
        return callback


def _build_hookshop_embed(user_id):
    owned    = get_owned_hooks(user_id)
    equipped = get_equipped_hook(user_id)
    embed = discord.Embed(
        title="🪝 Hook Shop",
        description=(
            f"**Equipped:** {FISHING_HOOKS[equipped]['emoji']} {equipped}\n"
            f"**General Level:** {get_general_level(user_id)}  |  **Wallet:** {format_coins(get_wallet(user_id))} coins\n\n"
            "Hooks boost **catch rate, rarity & legendary chances**."
        ),
        color=discord.Color.teal(),
    )
    for hname, hdata in FISHING_HOOKS.items():
        if hname in owned:
            status = "✅ Equipped" if hname == equipped else "✅ Owned"
        else:
            status = f"💰 {format_coins(hdata['price'])}"
        lvl_line = f"🔒 Lvl {hdata['level_req']}  " if hdata["level_req"] > 0 else ""
        embed.add_field(
            name=f"{hdata['emoji']} {hname}",
            value=(
                f"{status}  {lvl_line}\n"
                f"+{hdata['rare_bonus']} rare  +{hdata['shark_bonus']} shark\n"
                f"+{int(hdata['legendary_bonus']*100)}% legendary"
            ),
            inline=True,
        )
    embed.set_footer(text="Click Buy to purchase and auto-equip.")
    return embed


@bot.command(aliases=["hshop"])
async def hookshop(ctx):
    user_id = ctx.author.id
    await ctx.send(embed=_build_hookshop_embed(user_id), view=HookShopView(ctx.author, user_id))


@bot.command()
async def hook(ctx, *, hname: str = None):
    user_id = ctx.author.id
    if not hname:
        eq = get_equipped_hook(user_id)
        return await ctx.send(f"Equipped hook: **{FISHING_HOOKS[eq]['emoji']} {eq}**")
    match = next((n for n in FISHING_HOOKS if n.lower() == hname.strip().lower()), None)
    if not match:
        return await ctx.send("Unknown hook. Use `!hookshop`.")
    if match not in get_owned_hooks(user_id):
        return await ctx.send(f"You don\'t own **{match}**. Buy it from `!hookshop`.")
    hooks_equipped[user_id] = match
    save_data()
    await ctx.send(f"Equipped **{FISHING_HOOKS[match]['emoji']} {match}**.")


# ── Bait shop ────────────────────────────────────────────────────────────────
BAIT_BUY_AMOUNTS = [1, 5, 10, 50]


class BaitShopView(discord.ui.View):
    """
    Shows one row of bait-select buttons and one row of quantity buttons.
    The selected bait + quantity is stored on the view, confirmed with a Buy button.
    """
    def __init__(self, requester, user_id: int):
        super().__init__(timeout=120)
        self.requester    = requester
        self.user_id      = user_id
        self.selected_bait = None
        self.selected_qty  = 1
        self._build()

    def _build(self):
        self.clear_items()

        # Row 0: bait select
        for bname, bdata in FISHING_BAITS.items():
            is_selected = bname == self.selected_bait
            is_worm     = bname == "Worm"
            if is_worm:
                btn = discord.ui.Button(
                    label=f"{bdata['emoji']} Equip Worm",
                    style=discord.ButtonStyle.secondary,
                    row=0,
                )
                btn.callback = self._equip_worm_cb()
            else:
                btn = discord.ui.Button(
                    label=f"{bdata['emoji']} {bname}",
                    style=discord.ButtonStyle.success if is_selected else discord.ButtonStyle.primary,
                    row=0,
                )
                btn.callback = self._select_bait_cb(bname)
            self.add_item(btn)

        # Row 1: qty buttons (only shown when a non-worm bait is selected)
        if self.selected_bait and self.selected_bait != "Worm":
            for qty in BAIT_BUY_AMOUNTS:
                btn = discord.ui.Button(
                    label=f"x{qty}",
                    style=discord.ButtonStyle.success if qty == self.selected_qty else discord.ButtonStyle.secondary,
                    row=1,
                )
                btn.callback = self._select_qty_cb(qty)
                self.add_item(btn)

            # Row 2: confirm buy + equip buttons
            buy_btn = discord.ui.Button(label=f"🛒 Buy x{self.selected_qty}", style=discord.ButtonStyle.danger, row=2)
            buy_btn.callback = self._buy_cb()
            self.add_item(buy_btn)

            equip_btn = discord.ui.Button(label="✅ Equip this bait", style=discord.ButtonStyle.success, row=2)
            equip_btn.callback = self._equip_cb()
            self.add_item(equip_btn)

    def _select_bait_cb(self, bname):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("Not your shop.", ephemeral=True)
                return
            self.selected_bait = bname
            self.selected_qty  = 1
            self._build()
            await interaction.response.edit_message(embed=_build_baitshop_embed(self.user_id, self.selected_bait), view=self)
        return callback

    def _equip_worm_cb(self):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("Not your shop.", ephemeral=True)
                return
            bait_equipped[self.user_id] = "Worm"
            save_data()
            self._build()
            await interaction.response.edit_message(embed=_build_baitshop_embed(self.user_id, self.selected_bait), view=self)
        return callback

    def _select_qty_cb(self, qty):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("Not your shop.", ephemeral=True)
                return
            self.selected_qty = qty
            self._build()
            await interaction.response.edit_message(embed=_build_baitshop_embed(self.user_id, self.selected_bait), view=self)
        return callback

    def _buy_cb(self):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("Not your shop.", ephemeral=True)
                return
            bname = self.selected_bait
            qty   = self.selected_qty
            bdata = FISHING_BAITS[bname]

            level_req = bdata["level_req"]
            if get_general_level(self.user_id) < level_req:
                await interaction.response.send_message(
                    f"You need **General Level {level_req}** for **{bname}**. "
                    f"(You are Level {get_general_level(self.user_id)})", ephemeral=True)
                return
            total = bdata["price"] * qty
            if get_wallet(self.user_id) < total:
                await interaction.response.send_message(
                    f"You need **{format_coins(total)}** coins for {qty}× {bname}. "
                    f"(You have {format_coins(get_wallet(self.user_id))})", ephemeral=True)
                return
            wallet[self.user_id] -= total
            inv = get_bait_inventory(self.user_id)
            inv[bname] = inv.get(bname, 0) + qty
            save_data()
            self._build()
            await interaction.response.edit_message(embed=_build_baitshop_embed(self.user_id, self.selected_bait), view=self)
        return callback

    def _equip_cb(self):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("Not your shop.", ephemeral=True)
                return
            bname = self.selected_bait
            inv   = get_bait_inventory(self.user_id)
            if inv.get(bname, 0) <= 0:
                await interaction.response.send_message(
                    f"You don\'t have any **{bname}** yet. Buy some first!", ephemeral=True)
                return
            bait_equipped[self.user_id] = bname
            save_data()
            self._build()
            await interaction.response.edit_message(embed=_build_baitshop_embed(self.user_id, self.selected_bait), view=self)
        return callback


def _build_baitshop_embed(user_id, selected_bait=None):
    inv      = get_bait_inventory(user_id)
    equipped = get_equipped_bait(user_id)
    embed = discord.Embed(
        title="🎣 Bait Shop",
        description=(
            f"**Equipped:** {FISHING_BAITS[equipped]['emoji']} {equipped}\n"
            f"**General Level:** {get_general_level(user_id)}  |  **Wallet:** {format_coins(get_wallet(user_id))} coins\n\n"
            "Bait boosts **coin rewards** per catch. Consumed once per cast."
        ),
        color=discord.Color.blue(),
    )
    for bname, bdata in FISHING_BAITS.items():
        qty      = "∞" if inv.get(bname, 0) == -1 else str(inv.get(bname, 0))
        lvl_line = f"🔒 Lvl {bdata['level_req']}  " if bdata["level_req"] > 0 else ""
        selected_marker = " 👈" if bname == selected_bait else ""
        embed.add_field(
            name=f"{bdata['emoji']} {bname}{selected_marker}",
            value=(
                f"💰 {format_coins(bdata['price'])} each  {lvl_line}\n"
                f"+{int(bdata['reward_bonus']*100)}% coins\n"
                f"Stock: **{qty}**"
            ),
            inline=True,
        )
    if selected_bait and selected_bait != "Worm":
        bdata = FISHING_BAITS[selected_bait]
        embed.set_footer(text=f"Selected: {selected_bait} — pick a quantity then hit Buy.")
    else:
        embed.set_footer(text="Click a bait to select it, then choose a quantity.")
    return embed


@bot.command(aliases=["bshop"])
async def baitshop(ctx):
    user_id = ctx.author.id
    await ctx.send(embed=_build_baitshop_embed(user_id), view=BaitShopView(ctx.author, user_id))


@bot.command()
async def buybait(ctx, *, args: str = None):
    """Buy bait via command — usage: !buybait <name> <amount>"""
    user_id = ctx.author.id
    if not args:
        return await ctx.send("Usage: `!buybait <bait name> <amount>`")
    parts = args.rsplit(" ", 1)
    if len(parts) < 2 or not parts[-1].isdigit():
        return await ctx.send("Usage: `!buybait <bait name> <amount>`  e.g. `!buybait Shrimp 10`")
    bname_raw, qty_str = parts[0].strip(), parts[1]
    qty = int(qty_str)
    if qty <= 0:
        return await ctx.send("Amount must be at least 1.")
    match = next((n for n in FISHING_BAITS if n.lower() == bname_raw.lower()), None)
    if not match:
        return await ctx.send("Unknown bait. Use `!baitshop`.")
    if match == "Worm":
        return await ctx.send("Worm is free and unlimited!")
    bdata = FISHING_BAITS[match]
    if get_general_level(user_id) < bdata["level_req"]:
        return await ctx.send(f"You need **General Level {bdata['level_req']}** for **{match}**.")
    total = bdata["price"] * qty
    if get_wallet(user_id) < total:
        return await ctx.send(f"You need **{format_coins(total)}** coins. (Have {format_coins(get_wallet(user_id))})")
    wallet[user_id] -= total
    inv = get_bait_inventory(user_id)
    inv[match] = inv.get(match, 0) + qty
    save_data()
    await ctx.send(f"Bought **{qty}× {bdata['emoji']} {match}** for **{format_coins(total)}** coins! Stock: **{inv[match]}**")


@bot.command()
async def bait(ctx, *, bname: str = None):
    user_id = ctx.author.id
    if not bname:
        eq  = get_equipped_bait(user_id)
        inv = get_bait_inventory(user_id)
        qty = "∞" if inv.get(eq, 0) == -1 else str(inv.get(eq, 0))
        return await ctx.send(f"Equipped bait: **{FISHING_BAITS[eq]['emoji']} {eq}** (Stock: {qty})")
    match = next((n for n in FISHING_BAITS if n.lower() == bname.strip().lower()), None)
    if not match:
        return await ctx.send("Unknown bait. Use `!baitshop`.")
    inv = get_bait_inventory(user_id)
    if match != "Worm" and inv.get(match, 0) <= 0:
        return await ctx.send(f"You don\'t have any **{match}**. Buy some with `!baitshop`.")
    bait_equipped[user_id] = match
    save_data()
    await ctx.send(f"Equipped **{FISHING_BAITS[match]['emoji']} {match}**.")



# ======================== GENERAL LEVEL =======================================

@bot.command(aliases=["rank", "lvl"])
async def level(ctx, member: discord.Member = None):
    """Check your (or someone else's) general level."""
    target  = member or ctx.author
    user_id = target.id
    gen_lvl = get_general_level(user_id)
    gen_xp  = get_general_xp(user_id)

    bar_filled = min(20, int((gen_xp % GENERAL_XP_PER_LEVEL) / GENERAL_XP_PER_LEVEL * 20))
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    embed = discord.Embed(
        title=f"📊 {target.display_name}'s Level",
        color=discord.Color.purple(),
    )
    embed.add_field(
        name="⬆️ General Level",
        value=(
            f"**Level {gen_lvl}**\n"
            f"`{bar}` {gen_xp % GENERAL_XP_PER_LEVEL}/{GENERAL_XP_PER_LEVEL} XP\n"
            f"Total XP: {gen_xp:,}"
        ),
        inline=False,
    )
    embed.add_field(name="🎣 Rod",     value=get_equipped_rod(user_id), inline=True)
    embed.add_field(name="🪝 Hook",    value=f"{FISHING_HOOKS[get_equipped_hook(user_id)]['emoji']} {get_equipped_hook(user_id)}", inline=True)
    embed.add_field(name="🛵 Vehicle", value=f"{DELIVERY_VEHICLES[get_equipped_vehicle(user_id)]['emoji']} {get_equipped_vehicle(user_id)}", inline=True)
    await ctx.send(embed=embed)


# ===== MUSIC COMMANDS =====

def ensure_music_state(guild_id):
    music_queue.setdefault(guild_id, [])
    music_now.setdefault(guild_id, None)
    music_locks.setdefault(guild_id, asyncio.Lock())
    recent_play_requests.setdefault(guild_id, {})


def cancel_music_idle_disconnect(guild_id):
    task = music_idle_tasks.pop(guild_id, None)
    if task and not task.done():
        task.cancel()


def cleanup_recent_requests(guild_id):
    ensure_music_state(guild_id)
    now = time.monotonic()
    recent_play_requests[guild_id] = {
        key: ts
        for key, ts in recent_play_requests[guild_id].items()
        if now - ts < 8
    }


def can_queue_play(guild_id, user_id, query):
    cleanup_recent_requests(guild_id)
    key = (user_id, query.strip().lower())
    now = time.monotonic()
    last = recent_play_requests[guild_id].get(key, 0)

    if now - last < 3:
        return False, round(3 - (now - last), 1)

    recent_play_requests[guild_id][key] = now
    return True, 0


def format_duration(seconds):
    if not seconds:
        return "Unknown"
    seconds = int(seconds)
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{sec:02d}"
    return f"{minutes}:{sec:02d}"


def build_music_embed(player, *, paused=False):
    title = "⏸️ Paused" if paused else "🎶 Now Playing"
    embed = discord.Embed(
        title=title,
        description=f"**{player.title}**",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Artist", value=player.artist or "Unknown artist", inline=True)
    embed.add_field(name="Duration", value=format_duration(getattr(player, "duration", None)), inline=True)
    if getattr(player, "webpage_url", None):
        embed.add_field(name="Source", value=f"[Open track]({player.webpage_url})", inline=False)
    if getattr(player, "thumbnail", None):
        embed.set_thumbnail(url=player.thumbnail)
    autoplay_state = music_autoplay.get(getattr(player, "guild_id", None), False) if hasattr(player, "guild_id") else False
    embed.set_footer(text=f"Pause, stop, skip, or toggle autoplay ({'ON' if autoplay_state else 'OFF'})")
    return embed


async def schedule_music_idle_disconnect(guild, text_channel):
    guild_id = guild.id
    cancel_music_idle_disconnect(guild_id)

    async def _worker():
        try:
            await asyncio.sleep(600)
            voice_client = guild.voice_client
            if (
                voice_client
                and not voice_client.is_playing()
                and not voice_client.is_paused()
                and not music_queue.get(guild_id)
                and music_now.get(guild_id) is None
            ):
                await voice_client.disconnect()
                await text_channel.send("Left the voice channel after 10 minutes of inactivity.")
        except asyncio.CancelledError:
            return
        finally:
            music_idle_tasks.pop(guild_id, None)

    music_idle_tasks[guild_id] = bot.loop.create_task(_worker())


async def ensure_voice(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("Join a voice channel first.")
        return None

    voice_client = ctx.voice_client
    target_channel = ctx.author.voice.channel

    try:
        if voice_client is None:
            voice_client = await target_channel.connect()
        elif voice_client.channel != target_channel:
            await voice_client.move_to(target_channel)
    except discord.Forbidden:
        await ctx.send("I don't have permission to join or speak in that voice channel.")
        return None
    except discord.ClientException as e:
        await ctx.send(f"Voice connection error: `{e}`")
        return None
    except Exception as e:
        await ctx.send(f"Couldn't join the voice channel: `{e}`")
        return None

    return voice_client


class MusicControlView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=600)
        self.guild_id = guild_id
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client if interaction.guild else None
        if voice_client is None or interaction.user.voice is None or interaction.user.voice.channel != voice_client.channel:
            await interaction.response.send_message("You need to be in my voice channel to use these controls.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        current = music_now.get(self.guild_id)
        if voice_client is None or current is None:
            await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            return

        if voice_client.is_paused():
            voice_client.resume()
            paused = False
            note = "Resumed playback."
        elif voice_client.is_playing():
            voice_client.pause()
            paused = True
            note = "Paused playback."
        else:
            await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            return

        if self.message:
            await self.message.edit(embed=build_music_embed(current, paused=paused), view=self)
        await interaction.response.send_message(note, ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)
            return

        music_autoplay[self.guild_id] = False
        music_queue[self.guild_id].clear()
        music_now[self.guild_id] = None
        music_starting.discard(self.guild_id)
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        await interaction.response.send_message("Stopped playback and cleared the queue.", ephemeral=True)
        channel = music_text_channels.get(self.guild_id)
        if channel:
            await schedule_music_idle_disconnect(interaction.guild, channel)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()
            await interaction.response.send_message("Skipped to the next track.", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

    @discord.ui.button(label="Autoplay", style=discord.ButtonStyle.success)
    async def autoplay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = music_now.get(self.guild_id)
        if current is None and not music_queue.get(self.guild_id):
            await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            return

        enabled = not music_autoplay.get(self.guild_id, False)
        music_autoplay[self.guild_id] = enabled
        button.label = f"Autoplay: {'ON' if enabled else 'OFF'}"

        current = music_now.get(self.guild_id)
        if self.message and current is not None:
            await self.message.edit(embed=build_music_embed(current, paused=bool(interaction.guild.voice_client and interaction.guild.voice_client.is_paused())), view=self)

        await interaction.response.send_message(
            f"Autoplay is now {'enabled' if enabled else 'disabled'}.",
            ephemeral=True,
        )


@bot.command()
async def join(ctx):
    voice_client = await ensure_voice(ctx)
    if voice_client is not None:
        await ctx.send(f"Joined **{voice_client.channel.name}**.")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        guild_id = ctx.guild.id
        ensure_music_state(guild_id)
        cancel_music_idle_disconnect(guild_id)
        music_autoplay[guild_id] = False
        music_queue[guild_id].clear()
        music_now[guild_id] = None
        music_starting.discard(guild_id)
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")


@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("Nothing is playing.")
        return

    guild_id = ctx.guild.id
    ensure_music_state(guild_id)
    music_autoplay[guild_id] = False
    music_queue[guild_id].clear()
    music_now[guild_id] = None
    music_starting.discard(guild_id)

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        ctx.voice_client.stop()

    await ctx.send("Stopped music and cleared the queue.")
    await schedule_music_idle_disconnect(ctx.guild, ctx.channel)


@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client is None:
        await ctx.send("Nothing is playing.")
        return

    guild_id = ctx.guild.id
    current = music_now.get(guild_id)
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resumed playback.")
        if current and guild_id in music_control_messages:
            try:
                await music_control_messages[guild_id].edit(embed=build_music_embed(current, paused=False))
            except Exception:
                pass
    elif voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused playback.")
        if current and guild_id in music_control_messages:
            try:
                await music_control_messages[guild_id].edit(embed=build_music_embed(current, paused=True))
            except Exception:
                pass
    else:
        await ctx.send("Nothing is playing.")


async def play_next(ctx):
    guild_id = ctx.guild.id
    ensure_music_state(guild_id)
    music_text_channels[guild_id] = ctx.channel

    voice_client = ctx.guild.voice_client
    if voice_client is None:
        music_now[guild_id] = None
        music_queue[guild_id].clear()
        music_starting.discard(guild_id)
        return

    if voice_client.is_playing() or voice_client.is_paused():
        music_starting.discard(guild_id)
        return

    if not music_queue[guild_id]:
        music_now[guild_id] = None
        music_starting.discard(guild_id)
        await schedule_music_idle_disconnect(ctx.guild, ctx.channel)
        return

    cancel_music_idle_disconnect(guild_id)
    next_query = music_queue[guild_id].pop(0)

    try:
        player = await YTDLSource.from_url(next_query, loop=bot.loop, stream=True)
    except Exception as e:
        music_now[guild_id] = None
        music_starting.discard(guild_id)
        error_text = str(e)
        if "Sign in to confirm you're not a bot" in error_text:
            await ctx.send(
                "Couldn't play that track because YouTube blocked the server. "
                "Use a song name for SoundCloud search or a non-YouTube direct link."
            )
        elif "Requested format is not available" in error_text:
            await ctx.send(
                "Couldn't play that track from the current source. "
                "Try a different song name, a SoundCloud link, or a direct audio link."
            )
        else:
            await ctx.send(f"Couldn't play that track: `{e}`")

        if music_queue[guild_id]:
            music_starting.add(guild_id)
            bot.loop.create_task(play_next(ctx))
        else:
            await schedule_music_idle_disconnect(ctx.guild, ctx.channel)
        return

    player.guild_id = guild_id
    music_now[guild_id] = player

    def after_play(error):
        if error:
            print(f"Player error: {error}")
        if music_autoplay.get(guild_id):
            music_queue[guild_id].insert(0, next_query)
        music_now[guild_id] = None
        music_starting.discard(guild_id)
        bot.loop.call_soon_threadsafe(lambda: bot.loop.create_task(play_next(ctx)))

    try:
        voice_client.play(player, after=after_play)
    except Exception as e:
        music_now[guild_id] = None
        music_starting.discard(guild_id)
        await ctx.send(f"Couldn't start playback: `{e}`")
        if music_queue[guild_id]:
            music_starting.add(guild_id)
            bot.loop.create_task(play_next(ctx))
        else:
            await schedule_music_idle_disconnect(ctx.guild, ctx.channel)
        return

    music_starting.discard(guild_id)
    view = MusicControlView(guild_id)
    message = await ctx.send(embed=build_music_embed(player), view=view)
    view.message = message
    music_control_messages[guild_id] = message


@bot.command(aliases=["p"])
@commands.cooldown(2, 5, BucketType.user)
async def play(ctx, *, query):
    voice_client = await ensure_voice(ctx)
    if voice_client is None:
        return

    resolved_query = normalize_music_query(query)
    if resolved_query is None:
        await ctx.send("YouTube links are blocked on Railway right now. Use a song name for SoundCloud search or a non-YouTube direct link.")
        return

    guild_id = ctx.guild.id
    ensure_music_state(guild_id)
    music_text_channels[guild_id] = ctx.channel
    cancel_music_idle_disconnect(guild_id)

    allowed, wait_time = can_queue_play(guild_id, ctx.author.id, query)
    if not allowed:
        await ctx.send(f"Slow down. Try again in **{wait_time}s**.")
        return

    async with music_locks[guild_id]:
        if len(music_queue[guild_id]) >= 25:
            await ctx.send("Queue is full right now. Try again after some songs finish.")
            return

        music_queue[guild_id].append(resolved_query)
        if (
            ctx.voice_client.is_playing()
            or ctx.voice_client.is_paused()
            or guild_id in music_starting
        ):
            await ctx.send(f"Added to queue: **{query}**")
            return

        music_starting.add(guild_id)

    await play_next(ctx)


@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Slow down. Try again in **{error.retry_after:.1f}s**.")
        return
    raise error


@bot.command()
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("Skipped.")
    else:
        await ctx.send("Nothing is playing.")


@bot.command()
async def queue(ctx):
    guild_id = ctx.guild.id
    ensure_music_state(guild_id)

    if not music_queue[guild_id]:
        await ctx.send("The queue is empty.")
        return

    lines = []
    for index, item in enumerate(music_queue[guild_id][:10], start=1):
        lines.append(f"{index}. {item}")

    embed = discord.Embed(
        title="Music Queue",
        description="\n".join(lines),
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed)


@bot.command()
async def np(ctx):
    guild_id = ctx.guild.id
    ensure_music_state(guild_id)
    current = music_now.get(guild_id)

    if current is None:
        await ctx.send("Nothing is playing right now.")
        return

    await ctx.send(embed=build_music_embed(current, paused=bool(ctx.voice_client and ctx.voice_client.is_paused())))


@bot.command()
async def search(ctx, *, query):
    try:
        results = await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: search_youtube(f"scsearch5:{query}")
        )
    except Exception as e:
        await ctx.send(f"Search failed: `{e}`")
        return

    if not results:
        await ctx.send("No results found.")
        return

    embed = discord.Embed(
        title=f"SoundCloud Results for: {query}",
        color=discord.Color.blurple()
    )

    for index, item in enumerate(results[:5], start=1):
        title = item.get("title", "Unknown title")
        url = item.get("webpage_url", "No URL")
        embed.add_field(name=f"{index}. {title}", value=url, inline=False)

    embed.set_footer(text="Use !play or !p with a song name or one of these SoundCloud links.")
    await ctx.send(embed=embed)


# ============ BLACKLIST ============
blacklisted = set()

@bot.command(aliases=["bl"])
async def blacklist(ctx, member: discord.Member = None):
    if ctx.author.id != OWNER_ID:
        return
    if member is None:
        await ctx.send("Tag someone! `!bl @user`")
        return
    blacklisted.add(member.id)
    await ctx.send(f"🚫 {member.mention} has been blacklisted.")

@bot.command(aliases=["wl"])
async def whitelist(ctx, member: discord.Member = None):
    if ctx.author.id != OWNER_ID:
        return
    if member is None:
        await ctx.send("Tag someone! `!wl @user`")
        return
    blacklisted.discard(member.id)
    await ctx.send(f"✅ {member.mention} has been whitelisted.")

@bot.check
async def check_blacklist(ctx):
    if ctx.author.id in blacklisted:
        await ctx.send(f"🚫 {ctx.author.mention} you are blacklisted and cannot use any commands.")
        return False
    return True



# =========== TOKEN ==============

bot.run(os.environ.get("TOKEN"))







