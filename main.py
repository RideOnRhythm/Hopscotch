from discord.ext import commands
import discord
import asyncio
import logging
import os
from assets import database

discord.utils.setup_logging(level=logging.INFO, root=False)
bot = commands.Bot(command_prefix=('j.', 'J.', 'j,', 'J,', 'j', 'J'),
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
  await ctx.send('Done')


@bot.command()
async def sync_tree(ctx):
  if ctx.author.id not in (748388929631289436, 556307832241389581,
                           994223267462258688):
    return
  await bot.tree.sync()
  await ctx.send('Synced')


@bot.command()
async def reload(ctx):
  if ctx.author.id not in (748388929631289436, 556307832241389581,
                           994223267462258688):
    return
  try:
    await bot.reload_extension('cogs.user_profile')
    await bot.reload_extension('cogs.stats')
    await bot.reload_extension('cogs.minigames')
    await bot.reload_extension('cogs.role_organizer')
    await bot.reload_extension('cogs.utilities')
    await bot.reload_extension('cogs.grab_fun')
    await bot.reload_extension('cogs.school')
    # await bot.reload_extension('cogs.music')
  except Exception as e:
    raise e
  bot.database = await database.load_json()
  await ctx.send('Done reloading')


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
  await bot.load_extension('cogs.user_profile')
  await bot.load_extension('cogs.stats')
  await bot.load_extension('cogs.minigames')
  await bot.load_extension('cogs.role_organizer')
  await bot.load_extension('cogs.utilities')
  await bot.load_extension('cogs.channel_desc')
  await bot.load_extension('cogs.grab_fun')
  await bot.load_extension('cogs.school')
  # await bot.load_extension('cogs.music')
  bot.database = await database.load_json()
  await bot.start('MTAwMTY2ODI1MDk1MTc1MzczOA.GvMnfv.V6HZ0jJk8aEOXIuQQXhDa44QTtHqVHOcX7fHQE')


asyncio.run(main())
