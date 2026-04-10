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

@bot.command()
async def jerk(ctx):
    user = ctx.author

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


import os
bot.run(os.environ.get('TOKEN'))