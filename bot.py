import discord
from discord.ext import commands
import time

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} is now online")
    print("-------------------------")

@client.event
async def on_member_join(member):
    channel = client.get_channel(1173380031230259200)
    await channel.send(f"Welcome to the Chilly Cave {member}! Greet them or face the consequences. Also, be sure to read the <#962796206721994792> and visit <#962844080340086834> for extra roles.")

@client.event
async def on_member_remove(member):
    channel = client.get_channel(1173384679471202375)
    await channel.send(f"{member} has left the cave. Press F to pay respects.")

with open("SlurList.txt") as file:
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

@client.event
async def on_message(message):
    if message.author.bot:
        return
    print(message.content)
    for bad_word in bad_words:
        if bad_word in message.content:
            await message.delete()
            await message.channel.send("Slurs are strictly against the server's rules. You will be banned.")
            time.sleep(1)
            await message.channel.send("3")
            time.sleep(1)
            await message.channel.send("2")
            time.sleep(1)
            await message.channel.send("1")
            await message.author.ban(reason="Inappropriate language")
            # Send a direct message to the user
            guild_name = message.guild.name if message.guild else "the server"
            await message.author.send(f"You have been banned from {guild_name} for the following reason: {reason}")
            return
            

    await client.process_commands(message)

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"User {member} has been kicked for {reason}")
    
    # Send a direct message to the user
    guild_name = ctx.guild.name if ctx.guild else "the server"
    await member.send(f"You have been {ctx.command.name}ed from {guild_name} for the following reason: {reason}")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"User {member} has been banned for {reason}")
    
    # Send a direct message to the user
    guild_name = ctx.guild.name if ctx.guild else "the server"
    await member.send(f"You have been {ctx.command.name}ed from {guild_name} for the following reason: {reason}")


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")
