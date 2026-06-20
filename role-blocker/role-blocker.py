import discord
from discord.ext import commands

class RoleBlocker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blocked_role_id = 1480597515605770422 # The role ID to block users

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        # This event is dispatched when a thread channel is created and the genesis_message is sent.
        # It's a more reliable point to intervene if on_thread_initiate doesn't block.
        
        # Check if the creator (user) has the blocked role
        guild = self.bot.get_guild(thread.guild_id)
        if not guild:
            return

        member = guild.get_member(creator.id)
        if not member:
            return

        if discord.utils.get(member.roles, id=self.blocked_role_id):
            # User has the blocked role, send an error message and close the thread immediately
            error_embed = discord.Embed(
                title="Thread Creation Blocked",
                description="You are currently blacklisted from opening new support threads. If you believe this is an error, please contact a staff member directly.",
                color=discord.Color.red()
            )
            try:
                await creator.send(embed=error_embed)
            except discord.Forbidden:
                pass
            
            # Close the thread immediately
            try:
                # Based on Modmail's common structure, threads have a close method
                # or can be closed via the bot's modmail component.
                if hasattr(thread, 'close'):
                    await thread.close(closer=self.bot.user, silent=True, delete_channel=True, message="Blacklisted user attempted to open a thread.")
                elif hasattr(self.bot, 'modmail') and hasattr(self.bot.modmail, 'close_thread'):
                    await self.bot.modmail.close_thread(thread.channel.id, closer=self.bot.user, silent=True)
                else:
                    # Fallback: if we can't close it programmatically, at least delete the channel if possible
                    if hasattr(thread, 'channel') and thread.channel:
                        await thread.channel.delete(reason="Blacklisted user.")
            except Exception as e:
                print(f"Error closing thread for blacklisted user: {e}")

    @commands.Cog.listener()
    async def on_thread_initiate(self, thread, creator, category, initial_message):
        # Keep this as a first line of defense, even if it's not 100% reliable in all Modmail versions
        guild = self.bot.get_guild(thread.guild_id)
        if not guild:
            return

        member = guild.get_member(creator.id)
        if not member:
            return

        if discord.utils.get(member.roles, id=self.blocked_role_id):
            # Try to raise an exception that Modmail might catch to stop creation
            # Some versions of Modmail check for specific return values or exceptions here.
            raise commands.CheckFailure("User is blacklisted.")

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleBlocker(bot))
