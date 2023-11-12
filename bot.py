#import required dependencies
import discord
import responses
from discord.ext import commands

#import Bot Token
from apikeys import TOKEN

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
   
client.run(TOKEN)
    