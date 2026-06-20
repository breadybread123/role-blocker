import discord
from discord.ext import commands

class RoleBlocker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blocked_role_id = 1480597515605770422 # The role ID to block users

    @commands.Cog.listener()
    async def on_thread_initiate(self, thread, creator, category, initial_message):
        # Check if the creator (user) has the blocked role
        # We need to fetch the member object from the guild
        guild = self.bot.get_guild(thread.guild_id) # Assuming thread object has guild_id
        if not guild:
            print(f"Could not find guild for thread {thread.id}")
            return

        member = guild.get_member(creator.id)
        if not member:
            print(f"Could not find member {creator.id} in guild {guild.id}")
            return

        if discord.utils.get(member.roles, id=self.blocked_role_id):
            # User has the blocked role, send an error message and prevent thread creation
            error_embed = discord.Embed(
                title="Thread Creation Blocked",
                description="You are currently blacklisted from opening new support threads. If you believe this is an error, please contact a staff member directly.",
                color=discord.Color.red()
            )
            try:
                await creator.send(embed=error_embed)
            except discord.Forbidden:
                # If DMs are blocked, try to send in the channel if possible (though thread isn't fully initiated)
                # This might not work reliably as the thread is not fully set up yet.
                pass 
            
            # Prevent the thread from being created
            # This is a hypothetical way to stop thread creation in Modmail
            # Actual implementation might require raising an exception or returning a specific value
            # For now, we'll assume returning None or raising an error will stop the process.
            raise commands.CommandError("User is blacklisted from opening threads.")

    # If the plugin needs to be loaded via setup function
async def setup(bot: commands.Bot):
    await bot.add_cog(RoleBlocker(bot))
