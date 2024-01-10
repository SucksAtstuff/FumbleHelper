# run.py
from FumbleHelperDashboard.app import app as flask_app
from FumbleHelperBot.bot import client  # Import the bot instance
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

TOKEN = os.environ.get("DISCORD_TOKEN")

if __name__ == '__main__':
    # Start the Flask app
    flask_app.run(debug=True, host='0.0.0.0', port=8034)

    # Start the Discord bot
    client.run(TOKEN)
