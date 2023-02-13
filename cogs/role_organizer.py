from discord.ext import commands
from assets import database
import discord
import datetime
import string

locks = {
    'name_colors': [],
    'school_roles': [],
    'pronouns': [],
    'gaming': [],
    'server': []
}


async def roles_embed():
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now())
    embed.description = '__**Select a category:**__\n> Click on a button below to select the category you want to configure.'
    return embed


async def name_colors_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now())

    colors = [
        999924337882697728, 999924519592534146, 999924445319798935,
        1025730412003209236, 999924808500379739, 1025732223216914473,
        999924745069936660, 1002843836927721522
    ]
    current_role = next(
        (item
         for item in [role.id for role in ctx.author.roles] if item in colors),
        None)
    role_string = f'<@&{current_role}>'
    if current_role == 1002843836927721522:
        role_string = '<@&1002843836927721522> (Default)'
    embed.description = f'__**Editing Name Colors**__\n**Currently using**: {role_string}\n\n**A** ― <@&999924337882697728>\n**B** ― <@&999924519592534146>\n**C** ― <@&999924445319798935>\n**D** ― <@&1025730412003209236>\n**E** ― <@&999924808500379739>\n**F** ― <@&1025732223216914473>\n**G** ― <@&999924745069936660>\n**H** ― <@&1002843836927721522>\n'

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
        'legend': 1041704006709411880
    }
    inventory_roles = [
        roles.get(id)
        for id in filter(lambda item: item['id'] in roles, inventory)
    ]
    for ind, role in enumerate(inventory_roles):
        embed.description += f'**{string.ascii_uppercase[8:][ind]}** ― <@&{role}>\n'

    embed.description += '\n> To change the name color you are currently using, type and send the letter of the name color you want. Note that you can only have ONE color at once. Selecting another one will change the current one you\'re using.'
    return embed


async def school_roles_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now())
    embed.description = '**__Editing Section/Honors Class/Special PE__**\n\nSections: (You can only have 1 Section role)\n\n'

    sections = [858224685686325268, 858224260856938518, 858224148248788996]
    honors_class = [1027097851119013908, 1044512060379254805]
    special_pe = [
        1039871025845907526, 1039871059379359774, 1039871334416650320
    ]

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

    embed.description += '\n**Special PE**: (You can only have 1 Special PE role)**:\n'
    for ind, role in enumerate(special_pe):
        embed.description += f'{string.ascii_uppercase[5:][ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'

    embed.description += '> To add Section/Honors Class/Special PE roles, type and send the letter of the Section/Honors Class/Special PE roles you want. Note that Sections and Special PE roles can only have ONE role at once. Selecting another one will change the current one you\'re using.'
    return embed


async def pronouns_embed(cog, ctx):
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now())
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
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now())
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
    embed = discord.Embed(title='Roles', timestamp=datetime.datetime.now())
    embed.description = '**__Editing Announcements/Events/and more__**\n'

    server = [
        1025751709139619881, 858228825800441896, 858228567762665493,
        1010112913983410197, 1010113161392832543, 1010113746364026900,
        858228627157024780, 1010113868430852218, 960381580617080904,
        858166828194201640, 858228761955008533, 1015233233333538847,
        858166829847543859
    ]
    for ind, role in enumerate(server):
        embed.description += f'{string.ascii_uppercase[ind]} ― <@&{role}>'
        if role in [r.id for r in ctx.author.roles]:
            embed.description += ' **CURRENTLY USING**'
        embed.description += '\n'

    embed.description += '> To add these roles, type and send the letter of the roles you want.'
    return embed


class DefaultView(discord.ui.View):

    def __init__(self, cog, ctx, timeout=180):
        self.cog = cog
        self.ctx = ctx
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Name Colors',
                       style=discord.ButtonStyle.secondary)
    async def name_colors(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        embed = await name_colors_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            valid_letters = 'ABCDEFGH'
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
                'legend': 1041704006709411880
            }
            inventory_roles = [
                roles.get(id)
                for id in filter(lambda item: item['id'] in roles, inventory)
            ]
            for ind, role in enumerate(inventory_roles):
                valid_letters += string.ascii_uppercase[7:][ind]
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            colors = [
                999924337882697728, 999924519592534146, 999924445319798935,
                1025730412003209236, 999924808500379739, 1025732223216914473,
                999924745069936660, 1002843836927721522
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
            return

    @discord.ui.button(label='Section/Honors Class/Special PE',
                       style=discord.ButtonStyle.secondary)
    async def school_roles(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        embed = await school_roles_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            valid_letters = 'ABCDEFGH'
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
            all_roles = sections + honors_class + special_pe
            current_role = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in all_roles), None)
            if msg.content.upper() == string.ascii_uppercase[
                    all_roles.index(current_role)]:
                await self.ctx.author.remove_roles(
                    self.ctx.guild.get_role(current_role))
                await self.ctx.send(
                    f'Successfully removed role: {self.ctx.guild.get_role(current_role).name}!'
                )
            elif string.ascii_uppercase.index(
                    msg.content.upper()) < 3 or string.ascii_uppercase.index(
                        msg.content.upper()) > 4:
                new_role = self.ctx.guild.get_role(
                    all_roles[string.ascii_uppercase.index(
                        msg.content.upper())])
                await self.ctx.author.remove_roles(
                    self.ctx.guild.get_role(current_role))
                await self.ctx.author.add_roles(new_role)
                if current_role in sections:
                    category = 'Section'
                elif current_role in honors_class:
                    category = 'Honors Class'
                elif current_role in special_pe:
                    category = 'Special PE'
                await self.ctx.send(
                    f'Successfully changed your {category} to {new_role.name}!'
                )
            else:
                new_role = self.ctx.guild.get_role(
                    all_roles[string.ascii_uppercase.index(
                        msg.content.upper())])
                await self.ctx.author.add_roles(new_role)
                await self.ctx.send(
                    f'Successfully added role: {new_role.name}!')

            embed = await school_roles_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            return

    @discord.ui.button(label='Pronouns', style=discord.ButtonStyle.secondary)
    async def pronouns(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        embed = await pronouns_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            valid_letters = 'ABC'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            pronouns = [
                858166817938997248, 858166818615197696, 858166819046031381
            ]
            current_role = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in pronouns), None)

            if msg.content.upper() == string.ascii_uppercase[
                    pronouns.index(current_role)]:
                await self.ctx.author.remove_roles(
                    self.ctx.guild.get_role(current_role))
                await self.ctx.send(
                    f'Successfully removed role: {self.ctx.guild.get_role(current_role).name}!'
                )
            else:
                new_role = self.ctx.guild.get_role(
                    pronouns[string.ascii_uppercase.index(
                        msg.content.upper())])
                await self.ctx.author.add_roles(new_role)
                await self.ctx.send(
                    f'Successfully added role: {new_role.name}!')

            embed = await pronouns_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            return

    @discord.ui.button(label='Gaming', style=discord.ButtonStyle.secondary)
    async def gaming(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        embed = await gaming_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            valid_letters = 'ABCDE'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            gaming = [
                858228412894937109, 858228515455762462, 947794021600870410,
                858228860214312990, 937291486549135390
            ]
            current_role = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in gaming), None)

            if msg.content.upper() == string.ascii_uppercase[
                    gaming.index(current_role)]:
                await self.ctx.author.remove_roles(
                    self.ctx.guild.get_role(current_role))
                await self.ctx.send(
                    f'Successfully removed role: {self.ctx.guild.get_role(current_role).name}!'
                )
            else:
                new_role = self.ctx.guild.get_role(
                    gaming[string.ascii_uppercase.index(msg.content.upper())])
                await self.ctx.author.add_roles(new_role)
                await self.ctx.send(
                    f'Successfully added role: {new_role.name}!')

            embed = await gaming_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            return

    @discord.ui.button(label='Announcements/Events/and more',
                       style=discord.ButtonStyle.secondary)
    async def server(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        embed = await server_embed(self.cog, self.ctx)
        await interaction.response.edit_message(embed=embed)
        temp = await interaction.original_response()

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message', check=check)

            valid_letters = 'ABCDEFGHIJKLM'
            if msg.content.upper() not in valid_letters:
                await self.ctx.send('Please send a valid option.')
                continue

            server = [
                1025751709139619881, 858228825800441896, 858228567762665493,
                1010112913983410197, 1010113161392832543, 1010113746364026900,
                858228627157024780, 1010113868430852218, 960381580617080904,
                858166828194201640, 858228761955008533, 1015233233333538847,
                858166829847543859
            ]
            current_role = next(
                (item for item in [role.id for role in self.ctx.author.roles]
                 if item in server), None)

            if msg.content.upper() == server.index(current_role):
                await self.ctx.author.remove_roles(
                    self.ctx.guild.get_role(current_role))
                await self.ctx.send(
                    f'Successfully removed role: {self.ctx.guild.get_role(current_role).name}!'
                )
            else:
                new_role = self.ctx.guild.get_role(
                    server[string.ascii_uppercase.index(msg.content.upper())])
                await self.ctx.author.add_roles(new_role)
                await self.ctx.send(
                    f'Successfully added role: {new_role.name}!')

            embed = await server_embed(self.cog, self.ctx)
            await temp.edit(embed=embed)
            return


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
            1025732311888711750
        ]
        one_at_once = [
            999924337882697728, 999924519592534146, 999924445319798935,
            1025730412003209236, 999924808500379739, 1025732223216914473,
            999924745069936660, 1002843836927721522, 858224685686325268,
            858224260856938518, 858224148248788996, 1039871025845907526,
            1039871059379359774, 1039871334416650320
        ]
        one_at_once_groups = [[
            999924337882697728, 999924519592534146, 999924445319798935,
            1025730412003209236, 999924808500379739, 1025732223216914473,
            999924745069936660, 1002843836927721522
        ], [858224685686325268, 858224260856938518, 858224148248788996
            ], [1039871025845907526, 1039871059379359774, 1039871334416650320]]
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
        embed = await roles_embed()
        await ctx.send(embed=embed, view=DefaultView(self, ctx))


async def setup(bot):
    await bot.add_cog(RoleOrganizer(bot))
