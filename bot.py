#import required dependencies
import discord
from discord.ext import commands
import time
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@client.event
async def on_Ready():
    print(f"{client} is now online")
    print("-------------------------")

@client.command()
async def hello(ctx):
    await ctx.send("Hey there :)")
    
@client.event
async def on_member_join(member):
    channel = client.get_channel(1173380031230259200)
    await channel.send(f"WeLCome To the Chilly CavE {member} greEt tHeM or DeTh also bE sUre to rEaD the <#962796206721994792> and ViSit <#962844080340086834> FoR extra RoLes")

@client.event
async def on_member_join(member):
    channel = client.get_channel(1173384679471202375)
    await channel.send(f"{member} HaS LeFt ThE CaVe :(, Press F to pay respects")


with open("SlurList.txt") as file: # bad-words.txt contains one blacklisted phrase per line
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

@client.event    
async def on_message(message, member, reason=None):
    if message.author.bot:
        return
    print(message.content) #prints messages in console
    for bad_word in bad_words:
        if bad_word in message.content:
            await message.delete() #delete said message
            await message.channel.send("Slurs are strictly against the servers rules therefore you will be banned in")
            time.sleep(1)
            await message.channel.send("3")
            time.sleep(1)
            await message.channel.send("2")
            time.sleep(1)
            await message.channel.send("1")
            
            await member.ban(reason=reason)
            
@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"User {member} has been kicked for {reason}")
    
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permmisions to use this command")
        
@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"User {member} has been banned for {reason}")
    
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permmisions to use this command")