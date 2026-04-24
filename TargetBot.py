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

DATA_FILE = "/app/data/data.json"

music_queue = {}
music_now = {}
music_locks = {}
recent_play_requests = {}
music_starting = set()
private_bal = {}
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

# ── Delivery system ──────────────────────────────────────────────────────────
delivery_active = set()
delivery_vehicles_owned: dict[int, list] = {}
delivery_equipped_vehicle: dict[int, str] = {}

OWNER_ID = 756539405463978024

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
    "kraken": {
        "emoji": "🦑",
        "name":  "Kraken",
        "base_reward":   1_000_000,
        "base_chance":   0.001,          # 0.1 % at Lv 1 / Basic Rod
    },
    "bloop":  {
        "emoji": "🌊",
        "name":  "Bloop",
        "base_reward":   3_000_000,
        "base_chance":   0.0005,         # 0.05 % at Lv 1 / Basic Rod
    },
}

# ── Delivery vehicles ────────────────────────────────────────────────────────
DELIVERY_VEHICLES = {
    "Scooter":   {"price": 0,         "time_bonus": 0,  "reward_multiplier": 1.00, "emoji": "🛵", "steps_normal": 5, "steps_vip": 7},
    "Bike":      {"price": 25_000,    "time_bonus": 5,  "reward_multiplier": 1.10, "emoji": "🚲", "steps_normal": 5, "steps_vip": 6},
    "Car":       {"price": 200_000,   "time_bonus": 10, "reward_multiplier": 1.25, "emoji": "🚗", "steps_normal": 4, "steps_vip": 5},
    "Super Van": {"price": 2_000_000, "time_bonus": 20, "reward_multiplier": 1.50, "emoji": "🚀", "steps_normal": 3, "steps_vip": 4},
}

DELIVERY_BASE_TIME      = 20          # seconds before vehicle bonus
DELIVERY_DIRECTIONS     = ["LEFT", "RIGHT", "FORWARD", "BACK"]
DELIVERY_DIR_EMOJI      = {"LEFT": "⬅️", "RIGHT": "➡️", "FORWARD": "⬆️", "BACK": "⬇️"}
DELIVERY_VIP_CHANCE     = 0.05        # 5 % chance of VIP customer
DELIVERY_BASE_REWARD_NORMAL = (800,  2_500)
DELIVERY_BASE_REWARD_VIP    = (100_000, 100_000)


def load_data():
    global farm_xp, farm_level, player_health, player_lives, player_points, wallet, bank, economy_claims, jail
    global fishing_xp, fishing_level, fishing_rods_owned, fishing_equipped_rod, private_bal
    global delivery_vehicles_owned, delivery_equipped_vehicle

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
    fishing_level = {int(k): v for k, v in data.get("fishing_level", {}).items()}
    fishing_xp = {int(k): v for k, v in data.get("fishing_xp", {}).items()}
    fishing_rods_owned = {int(k): v for k, v in data.get("fishing_rods_owned", {}).items()}
    fishing_equipped_rod = {int(k): v for k, v in data.get("fishing_equipped_rod", {}).items()}
    delivery_vehicles_owned = {int(k): v for k, v in data.get("delivery_vehicles_owned", {}).items()}
    delivery_equipped_vehicle = {int(k): v for k, v in data.get("delivery_equipped_vehicle", {}).items()}


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
            "fishing_level": {str(k): v for k, v in fishing_level.items()},
            "fishing_rods_owned": {str(k): v for k, v in fishing_rods_owned.items()},
            "fishing_equipped_rod": {str(k): v for k, v in fishing_equipped_rod.items()},
            "delivery_vehicles_owned": {str(k): v for k, v in delivery_vehicles_owned.items()},
            "delivery_equipped_vehicle": {str(k): v for k, v in delivery_equipped_vehicle.items()},
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


def get_owned_rods(user_id):
    rods = fishing_rods_owned.setdefault(user_id, ["Basic Rod"])
    if "Basic Rod" not in rods:
        rods.insert(0, "Basic Rod")
    return rods


def get_equipped_rod(user_id):
    equipped = fishing_equipped_rod.setdefault(user_id, "Basic Rod")
    if equipped not in get_owned_rods(user_id):
        equipped = "Basic Rod"
        fishing_equipped_rod[user_id] = equipped
    return equipped


def find_rod_name(name):
    wanted = str(name).strip().lower()
    for rod_name in FISHING_RODS:
        if rod_name.lower() == wanted:
            return rod_name
    return None


def build_fishing_grid(catch_position):
    cells = ["⬜"] * 9
    cells[catch_position - 1] = "🐟"
    return "\n".join([
        " ".join(cells[0:3]),
        " ".join(cells[3:6]),
        " ".join(cells[6:9]),
    ])


def choose_fish_catch(rod_name):
    rod_data = FISHING_RODS[rod_name]
    boot_weight = 8
    rare_weight = 20 + rod_data["rare_bonus"]
    shark_weight = 2 + rod_data["shark_bonus"]
    small_weight = max(1, 100 - boot_weight - rare_weight - shark_weight)

    return random.choices(
        ["small", "rare", "shark", "boot"],
        weights=[small_weight, rare_weight, shark_weight, boot_weight],
        k=1,
    )[0]


def _legendary_chance_multiplier(fishing_level_val: int, rare_bonus: int) -> float:
    """
    Scales legendary spawn chance slightly with progression.
    Max multiplier is capped at 3.0x to keep both fish endgame-rare.
      - Level 0  / Basic Rod  → 1.00x  (base chance)
      - Level 50 / OP Rod     → ≈ 2.1x
      - Level 100/ Unbelievable → ≈ 3.0x
    """
    level_factor = 1.0 + min(fishing_level_val, 100) * 0.01   # up to +100 %
    rod_factor   = 1.0 + min(rare_bonus, 30)        * 0.033   # up to +99 %
    return min(level_factor * rod_factor, 3.0)


def check_legendary_catch(rod_name: str, fishing_level_val: int) -> str | None:
    """
    Independent lottery for Kraken / Bloop before the normal catch table.
    Returns 'kraken', 'bloop', or None.
    """
    rod_data   = FISHING_RODS[rod_name]
    multiplier = _legendary_chance_multiplier(fishing_level_val, rod_data["rare_bonus"])

    kraken_chance = FISHING_CATCHES["kraken"]["base_chance"] * multiplier
    bloop_chance  = FISHING_CATCHES["bloop"]["base_chance"]  * multiplier

    roll = random.random()
    if roll < bloop_chance:         # Bloop checked first (rarer, so narrower window)
        return "bloop"
    if roll < bloop_chance + kraken_chance:
        return "kraken"
    return None


def legendary_reward(catch_key: str, rod_name: str, fishing_level_val: int) -> int:
    """Scales legendary fish coin reward with rod multiplier and level."""
    base          = FISHING_CATCHES[catch_key]["base_reward"]
    rod_mult      = FISHING_RODS[rod_name]["reward_multiplier"]
    level_bonus   = 1.0 + min(fishing_level_val, 100) * 0.005   # up to +50 %
    return int(base * rod_mult * level_bonus)


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


def clean_lyrics_title(text):
    if not text:
        return ""

    cleaned = text
    cleaned = re.sub(r"\([^)]*(official|video|audio|lyrics?|visualizer|hd|4k)[^)]*\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[[^\]]*(official|video|audio|lyrics?|visualizer|hd|4k)[^\]]*\]", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(official video|official audio|lyrics video|lyric video|visualizer|audio|lyrics|hd|4k)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    return cleaned.strip()


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

        # Add breathing room so the text feels larger / less cramped.
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
        embed.description += f"\n\n[Open track]({source_url})"
    embed.set_footer(text=f"Lyrics page {page_index + 1}/{total_pages}")
    return embed


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

@bot.command()
async def lyrics(ctx):
    guild = ctx.guild

    if guild.id not in music_now or music_now[guild.id] is None:
        return await ctx.send("Nothing is playing right now.")

    current = music_now[guild.id]
    title = current.title
    artist = getattr(current, "artist", None)
    track = getattr(current, "track", None)
    source_url = getattr(current, "webpage_url", None)

    await ctx.send(f"Searching lyrics for: **{title}**")

    try:
        lyrics_text = None
        found_label = title

        cleaned_title = clean_lyrics_title(title)
        cleaned_track = clean_lyrics_title(track or title)
        cleaned_artist = clean_lyrics_title(artist or "")

        search_queries = []
        if cleaned_artist and cleaned_track:
            search_queries.append(f"{cleaned_artist} {cleaned_track}")
        if cleaned_title:
            search_queries.append(cleaned_title)
        if title not in search_queries:
            search_queries.append(title)

        for search_query in search_queries:
            lrclib_url = f"https://lrclib.net/api/search?q={quote_plus(search_query)}"
            response = requests.get(
                lrclib_url,
                timeout=10,
                headers={"User-Agent": "TargetBot/1.0"}
            )

            if not response.ok:
                continue

            results = response.json()
            if not isinstance(results, list) or not results:
                continue

            best = results[0]
            lyrics_text = best.get("plainLyrics") or best.get("syncedLyrics")
            if lyrics_text:
                best_artist = best.get("artistName") or artist or "Unknown artist"
                best_track = best.get("trackName") or track or title
                found_label = f"{best_artist} - {best_track}"
                break

        if not lyrics_text:
            title_parts = [part.strip() for part in cleaned_title.split(" - ") if part.strip()]
            fallback_pairs = []

            if cleaned_artist and cleaned_track:
                fallback_pairs.append((cleaned_artist, cleaned_track))
            if len(title_parts) > 1:
                fallback_pairs.append((title_parts[0], title_parts[-1]))
            fallback_pairs.append((artist or "unknown", track or cleaned_title or title))

            seen_pairs = set()
            for fallback_artist, fallback_song in fallback_pairs:
                pair = (fallback_artist.strip().lower(), fallback_song.strip().lower())
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                fallback_url = (
                    f"https://api.lyrics.ovh/v1/"
                    f"{quote_plus(fallback_artist)}/{quote_plus(fallback_song)}"
                )
                fallback_response = requests.get(
                    fallback_url,
                    timeout=10,
                    headers={"User-Agent": "TargetBot/1.0"}
                )

                if not fallback_response.ok:
                    continue

                data = fallback_response.json()
                if "lyrics" in data and data["lyrics"].strip():
                    lyrics_text = data["lyrics"]
                    found_label = f"{fallback_artist} - {fallback_song}"
                    break

        if not lyrics_text:
            return await ctx.send("Lyrics not found.")

        lyrics_text = format_lyrics_for_embed(lyrics_text)
        chunks = split_lyrics_chunks(lyrics_text, chunk_size=900)
        view = LyricsPaginatorView(ctx.author, found_label, chunks, source_url)
        message = await ctx.send(embed=view.current_embed(), view=view)
        view.message = message

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
            "I can handle economy, fun, jail, minigames, and music commands.\n\n"
            "If you need help, use `!commands`, `!cmds`, or `!help`."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(name="💰 Economy", value=(
        "`!balance` / `!bal @user`\n"
        "`!daily`\n"
        "`!weekly`\n"
        "`!monthly`\n"
        "`!transfer @user amount`\n"
        "`!deposit amount` / `!dep`\n"
        "`!withdraw amount` / `!wit`\n"
        "`!leaderboard` / `!lb` / `!rich`\n"
        "`!prv` / `!private` (hide balance)"
    ), inline=False)

    embed.add_field(name="🎰 Gambling", value=(
        "`!slots amount`\n"
        "`!blackjack amount` / `!bj`"
    ), inline=False)

    embed.add_field(name="🚔 Jail / Crime System", value=(
        "`!rob @user`\n"
        "`!guard`\n"
        "`!escape`\n"
        "`!bail`"
    ), inline=False)

    embed.add_field(name="🎮 Minigames", value=(
        "`!jerk`\n"
        "`!bazooka @user`"
    ), inline=False)

    embed.add_field(name="💘 Social / Fun", value=(
        "`!ship`\n"
        "`!date`\n"
        "`!stalk`\n"
        "`!gay`\n"
        "`!wanted`"
    ), inline=False)

    embed.add_field(name="🕵️ Utility / Admin", value=(
        "`!entity`\n"
        "`!expose @accomplice @victim`\n"
        "`!ping @user times` (owner only)\n"
        "`!afk reason`\n"
        "`!help`\n"
        "`!commands` / `!cmds`"
    ), inline=False)

    embed.set_footer(text="Need help? Use !commands, !cmds, or !help.")

    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed)
            break


# ================ HELP ==================
@bot.command()
async def help(ctx):

    await ctx.message.delete()

    embed = discord.Embed(
        title="📋 TargetBot Commands",
        description="Here's everything I can do!",
        color=discord.Color.blurple()
    )

    embed.add_field(name="💰 Economy", value=(
        "`!daily` — Collect coins every 24h\n"
        "`!weekly` — Weekly reward\n"
        "`!monthly` — Monthly reward\n"
        "`!balance` / `!bal` — Check your coin balance\n"
        "`!transfer @user amount` — Send coins\n"
        "`!deposit` / `!dep` — Bank deposit\n"
        "`!withdraw` / `!wit` — Bank withdraw\n"
        "`!leaderboard` / `!lb` — Richest players\n"
        "`!private` / `!prv` — Hide your balance"
    ), inline=False)

    embed.add_field(name="🎰 Gambling", value=(
        "`!slots amount` — Slot machine\n"
        "`!blackjack` / `!bj` — Blackjack game"
    ), inline=False)

    embed.add_field(name="🚔 Jail / Crime", value=(
        "`!rob @user` — Try to rob someone\n"
        "`!guard` — Jail guard event\n"
        "`!escape` — Escape jail\n"
        "`!bail` — Pay to get out"
    ), inline=False)

    embed.add_field(name="🎮 Minigames", value=(
        "`!jerk` — Tap XP game\n"
        "`!bazooka @user` — Reaction fight game"
    ), inline=False)

    embed.add_field(name="💘 Social / Fun", value=(
        "`!ship` — Compatibility\n"
        "`!date` — Random date\n"
        "`!stalk` — Creepy message event\n"
        "`!gay` — Random picker\n"
        "`!wanted` — Wanted poster\n"
        "`!expose @a @b` — Expose someone"
    ), inline=False)

    embed.add_field(name="🕵️ Utility", value=(
        "`!help` — Show this help menu\n"
        "`!avatar` / `!av` — Show avatar\n"
        "`!entity` — Scan system\n"
        "`!afk reason` — Set AFK\n"
        "`!ping @user times` — Spam ping (owner)\n"
        "`!commands` / `!cmds` — Website commands"
    ), inline=False)

    embed.add_field(name="🎧 Music", value=(
        "`!join` — Join voice channel\n"
        "`!leave` — Leave voice\n"
        "`!play <song/link>` — Play music or add to queue\n"
        "`!search <query>` — Search SoundCloud\n"
        "`!skip` — Skip current song\n"
        "`!stop` — Stop music and clear queue\n"
        "`!queue` — Show queued songs\n"
        "`!np` — Show current song"
    ), inline=False)

    embed.set_footer(text="Use !commands for the commands website 🔥")

    try:
        await ctx.author.send(embed=embed)
    except discord.Forbidden:
        await ctx.send(embed=embed, delete_after=30)




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
    await ctx.send("?? your balance is now private")


@bot.command(aliases=["unprv"])
async def unprivate(ctx):
    user = ctx.author.id
    private_bal.pop(user, None)
    save_data()
    await ctx.send("?? your balance is no longer private")



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
        self.user_id = user_id

        for rod_name, rod_data in FISHING_RODS.items():
            style = discord.ButtonStyle.success if rod_data["price"] == 0 else discord.ButtonStyle.primary
            button = discord.ui.Button(
                label=rod_name,
                style=style,
                row=0 if len(self.children) < 5 else 1
            )
            button.callback = self.make_callback(rod_name)
            self.add_item(button)

    def make_callback(self, rod_name):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.requester.id:
                await interaction.response.send_message("This isn't your fish shop.", ephemeral=True)
                return

            owned = get_owned_rods(self.user_id)
            if rod_name in owned:
                await interaction.response.send_message(f"You already own **{rod_name}**.", ephemeral=True)
                return

            price = FISHING_RODS[rod_name]["price"]
            if get_wallet(self.user_id) < price:
                await interaction.response.send_message(
                    f"You need **{format_coins(price)}** coins for **{rod_name}**.",
                    ephemeral=True
                )
                return

            wallet[self.user_id] -= price
            owned.append(rod_name)
            save_data()
            await interaction.response.send_message(
                f"Bought **{rod_name}** for **{format_coins(price)}** coins. Use `!rod {rod_name}` to equip it.",
                ephemeral=True
            )

        return callback


@bot.command()
async def fishshop(ctx):
    user_id = ctx.author.id
    owned = get_owned_rods(user_id)
    equipped = get_equipped_rod(user_id)
    level = get_fishing_level_value(user_id)
    xp = get_fishing_xp(user_id)

    embed = discord.Embed(
        title="🎣 Fishing Rod Shop",
        description=(
            f"**Fishing Level:** {level}\n"
            f"**Fishing XP:** {xp}\n"
            f"**Equipped Rod:** {equipped}\n"
            f"**Wallet:** {format_coins(get_wallet(user_id))} coins"
        ),
        color=discord.Color.blurple()
    )

    for rod_name, rod_data in FISHING_RODS.items():
        status = "Owned" if rod_name in owned else f"Price: {format_coins(rod_data['price'])}"
        embed.add_field(
            name=rod_name,
            value=(
                f"{status}\n"
                f"Reward x{rod_data['reward_multiplier']}\n"
                f"Reaction: {rod_data['reaction_time']}s"
            ),
            inline=False
        )

    embed.set_footer(text="Use the buttons to buy rods, then equip one with !rod <name>.")
    await ctx.send(embed=embed, view=FishShopView(ctx.author, user_id))


@bot.command()
async def rod(ctx, *, rod_name: str = None):
    user_id = ctx.author.id

    if not rod_name:
        equipped = get_equipped_rod(user_id)
        await ctx.send(f"Your equipped rod is **{equipped}**.")
        return

    matched_rod = find_rod_name(rod_name)
    if not matched_rod:
        await ctx.send("Unknown rod. Use `!fishshop` to see available rods.")
        return

    if matched_rod not in get_owned_rods(user_id):
        await ctx.send(f"You don't own **{matched_rod}** yet.")
        return

    fishing_equipped_rod[user_id] = matched_rod
    save_data()
    await ctx.send(f"Equipped **{matched_rod}**.")


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

        rod_data = FISHING_RODS[equipped]

        waiting_embed = discord.Embed(
            title="🎣 Fishing Time",
            description="You threw your bait into the water...\n\nWaiting for a fish...",
            color=discord.Color.blurple()
        )
        waiting_embed.set_footer(text=f"Rod: {equipped}")

        game_message = await ctx.send(embed=waiting_embed)

        await asyncio.sleep(2)

        position = random.randint(1, 9)
        grid = build_fishing_grid(position)

        prompt_embed = discord.Embed(
            title="🎣 A Fish Appeared!",
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
        prompt_embed.set_footer(text=f"Rod: {equipped} • Time: {rod_data['reaction_time']}s")
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
            fishing_level_val = get_fishing_level_value(user_id)

            # ── Legendary check (independent lottery) ───────────────────────
            legendary_key = check_legendary_catch(equipped, fishing_level_val)

            if legendary_key:
                catch_key = legendary_key
                catch     = FISHING_CATCHES[catch_key]
                reward    = legendary_reward(catch_key, equipped, fishing_level_val)
            else:
                catch_key = choose_fish_catch(equipped)
                catch     = FISHING_CATCHES[catch_key]
                reward    = int(catch["reward"] * rod_data["reward_multiplier"])
            # ────────────────────────────────────────────────────────────────

            wallet.setdefault(user_id, 0)
            wallet[user_id] += reward

            leveled_up = False
            new_level = get_fishing_level_value(user_id)

            if catch_key not in ("boot",):
                xp_gained = random.randint(20, 50)
                old_level = get_fishing_level_value(user_id)
                fishing_xp[user_id] = get_fishing_xp(user_id) + xp_gained
                new_level = fishing_xp[user_id] // 100
                fishing_level[user_id] = new_level
                leveled_up = new_level > old_level
            else:
                xp_gained = 0

            save_data()

            if legendary_key:
                # Legendary catch — special embed
                result_embed = discord.Embed(
                    title=f"🌟 LEGENDARY CATCH! {catch['emoji']} {catch['name']}!",
                    description=(
                        f"{grid}\n\n"
                        f"⚠️ You pulled up a **{catch['name']}** from the depths!\n\n"
                        f"**+{format_coins(reward)} coins**\n"
                        f"**+{xp_gained} XP**"
                    ),
                    color=discord.Color.gold()
                )
            else:
                result_embed = discord.Embed(
                    title=f"{catch['emoji']} You got a {catch['name']}!",
                    description=(
                        f"{grid}\n\n"
                        f"**+{format_coins(reward)} coins**\n"
                        f"**+{xp_gained} XP**"
                    ),
                    color=discord.Color.green() if catch_key != "boot" else discord.Color.orange()
                )
            result_embed.add_field(name="Fishing Level", value=str(new_level), inline=True)
            result_embed.add_field(name="Rod", value=equipped, inline=True)
            if leveled_up:
                result_embed.add_field(name="Level Up!", value=f"You reached **Level {new_level}**!", inline=False)
        else:
            boot = FISHING_CATCHES["boot"]
            reward = int(boot["reward"] * rod_data["reward_multiplier"])
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
            result_embed.add_field(name="Rod", value=equipped, inline=True)
            result_embed = discord.Embed(
                title=f"{boot['emoji']} You caught an {boot['name']}",
                description=(
                    f"{grid}\n\n"
                    "Wrong spot or too slow.\n"
                    "**+0 coins**"
                ),
                color=discord.Color.orange()
            )
            result_embed.add_field(name="Rod", value=equipped, inline=True)

        result_embed.set_footer(text=f"Wallet: {format_coins(get_wallet(user_id))} coins")
        await game_message.edit(embed=result_embed)

    finally:
        fishing_active.discard(user_id)


# ============== Owner Power =============

@bot.command()
async def wish(ctx, *args):
    if ctx.author.id != OWNER_ID:
        return

    if not args:
        await ctx.send(
            "Usage: `!wish @user <amount>` or `!wish <amount>` or "
            "`!wish @user reset` or `!wish @user remove <amount>`"
        )
        return

    target = ctx.author
    parts = list(args)
    converter = commands.MemberConverter()

    try:
        possible_target = await converter.convert(ctx, parts[0])
        target = possible_target
        parts = parts[1:]
    except commands.BadArgument:
        pass

    if not parts:
        await ctx.send("Give an amount, or use `reset`, or `remove <amount>`.")
        return

    action = str(parts[0]).strip().lower()

    if action == "reset":
        claims = get_claims(target.id)
        claims["daily"] = 0
        claims["weekly"] = 0
        claims["monthly"] = 0
        save_data()
        await ctx.send(f"Reset all claim timers for {target.mention}.")
        return

    if action in {"remove", "take", "delete", "del"}:
        if len(parts) < 2:
            await ctx.send("Usage: `!wish @user remove <amount>`")
            return

        wish_amount = parse_amount_input(parts[1], balance=get_wallet(target.id), allow_all=True)
        if wish_amount is None:
            await ctx.send("Invalid amount.")
            return

        wallet.setdefault(target.id, 0)
        wallet[target.id] = max(0, wallet[target.id] - wish_amount)
        save_data()
        await ctx.send(f"Removed **{wish_amount:,}** coins from {target.mention}.")
        return

    wish_amount = parse_amount_input(parts[0])
    if wish_amount is None:
        await ctx.send("Invalid amount.")
        return

    wallet.setdefault(target.id, 0)
    wallet[target.id] += wish_amount
    save_data()

    if target.id == ctx.author.id:
        await ctx.send(f"Granted yourself **{wish_amount:,}** coins.")
    else:
        await ctx.send(f"Granted **{wish_amount:,}** coins to {target.mention}.")


# ===== TRANSFER =====
@bot.command()
async def transfer(ctx, member: discord.Member, amount: str):
    sender = ctx.author.id
    target = member.id
    amount = parse_amount_input(amount, balance=get_wallet(sender), allow_all=True)

    if amount is None or amount <= 0:
        return await ctx.send("Invalid amount.")

    if get_wallet(sender) < amount:
        return await ctx.send("Not enough coins.")

    wallet.setdefault(sender, 0)
    wallet.setdefault(target, 0)

    wallet[sender] -= amount
    wallet[target] += amount
    save_data()

    await ctx.send(f"{ctx.author.mention} sent **{amount}** coins to {member.mention}.")


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
            price = DELIVERY_VEHICLES[vname]["price"]
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
        embed.add_field(
            name=f"{vdata['emoji']} {vname}",
            value=(
                f"{status}\n"
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
        final_reward = int(base_reward * vdata["reward_multiplier"] * speed_bonus)

        wallet.setdefault(user_id, 0)
        wallet[user_id] += final_reward
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
                f"💰 **+{format_coins(final_reward)} coins**"
            ),
            color=discord.Color.green(),
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


# ===== MUSIC COMMANDS =====

def ensure_music_state(guild_id):
    music_queue.setdefault(guild_id, [])
    music_now.setdefault(guild_id, None)
    music_locks.setdefault(guild_id, asyncio.Lock())
    recent_play_requests.setdefault(guild_id, {})


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
    music_queue[guild_id].clear()
    music_now[guild_id] = None
    music_starting.discard(guild_id)

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        ctx.voice_client.stop()

    await ctx.send("Stopped music and cleared the queue.")


async def play_next(ctx):
    guild_id = ctx.guild.id
    ensure_music_state(guild_id)

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
        return

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
        return

    music_now[guild_id] = player

    def after_play(error):
        if error:
            print(f"Player error: {error}")
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
        return

    music_starting.discard(guild_id)
    await ctx.send(f"Now playing: **{player.title}**")


@bot.command()
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

    await ctx.send(f"Now playing: **{current.title}**")


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

    embed.set_footer(text="Use !play with the song name or one of these SoundCloud links.")
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







