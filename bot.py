# Import necessary libraries
import discord
from discord.ext import commands
import time
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
import asyncio
import re
import datetime
import os

# Set up Discord bot with command prefix "!" and enable member intents
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

# Event: When the bot is ready
@client.event
async def on_ready():
    print(f"{client.user} is now online")
    print("-------------------------")

# Event: When a new member joins the server
@client.event
async def on_member_join(member):
    # Get the welcome channel by ID and send a welcome message with instructions
    channel = client.get_channel(1173380031230259200)
    await channel.send(f"WeLCome To the Chilly CavE {member} greEt tHeM or DeTh also bE sUre to rEaD the <#962796206721994792> and ViSit <#962844080340086834> FoR extra RoLes")

# Event: When a member leaves the server
@client.event
async def on_member_remove(member):
    # Get the farewell channel by ID and send a message when a member leaves
    channel = client.get_channel(1173384679471202375)
    await channel.send(f"{member} HaS LeFt ThE CaVe :(. Press F to pay respects.")

# Read the list of slurs from "SlurList.txt" and store in bad_words list
with open("SlurList.txt") as file:
    # Remove leading/trailing whitespaces and convert to lowercase for case-insensitive comparison
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

# Define the folder name for mod logs
MODLOGS_FOLDER = "Modlogs"

# Ensure the folder exists, create it if not
if not os.path.exists(MODLOGS_FOLDER):
    os.makedirs(MODLOGS_FOLDER)

# Function: Log a punishment to a user's mod logs
def log_punishment(ctx, member, action, reason=None, duration=None):
    # Get the current timestamp in the specified format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = member.name
    user_id = member.id
    issuer = ctx.author.name

    # Specify the folder path and file path
    folder_path = os.path.join(MODLOGS_FOLDER, username)
    file_path = os.path.join(folder_path, f"{username}_punishments.txt")

    # Ensure the folder exists, create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Log the punishment details to the user's mod logs file
    with open(file_path, "a") as file:
        file.write(f"{timestamp} - {action} by {issuer} - Reason: {reason} - Duration: {duration}\n")

# Function: Retrieve mod logs for a user
def get_mod_logs(user):
    folder_path = os.path.join(MODLOGS_FOLDER, user.name)
    file_path = os.path.join(folder_path, f"{user.name}_punishments.txt")

    # Check if the log file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    else:
        return "No mod logs found for this user."

# Command: Display mod logs for a user in an embed
@client.command()
async def modlogs(ctx, user: discord.User):
    # Create an embed object with a red color
    embed = discord.Embed(
        title=f"Mod Logs for {user.name}",
        color=0xe74c3c  # Red color
    )

    # Retrieve mod logs for the user
    logs = get_mod_logs(user)

    # Add mod logs to the embed
    embed.add_field(name="Mod Logs", value=logs)

    # Send the embed to the same channel
    await ctx.send(embed=embed)

# Event: When a message is sent in a channel
@client.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from other bots

    # Log the message in the console along with the channel
    print(f"{message.channel} - {message.author}: {message.content}")

    # Check for slurs in the message content
    for bad_word in bad_words:
        if bad_word in message.content:
            # Delete the message
            await message.delete()

            # Inform the user about the server rules
            await message.channel.send("Slurs are strictly against this server's rules. You will be banned.")
            time.sleep(1)
            await message.channel.send("3")
            time.sleep(1)
            await message.channel.send("2")
            time.sleep(1)
            await message.channel.send("1")

            # Try to send a direct message to the user using create_dm
            try:
                dm_channel = await message.author.create_dm()
                await dm_channel.send(f"You have been banned from {message.guild.name if message.guild else 'the server'} for the following reason: Said a slur")
            except discord.Forbidden:
                print(f"Failed to send a direct message to {message.author} (Forbidden)")

            # Ban the user
            await message.author.ban(reason="Said a slur")

            return

    # Process other commands in the message
    await client.process_commands(message)

# Command: Kick a member from the server
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Broke the rules"):
    # Inform about the kick
    await ctx.send(f"User {member} has been kicked for {reason}")

    # Try to send a direct message to the user using create_dm
    try:
        dm_channel = await member.create_dm()
        # change the link in the message to a google form link
        await dm_channel.send(f"You have been kicked from {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}: You can appeal the punishment here: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print(f"DM sent to {member} for kick confirmation.")
    except discord.Forbidden:
        print(f"Failed to send a direct message to {member}")

    # Log the kick in mod logs
    log_punishment(ctx, member, "Kick", reason)

    # Kick the user
    await member.kick(reason=reason)

# Error handler for kick command
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")

# Command: Ban a member from the server
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Broke the rules"):
    # Inform about the ban
    await ctx.send(f"User {member} has been banned for {reason}")

    # Try to send a direct message to the user using create_dm
    try:
        dm_channel = await member.create_dm()
        # change the link in the message to a google form link
        await dm_channel.send(f"You have been banned from {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}: You can appeal the punishment here: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print(f"DM sent to {member} for ban confirmation.")
    except discord.Forbidden:
        print(f"Failed to send a direct message to {member} (Forbidden)")

    # Log the ban in mod logs
    log_punishment(ctx, member, "Ban", reason)

    # Ban the user
    await member.ban(reason=reason)

# Error handler for ban command
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")

# Command: Unban a member from the server
@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member, *, reason="Appeal Approved"):
    banned_users = await ctx.guild.bans()

    # Check if the provided member is an ID
    try:
        user_id = int(member)
        user = await client.fetch_user(user_id)
    except ValueError:
        # If not an ID, try to find the user by username and discriminator
        member_name, member_discriminator = member.split('#')
        user = discord.utils.get(banned_users, user__name=member_name, user__discriminator=member_discriminator)

    if user:
        # Unban the user
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"User {user} has been unbanned.")

        # Log the unban in mod logs
        log_punishment(ctx, user, "Unban", reason)

        # Send DM to the unbanned user
        try:
            dm_channel = await user.create_dm()
            await dm_channel.send(f"You have been unbanned from {ctx.guild.name if ctx.guild else 'the server'}.")
        except discord.Forbidden:
            print(f"Failed to send a direct message to {user} (Forbidden)")
    else:
        await ctx.send(f"User {member} was not found in the ban list.")

# Error handler for unban command
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide the full username (including discriminator) or user ID of the user you want to unban.")

# Define a dictionary to store muted users and their unmute tasks
muted_users = {}

# Function: Parse duration string into numeric value and unit
def parse_duration(duration_str):
    match = re.match(r"(\d+)\s*([smhdw]?)", duration_str)
    if match:
        value, unit = int(match.group(1)), match.group(2).lower()
        return value, unit
    return None, None

# Function: Convert duration to seconds based on specified unit
def convert_to_seconds(value, unit):
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 60 * 60
    elif unit == 'd':
        return value * 24 * 60 * 60
    elif unit == 'w':
        return value * 7 * 24 * 60 * 60
    else:
        return None

# Command: Mute a member for a specified duration with an optional reason
@client.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, duration_and_reason: str = None):
    # Check if a mute role exists, or create one
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        # Create a Muted role if it doesn't exist and set permissions in all channels
        mute_role = await ctx.guild.create_role(name="Muted", reason="To mute members")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)

    if duration_and_reason:
        # Parse duration and reason from the input
        duration, reason = parse_duration_and_reason(duration_and_reason)

        if duration is not None:
            # Add the mute role to the member
            await member.add_roles(mute_role)
            await ctx.send(f"{member.mention} has been muted for {duration}{' for the reason: ' + reason if reason else ''}.")

            # Log the mute in mod logs with reason and duration
            log_punishment(ctx, member, "Mute", reason, duration)

            # Send a DM to the muted member
            try:
                dm_channel = await member.create_dm()
                await dm_channel.send(f"You have been muted in {ctx.guild.name if ctx.guild else 'the server'} for {duration}.{' Reason: ' + reason if reason else ''}")
                print(f"DM sent to {member} for mute confirmation.")
            except discord.Forbidden:
                print(f"Failed to send a direct message to {member} (Forbidden).")

            # Schedule an automatic unmute after the specified duration
            value, unit = parse_duration(duration)
            if value is not None and unit is not None:
                seconds = convert_to_seconds(value, unit)
                if seconds is not None:
                    muted_users[member.id] = asyncio.create_task(auto_unmute(ctx, member, seconds))
                else:
                    await ctx.send("Invalid time unit. Please use 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days, or 'w' for weeks.")
            else:
                await ctx.send("Invalid duration format. Please provide a valid duration, e.g., '5m' for 5 minutes.")
        else:
            await ctx.send("Invalid duration format. Please provide a valid duration, e.g., '5m' for 5 minutes.")
    else:
        await ctx.send("Please provide a duration for the mute.")

# Function: Parse duration and reason from the input string
def parse_duration_and_reason(input_str):
    parts = input_str.split(maxsplit=1)

    if len(parts) == 1:
        return parts[0], None
    elif len(parts) == 2:
        return parts
    else:
        return None, None

# Function: Automatically unmute a member after the specified duration
async def auto_unmute(ctx, member, seconds):
    await asyncio.sleep(seconds)
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.send(f"{member.mention} has been automatically unmuted after {seconds} seconds.")

        # Log the automatic unmute in mod logs
        log_punishment(ctx, member, "Unmute")

        # Remove the user from the dictionary to avoid errors during manual unmute
        if member.id in muted_users:
            del muted_users[member.id]

        # Send a DM to the unmuted member
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(f"You have been automatically unmuted in {ctx.guild.name if ctx.guild else 'the server'} after {seconds} seconds.")
        except discord.Forbidden:
            print(f"Failed to send a direct message to {member} (Forbidden).")


# Command: Unmute a member
@client.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    # Check if the member has the Muted role
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role in member.roles:
        # Remove the mute role from the member
        await member.remove_roles(mute_role)
        await ctx.send(f"{member.mention} has been unmuted.")
        
        # Log the unmute in mod logs
        log_punishment(ctx, member, "Unmute")
        
        # Cancel the automatic unmute if it's still scheduled
        if member.id in muted_users:
            muted_users[member.id].cancel()
            del muted_users[member.id]
        
        # Send a DM to the unmuted member
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(f"You have been unmuted in {ctx.guild.name if ctx.guild else 'the server'}.")
            print(f"DM sent to {member} for unmute confirmation.")
        except discord.Forbidden:
            print(f"Failed to send a direct message to {member} (Forbidden).")
    else:
        await ctx.send(f"{member.mention} is not muted.")

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please provide a valid member for the unmute.")

        

# Define a function to add a note to a user's mod logs
def add_note(member, note):
    # Log the note
    log_punishment(member, "Note", note)

    # Add the note to the user's mod logs file
    with open(f"{MODLOGS_FOLDER}/{member.name}/{member.name}_punishments.txt", "a") as file:
        file.write(f"Note: {note}\n")

@client.command()
async def note(ctx, member: discord.Member, *, note):
    # Add the note to the user's mod logs
    add_note(member, f"{ctx.author.name} added a note: {note}")

    # Send a DM to the user
    try:
        dm_channel = await member.create_dm()
        await dm_channel.send(f"A note has been added to your mod logs in {ctx.guild.name if ctx.guild else 'the server'}: {note}")
    except discord.Forbidden:
        print(f"Failed to send a direct message to {member} (Forbidden).")

    # Send a confirmation message
    await ctx.send(f"Note added for {member.name}: {note}")
    

# Define a function to add a warning to a user's mod logs
def add_warning(member, reason):
    # Log the warning
    log_punishment(member, "Warning", reason)

    # Add the warning to the user's mod logs file
    with open(f"{MODLOGS_FOLDER}/{member.name}/{member.name}_punishments.txt", "a") as file:
        file.write(f"Warning: {reason}\n")
        
@client.command()
async def warn(ctx, member: discord.Member, *, reason):
    # Add the warning to the user's mod logs
    add_warning(member, reason)

    # Send a DM to the warned user
    try:
        dm_channel = await member.create_dm()
        await dm_channel.send(f"You have been warned in {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}")
    except discord.Forbidden:
        print(f"Failed to send a direct message to {member} (Forbidden).")

    # Send a confirmation message
    await ctx.send(f"User {member.name} has been warned for: {reason}")

# Command: Send a message to a specific channel
@client.command()
async def send_message(ctx, channel_id: int, *, message: str):
    # Get the channel using the provided ID
    channel = client.get_channel(channel_id)

    if channel:
        # Send the message to the specified channel
        await channel.send(message)
        # Send a confirmation message to the command invoker
        await ctx.send(f"Message sent to <#{channel_id}>: {message}")
    else:
        # If the channel is not found, inform the user
        await ctx.send("Channel not found.")

# Command: Send a direct message to a member
@client.command()
async def send_dm(ctx, member_id: int, *, message: str):
    # Get the member using the provided ID
    member = client.get_user(member_id)

    if member:
        # Send a direct message to the member
        await member.send(message)
        # Send a confirmation message to the command invoker
        await ctx.send(f"Direct message sent to {member.name}: {message}")
    else:
        # If the member is not found, inform the user
        await ctx.send("Member not found.")
