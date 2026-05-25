import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

# Set up intents
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# CONFIGURATION IDs
STORAGE_CHANNEL_ID = 1508530457090719874
PUBLIC_LOG_CHANNEL_ID = 1508522466312585246
ADMIN_USER_ID = 1454359635229413377

@bot.event
async def on_ready():
    print(f"--- International Court of Zedar Bot ---")
    print(f"Logged in successfully as: {bot.user.name}")
    print(f"----------------------------------------")

# ==========================================
#        INTERACTIVE INTERACTION VIEWS
# ==========================================

class ApprovalView(View):
    """Interactive buttons sent to the admin for approving/denying law firms."""
    def __init__(self, applicant, ign, firm_name):
        super().__init__(timeout=None) 
        self.applicant = applicant
        self.ign = ign
        self.firm_name = firm_name

    @discord.ui.button(label="Accept ✅", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable buttons after click
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        # Notify Public Log Channel
        log_channel = bot.get_channel(PUBLIC_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="💼 Law Firm Registered Successfully", 
                color=discord.Color.green()
            )
            embed.add_field(name="Law Firm Name", value=f"**{self.firm_name}**", inline=False)
            embed.add_field(name="Firm Owner", value=f"{self.applicant.mention} ({self.applicant.name})", inline=True)
            embed.add_field(name="Minecraft IGN", value=self.ign, inline=True)
            embed.add_field(name="Owner Discord ID", value=self.applicant.id, inline=False)
            embed.add_field(name="Approved By", value=interaction.user.mention, inline=False)
            await log_channel.send(embed=embed)

        # Notify Applicant via DM
        try:
            await self.applicant.send(f"🎉 **Application Approved!** Your law firm, **{self.firm_name}**, has been officially registered with the International Court of Zedar.")
        except discord.Forbidden:
            pass 

        await interaction.followup.send(f"✅ Approved application for {self.applicant.name}'s firm: {self.firm_name}.")

    @discord.ui.button(label="Deny ❌", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        # Notify Applicant via DM
        try:
            await self.applicant.send(f"❌ **Application Denied:** Your application to register **{self.firm_name}** was rejected by the Court administration.")
        except discord.Forbidden:
            pass

        await interaction.followup.send(f"❌ Denied application for {self.applicant.name}.")


# ==========================================
#          FUNCTIONAL COMMANDS
# ==========================================

@bot.command(name="registerlawfirm")
async def registerlawfirm(ctx):
    """Starts the multi-step law firm registration process via DM."""
    applicant = ctx.author

    # 1. Ask for Minecraft IGN
    try:
        await applicant.send("💼 **International Court of Zedar — Law Firm Registration**\n\n**Step 1:** Please reply to this message with your Minecraft **In-Game Name (IGN)**:")
        await ctx.send(f"✉️ {applicant.mention}, I've sent you a DM to start your law firm registration.")
    except discord.Forbidden:
        await ctx.send(f"❌ {applicant.mention}, I couldn't DM you! Please open your DMs in your privacy settings.")
        return

    def check(m):
        return m.author == applicant and isinstance(m.channel, discord.DMChannel)

    # Collect Step 1 response
    try:
        msg1 = await bot.wait_for('message', check=check, timeout=300.0)
        user_ign = msg1.content
    except asyncio.TimeoutError:
        try:
            await applicant.send("❌ Registration timed out. Please run `!registerlawfirm` in the server again when you're ready.")
        except discord.Forbidden:
            pass
        return

    # 2. Ask for Law Firm Name
    try:
        await applicant.send("📝 **Step 2:** Got it! Now, please reply with the official **Name of your Law Firm**:")
    except discord.Forbidden:
        return

    # Collect Step 2 response
    try:
        msg2 = await bot.wait_for('message', check=check, timeout=300.0)
        firm_name = msg2.content
    except asyncio.TimeoutError:
        try:
            await applicant.send("❌ Registration timed out. Please run `!registerlawfirm` in the server again to restart.")
        except discord.Forbidden:
            pass
        return

    # 3. Confirmation to Applicant
    await applicant.send(f"⏳ Thank you! Your application for **{firm_name}** has been submitted to Court administration for approval.")

    # 4. DM the Admin for approval
    admin = await bot.fetch_user(ADMIN_USER_ID)
    if admin:
        embed = discord.Embed(
            title="⚖️ Pending Law Firm Registration", 
            description="A user is requesting to register a new law firm.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Proposed Firm Name", value=f"**{firm_name}**", inline=False)
        embed.add_field(name="User", value=f"{applicant.mention} ({applicant.name})", inline=True)
        embed.add_field(name="Minecraft IGN", value=user_ign, inline=True)
        embed.add_field(name="User ID", value=applicant.id, inline=False)
        
        view = ApprovalView(applicant, user_ign, firm_name)
        await admin.send(embed=embed, view=view)
    else:
        print(f"CRITICAL ERROR: Admin user with ID {ADMIN_USER_ID} could not be found.")


@bot.command(name="store")
async def store(ctx, *, message_text: str = None):
    """Stores text and attachments into the dedicated evidence/storage channel."""
    storage_channel = bot.get_channel(STORAGE_CHANNEL_ID)
    
    if not storage_channel:
        await ctx.send("❌ Error: Could not find the storage channel.")
        return

    if not message_text and not ctx.message.attachments:
        await ctx.send("❌ Please provide some text or attach a file to store.")
        return

    files_to_send = []
    for attachment in ctx.message.attachments:
        file_obj = await attachment.to_file()
        files_to_send.append(file_obj)

    log_content = f"📁 **New Evidence Deposited**\n" \
                  f"**Submitted by:** {ctx.author.mention} ({ctx.author.id})\n" \
                  f"**Channel:** {ctx.channel.mention}\n"
    
    if message_text:
        log_content += f"**Message:** {message_text}"

    try:
        await storage_channel.send(content=log_content, files=files_to_send)
        await ctx.send("✅ Evidence safely logged in the archives.")
    except discord.Forbidden:
        await ctx.send("❌ Error: The bot lacks permission to write to the storage channel.")
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
        await ctx.send("❌ Please specify the number of messages to purge.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please provide a valid integer.")

# ==========================================
#          COURT PLACEHOLDER COMMANDS
# ==========================================

@bot.command(name="sue")
async def sue(ctx, *args):
    await ctx.send("⚖️ *Lawsuit filed with the court clerk. (Testing Only)*")

@bot.command(name="subpoena")
async def subpoena(ctx, *args):
    await ctx.send("📜 *Subpoena issued. (Testing Only)*")

@bot.command(name="verdict")
async def verdict(ctx, *args):
    await ctx.send("🔨 *The judge bangs the gavel. Verdict pending... (Testing Only)*")

# Replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token from the Discord Developer Portal
bot.run('MTUwODUyNTkzNTg0NDkxNzM2OQ.GZ1Ggl.qdYTFpXNul6LBUALUJnfZAPrBeujjlgN_v68YU')
