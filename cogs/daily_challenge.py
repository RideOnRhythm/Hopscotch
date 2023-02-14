from discord.ext import commands
import discord
import random
from assets import database


class DailyChallenge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quest(self, ctx):
        embed = discord.Embed(title='Quest', color=discord.color.og_blurple())

        required_amount = await database.get_other_attribute(self.bot.database, 'current_daily_required_msg')
        member_amount = await database.get_daily_message(self.bot.database, ctx.author)

        embed.description = f'**__DAILY QUEST__**\n> Send **{required_amount}** messages\n*Resets everyday at 12:00AM'
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.author not in message_counters:
            await database.set_daily_message(self.bot.database, message.author, 1, increment=False)
        else:
            await database.set_daily_message(self.bot.database, message.author, 1)

        required_amount = await database.get_other_attribute(self.bot.database, 'current_daily_required_msg')
        if await database.get_daily_message(self.bot.database, message.author) >= required_amount:
            rng = random.randint(500, 1000)
            await database.set_coins(self.bot.database, message.author, rng)


async def setup(bot):
    await bot.add_cog(DailyChallenge(bot))
