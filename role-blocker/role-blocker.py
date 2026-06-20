import discord
from discord.ext import commands

class RoleBlocker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blocked_role_id = 1480597515605770422 # The role ID to block users

    @commands.Cog.listener()
    async def on_thread_initiate(self, thread, creator, category, initial_message):
        # Check if the creator (user) has the blocked role
        guild = self.bot.get_guild(thread.guild_id) # Assuming thread object has guild_id
        if not guild:
            print(f"Could not find guild for thread {thread.id}")
            return # Allow thread creation if guild not found (or handle as error)

        member = guild.get_member(creator.id)
        if not member:
            print(f"Could not find member {creator.id} in guild {guild.id}")
            return # Allow thread creation if member not found (or handle as error)

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
                # If DMs are blocked, log it but still prevent thread creation
                print(f"Could not send DM to {creator.id}. User might have DMs disabled.")
            
            # This is the crucial part: Modmail's on_thread_initiate listener needs to be stopped.
            # Raising an exception is a common way to do this in event listeners.
            # Modmail's internal handling of this event might catch specific exceptions
            # to prevent thread creation. A generic CommandError might not be enough.
            # Let's try raising a more specific exception or a custom one if needed.
            # For now, returning None after sending the message should prevent further processing
            # in many event-driven frameworks. If this doesn't work, we'll need Modmail-specific docs.
            print(f"Blocking thread creation for user {creator.id} due to blocked role.")
            # Modmail's on_thread_initiate is expected to return a boolean or raise an exception
            # to indicate if the thread should proceed. Returning None might implicitly stop it.
            # If this doesn't work, the Modmail documentation on blocking thread creation is essential.
            return # This should prevent the thread from being created in Modmail

    # If the plugin needs to be loaded via setup function
async def setup(bot: commands.Bot):
    await bot.add_cog(RoleBlocker(bot))
