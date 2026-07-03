import os
import discord
from discord.ext import commands
import random
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.dm_messages = True      

bot = commands.Bot(command_prefix="!", intents=intents)

# 💾 CONFIGURATION 
LOG_CHANNEL_ID = 1522588698091458571   # Your private log channel ID
SERVER_ID = 1516866920668729557       # Your main Server/Guild ID
VERIFIED_ROLE_ID = 1516895163635601539 # The ID of your 'Verified' role
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# 📧 EMAIL CONFIGURATION (Gmail Example)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # Your personal Gmail
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") # Your 16-character Google App Password

# This dictionary keeps track of users who are in the middle of verifying
# Format: { user_id: { "student_id": "123456", "code": "987654" } }
pending_verifications = {}

async def send_verification_email(recipient_email, code):
    """Asynchronously sends the verification code via email."""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = "TCG Server Verification Code"
    
    body = f"Hello!\n\nYour 6-digit verification code for the Discord server is: {code}\n\nPlease reply directly to the bot with this code."
    msg.attach(MIMEText(body, "plain"))
    
    # Connects to Gmail's secure SMTP server without blocking the bot
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        username=SENDER_EMAIL,
        password=SENDER_PASSWORD,
        start_tls=True
    )

@bot.event
async def on_ready():
    print(f'Verification bot is online as {bot.user.name}')

@bot.event
async def on_member_join(member):
    try:
        await member.send(
            f"Welcome to the server, {member.name}! 👋\n"
            "To unlock the server channels, please reply directly to this message with your **Student ID Number** (just the numbers)."
        )
    except discord.Forbidden:
        print(f"Could not send DM to {member.name}.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        user_input = message.content.strip()
        user_id = message.author.id

        # PHASE 2: User is replying with the 6-digit code we emailed them
        if user_id in pending_verifications:
            saved_data = pending_verifications[user_id]
            
            if user_input == saved_data["code"]:
                guild = bot.get_guild(SERVER_ID)
                member = guild.get_member(user_id) if guild else None
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                verified_role = guild.get_role(VERIFIED_ROLE_ID) if guild else None
                
                if member and log_channel and verified_role:
                    # 1. Log the verified student details for mods
                    await log_channel.send(
                        f"✅ **User Verified Successfully**\n"
                        f"👤 **User:** {message.author.mention} ({message.author.name})\n"
                        f"🆔 **Student ID:** `up{saved_data['student_id']}`\n"
                    )
                    
                    try:
                        # 2. Give them access to the server
                        await member.add_roles(verified_role)
                        await message.channel.send("🎉 **Success!** Code accepted. Your channels are now unlocked. Welcome!")
                        # Remove them from the waiting list
                        del pending_verifications[user_id]
                    except discord.Forbidden:
                        await message.channel.send("An error occurred adding your role. Please contact a committee member.")
                return
            else:
                await message.channel.send("❌ Incorrect code. Please check your student email and try again, or re-type your Student ID to send a new code.")
                return

        # PHASE 1: User is submitting their ID for the first time
        if user_input.isdigit() and len(user_input) == 7:
            student_id = user_input
            student_email = f"up{student_id}@myport.ac.uk"
            
            # Generate a random 6-digit number string
            verification_code = str(random.randint(100000, 999999))
            
            # Save their details temporarily
            pending_verifications[user_id] = {
                "student_id": student_id,
                "code": verification_code
            }
            
            await message.channel.send(f"📬 Sending a verification code to `{student_email}`... Please wait a moment.")
            
            try:
                # Fire off the email asynchronously
                await send_verification_email(student_email, verification_code)
                await message.channel.send("📩 Code sent! Please check your university email inbox (and spam folder) and reply here with the 6-digit code.")
            except Exception as e:
                print(f"Email Error: {e}")
                await message.channel.send("❌ Failed to send email. Please ensure your ID is correct or contact a committee member.")
                if user_id in pending_verifications:
                    del pending_verifications[user_id]
            return
        
        # If it doesn't fit either phase, give them standard instructions
        await message.channel.send("Please enter a valid Student ID number to begin verification.")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
