import discordi
from discord.ext import commands
import asyncio
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents)
bot.remove_command("help")  # disable default help


# -------------------------
# BASIC COMMANDS
# -------------------------

@bot.command()
async def help(ctx):
    text = (
        "**Available Commands:**\n"
        "?help — Show this help menu\n"
        "?ban @user — Ban a user\n"
        "?kick @user — Kick a user\n"
        "?giveaway <reward> <hours> — Start a timed giveaway\n"
        "?userinfo @user — Show info about a user\n"
        "?serverinfo — Show server statistics\n"
        "?clear <amount> — Delete messages\n"
        "?coinflip — Heads or tails\n"
        "?roll — Roll a number between 1 and 100"
    )
    await ctx.send(text)

@bot.command()
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked.")

@bot.command()
async def giveaway(ctx, reward: str, hours: float):
    await ctx.send(f"🎉 **GIVEAWAY STARTED!** 🎉\nPrize: **{reward}**\nEnds in **{hours} hours**.\nReact with 🎉 to enter!")
    msg = await ctx.channel.history(limit=1).flatten()
    msg = msg[0]
    await msg.add_reaction("🎉")

    await asyncio.sleep(hours * 3600)

    msg = await ctx.channel.fetch_message(msg.id)
    users = await msg.reactions[0].users().flatten()
    users = [u for u in users if not u.bot]

    if len(users) == 0:
        await ctx.send("No valid entries.")
        return

    winner = random.choice(users)
    await ctx.send(f"🎉 **WINNER:** {winner.mention} — You won **{reward}**!")

    @bot.event
    async def on_member_join(member):
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"👋 Welcome {member.mention}! Type **?help** to see my commands.")

    @bot.event
    async def on_member_remove(member):
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"👋 {member.name} has left the server.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if "what is" in content or "when is" in content:
        channel = bot.get_channel(1467093141340553237)

        if channel:
            await channel.send(
                f"{message.author.mention}.",
                delete_after=1
            )
            await message.reply(f"<#{1467093141340553237}>")
        return

    await bot.process_commands(message)






# -------------------------
# EXTRA USEFUL COMMANDS
# -------------------------

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info: {member}", color=0x3498db)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined Server", value=member.joined_at)
    embed.add_field(name="Account Created", value=member.created_at)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="Server Info", color=0x2ecc71)
    embed.add_field(name="Name", value=guild.name)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Owner", value=guild.owner)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Deleted {amount} messages.", delete_after=3)

@bot.command()
async def coinflip(ctx):
    await ctx.send(f"The coin landed on **{random.choice(['Heads', 'Tails'])}**.")

@bot.command()
async def roll(ctx):
    await ctx.send(f"You rolled **{random.randint(1, 100)}**!")

# -------------------------
@bot.event
async def on_ready():
    activity = discord.Streaming(
        name="?help for help",
        url="https://twitch.tv/discord"  # any valid URL required by Discord
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Logged in as {bot.user}")


bot.run(os.getenv("TOKEN"))

