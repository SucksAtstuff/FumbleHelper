#import required dependencies
import discord
from discord.ext import commands
import time
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} is now online")
    print("-------------------------")

@client.event
async def on_member_join(member):
    channel = client.get_channel(1173380031230259200)
    await channel.send(f"WeLCome To the Chilly CavE {member}greEt tHeM or DeTh also bE sUre to rEaD the <#962796206721994792> and ViSit <#962844080340086834> FoR extra RoLes")

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

    # Log the message in the console along with the channel
    print(f"{message.channel} - {message.author}: {message.content}")

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

            # Try to send a direct message to the user using create_dm
            try:
                dm_channel = await message.author.create_dm()
                await dm_channel.send(f"You have been banned from {message.guild.name if message.guild else 'the server'} for the following reason: {reason}")
            except discord.Forbidden:
                print(f"Failed to send a direct message to {message.author} (Forbidden)")

            return

    await client.process_commands(message)


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f"User {member} has been kicked for {reason}")
    
    # Try to send a direct message to the user using create_dm
    try:
        dm_channel = await member.create_dm()
        # change the link in the message to a google form link
        await dm_channel.send(f"You have been kicked from {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}: You can appeal the punishment here: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    except discord.Forbidden:
        print(f"Failed to send a direct message to {member} (Forbidden)")
    
    await member.kick(reason=reason)

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f"User {member} has been banned for {reason}")
    
    # Try to send a direct message to the user using create_dm
    try:
        dm_channel = await member.create_dm()
        # change the link in the message to a google form link
        await dm_channel.send(f"You have been banned from {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}: You can appeal the punishment here: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    except discord.Forbidden:
        print(f"Failed to send a direct message to {member} (Forbidden)")
    
    await member.ban(reason=reason)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")