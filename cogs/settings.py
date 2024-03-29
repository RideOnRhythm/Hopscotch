import asyncio
import datetime
import discord
import string
from discord.ext import commands
from assets import database

member_locks = {}


async def c4_settings_embed(cog, ctx):
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


async def quest_settings_embed(cog, ctx):
    embed = discord.Embed(title='Settings',
                          color=discord.Color.random(),
                          timestamp=datetime.datetime.now())

    complete_message = await database.get_settings(cog.bot.database, ctx.author,
                                             'complete_message')
    embed.description = f'''__**Quest Settings**__
**Send a message when Daily Challenge is completed**: {complete_message}
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
    if ctx.author.id in (748388929631289436, 994223267462258688, 556307832241389581):
        owned_themes = [{
                'name': 'Anika In Space',
                'id': 'anikainspace',
                'description': 'Its time to go on an adventure!',
                'icon': '<:THEME_anika:1073873897360982076>',
                'category': 'C4 Themes',
                'price': 5000,
                'quantity': None
            },{
                'name': 'Galaxy',
                'id': 'galaxy',
                'description':
                'Held together by gravity, a beautiful purple galaxy theme for your C4 games!',
                'icon': '<:THEME_galaxy:1073875133925699624>',
                'category': 'C4 Themes',
                'price': 10000,
                'quantity': None
            },{
                'name': 'Sakura',
                'id': 'sakura',
                'description': 'A pink sakura theme for your C4 games!',
                'icon': '<:THEME_sakura:1065929561419825162>',
                'category': 'C4 Themes',
                'price': 15000,
                'quantity': None
            },{
                'name': 'Pink-Blue',
                'id': 'pinkblue',
                'description': 'Why are the colors changing?',
                'icon': '<a:THEME_colorful:1065931156685606973>',
                'category': 'C4 Themes',
                'price': 20000,
                'quantity': None
            },
                {'name': 'Charles',
                'id': 'charles',
                'description': 'ummm...',
                'icon': '<:THEME_charles:1073876973824266351>',
                'category': 'C4 Themes',
                'price': 69420,
                'quantity': None}]
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

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label='Back', style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        member_locks[self.ctx.author] = True
        embed = await c4_settings_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed,
                                                view=C4SettingsView(
                                                    self.cog, self.ctx))


class C4SettingsView(discord.ui.View):

    def __init__(self, cog, ctx, timeout=180):
        self.cog = cog
        self.ctx = ctx
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('C4 Settings', 'Quest Settings')
                       ])
    async def select(self, interaction: discord.Interaction,
                          select: discord.ui.Select):
        if select.values[0] == 'C4 Settings':
            embed = await c4_settings_embed(self.cog, self.ctx)
            await interaction.response.edit_message(embed=embed, view=C4SettingsView(self.cog, self.ctx))
        elif select.values[0] == 'Quest Settings':
            embed = await quest_settings_embed(self.cog, self.ctx)
            await interaction.response.edit_message(embed=embed, view=DailyQuestView(self.cog, self.ctx))

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


class DailyQuestView(discord.ui.View):
    def __init__(self, cog, ctx, timeout=180):
        self.cog = cog
        self.ctx = ctx
        super().__init__(timeout=timeout)
    
    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('C4 Settings', 'Quest Settings')
                       ])
    async def select(self, interaction: discord.Interaction,
                          select: discord.ui.Select):
        if select.values[0] == 'C4 Settings':
            embed = await c4_settings_embed(self.cog, self.ctx)
            await interaction.response.edit_message(embed=embed, view=C4SettingsView(self.cog, self.ctx))
        elif select.values[0] == 'Quest Settings':
            embed = await quest_settings_embed(self.cog, self.ctx)
            await interaction.response.edit_message(embed=embed, view=DailyQuestView(self.cog, self.ctx))
    
    @discord.ui.button(label='Switch Quest Completion Message',
                       style=discord.ButtonStyle.secondary)
    async def switch_quest_completion(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        complete_message = await database.get_settings(self.cog.bot.database, ctx.author,
                                             'complete_message')
        if complete_message == 'Enabled':
            await database.set_settings(self.cog.bot.database, self.ctx.author,
                                        'Disabled', 'complete_message')
            await interaction.response.send_message(
                'Disabled Quest Completion Message.')
        elif complete_message == 'Disabled':
            await database.set_settings(self.cog.bot.database, self.ctx.author,
                                        'Enabled', 'complete_message')
            await interaction.response.send_message(
                'Enabled Quest Completion Message.')


class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def settings(self, ctx):
        embed = await c4_settings_embed(self, ctx)
        await ctx.send(embed=embed, view=C4SettingsView(self, ctx))


async def setup(bot):
    await bot.add_cog(Settings(bot))
