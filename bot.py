import discord
import responses
from discord.ext import commands, ipc

class MyBot(commands.Bot):

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

		self.ipc = ipc.Server(self,secret_key = "Swas")

	async def on_ready(self):
		"""Called upon the READY event"""
		print("Bot is ready.")

	async def on_ipc_ready(self):
		"""Called upon the IPC Server being ready"""
		print("Ipc server is ready.")

	async def on_ipc_error(self, endpoint, error):
		"""Called upon an error being raised within an IPC route"""
		print(endpoint, "raised", error)

async def send_message(message, user_message, is_private):
    try:
        response = responses.get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
        
    except Exception as e:
        print(e)

def run_discord_bot(): 
    TOKEN = "MTE3MzA1MzM2MDIwMzYzNjg0Nw.GDjiG2.Bb94mDFCj-3_fPvzPx1kbLP_RPqfIfFuY6ViNs"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
      
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        print(f"{username} said {user_message} ({channel})")
        
        if user_message[0] =="?":
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
            
        else:
            await send_message(message, user_message, is_private=False)
            
    client.run(TOKEN)
    