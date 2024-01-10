import bot
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

TOKEN = os.environ.get("DISCORD_TOKEN")

if __name__ == "__main__":
    bot.client.run(TOKEN)