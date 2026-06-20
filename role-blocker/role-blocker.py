import discord
from discord.ext import commands

class RoleBlocker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blocked_role_id = 1480597515605770422 # The role ID to block users

    async def _close_modmail_thread(self, thread, creator, close_reason):
        try:
            # 1. Send closing message to the user who opened the ticket (via DM)
            user_embed = discord.Embed(
                title="Thread Blocked",
                description=f"Your ticket has been closed. Reason: {close_reason}", 
                color=discord.Color.red()
            )
            try:
                await creator.send(embed=user_embed)
            except discord.Forbidden:
                pass

            # 2. Attempt to close the thread using Modmail's internal mechanism (as in the previous plugin)
            # This ensures resources are cleaned up properly in Modmail.
            if hasattr(thread, 'close'):
                # Some Modmail versions have the close method on the thread object
                await thread.close(closer=self.bot.user, silent=True, delete_channel=True, message=close_reason)
            elif hasattr(self.bot, 'modmail') and hasattr(self.bot.modmail, 'close_thread'):
                # Others use a central modmail component
                await self.bot.modmail.close_thread(thread.channel.id, closer=self.bot.user, silent=True)
            else:
                # Fallback if no programmatic close is found, at least delete the channel
                if hasattr(thread, 'channel') and thread.channel:
                    await thread.channel.delete(reason=f"Blocked user: {close_reason}")

        except Exception as e:
            print(f"Error closing Modmail thread for blocked user: {e}")

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        # This event is dispatched when a thread channel is created.
        # Check if the creator (user) has the blocked role
        guild = self.bot.get_guild(thread.guild_id)
        if not guild:
            return

        member = guild.get_member(creator.id)
        if not member:
            return

        if discord.utils.get(member.roles, id=self.blocked_role_id):
            # User is blacklisted, close the thread immediately using Modmail API
            await self._close_modmail_thread(thread, creator, "User is blacklisted from opening support threads.")

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleBlocker(bot))
