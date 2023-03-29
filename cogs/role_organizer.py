from discord.ext import commands
from assets import database
from discord import ButtonStyle, Emoji, PartialEmoji
from typing import Optional, Union
import discord
import datetime
import asyncio
import string

# very messy code coming up ahead
name_colors_locks = set([])
school_locks = set([])
pronoun_locks = set([])
gaming_locks = set([])
server_locks = set([])
smp_locks = set([])
sleep = 0.75


async def roles_embed():
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now(), color=discord.Color.random())
    embed.description = '__**Select a category:**__\n> Click on a button below to select the category you want to configure.'
    return embed


async def name_colors_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now(), color=discord.Color.random())

    colors = [
        999924337882697728, 999924519592534146, 999924445319798935,
        1025730412003209236, 999924808500379739, 1025732223216914473,
        999924745069936660, 1026791699361562684, 1002843836927721522
    ]
    current_role = next(
        (item
         for item in [role.id for role in ctx.author.roles] if item in colors),
        None)
    role_string = f'<@&{current_role}>'
    if current_role == 1002843836927721522:
        role_string = '<@&1002843836927721522> (Default)'
    embed.description = f'__**Editing Name Colors**__\n**Currently using**: {role_string}\n\n**A** ― <@&999924337882697728>\n**B** ― <@&999924519592534146>\n**C** ― <@&999924445319798935>\n**D** ― <@&1025730412003209236>\n**E** ― <@&999924808500379739>\n**F** ― <@&1025732223216914473>\n**G** ― <@&999924745069936660>\n**H** ― <@&1026791699361562684>\n**I** ― <@&1002843836927721522>\n'

    inventory = await database.get_attribute(cog.bot.database, ctx.author,
                                             'inventory')
    roles = {
        'aqua': 1025730208617201714,
        'lightmaroon': 1026791817984876587,
        'rosegold': 1025732623143796746,
        'lightpurple': 1025730083207532616,
        'lightred': 1025730536297222255,
        'lightyellow': 999924635648938034,
        'lightgreen': 1025732311888711750,
        'darkblue': 1025730320865173635,
        'lightpink': 1072390959846928494,
        'legend': 1041704006709411880
    }
    inventory_roles = [
        roles.get(id['id'])
        for id in filter(lambda item: item['id'] in roles, inventory)
    ]
    for ind, role in enumerate(inventory_roles):
        embed.description += f'**{string.ascii_uppercase[9:][ind]}** ― <@&{role}>\n'

    embed.description += '\n> To change the name color you are currently using, type and send the letter of the name color you want. Note that you can only have ONE color at once. Selecting another one will change the current one you\'re using.'
    return embed


async def school_roles_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now(), color=discord.Color.random())
    embed.description = '**__Editing Section/Honors Class/Special PE/Chinese__**\n\n'

    sections = [858224685686325268, 858224260856938518, 858224148248788996]
    honors_class = [1027097851119013908, 1044512060379254805]
    special_pe = [
        1039871025845907526, 1039871059379359774, 1039871334416650320
    ]
    chinese = [1014844875058982983, 1039452681888083998, 1014845262734311516]

    embed.description += '**Sections**: (You can only have 1 Section role)\n'
    for ind, role in enumerate(sections):
        embed.description += f'{string.ascii_uppercase[ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '\n**Honors Class**:\n'
    for ind, role in enumerate(honors_class):
        embed.description += f'{string.ascii_uppercase[3:][ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '\n**Special PE**: (You can only have 1 Special PE role):\n'
    for ind, role in enumerate(special_pe):
        embed.description += f'{string.ascii_uppercase[5:][ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'
    
    embed.description += '\n**Chinese**: (You can only have 1 Chinese role):\n'
    for ind, role in enumerate(chinese):
        embed.description += f'{string.ascii_uppercase[8:][ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '\n> To add Section/Honors Class/Special PE/Chinese roles, type and send the letter of the Section/Honors Class/Special PE/Chinese roles you want. Note that Sections, Special PE, and Chinese roles can only have ONE role at once. Selecting another one will change the current one you\'re using.'
    return embed


async def pronouns_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now(), color=discord.Color.random())
    embed.description = '**__Editing Pronouns__**\n'

    pronouns = [858166817938997248, 858166818615197696, 858166819046031381]
    for ind, role in enumerate(pronouns):
        embed.description += f'{string.ascii_uppercase[ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '> To add Pronoun roles, type and send the letter of the Pronoun roles you want.'
    return embed


async def gaming_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now(), color=discord.Color.random())
    embed.description = '**__Editing Gaming__**\n'

    gaming = [
        858228412894937109, 858228515455762462, 947794021600870410,
        858228860214312990, 937291486549135390
    ]
    for ind, role in enumerate(gaming):
        embed.description += f'{string.ascii_uppercase[ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '> To add Gaming roles, type and send the letter of the Gaming roles you want.'
    return embed


async def server_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now(), color=discord.Color.random())
    embed.description = '**__Editing Announcements/Events/and more__**\n'

    server = [
        1025751709139619881, 858228825800441896, 858228567762665493,
        1010112913983410197, 1010113161392832543, 1010113746364026900,
        858228627157024780, 1010113868430852218, 960381580617080904,
        858166828194201640, 858228761955008533, 1015233233333538847,
        858166829847543859, 1090514249564033114
    ]
    for ind, role in enumerate(server):
        embed.description += f'{string.ascii_uppercase[ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '> To add these roles, type and send the letter of the roles you want.'
    return embed


async def smp_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now(), color=discord.Color.random())
    embed.description = '**__Editing SMP Roles__**\n'

    smp = [1086510190297358396, 1086510237839806536, 1086510068675129477, 1086510326025048065, 1085477806839955516, 1086510551129129031, 1086896061425127544]
    for ind, role in enumerate(smp):
        embed.description += f'{string.ascii_uppercase[ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '> To add these roles, type and send the letter of the roles you want.'
    return embed


class SMPButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[Union[str, Emoji, PartialEmoji]] = None, row: Optional[int] = None, cog, ctx):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.cog = cog
        self.ctx = ctx
    
    async def callback(self, interaction: discord.Interaction):
        await asyncio.sleep(sleep)
        name_colors_locks.add(self.ctx.author)
        school_locks.add(self.ctx.author)
        pronoun_locks.add(self.ctx.author)
        gaming_locks.add(self.ctx.author)
        server_locks.add(self.ctx.author)
        if self.ctx.author in smp_locks:
            smp_locks.remove(self.ctx.author)
        else:
            smp_locks.add(self.ctx.author)

        embed = await smp_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:
            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            if self.ctx.author in smp_locks:
                return

            valid_letters = 'ABCDEFG'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            smp = [1086510190297358396, 1086510237839806536, 1086510068675129477, 1086510326025048065, 1085477806839955516, 1086510551129129031, 1086896061425127544]
            try:
                if smp[string.ascii_uppercase.index(
                        msg.content.upper())] in [
                            role.id for role in self.ctx.author.roles
                        ]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(
                            smp[string.ascii_uppercase.index(
                                msg.content.upper())]))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(smp[string.ascii_uppercase.index(msg.content.upper())]).name}!'
                    )
                    embed = await server_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
            except ValueError:
                pass
            new_role = self.ctx.guild.get_role(
                smp[string.ascii_uppercase.index(msg.content.upper())])
            await self.ctx.author.add_roles(new_role)
            await self.ctx.send(f'Successfully added role: {new_role.name}!')

            embed = await smp_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            continue


class DefaultView(discord.ui.View):

    def __init__(self, cog, ctx, timeout=180):
        self.cog = cog
        self.ctx = ctx
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label='Name Colors',
                       style=discord.ButtonStyle.secondary)
    async def name_colors(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await asyncio.sleep(sleep)
        if self.ctx.author in name_colors_locks:
            name_colors_locks.remove(self.ctx.author)
        else:
            name_colors_locks.add(self.ctx.author)
        school_locks.add(self.ctx.author)
        pronoun_locks.add(self.ctx.author)
        gaming_locks.add(self.ctx.author)
        server_locks.add(self.ctx.author)
        smp_locks.add(self.ctx.author)

        embed = await name_colors_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            if self.ctx.author in name_colors_locks:
                return

            valid_letters = 'ABCDEFGHI'
            inventory = await database.get_attribute(self.cog.bot.database,
                                                     self.ctx.author,
                                                     'inventory')
            roles = {
                'aqua': 1025730208617201714,
                'lightmaroon': 1026791817984876587,
                'rosegold': 1025732623143796746,
                'lightpurple': 1025730083207532616,
                'lightred': 1025730536297222255,
                'lightyellow': 999924635648938034,
                'lightgreen': 1025732311888711750,
                'darkblue': 1025730320865173635,
                'lightpink': 1072390959846928494,
                'legend': 1041704006709411880
            }
            inventory_roles = [
                roles.get(id['id'])
                for id in filter(lambda item: item['id'] in roles, inventory)
            ]
            for ind, role in enumerate(inventory_roles):
                valid_letters += string.ascii_uppercase[9:][ind]
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            colors = [
                999924337882697728, 999924519592534146, 999924445319798935,
                1025730412003209236, 999924808500379739, 1025732223216914473,
                999924745069936660, 1026791699361562684, 1002843836927721522
            ]
            current_role = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in colors), None)
            if msg.content.upper() == string.ascii_uppercase[
                    colors.index(current_role)]:
                await self.ctx.author.remove_roles(
                    self.ctx.guild.get_role(current_role))
                await self.ctx.author.add_roles(
                    self.ctx.guild.get_role(1002843836927721522))
                await self.ctx.send(
                    'Successfully removed your name color. You are now using the default color: Pink (Default).'
                )
            else:
                all_roles = colors + inventory_roles
                new_role = self.ctx.guild.get_role(
                    all_roles[string.ascii_uppercase.index(
                        msg.content.upper())])
                await self.ctx.author.remove_roles(
                    self.ctx.guild.get_role(current_role))
                await self.ctx.author.add_roles(new_role)
                await self.ctx.send(
                    f'Successfully changed your name color to {new_role.name}!'
                )
            embed = await name_colors_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            continue

    @discord.ui.button(label='Section/Honors Class/Special PE/Chinese',
                       style=discord.ButtonStyle.secondary)
    async def school_roles(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await asyncio.sleep(sleep)
        name_colors_locks.add(self.ctx.author)
        if self.ctx.author in school_locks:
            school_locks.remove(self.ctx.author)
        else:
            school_locks.add(self.ctx.author)
        pronoun_locks.add(self.ctx.author)
        gaming_locks.add(self.ctx.author)
        server_locks.add(self.ctx.author)
        smp_locks.add(self.ctx.author)

        embed = await school_roles_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            if self.ctx.author in school_locks:
                return

            valid_letters = 'ABCDEFGHIJK'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            sections = [
                858224685686325268, 858224260856938518, 858224148248788996
            ]
            honors_class = [1027097851119013908, 1044512060379254805]
            special_pe = [
                1039871025845907526, 1039871059379359774, 1039871334416650320
            ]
            chinese = [
                1014844875058982983, 1039452681888083998, 1014845262734311516
            ]
            all_roles = sections + honors_class + special_pe + chinese
            current_role = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in all_roles), None)
            section_current = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in sections), None)
            honors_current = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in honors_class), None)
            special_current = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in special_pe), None)
            chinese_current = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in chinese), None)
            try:
                if msg.content.upper() == string.ascii_uppercase[
                        all_roles.index(section_current)]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(section_current))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(section_current).name}!'
                    )
                    embed = await school_roles_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
                elif msg.content.upper() == string.ascii_uppercase[
                        all_roles.index(honors_current)]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(honors_current))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(honors_current).name}!'
                    )
                    embed = await school_roles_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
                elif msg.content.upper() == string.ascii_uppercase[
                        all_roles.index(special_current)]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(special_current))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(special_current).name}!'
                    )
                    embed = await school_roles_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
                elif msg.content.upper() == string.ascii_uppercase[
                        all_roles.index(chinese_current)]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(chinese_current))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(chinese_current).name}!'
                    )
                    embed = await school_roles_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
            except ValueError:
                pass
            if string.ascii_uppercase.index(
                    msg.content.upper()) < 3 or string.ascii_uppercase.index(
                        msg.content.upper()) > 4 and current_role is not None:
                new_role = self.ctx.guild.get_role(
                    all_roles[string.ascii_uppercase.index(
                        msg.content.upper())])
                if new_role.id in sections and section_current is not None:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(section_current))
                    category = 'Section'
                    await self.ctx.author.add_roles(new_role)
                    await self.ctx.send(
                        f'Successfully changed your {category} to {new_role.name}!'
                    )
                    embed = await school_roles_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
                elif new_role.id in special_pe and special_current is not None:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(special_current))
                    category = 'Special PE'
                    await self.ctx.author.add_roles(new_role)
                    await self.ctx.send(
                        f'Successfully changed your {category} to {new_role.name}!'
                    )
                    embed = await school_roles_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
                elif new_role.id in chinese and chinese_current is not None:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(chinese_current))
                    category = 'Chinese'
                    await self.ctx.author.add_roles(new_role)
                    await self.ctx.send(
                        f'Successfully changed your {category} to {new_role.name}!'
                    )
                    embed = await school_roles_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
            new_role = self.ctx.guild.get_role(
                all_roles[string.ascii_uppercase.index(msg.content.upper())])
            await self.ctx.author.add_roles(new_role)
            await self.ctx.send(f'Successfully added role: {new_role.name}!')

            embed = await school_roles_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            continue

    @discord.ui.button(label='Pronouns', style=discord.ButtonStyle.secondary)
    async def pronouns(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await asyncio.sleep(sleep)
        name_colors_locks.add(self.ctx.author)
        school_locks.add(self.ctx.author)
        if self.ctx.author in pronoun_locks:
            pronoun_locks.remove(self.ctx.author)
        else:
            pronoun_locks.add(self.ctx.author)
        gaming_locks.add(self.ctx.author)
        server_locks.add(self.ctx.author)
        smp_locks.add(self.ctx.author)

        embed = await pronouns_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            if self.ctx.author in pronoun_locks:
                return

            valid_letters = 'ABC'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            pronouns = [
                858166817938997248, 858166818615197696, 858166819046031381
            ]
            try:
                if pronouns[string.ascii_uppercase.index(
                        msg.content.upper())] in [
                            role.id for role in self.ctx.author.roles
                        ]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(
                            pronouns[string.ascii_uppercase.index(
                                msg.content.upper())]))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(pronouns[string.ascii_uppercase.index(msg.content.upper())]).name}!'
                    )
                    embed = await pronouns_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
            except ValueError:
                pass
            new_role = self.ctx.guild.get_role(
                pronouns[string.ascii_uppercase.index(msg.content.upper())])
            await self.ctx.author.add_roles(new_role)
            await self.ctx.send(f'Successfully added role: {new_role.name}!')

            embed = await pronouns_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            continue

    @discord.ui.button(label='Gaming', style=discord.ButtonStyle.secondary)
    async def gaming(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        await asyncio.sleep(sleep)
        name_colors_locks.add(self.ctx.author)
        school_locks.add(self.ctx.author)
        pronoun_locks.add(self.ctx.author)
        if self.ctx.author in gaming_locks:
            gaming_locks.remove(self.ctx.author)
        else:
            gaming_locks.add(self.ctx.author)
        server_locks.add(self.ctx.author)
        smp_locks.add(self.ctx.author)

        embed = await gaming_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            if self.ctx.author in gaming_locks:
                return

            valid_letters = 'ABCDE'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            gaming = [
                858228412894937109, 858228515455762462, 947794021600870410,
                858228860214312990, 937291486549135390
            ]

            try:
                if gaming[string.ascii_uppercase.index(
                        msg.content.upper())] in [
                            role.id for role in self.ctx.author.roles
                        ]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(
                            gaming[string.ascii_uppercase.index(
                                msg.content.upper())]))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(gaming[string.ascii_uppercase.index(msg.content.upper())]).name}!'
                    )
                    embed = await gaming_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
            except ValueError:
                pass
            new_role = self.ctx.guild.get_role(
                gaming[string.ascii_uppercase.index(msg.content.upper())])
            await self.ctx.author.add_roles(new_role)
            await self.ctx.send(f'Successfully added role: {new_role.name}!')

            embed = await gaming_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            continue

    @discord.ui.button(label='Announcements/Events/and more',
                       style=discord.ButtonStyle.secondary)
    async def server(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        await asyncio.sleep(sleep)
        name_colors_locks.add(self.ctx.author)
        school_locks.add(self.ctx.author)
        pronoun_locks.add(self.ctx.author)
        gaming_locks.add(self.ctx.author)
        if self.ctx.author in server_locks:
            server_locks.remove(self.ctx.author)
        else:
            server_locks.add(self.ctx.author)
        smp_locks.add(self.ctx.author)

        embed = await server_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            if self.ctx.author in server_locks:
                return

            valid_letters = 'ABCDEFGHIJKLMN'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            server = [
                1025751709139619881, 858228825800441896, 858228567762665493,
                1010112913983410197, 1010113161392832543, 1010113746364026900,
                858228627157024780, 1010113868430852218, 960381580617080904,
                858166828194201640, 858228761955008533, 1015233233333538847,
                858166829847543859, 1090514249564033114
            ]
            try:
                if server[string.ascii_uppercase.index(
                        msg.content.upper())] in [
                            role.id for role in self.ctx.author.roles
                        ]:
                    await self.ctx.author.remove_roles(
                        self.ctx.guild.get_role(
                            server[string.ascii_uppercase.index(
                                msg.content.upper())]))
                    await self.ctx.send(
                        f'Successfully removed role: {self.ctx.guild.get_role(server[string.ascii_uppercase.index(msg.content.upper())]).name}!'
                    )
                    embed = await server_embed(self.cog, self.ctx)
                    await temp.edit(embed=embed)
                    continue
            except ValueError:
                pass
            new_role = self.ctx.guild.get_role(
                server[string.ascii_uppercase.index(msg.content.upper())])
            await self.ctx.author.add_roles(new_role)
            await self.ctx.send(f'Successfully added role: {new_role.name}!')

            embed = await server_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            continue

    @discord.ui.button(label='Exit', style=discord.ButtonStyle.danger)
    async def exit(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        name_colors_locks.add(self.ctx.author)
        school_locks.add(self.ctx.author)
        pronoun_locks.add(self.ctx.author)
        gaming_locks.add(self.ctx.author)
        server_locks.add(self.ctx.author)

        embed = await roles_embed()
        await interaction.response.edit_message(embed=embed)


class RoleOrganizer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def update_roles(self, member):
        guild = member.guild
        normal_roles = list(
            filter(lambda r: r.name != '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯',
                   member.roles))[1:]
        organizer_roles = list(
            filter(lambda r: r.name == '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯',
                   member.roles))
        for role in normal_roles:
            # Find the next organizer above the role, and add it to the member
            organizer = discord.utils.find(
                lambda r: r.name == '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯',
                guild.roles[guild.roles.index(role):])
            if organizer not in member.roles and organizer is not None:
                await member.add_roles(organizer)
        for ind, organizer in enumerate(organizer_roles):
            # If the next organizer role is right after the current one, remove the next organizer role
            if ind == len(organizer_roles) - 1:
                break
            if member.roles.index(
                    organizer_roles[ind +
                                    1]) - member.roles.index(organizer) == 1:
                await member.remove_roles(organizer_roles[ind + 1])
        # If the first organizer role is the first role of the member, remove the role
        if member.roles.index(organizer_roles[0]) == 1:
            await member.remove_roles(organizer_roles[0])

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles or after.bot:
            return
        exclusive_roles = [
            1064445950992597042, 1052103824346710056, 858166817145880587,
            957799704660439041, 1044612642599358475, 957803140864950302,
            858222265098174474, 858228707767877632, 1026064526698889286,
            1067326246867980318, 1036568309501526026, 1036842427622903878,
            1063688787722522666, 1055792475245129759, 1058290811835531304,
            1045704861783695450, 1048233290143907900, 1048233980329213983,
            1048234335930683473, 1025730208617201714, 1026791817984876587,
            1025732623143796746, 1025730083207532616, 1025730536297222255,
            999924635648938034, 1025732311888711750, 1025732311888711750,
            1025732311888711750, 1082306933505130546
        ]
        one_at_once = [
            999924337882697728, 999924519592534146, 999924445319798935,
            1025730412003209236, 999924808500379739, 1025732223216914473,
            999924745069936660, 1002843836927721522, 858224685686325268,
            858224260856938518, 858224148248788996, 1039871025845907526,
            1039871059379359774, 1039871334416650320, 1026791699361562684, 
            1014844875058982983, 1039452681888083998, 1014845262734311516
        ]
        one_at_once_groups = [[
            999924337882697728, 999924519592534146, 999924445319798935,
            1025730412003209236, 999924808500379739, 1025732223216914473,
            999924745069936660, 1026791699361562684, 1002843836927721522
        ], [858224685686325268, 858224260856938518, 858224148248788996
            ], [1039871025845907526, 1039871059379359774, 1039871334416650320], [1014844875058982983, 1039452681888083998, 1014845262734311516]]
        added_role = next(
            (role for role in after.roles if role not in before.roles), None)
        hops_dev = after.guild.get_role(934678477825802270)
        if added_role is not None:
            if added_role.id in exclusive_roles or added_role.id in one_at_once:
                entries = [
                    entry async for entry in after.guild.audit_logs(
                        limit=1,
                        action=discord.AuditLogAction.member_role_update)
                ]
                role_entry = next(
                    (entry for entry in entries
                     if (hops_dev in entry.user.roles or entry.user.bot)
                     and entry.target == after), None)
                inventory = await database.get_attribute(
                    self.bot.database, after, 'inventory')
                roles = {
                    'aqua': 1025730208617201714,
                    'lightmaroon': 1026791817984876587,
                    'rosegold': 1025732623143796746,
                    'lightpurple': 1025730083207532616,
                    'lightred': 1025730536297222255,
                    'lightyellow': 999924635648938034,
                    'lightgreen': 1025732311888711750,
                    'darkblue': 1025730320865173635,
                    'lightpink': 1072390959846928494,
                    'legend': 1041704006709411880
                }
                for i in one_at_once_groups:
                    if len(
                            list(
                                filter(
                                    lambda x: x in
                                    [role.id
                                     for role in after.roles], i))) >= 2:
                        await after.remove_roles(added_role)
                if not role_entry and not roles.get(
                        next((item['id'] for item in inventory
                              if item['category'] == 'Name Colors'),
                             None)) in [role.id for role in after.roles]:
                    await after.remove_roles(added_role)
        else:
            removed_role = next(
                (role for role in before.roles if role not in after.roles),
                None)
            if removed_role is None:
                return
            if removed_role.id in exclusive_roles:
                entries = [
                    entry async for entry in after.guild.audit_logs(
                        limit=1,
                        action=discord.AuditLogAction.member_role_update)
                ]
                role_entry = next(
                    (entry for entry in entries
                     if (hops_dev in entry.user.roles or entry.user.bot)
                     and entry.target == after), None)
                if not role_entry:
                    await after.add_roles(removed_role)
        await self.update_roles(after)

    @commands.command()
    async def roles(self, ctx):
        name_colors_locks.add(ctx.author)
        embed = await roles_embed()
        view = DefaultView(self, ctx)
        smp_role = ctx.guild.get_role(1085464616018120744)
        if smp_role in ctx.author.roles:
            view.add_item(SMPButton(label='SMP Roles', cog=self, ctx=ctx))
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(RoleOrganizer(bot))
