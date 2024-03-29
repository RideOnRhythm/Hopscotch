from discord.ext import commands
import discord
import random
from assets import database


class DailyChallenge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quest(self, ctx):
        embed = discord.Embed(title='Quest', color=discord.Color.og_blurple())

        required_amount = await database.get_other_attribute(self.bot.database, 'current_daily_required_msg')
        try:
            member_amount = await database.get_daily_message(self.bot.database, ctx.author)
        except KeyError:
            member_amount = 0

        if member_amount < required_amount:
            embed.description = f'**__DAILY QUEST__**\n> Send **{required_amount - member_amount}** messages\n*Resets everyday at 12:00AM'
        else:
            reward = await database.get_other_attribute(self.bot.database, 'daily_quest_rewards')
            embed.description = f'**__DAILY QUEST__**\n> You have completed the daily quest and earned **{reward[str(ctx.author.id)]}** 🪙. Come back again tomorrow!'

        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        rewards = await database.get_other_attribute(self.bot.database, 'daily_quest_rewards')
        required_amount = await database.get_other_attribute(self.bot.database, 'current_daily_required_msg')
        message_counters = await database.get_other_attribute(self.bot.database, 'daily_message_counts')
        if str(message.author.id) in rewards:
            return
        if str(message.author.id) not in message_counters:
            await database.set_daily_message(self.bot.database, message.author, 1, increment=False)
        else:
            await database.set_daily_message(self.bot.database, message.author, 1)

        if await database.get_daily_message(self.bot.database, message.author) >= required_amount:
            rng = random.randint(500, 1000)
            await database.set_daily_reward(self.bot.database, message.author, rng, increment=False)
            await database.set_coins(self.bot.database, message.author, rng)
            complete_message = await database.get_settings(self.bot.database, message.author,
                                             'complete_message')    
            await database.set_daily_message(self.bot.database, message.author, 0, increment=False)
            if complete_message == 'Enabled':
                await message.reply(f'You have completed today\'s daily challenge and have earned **{rng}** 🪙.')


async def setup(bot):
    await bot.add_cog(DailyChallenge(bot))
