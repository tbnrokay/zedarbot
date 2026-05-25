import discord
from discord.ext import commands

# Set up intents
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# STORAGE CONFIGURATION
STORAGE_CHANNEL_ID = 1508530457090719874

@bot.event
async def on_ready():
    print(f"--- International Court of Zedar Bot ---")
    print(f"Logged in successfully as: {bot.user.name}")
    print(f"----------------------------------------")

# ==========================================
#          FUNCTIONAL COMMANDS
# ==========================================

@bot.command(name="store")
async def store(ctx, *, message_text: str = None):
    """Stores text and attachments into the dedicated evidence/storage channel."""
    storage_channel = bot.get_channel(STORAGE_CHANNEL_ID)
    
    if not storage_channel:
        await ctx.send("❌ Error: Could not find the storage channel. Check bot permissions or ID.")
        return

    # Check if the user actually sent anything (text or files)
    if not message_text and not ctx.message.attachments:
        await ctx.send("❌ Please provide some text or attach a file to store.")
        return

    # Convert discord attachments into a list of file objects to re-upload
    files_to_send = []
    for attachment in ctx.message.attachments:
        # This downloads the file into memory and prepares it for sending
        file_obj = await attachment.to_file()
        files_to_send.append(file_obj)

    # Format the log message nicely for the storage channel
    log_content = f"📁 **New Evidence Deposited**\n" \
                  f"**Submitted by:** {ctx.author.mention} ({ctx.author.id})\n" \
                  f"**Channel:** {ctx.channel.mention}\n"
    
    if message_text:
        log_content += f"**Message:** {message_text}"

    try:
        # Send everything to the storage channel
        await storage_channel.send(content=log_content, files=files_to_send)
        await ctx.send("✅ Evidence safely logged in the archives.")
    except discord.Forbidden:
        await ctx.send("❌ Error: The bot does not have permission to send messages/files to the storage channel.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")


@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Purges a specified number of messages from the channel."""
    if amount <= 0:
        await ctx.send("Please specify a number greater than 0.", delete_after=5)
        return
        
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"⚖️ **Court Order:** {len(deleted) - 1} messages have been purged.", delete_after=5)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You do not have permission to alter court records (Manage Messages).")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please specify the number of messages to purge. Example: `!purge 10`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please provide a valid integer for the number of messages.")

# ==========================================
#          COURT PLACEHOLDER COMMANDS
# ==========================================

@bot.command(name="sue")
async def sue(ctx, *args):
    await ctx.send("⚖️ *Lawsuit filed with the court clerk. (Testing Only)*")

@bot.command(name="registerlawfirm")
async def registerlawfirm(ctx, *args):
    await ctx.send("💼 *Law firm registration received. pending review... (Testing Only)*")

@bot.command(name="subpoena")
async def subpoena(ctx, *args):
    await ctx.send("📜 *Subpoena issued. (Testing Only)*")

@bot.command(name="verdict")
async def verdict(ctx, *args):
    await ctx.send("🔨 *The judge bangs the gavel. Verdict pending... (Testing Only)*")

# Replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token from the Discord Developer Portal
bot.run('YOUR_BOT_TOKEN_HERE')
