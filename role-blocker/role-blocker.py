import discord
from discord.ext import commands

class RoleBlocker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blocked_role_id = 1480597515605770422 # The role ID to block users

    @commands.Cog.listener()
    async def on_message(self, message):
        # Only process DMs to the bot
        if message.guild is not None or message.author.bot:
            return

        # Fetch the member from the main guild to check roles
        # We assume the bot is in at least one guild where this role exists
        for guild in self.bot.guilds:
            member = guild.get_member(message.author.id)
            if member:
                if discord.utils.get(member.roles, id=self.blocked_role_id):
                    # User is blacklisted, send error and stop Modmail from seeing this message
                    error_embed = discord.Embed(
                        title="Access Denied",
                        description="You are currently blacklisted from opening new support threads. If you believe this is an error, please contact a staff member directly.",
                        color=discord.Color.red()
                    )
                    try:
                        await message.author.send(embed=error_embed)
                    except discord.Forbidden:
                        pass
                    
                    # To stop Modmail from processing this message, we can't easily "cancel" the event
                    # for other listeners in discord.py. However, many Modmail versions check if a 
                    # message has already been handled or if a certain condition is met.
                    # Since we can't easily block other listeners, let's also use the reactive approach
                    # but more aggressively.
                    return

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        # Aggressive reactive closing
        guild = self.bot.get_guild(thread.guild_id)
        if not guild:
            return

        member = guild.get_member(creator.id)
        if not member:
            return

        if discord.utils.get(member.roles, id=self.blocked_role_id):
            # Close and delete the channel immediately
            try:
                # 1. Send closing message to user
                error_embed = discord.Embed(
                    title="Thread Blocked",
                    description="You are blacklisted. This thread is being closed automatically.",
                    color=discord.Color.red()
                )
                await creator.send(embed=error_embed)

                # 2. Delete the channel directly via discord.py API
                # This is the most direct way to make it "disappear" from the staff view
                if hasattr(thread, 'channel') and thread.channel:
                    await thread.channel.delete(reason="Blacklisted user.")
                
                # 3. Try to call Modmail's internal close if possible
                if hasattr(thread, 'close'):
                    await thread.close(closer=self.bot.user, silent=True, delete_channel=True)
            except Exception as e:
                print(f"Aggressive close failed: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleBlocker(bot))
