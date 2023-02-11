import asyncio
import datetime
import discord
import string
from discord.ext import commands
from assets import database

member_locks = {}


async def settings_embed(cog, ctx):
    embed = discord.Embed(title='Settings',
                          color=discord.Color.random(),
                          timestamp=datetime.datetime.now())

    game_theme = await database.get_settings(cog.bot.database, ctx.author,
                                             'c4gametheme')
    extreme_theme = await database.get_settings(cog.bot.database, ctx.author,
                                                'c4extremetheme')
    number_row = await database.get_settings(cog.bot.database, ctx.author,
                                             'number_row')
    embed.description = f'''__**C4 Theme**__
**Game Theme**: {game_theme}
**Extreme Theme**: {extreme_theme}
**Show Column Number**: {number_row}

> To change your theme, select a button below.
        '''

    return embed


async def change_theme(cog, ctx, attribute, interaction):
    embed = discord.Embed(title='Settings',
                          color=discord.Color.random(),
                          timestamp=datetime.datetime.now())
    if attribute == 'c4gametheme':
        embed.description = '__**Editing C4 Game Theme**__'
    elif attribute == 'c4extremetheme':
        embed.description = '__**Editing C4 Extreme Theme**__'
    embed.description += '\nBelow are the themes you currently own. To select one, send the letter of the theme you would like to use.\n'

    owned_themes = await database.get_items(cog.bot.database, ctx.author)
    owned_themes = filter(lambda x: x['category'] == 'C4 Themes', owned_themes)
    embed.description += '\n**A** - Default'
    letter_map = {'A': 'Default'}
    for ind, theme in enumerate(owned_themes):
        embed.description += f'\n**{string.ascii_uppercase[1:][ind]}** - {theme["name"]}'
        letter_map[string.ascii_uppercase[1:][ind]] = theme['name']
    await interaction.response.edit_message(embed=embed,
                                            view=GameThemeView(cog, ctx))

    while True:

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        msg = await cog.bot.wait_for('message', timeout=300, check=check)
        if member_locks.get(ctx.author):
            return
        if msg.content.upper() not in letter_map:
            temp = await ctx.send(
                'Please send the letter of the theme you would like to use.')
            await asyncio.sleep(5)
            await temp.delete()
            continue
        await database.set_settings(cog.bot.database, ctx.author,
                                    letter_map[msg.content.upper()], attribute)
        temp = await ctx.send('Theme equipped.')
        await asyncio.sleep(5)
        await temp.delete()
        return


class GameThemeView(discord.ui.View):

    def __init__(self, cog, ctx, timeout=180):
        self.cog = cog
        self.ctx = ctx
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        member_locks[self.ctx.author] = True
        embed = await settings_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed,
                                                view=SettingsView(
                                                    self.cog, self.ctx))


class SettingsView(discord.ui.View):

    def __init__(self, cog, ctx, timeout=180):
        self.cog = cog
        self.ctx = ctx
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Edit Game Theme',
                       style=discord.ButtonStyle.secondary)
    async def edit_game_theme(self, interaction: discord.Interaction,
                              button: discord.ui.Button):
        if member_locks.get(self.ctx.author):
            member_locks.pop(self.ctx.author)
        await change_theme(self.cog, self.ctx, 'c4gametheme', interaction)

    @discord.ui.button(label='Edit Extreme Theme',
                       style=discord.ButtonStyle.secondary)
    async def edit_extreme_theme(self, interaction: discord.Interaction,
                                 button: discord.ui.Button):
        if member_locks.get(self.ctx.author):
            member_locks.pop(self.ctx.author)
        await change_theme(self.cog, self.ctx, 'c4extremetheme', interaction)

    @discord.ui.button(label='Switch Show Column Number',
                       style=discord.ButtonStyle.secondary)
    async def switch_number_row(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        number_row = await database.get_settings(self.cog.bot.database,
                                                 self.ctx.author, 'number_row')
        if number_row == 'Enabled':
            await database.set_settings(self.cog.bot.database, self.ctx.author,
                                        'Disabled', 'number_row')
            await interaction.response.send_message(
                'Disabled Show Column Number.')
        elif number_row == 'Disabled':
            await database.set_settings(self.cog.bot.database, self.ctx.author,
                                        'Enabled', 'number_row')
            await interaction.response.send_message(
                'Enabled Show Column Number.')


class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def settings(self, ctx):
        embed = await settings_embed(self, ctx)
        await ctx.send(embed=embed, view=SettingsView(self, ctx))


async def setup(bot):
    await bot.add_cog(Settings(bot))
