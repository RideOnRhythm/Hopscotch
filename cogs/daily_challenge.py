from discord.ext import commands
import discord
import random

message_counters = {}


class DailyChallenge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quest(self, ctx):
        embed = discord.Embed(title='Quest')
        embed.description = 'Required Amount of Messages: '
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.author not in message_counters:
            message_counters[message.author] = 1
        else:
            message_counters[message.author] += 1

        required_amount = await database.get_other_attribute(self.bot.database, 'current_daily_required_msg')
        if message_counters[message.author] >= required_amount:
            pass


async def setup(bot):
    await bot.add_cog(DailyChallenge(bot))
