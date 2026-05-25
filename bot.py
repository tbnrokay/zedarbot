import discord
from discord.ext import commands

# Set up intents (Required for modern discord bots)
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read message content

# Define your command prefix here (e.g., !)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"--- International Court of Zedar Bot ---")
    print(f"Logged in successfully as: {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print(f"----------------------------------------")

# ==========================================
#          FUNCTIONAL COMMANDS
# ==========================================

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Purges a specified number of messages from the channel."""
    if amount <= 0:
        await ctx.send("Please specify a number greater than 0.", delete_after=5)
        return
        
    # We add 1 to the amount to include the user's !purge command message itself
    deleted = await ctx.channel.purge(limit=amount + 1)
    
    # Send a temporary confirmation message (subtracting 1 so the number matches user intent)
    await ctx.send(f"⚖️ **Court Order:** {len(deleted) - 1} messages have been purged.", delete_after=5)

@purge.error
async def purge_error(ctx, error):
    """Error handling for the purge command."""
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
    """Placeholder for filing a lawsuit."""
    # It does nothing, but acknowledging it helps for testing responsiveness
    await ctx.send("⚖️ *Lawsuit filed with the court clerk. (Testing Only)*")

@bot.command(name="registerlawfirm")
async def registerlawfirm(ctx, *args):
    """Placeholder for registering a legal firm."""
    await ctx.send("💼 *Law firm registration received. pending review... (Testing Only)*")

@bot.command(name="subpoena")
async def subpoena(ctx, *args):
    """Placeholder for summoning a witness or evidence."""
    await ctx.send("📜 *Subpoena issued. (Testing Only)*")

@bot.command(name="verdict")
async def verdict(ctx, *args):
    """Placeholder for court rulings."""
    await ctx.send("🔨 *The judge bangs the gavel. Verdict pending... (Testing Only)*")

# Replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token from the Discord Developer Portal
bot.run('YOUR_BOT_TOKEN_HERE')
