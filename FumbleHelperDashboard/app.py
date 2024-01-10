# FumbleHelperDashboard/app.py
from flask import Flask, redirect, request, url_for, session, render_template
from discord.ext import commands
import os
import requests
import logging

from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'

# Discord OAuth configuration
client_id = os.environ.get("clientID")  # Replace with your actual client ID
client_secret = os.environ.get("clientSecret")  # Replace with your actual client secret
redirect_uri = os.environ.get("redirectUri")
discord_bot_token = 'your_discord_bot_token'  # Not used in this part of the code
discord_guild_id = 'your_discord_guild_id'  # Replace with your actual guild ID


def get_user_guilds(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
    
    guilds_data = response.json()
    user_guilds = []

    for guild in guilds_data:
        guild_permissions = guild.get('permissions', 0)

        guild_info = {
            'id': guild['id'],
            'name': guild['name'],
            'icon': guild['icon'],
            'icon_url': f'https://cdn.discordapp.com/icons/{guild["id"]}/{guild["icon"]}.png' if guild.get('icon') else None,
            'permissions': guild_permissions
        }
        user_guilds.append(guild_info)

    return user_guilds



def can_manage_guild(guild_permissions):
    print(f"Guild Permissions (Before Check): {guild_permissions}")
    is_manager = (guild_permissions & 0x00000020) == 0x00000020
    print(f"Can Manage Guild: {is_manager}")
    return is_manager

@app.route('/')
def home():
    logging.debug('Home route called...')
    user_id = session.get('user_id')
    if user_id:
        access_token = session.get('access_token')
        if access_token:
            guilds_data = get_user_guilds(access_token)
            user_guilds = [guild for guild in guilds_data if can_manage_guild(guild['permissions'])]

            return render_template('index.html', user_id=user_id, user_guilds=user_guilds)

    return render_template('index.html', user_id=None)

@app.route('/configure/<guild_name>', methods=['GET', 'POST'])
def configure(guild_name):
    # Add logic to handle both GET and POST requests
    if request.method == 'POST':
        # Handle POST request logic
        pass
    else:
        # Handle GET request logic
        pass

    # Render a template with the configuration options, passing guild_name
    return render_template('configure.html', guild_name=guild_name)



@app.route('/login')
def login():
    logging.debug('Login route called...')
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify guilds')

@app.route('/callback')
def callback():
    logging.debug('Callback route called...')
    code = request.args.get('code')
    if code:
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'scope': 'identify guilds'
        }
        response = requests.post('https://discord.com/api/oauth2/token', data=data)
        token_data = response.json()

        if 'error' in token_data:
            return f"OAuth error: {token_data['error']} - {token_data.get('error_description', '')}"

        headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
        user_response = requests.get('https://discord.com/api/users/@me', headers=headers)

        if user_response.status_code == 200:
            user_data = user_response.json()
            session['user_id'] = user_data['id']
            session['access_token'] = token_data['access_token']
            return redirect(url_for('home'))

    return 'Login failed'