from discord.ext import commands
import discord
import asyncio
import logging
import os
from assets import database
from dotenv import load_dotenv


class HopscotchBot(commands.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def is_owner(self, user: discord.User):
        if user.id in [member.id for member in self.application.team.members]:
            return True

        return await super().is_owner(user)


load_dotenv()
discord.utils.setup_logging(level=logging.INFO, root=False)
bot = HopscotchBot(command_prefix=('j.', 'J.', 'j,', 'J,', 'j', 'J'),
                   case_insensitive=True,
                   intents=discord.Intents.all(),
                   help_command=None)


@bot.command()
async def fix_database(ctx):
    if ctx.author.id not in (748388929631289436, 556307832241389581,
                             994223267462258688):
        return
    await ctx.send('Fixing database...')
    await database.create_nonexistent_keys(bot.database)
    await database.create_settings(bot.database)
    await ctx.send('Done')


@bot.command()
async def sync_tree(ctx):
    if ctx.author.id not in (748388929631289436, 556307832241389581,
                             994223267462258688):
        return
    await bot.tree.sync()
    await ctx.send('Synced')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f'This command is on cooldown. Please wait {int(error.retry_after)} seconds.'
        )
    elif not isinstance(error, ImportError) and not isinstance(
            error, ModuleNotFoundError):
        raise error


async def main():
    await bot.load_extension('jishaku')
    await bot.load_extension('cogs.utilities')
    await bot.load_extension('cogs.user_profile')
    await bot.load_extension('cogs.stats')
    await bot.load_extension('cogs.minigames')
    await bot.load_extension('cogs.role_organizer')
    await bot.load_extension('cogs.channel_desc')
    await bot.load_extension('cogs.grab_fun')
    await bot.load_extension('cogs.school')
    await bot.load_extension('cogs.inventory')
    await bot.load_extension('cogs.ai')
    await bot.load_extension('cogs.music')
    await bot.load_extension('cogs.nft')
    await bot.load_extension('cogs.settings')
    await bot.load_extension('cogs.hardcode')
    await bot.load_extension('cogs.daily_challenge')
    await bot.load_extension('cogs.two_factor')
    bot.database = await database.load_json()
    await bot.start(os.getenv('token'))


asyncio.run(main())
