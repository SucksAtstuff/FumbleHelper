# Import necessary libraries
import discord
from discord.ext import commands
from discord import Member
from discord import Role
from discord.ext.commands import has_permissions, MissingPermissions

import time
import asyncio
import re
import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# FumbleHelperBot/bot.py
from FumbleHelperDashboard.app import app as web_app

appealLink = os.environ.get("appealLink")
welcomeChannel = os.environ.get("welcomeChannel")
farewellChannel = os.environ.get("farewellChannel")
logChannel = os.environ.get("logChannel")

# Ensure that you add the intents argument
intents = discord.Intents.default()
intents.members = True  # Enable member-related events

TOKEN = os.environ.get("DISCORD_TOKEN")
client = commands.Bot(command_prefix='!', intents=intents)

# ==============================================================================
# Event Handling:
# ==============================================================================

# Event Handling: Bot startup ================================================

# Event: When the bot is ready
@client.event
async def on_ready():
    print(f"{client.user} is now online")
    print("-------------------------")
    
    # Run the web application when the bot is ready
    web_app.run()
    
# Functions: Open slur list ====================================================
# Read the list of slurs from "SlurList.txt" and store in bad_words list

with open("FumbleHelperBot/SlurList.txt") as file:
    # Remove leading/trailing whitespaces and convert to lowercase for case-insensitive comparison
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]


# Event Handling: Member join ==================================================

# Event: When a new member joins the server
@client.event
async def on_member_join(member):
    # Log the member join event
    await log_member_change(member, "join", client)
    
    # Get the welcome channel by ID and send a welcome message with instructions
    channel = client.get_channel(welcomeChannel)

    await channel.send(f"WeLCome To the Chilly CavE {member.mention} greEt tHeM or DeTh also bE sUre to rEaD the <#962796206721994792> and ViSit <#962844080340086834> FoR extra RoLes")

# Event Handling: Member remove ================================================

# Event: When a member leaves the server
@client.event
async def on_member_remove(member):
    # Log the member leave event
    await log_member_change(member, "leave", client)
    
    # Get the farewell channel by ID and send a message when a member leaves
    channel = client.get_channel(farewellChannel)

    await channel.send(f"{member} HaS LeFt ThE CaVe :(. Press F to pay respects.")



# Event Handling: Member update ================================================

# Event: When a member updates
@client.event

async def on_member_update(before, after):
    # Check for role changes
    if before.roles != after.roles:
        # Determine added roles
        added_roles = [role for role in after.roles if role not in before.roles]
        
        # Call your log_role_change function
        await log_role_change(after, added_roles, client)

# Event Handling: Server boost =================================================

# Event: When a member boosts the server
@client.event
async def on_boost(ctx, boost):
    # Get the channel where you want to send a message about the boost
    boost_channel_id = welcomeChannel  # Replace with the actual channel ID

    boost_channel = client.get_channel(boost_channel_id)

    if boost_channel:
        # Send a message in the boost channel
        await boost_channel.send(f"Thank you, {boost.member.mention}, for boosting {boost.guild.name} :D")
    else:
        # Print a message or log an error if the boost channel is not found
        print("Boost channel not found.")

# Event Handling: Message sent =================================================

# Event: When a message is sent in a channel
@client.event

async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from other bots
    
    # Log the message in the console along with the channel
    print(f"{message.channel} - {message.author}: {message.content}")

    # Check if the message is from a DM (Direct Message)
    if isinstance(message.channel, discord.DMChannel):
        # Get the target channel by ID (replace CHANNEL_ID with your channel ID)
        target_channel = client.get_channel(logChannel)

        if target_channel:
            # Send the message to the specified channel
            await target_channel.send(f"DM from {message.author.mention}: {message.content}")
        else:
            # Print a message if the target channel is not found (replace with appropriate handling)
            print("Target channel not found.")

    

   # Check for slurs in the message content
    for bad_word in bad_words:
        if bad_word in message.content:
            # Delete the message
            await message.delete()

            # Check if the bot's role is lower or equal to the member's role
            if message.guild.me.top_role <= message.author.top_role:
                await message.channel.send("I cannot ban this member as they have a higher or equal role to me.")
                return
            # Inform the member about the server rules
            await message.channel.send("Slurs are strictly against this server's rules. You will be banned.")
            time.sleep(1)
            await message.channel.send("3")
            time.sleep(1)
            await message.channel.send("2")
            time.sleep(1)
            await message.channel.send("1")
            # Try to send a direct message to the member using create_dm
            try:
                dm_channel = await message.author.create_dm()
                await dm_channel.send(f"You have been banned from {message.guild.name if message.guild else 'the server'} for the following reason: Said a slur, you can appeal the ban here: {appealLink}")

                print(f"DM sent to {message.author} for slur ban confirmation.")
            except discord.Forbidden:
                print(f"Failed to send a direct message to {message.author} (Forbidden)")
            # Ban the member
            await message.author.ban(reason="Said a slur")
            return
    # Process other commands in the message
    await client.process_commands(message)

# ==============================================================================
# Mod Logs and File Handling
# ==============================================================================
async def log_member_change(member, event_type, client):
    # Get the current timestamp in the specified format
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Extract relevant information about the member
    username = member.name  # Username of the member
    member_id = member.id  # User ID of the member

    # Define the issuer, in this case, set to "member.mention"
    # You can customize this or get the actual invoker if available
    issuer = member.mention
    
    # Specify the folder path and file path for member change logs
    folder_path = os.path.join(MODLOGS_FOLDER, username)
    file_path = os.path.join(folder_path, f"{username}_member_changes.txt")

    # Ensure the folder exists, create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Log the member change details to the member's member change log file
    with open(file_path, "a") as file:
        file.write(f"{timestamp} - {event_type.capitalize()} by {issuer} - User ID: {member_id}\n")

    # Send an embed to the log channel
    log_channel_id = logChannel  # Replace with the actual log channel ID
    log_channel = client.get_channel(log_channel_id)

    # Check if the log channel exists
    if log_channel:
        # Get the server's current member count
        server = member.guild
        member_count = server.member_count

        # Customize the embed color based on the event type
        if event_type.lower() == 'join':
            embed_color = 0x2ecc71  # Green color for join
        elif event_type.lower() == 'leave':
            embed_color = 0xe74c3c  # Red color for leave
        else:
            embed_color = 0x3498db  # Default blue color

        # Create an embed with information about the member change
        embed = discord.Embed(
            title=f"Member {event_type.capitalize()}",
            color=embed_color
        )

        embed.add_field(name="User", value=f"{member.mention} ({member_id})", inline=False)
        embed.add_field(name="Event Type", value=event_type.capitalize(), inline=False)
        embed.add_field(name="Members", value=member_count, inline=False)

        # Add the timestamp as a small field in the bottom left corner
        embed.set_footer(text=timestamp, icon_url="")  # You can add an icon URL if needed

        # Send the embed to the log channel
        await log_channel.send(embed=embed)
    else:
        # Print an error message if the log channel is not found
        print(f"Log channel not found. Make sure the log_channel_id is set correctly.")



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
    member_id = member.id
    issuer = ctx.author.name

    # Specify the folder path and file path
    folder_path = os.path.join(MODLOGS_FOLDER, username)
    file_path = os.path.join(folder_path, f"{username}_punishments.txt")

    # Ensure the folder exists, create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Log the punishment details to the member's mod logs file
    with open(file_path, "a") as file:
        file.write(f"{timestamp} - {action} by {issuer} - Reason: {reason} - Duration: {duration}\n")

# Function: Retrieve mod logs for a user
def get_mod_logs(member):
    folder_path = os.path.join(MODLOGS_FOLDER, member.name)
    file_path = os.path.join(folder_path, f"{member.name}_punishments.txt")

    # Check if the log file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    else:
        return "No mod logs found for this member."

@client.event
async def on_message_delete(message):
    await log_message_deletion(message)

# Function: Log a message deletion event
async def log_message_deletion(message):
    # Get the current timestamp in UTC format
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Extract relevant information about the deleted message
    member = message.author
    username = member.name
    member_id = member.id
    content = message.content
    channel = message.channel

    # Specify the folder path and file path for message deletion logs
    folder_path = os.path.join(MODLOGS_FOLDER, username)
    file_path = os.path.join(folder_path, f"{username}_message_deletions.txt")

    # Ensure the folder exists, create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)



    # Log the message deletion details to the user's message deletion log file
    with open(file_path, "a") as file:
        # Write timestamp, issuer, and user information
        file.write(f"{timestamp} - Message by {member} - User ID: {member_id} - Channel: {channel.name}\n")
        
        # Write the content of the deleted message
        file.write(f"Content: {content}\n\n")

    # Send an embed to the log channel
    log_channel_id = logChannel  # Replace with the actual log channel ID
    log_channel = client.get_channel(log_channel_id)

    # Check if the log channel exists
    if log_channel:
        # Create an embed with information about the deleted message
        embed = discord.Embed(
            title="Message Deleted",
            color=0xe74c3c  # You can customize the colour
        )

        embed.add_field(name="Channel", value=f"{channel.mention} ({channel.name})", inline=False)
        embed.add_field(name="Message ID", value=f"[{message.id}](https://discordapp.com/channels/{message.guild.id}/{channel.id}/{message.id})", inline=False)
        embed.add_field(name="Message Author", value=f"{member.mention} ({member_id})", inline=False)
        embed.add_field(name="Message", value=content, inline=False)
        embed.set_footer(text=f"{timestamp}", icon_url="")  # Use the timestamp here

        # Send the embed to the log channel
        await log_channel.send(embed=embed)
    else:
        # Print an error message if the log channel is not found
        print(f"Log channel not found. Make sure the log_channel_id is set correctly.")





# Event: When a message is edited
@client.event
async def on_message_edit(before, after):
    # Check if the content of the message has changed
    if before.content != after.content:
        # Get the log channel by ID
        log_channel_id = logChannel  # Replace with the actual log channel ID
        log_channel = client.get_channel(log_channel_id)

        # Check if the log channel exists
        if log_channel:
            # Create an embed with information about the edited message
            embed = discord.Embed(
                title="Message Edited",
                color=0xf1c40f  # You can customize the color
            )

            embed.add_field(name="Channel", value=f"{after.channel.mention} ({after.channel.name})", inline=False)
            embed.add_field(name="Message ID", value=f"[{after.id}](https://discordapp.com/channels/{after.guild.id}/{after.channel.id}/{after.id})", inline=False)
            embed.add_field(name="Message author:", value=f"{before.author.mention} ({before.author.id})", inline=False)

            embed.add_field(name="Before", value=before.content, inline=True)
            embed.add_field(name="After", value=after.content, inline=True)

            # Add the timestamp as a small field in the bottom left corner
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Timestamp: {timestamp}", icon_url="")  # Use the desired timestamp format
            
            # Send the embed to the log channel
            await log_channel.send(embed=embed)

        else:
            # Print an error message if the log channel is not found
            print(f"Log channel not found. Make sure the log_channel_id is set correctly.")


# Function: Log a member role change event
async def log_role_change(member, added_roles, client):
    # Get the current timestamp in the specified format
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Extract relevant information about the member
    username = member.name  # Username of the member
    member_id = member.id  # User ID of the member

    # Specify the folder path and file path for role change logs
    folder_path = os.path.join(MODLOGS_FOLDER, username)
    file_path = os.path.join(folder_path, f"{username}_role_changes.txt")
    
    # Ensure the folder exists, create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Convert Role objects to strings
    added_roles_str = [role.name for role in added_roles]

    # Join the role names in the log message
    roles_added_str = ', '.join(added_roles_str)

    # Log the role change details to the user's role change log file
    with open(file_path, "a") as file:
        file.write(f"{timestamp} - User ID: {member_id}, Roles Added: {roles_added_str}\n")

    # Send an embed to the log channel
    log_channel_id = logChannel  # Replace with the actual log channel ID
    log_channel = client.get_channel(log_channel_id)

    # Check if the log channel exists
    if log_channel:
        # Create an embed with information about the role change
        embed = discord.Embed(
            title=f"Role Change - {member.mention}",
            color=0xffcc00  # Yellow color
        )

        embed.add_field(name="User", value=f"{member.mention} ({member_id})", inline=False)
        embed.add_field(name="Roles Added", value=", ".join([f"<@&{role.id}>" for role in added_roles]), inline=False)
        embed.add_field(name="Timestamp", value=timestamp, inline=False)

        # Send the embed to the log channel
        await log_channel.send(embed=embed)
    else:
        # Print an error message if the log channel is not found
        print(f"Log channel not found. Make sure the log_channel_id is set correctly.")

# ==============================================================================
# Other Functions
# ==============================================================================

# Define a dictionary to store muted users and their unmute tasks
muted_members = {}

# Functions: Parse duration ====================================================

# Function: Parse duration string into numeric value and unit
def parse_duration(duration_str):
    match = re.match(r"(\d+)\s*([smhdw]?)", duration_str)
    if match:
        value, unit = int(match.group(1)), match.group(2).lower()
        return value, unit
    return None, None

# Functions: Parse duration and reason =========================================

# Function: Parse duration and reason from the input string
def parse_duration_and_reason(input_str):
    parts = input_str.split(maxsplit=1)
    
    if len(parts) == 1:
        return parts[0], None
    elif len(parts) == 2:
        return parts
    else:
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

# Functions: Automatically unmute ==============================================

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
        if member.id in muted_members:
            del muted_members[member.id]



        # Send a DM to the unmuted member
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(f"You have been automatically unmuted in {ctx.guild.name if ctx.guild else 'the server'} after {seconds} seconds.")
        except discord.Forbidden:
            print(f"Failed to send a direct message to {member} (Forbidden).")

# Functions: Add note ==========================================================
def add_note(ctx, member, note):
    # Convert mention to member object
    if isinstance(member, str):
        member_id = int(member.replace('<@', '').replace('>', ''))
        member = ctx.guild.get_member(member_id)

    # Log the note
    log_punishment(ctx, member, "Note", note)

    # Add the note to the user's mod logs file
    with open(f"{MODLOGS_FOLDER}/{member.name}/{member.name}_punishments.txt", "a") as file:
        file.write(f"Note: {note}\n")

        

# Functions: Add warning =======================================================
def add_warning(ctx, member, reason):
    # Convert mention to member object
    if isinstance(member, str):
        member_id = int(member.replace('<@', '').replace('>', ''))
        member = ctx.guild.get_member(member_id)

    # Log the warning
    log_punishment(ctx, member, "Warning", reason)

    # Add the warning to the user's mod logs file
    with open(f"{MODLOGS_FOLDER}/{member.name}/{member.name}_punishments.txt", "a") as file:
        file.write(f"Warning: {reason}\n")


# ==============================================================================
# Commands
# ==============================================================================

# Commands: Kick ===============================================================

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
        await dm_channel.send(f"You have been kicked from {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}: You can appeal the punishment here: {appealLink}")
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



# Commands: Ban ================================================================

# Command: Ban a member from the server
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Broke the rules"):
    # Check if the bot's role is lower or equal to the member's role
    if ctx.guild.me.top_role <= member.top_role:
        await ctx.send("I cannot ban this user because they have a higher or equal role.")
        return

    # Check if the command issuer's role is lower or equal to the member's role
    if ctx.author.top_role <= member.top_role:
        await ctx.send("You do not have the authority to ban this user.")
        return

    # Inform about the ban
    await ctx.send(f"User {member} has been banned for {reason}")

    # Try to send a direct message to the user using create_dm
    try:
        dm_channel = await member.create_dm()
        # change the link in the message to a google form link
        await dm_channel.send(f"You have been banned from {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}: You can appeal the punishment here: {appealLink}")
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

# Commands: Unban ==============================================================

# Command: Unban a member from the server
@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member, *, reason="Appeal Approved"):
    banned_users = await ctx.guild.bans()

    # Check if the provided member is an ID
    try:
        member_id = int(member)
        member = await client.fetch_user(member_id)
    except ValueError:
        # If not an ID, try to find the user by username and discriminator
        member_name, member_discriminator = member.split('#')
        member = discord.utils.get(banned_users, user__name=member_name, user__discriminator=member_discriminator)

    if member:
        # Unban the user
        await ctx.guild.unban(member, reason=reason)
        await ctx.send(f"User {member} has been unbanned.")

        # Log the unban in mod logs
        log_punishment(ctx, member, "Unban", reason)

        # Send DM to the unbanned user
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(f"You have been unbanned from {ctx.guild.name if ctx.guild else 'the server'}.")
        except discord.Forbidden:
            print(f"Failed to send a direct message to {member} (Forbidden)")
    else:
        await ctx.send(f"User {member} was not found in the ban list.")

# Error handler for unban command
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide the full username (including discriminator) or user ID of the user you want to unban.")

# Commands: note ===============================================================
@client.command()
@commands.has_permissions(manage_messages=True)
async def note(ctx, member: discord.Member, *, note):
    # Send a confirmation message
    await ctx.send(f"Note added for {member.mention}: {note}")

# Commands: Modlogs ============================================================

# Command: Display mod logs for a user in an embed
@client.command()
@commands.has_permissions(manage_messages=True)
async def modlogs(ctx, member: discord.Member):
    # Create an embed object with a red color
    embed = discord.Embed(
        title=f"Mod Logs for {member.mention}",
        color=0xe74c3c  # Red color
    )

    # Retrieve mod logs for the member
    logs = get_mod_logs(member)
    
    # Add mod logs to the embed
    embed.add_field(name="Mod Logs", value=logs)

    # Send the embed to the same channel
    await ctx.send(embed=embed)

# Commands: Mute ===============================================================

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
                await dm_channel.send(f"You have been muted in {ctx.guild.name if ctx.guild else 'the server'} for {duration}.{' Reason: ' + reason if reason else ''} you can appeal the mute here: {appealLink}")
                
                print(f"DM sent to {member} for mute confirmation.")
            except discord.Forbidden:
                print(f"Failed to send a direct message to {member} (Forbidden).")

            # Schedule an automatic unmute after the specified duration
            value, unit = parse_duration(duration)
            
            if value is not None and unit is not None:
                seconds = convert_to_seconds(value, unit)
                if seconds is not None:
                    muted_members[member.id] = asyncio.create_task(auto_unmute(ctx, member, seconds))
                else:
                    await ctx.send("Invalid time unit. Please use 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days, or 'w' for weeks.")
            else:
                await ctx.send("Invalid duration format. Please provide a valid duration, e.g., '5m' for 5 minutes.")
        else:
            await ctx.send("Invalid duration format. Please provide a valid duration, e.g., '5m' for 5 minutes.")
    else:
        await ctx.send("Please provide a duration for the mute.")

# Commands: Unmute =============================================================

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
        if member.id in muted_members:
            muted_members[member.id].cancel()
            del muted_members[member.id]

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

# Commands: Warn ===============================================================

@client.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason):
    # Send a DM to the warned user
    try:
        dm_channel = await member.create_dm()
        await dm_channel.send(f"You have been warned in {ctx.guild.name if ctx.guild else 'the server'} for the following reason: {reason}")
    except discord.Forbidden:
        print(f"Failed to send a direct message to {member} (Forbidden).")

    # Send a confirmation message
    await ctx.send(f"User {member.mention} has been warned for: {reason}")

# Commands: Send message =======================================================

# Command: Send a message to a specific channel
@client.command()
@commands.has_permissions(administrator=True)
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

# Commands: Send direct message ================================================
# Command: Send a direct message to a member
@client.command()
@commands.has_permissions(administrator=True)
async def send_dm(ctx, member_id: int, *, message: str):
    # Get the member using the provided ID
    member = ctx.guild.get_member(member_id)
    
    if member:
        # Send a direct message to the member
        await member.send(message)
        
        # Send a confirmation message to the command invoker
        await ctx.send(f"Direct message sent to {member.mention}: {message}")
    else:
        # If the member is not found, inform the user
        await ctx.send("Member not found.")

# This block ensures that the bot only runs when this script is executed directly
if __name__ == "__main__":
    print("This script should not be run directly. Run 'run.py' instead.")