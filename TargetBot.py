import discord
from discord.ext import commands
import random
import asyncio
import json
import os
import string

DATA_FILE = "data.json"

player_health = {}
player_lives = {}
player_points = {}
farm_xp = {}
farm_level = {}

def load_data():
    global farm_xp, farm_level, player_health, player_lives, player_points
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            farm_xp = {int(k): v for k, v in data.get("xp", {}).items()}
            farm_level = {int(k): v for k, v in data.get("level", {}).items()}
            player_health = {int(k): v for k, v in data.get("player_health", {}).items()}
            player_lives = {int(k): v for k, v in data.get("player_lives", {}).items()}
            player_points = {int(k): v for k, v in data.get("player_points", {}).items()}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "xp": {str(k): v for k, v in farm_xp.items()},
            "level": {str(k): v for k, v in farm_level.items()},
            "player_health": {str(k): v for k, v in player_health.items()},
            "player_lives": {str(k): v for k, v in player_lives.items()},
            "player_points": {str(k): v for k, v in player_points.items()}
        }, f, indent=4)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    load_data()
    print(f'Logged as {bot.user}')

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

# ============ AFK ============
afk_users = {}

@bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = {"reason": reason, "time": discord.utils.utcnow()}
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

    # remove afk when they send a message
    if message.author.id in afk_users:
        afk_data = afk_users.pop(message.author.id)
        time_away = discord.utils.utcnow() - afk_data["time"]
        minutes = int(time_away.total_seconds() // 60)
        embed = discord.Embed(
            description=f"Welcome back {message.author.mention}! You were AFK for **{minutes} min**",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)
        await bot.process_commands(message)
        return

    # notify if they mention an afk user
    notified = []
    for mentioned in message.mentions:
        if mentioned.id in afk_users and mentioned.id not in notified:
            notified.append(mentioned.id)
            afk_data = afk_users[mentioned.id]
            await message.channel.send(f"{message.author.mention}")
            embed = discord.Embed(
                description=f"Hey {message.author.mention}, {mentioned.mention} is currently AFK: **{afk_data['reason']}**",
                color=discord.Color.light_gray()
            )
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

# ============= Bazooka ==============

import random
import string

player_health = {}
player_lives = {}
player_points = {}

def generate_random_word(length=5):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

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
farm_xp = {}
farm_level = {}
jerk_cooldown = {}
jerk_active = set()

def get_level(xp):
    return xp // 100

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
        buttons = ["🍎", "🍊", "🍌"]
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
OWNER_ID = 756539405463978024
entity_cooldown = {}

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

    for _ in range(times):
        await ctx.send(member.mention)
        await asyncio.sleep(0)


# ================== LINK COMMAND ==================
@bot.command(name="link")
async def link(ctx):
    website_url = "https://iaidenz.pythonanywhere.com/track "   # Your site

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

    # Try sending in DM (only you see it)
    try:
        await ctx.author.send(embed=embed, view=view)
        await ctx.send("✅ Sent you the commands link in DM!", delete_after=8)
    except discord.Forbidden:
        # If DMs are closed, send in channel
        await ctx.send(embed=embed, view=view)


import os
bot.run(os.environ.get('TOKEN'))
