import asyncio
import random
import time
import discord
from discord.ext import commands
from assets import database
from assets.connectfour import ConnectFour
from assets.connectfour import ConnectFourAI
from assets.connectfour import Gamemode


class SelectMemberView(discord.ui.View):

    def __init__(self, cog, ctx, timeout=180):
        self.cog = cog
        self.ctx = ctx
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    async def gamemode_selection(self, ctx, member, interaction):
        embed = discord.Embed(
            title=
            f'{ctx.author.display_name} is challenging you to a connect four game!',
            description='Do you accept?',
            color=discord.Colour.random())
        await interaction.response.edit_message(embed=embed)
        to_edit = await interaction.original_response()
        await to_edit.reply(member.mention)
        await to_edit.add_reaction('✅')
        await to_edit.add_reaction('❌')

        def check(r, u):
            return u == member and r.message == to_edit and str(
                r.emoji) in ('✅', '❌')

        reaction, user = await self.cog.bot.wait_for('reaction_add',
                                                     timeout=300,
                                                     check=check)

        if str(reaction.emoji) == '❌':
            return 'refusal'

        await to_edit.clear_reactions()
        embed = discord.Embed(
            title='Select a Gamemode',
            description=
            '**A** ― Normal\n**B** ― Extreme\n**C** ― Invisible\n**D** ― Swiftplay\n\n> Type "**A**", "**B**", "**C**", or "**D**" in chat to select your gamemode.',
            color=discord.Colour.random())
        await to_edit.edit(embed=embed)

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message',
                                              check=check,
                                              timeout=300)

            choices = {
                'a': Gamemode.NORMAL,
                'b': Gamemode.EXTREME,
                'c': Gamemode.INVISIBLE,
                'd': Gamemode.SWIFTPLAY
            }
            if msg.content.lower() not in choices:
                if msg.content.lower() == 'end':
                    return None
                await msg.channel.send('Please select your gamemode.')
                continue
            return choices[msg.content.lower()]

    @discord.ui.select(cls=discord.ui.UserSelect)
    async def select_member(self, interaction: discord.Interaction,
                            select: discord.ui.UserSelect):
        member = select.values[0]
        if member.bot:
            await interaction.response.send_message(
                f'{self.ctx.author.mention}, your opponent cannot be a bot.')
            return
        elif member == self.ctx.author:
            await interaction.response.send_message(
                f'{self.ctx.author.mention}, your opponent cannot be yourself.'
            )
            return
        elif member in self.cog.games:
            await interaction.response.send_message(
                f'{self.ctx.author.mention}, your opponent, {member.display_name}, is currently in another game.'
            )
            return

        gamemode = await self.gamemode_selection(self.ctx, member, interaction)
        if gamemode is None:
            await self.ctx.send(
                f'{self.ctx.author.display_name} and {member.display_name}\'s game has been ended by {self.ctx.author.display_name}'
            )
            return
        elif gamemode == 'refusal':
            await self.ctx.send(
                f'{self.ctx.author.display_name} and {member.display_name}\'s game has been ended by {member.display_name}'
            )
            return

        if gamemode == Gamemode.EXTREME:
            self.cog.colors[self.ctx.author] = ':blue_circle:'
            self.cog.colors[member] = ':yellow_circle:'
            self.cog.hexes[':blue_circle:'] = 0x0000ff
            self.cog.hexes[':yellow_circle:'] = 0xffff00
        else:
            self.cog.colors[self.ctx.author] = ':red_circle:'
            self.cog.colors[member] = ':yellow_circle:'
            self.cog.hexes[':red_circle:'] = 0xff0000
            self.cog.hexes[':yellow_circle:'] = 0xffff00

        if self.ctx.author not in self.cog.games:
            if gamemode in (Gamemode.NORMAL, Gamemode.INVISIBLE,
                            Gamemode.SWIFTPLAY):
                self.cog.games[self.ctx.author] = ConnectFour(
                    '', [self.ctx.author, member])
            elif gamemode == Gamemode.EXTREME:
                self.cog.games[self.ctx.author] = ConnectFour(
                    '', [self.ctx.author, member])
            self.cog.games[self.ctx.author].bot = self.cog.bot
            self.cog.games[self.ctx.author].gamemode = gamemode
            self.cog.games[self.ctx.author].channel = self.ctx.channel
            self.cog.games[member] = self.cog.games[self.ctx.author]
            self.cog.games[member].channel = self.ctx.channel
            self.cog.games[member].gamemode = gamemode
            self.cog.games[self.ctx.author].turn = self.cog.games[
                self.ctx.author].players[0]

            if self.cog.games[self.ctx.author].gamemode == Gamemode.INVISIBLE:
                embed = discord.Embed(
                    title=
                    f'{self.ctx.author.display_name} and {member.display_name}\'s game:',
                    color=self.cog.hexes[self.cog.colors[self.cog.games[
                        self.ctx.author].turn]])
                embed.add_field(name='Game:',
                                value=((':black_large_square:' * 7) + '\n') *
                                6)
            else:
                embed = discord.Embed(
                    title=
                    f'{self.ctx.author.display_name} and {member.display_name}\'s game:',
                    description='',
                    color=self.cog.hexes[self.cog.colors[self.cog.games[
                        self.ctx.author].turn]])
                if self.cog.games[
                        self.ctx.author].gamemode == Gamemode.SWIFTPLAY:
                    embed.description += f'\n**TIME LEFT:** {str(discord.utils.get(self.cog.bot.emojis, name="5secondtimer"))}'
                embed.description += f'🔵 ― {self.cog.games[self.ctx.author].red.mention}\n🟡 ― {self.cog.games[self.ctx.author].yellow.mention}\n\n**Game:**\n{self.cog.games[self.ctx.author].print_board()}'
            embed.set_footer(
                text=f'Move Count: {self.cog.games[self.ctx.author].move_count}'
            )
            await self.ctx.send(
                content=self.cog.games[self.ctx.author].turn.mention,
                embed=embed)

            while True:

                def check(m):
                    return m.author in self.cog.games and self.cog.games[
                        self.ctx.
                        author].turn == m.author and m.channel == self.cog.games[
                            m.author].channel

                try:
                    if self.cog.games[
                            self.ctx.author].gamemode == Gamemode.SWIFTPLAY:
                        msg = await self.cog.bot.wait_for('message',
                                                          check=check,
                                                          timeout=5)
                    else:
                        msg = await self.cog.bot.wait_for('message',
                                                          check=check,
                                                          timeout=300)
                except:
                    if self.cog.games[
                            self.ctx.author].gamemode == Gamemode.SWIFTPLAY:
                        rng = random.randint(100, 200)
                        gem_rng = random.randint(0, 3)
                        embed = discord.Embed(
                            title=
                            f'{self.cog.games[self.ctx.author].players[0].display_name} and {self.cog.games[self.ctx.author].players[1].display_name}\'s game:',
                            description=
                            f'You ran out of time! {self.cog.games[self.ctx.author].players[1]} wins the game!\n{rng:,} :coin: and {gem_rng} :gem: has been added to your account.',
                            color=self.cog.hexes[self.cog.colors[
                                self.cog.games[self.ctx.author].turn]])
                        await self.cog.database_operations(
                            self.cog.games[self.ctx.author].players[1],
                            self.cog.games[self.ctx.author].players[0], rng,
                            'swift')
                        await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                        embed.description += f'Game:\n{self.cog.games[self.ctx.author].print_board()}'
                        await self.ctx.send(embed=embed)
                    temp = self.cog.games[self.ctx.author]
                    gamemode = self.cog.games[self.ctx.author].gamemode
                    loser = temp.players[0]
                    self.cog.games.pop(temp.players[0])
                    self.cog.games.pop(temp.players[1])
                    if gamemode == Gamemode.SWIFTPLAY:

                        def check(m):
                            return m.author.id == loser.id and 'lag' in m.content.lower(
                            )

                        for _ in range(10):
                            try:
                                msg = await self.cog.bot.wait_for('message',
                                                                  check=check,
                                                                  timeout=40)
                            except asyncio.TimeoutError:
                                return
                            else:
                                await msg.channel.send(
                                    'https://media.discordapp.net/attachments/1055814810459193426/1059658024689614928/unknown.png'
                                )
                                return
                    return

                if msg.content in ['1', '2', '3', '4', '5', '6', '7']:
                    if self.cog.games[msg.author].is_full(int(msg.content)):
                        await msg.channel.send(
                            f'{msg.author.mention}, you are not allowed to place anything in that column anymore.'
                        )
                        continue
                    self.cog.games[msg.author].players = self.cog.games[
                        msg.author].players[::-1]
                    self.cog.games[msg.author].turn = self.cog.games[
                        msg.author].players[0]
                    self.cog.games[msg.author].place(
                        int(msg.content), self.cog.colors[msg.author])
                    if self.cog.games[msg.author].win_check(
                            self.cog.colors[msg.author]):
                        rng = random.randint(300, 400)
                        gem_rng = random.randint(0, 5)
                        if self.cog.games[
                                self.ctx.
                                author].gamemode == Gamemode.INVISIBLE:
                            embed = discord.Embed(
                                title=
                                f'{self.ctx.author.display_name} and {member.display_name}\'s game:',
                                description=
                                f'{msg.author.display_name} has **won!**\n{rng:,} :coin: and {gem_rng} :gem: has been added to your account.\n\n**Game:**\n{self.cog.games[self.ctx.author].print_board()}',
                                color=self.cog.hexes[self.cog.colors[
                                    self.cog.games[self.ctx.author].turn]])

                            await self.cog.database_operations(
                                self.cog.games[msg.author].players[1],
                                self.cog.games[msg.author].players[0], rng,
                                'invisible')
                            await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                        elif self.cog.games[
                                self.ctx.author].gamemode == Gamemode.EXTREME:
                            embed = discord.Embed(
                                title=
                                f'{self.ctx.author.display_name} and {member.display_name}\'s game:',
                                description=
                                f'{msg.author.display_name} has **won!**\n{rng:,} :coin: and {gem_rng} :gem: has been added to your account.\n\n**Game:**\n{self.cog.games[self.ctx.author].print_board()}',
                                color=self.cog.hexes[self.cog.colors[
                                    self.cog.games[self.ctx.author].turn]])
                            await self.cog.database_operations(
                                self.cog.games[msg.author].players[1],
                                self.cog.games[msg.author].players[0], rng,
                                'extreme')
                            await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                        else:
                            rng = random.randint(300, 400)
                            gem_rng = random.randint(0, 5)
                            embed = discord.Embed(
                                title=
                                f'{self.ctx.author.display_name} and {member.display_name}\'s game:',
                                description=
                                f'{msg.author.display_name} has **won!**\n{rng:,} :coin: has been added to your account.\n\n**Game:**\n{self.cog.games[self.ctx.author].print_board()}',
                                color=self.cog.hexes[self.cog.colors[
                                    self.cog.games[self.ctx.author].turn]])
                            if self.cog.games[
                                    self.ctx.
                                    author].gamemode == Gamemode.SWIFTPLAY:
                                rng = random.randint(100, 200)
                                gem_rng = random.randint(0, 3)
                                await self.cog.database_operations(
                                    self.cog.games[msg.author].players[1],
                                    self.cog.games[msg.author].players[0], rng,
                                    'swift')
                                await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                            else:
                                await self.cog.database_operations(
                                    self.cog.games[msg.author].players[1],
                                    self.cog.games[msg.author].players[0], rng,
                                    'normal')
                                await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                        await msg.channel.send(embed=embed)

                        temp = self.cog.games[msg.author]
                        self.cog.games.pop(temp.players[0])
                        self.cog.games.pop(temp.players[1])
                        return

                    if self.cog.games[msg.author].all_full():
                        embed = discord.Embed(
                            title=
                            f'{self.cog.games[msg.author].players[0].display_name} and {self.cog.games[msg.author].players[1].display_name}\'s game:',
                            description=
                            f'🔴 ― {self.cog.games[self.ctx.author].red.mention}\n🟡 ― {self.cog.games[self.ctx.author].yellow.mention}\n\nThe game has ended in a tie.',
                            color=self.cog.hexes[self.cog.colors[
                                self.cog.games[self.ctx.author].turn]])
                        embed.description += f'Game:\n{self.cog.games[self.ctx.author].print_board()}'
                        await msg.channel.send(embed=embed)

                        temp = self.cog.games[msg.author]
                        self.cog.games.pop(temp.players[0])
                        self.cog.games.pop(temp.players[1])
                        return

                    embed = discord.Embed(
                        title=
                        f'{self.cog.games[msg.author].players[0].display_name} and {self.cog.games[msg.author].players[1].display_name}\'s game:',
                        color=self.cog.hexes[self.cog.colors[self.cog.games[
                            msg.author].turn]])
                    if self.cog.games[
                            self.ctx.author].gamemode == Gamemode.INVISIBLE:
                        embed.add_field(
                            name='Game:',
                            value=((':black_large_square:' * 7) + '\n') * 6)
                    else:
                        embed.description = f'**Game:**\n{self.cog.games[self.ctx.author].print_board()}'
                    embed.set_footer(
                        text=
                        f'Move Count: {self.cog.games[self.ctx.author].move_count}'
                    )
                    if self.cog.games[
                            self.ctx.author].gamemode == Gamemode.SWIFTPLAY:
                        embed.description = f'**TIME LEFT:** {str(discord.utils.get(self.cog.bot.emojis, name="5secondtimer"))}'
                        explosion_event = await msg.channel.send(
                            content=
                            f'{self.cog.games[msg.author].turn.mention}',
                            embed=embed)
                    else:
                        explosion_event = await msg.channel.send(
                            content=self.cog.games[msg.author].turn.mention,
                            embed=embed)
                    if self.cog.games[msg.author].gamemode == Gamemode.EXTREME:
                        if time.time() - self.cog.games[msg.author].last > 60:
                            rng = random.randint(1, 125)
                            if self.cog.games[msg.author].guaranteed:
                                rng = 1
                            if rng in range(1, 101):
                                coords_list = [
                                    self.cog.games[
                                        msg.author].extreme_explosion()
                                ]
                                if self.cog.games[msg.author].guaranteed:
                                    coords_list.append(self.cog.games[
                                        msg.author].extreme_explosion())
                                embed.description = f'**Game:**\n{self.cog.games[self.ctx.author].print_board()}'
                                await explosion_event.edit(embed=embed)
                                await asyncio.sleep(4.8)
                                for coord in coords_list:
                                    self.cog.games[msg.author].extreme_petrify(
                                        coord)
                                embed.description = f'**Game:**\n{self.cog.games[self.ctx.author].print_board()}'
                                await explosion_event.edit(embed=embed)
                                self.cog.games[msg.author].guaranteed = False
                            else:
                                self.cog.games[msg.author].guaranteed = True
                            self.cog.games[
                                msg.author].last = time.time() + 28800
                elif msg.content.lower(
                ) in ('forfeit', 'resign',
                      'mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry.'
                      .lower()):
                    if self.cog.games[
                            self.ctx.author].gamemode == Gamemode.SWIFTPLAY:
                        rng = random.randint(100, 200)
                        gem_rng = random.randint(0, 3)
                    else:
                        rng = random.randint(300, 400)
                        gem_rng = random.randint(0, 5)
                    if self.cog.games[
                            self.ctx.author].gamemode == Gamemode.INVISIBLE:
                        embed = discord.Embed(
                            title=
                            f'{self.cog.games[msg.author].players[0].display_name} and {self.cog.games[msg.author].players[1].display_name}\'s game:',
                            description=
                            f'🔴 ― {self.cog.games[self.ctx.author].red.mention}\n🟡 ― {self.cog.games[self.ctx.author].yellow.mention}\n\n{self.cog.games[msg.author].players[1].display_name} has **won!**\n{rng:,} :coin: and {gem_rng} :gem: has been added to your account.',
                            color=self.cog.hexes[self.cog.colors[
                                self.cog.games[self.ctx.author].turn]])
                        embed.add_field(name='Game:',
                                        value=self.cog.games[
                                            self.ctx.author].print_board())
                        await self.cog.database_operations(
                            self.cog.games[msg.author].players[1],
                            self.cog.games[msg.author].players[0], rng,
                            'invisible')
                        await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                    elif self.cog.games[
                            self.ctx.author].gamemode == Gamemode.EXTREME:
                        embed = discord.Embed(
                            title=
                            f'{self.ctx.author.display_name} and {member.display_name}\'s game:',
                            description=
                            f'{self.cog.games[msg.author].players[1].display_name} has **won!**\n{rng:,} :coin: and {gem_rng} :gem: has been added to your account.\n\n**Game:**\n{self.cog.games[self.ctx.author].print_board()}',
                            color=self.cog.hexes[self.cog.colors[
                                self.cog.games[self.ctx.author].turn]])
                        await self.cog.database_operations(
                            self.cog.games[msg.author].players[1],
                            self.cog.games[msg.author].players[0], rng,
                            'extreme')
                        await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                    else:
                        embed = discord.Embed(
                            title=
                            f'{self.ctx.author.display_name} and {member.display_name}\'s game:',
                            description=
                            f'{self.cog.games[msg.author].players[1].display_name} has **won!**\n{rng:,} :coin: and {gem_rng} :gem: has been added to your account.\n\n**Game:**\n{self.cog.games[self.ctx.author].print_board()}',
                            color=self.cog.hexes[self.cog.colors[
                                self.cog.games[self.ctx.author].turn]])
                        if self.cog.games[
                                self.ctx.
                                author].gamemode == Gamemode.SWIFTPLAY:
                            await self.cog.database_operations(
                                self.cog.games[msg.author].players[1],
                                self.cog.games[msg.author].players[0], rng,
                                'swift')
                            await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                        else:
                            await self.cog.database_operations(
                                self.cog.games[msg.author].players[1],
                                self.cog.games[msg.author].players[0], rng,
                                'normal')
                            await database.set_gems(self.cog.bot.database, self.cog.games[self.ctx.author].players[1], gem_rng)
                    await msg.channel.send(embed=embed)

                    temp = self.cog.games[msg.author]
                    self.cog.games.pop(temp.players[0])
                    self.cog.games.pop(temp.players[1])
                    return
                elif msg.content not in [
                        '1', '2', '3', '4', '5', '6', '7'
                ] and self.cog.games[
                        msg.author].turn == msg.author and self.cog.games[
                            msg.author].channel == msg.channel:
                    await msg.channel.send(
                        f'{msg.author.mention}, please type anything from 1 to 7.'
                    )
                    continue


class RelationshipStatusView(discord.ui.View):

    def __init__(self, cog, ctx, embed, timeout=180):
        self.cog = cog
        self.ctx = ctx
        self.embed = embed
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Singleplayer",
                       style=discord.ButtonStyle.secondary)
    async def single(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        embed = discord.Embed(title='Select a Difficulty',
                              color=discord.Color.fuchsia())
        embed.description = '**A** ― Easy\n**B** ― Normal\n**C** ― Medium\n**D** ― Hard\n**E** ― Expert\n**F** ― Impossible\n\n> Type "**A**", "**B**", "**C**", "**D**", "**E**", or "**F**" in chat to select your difficulty.'
        await interaction.response.edit_message(embed=embed, view=None)

        while True:

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            msg = await self.cog.bot.wait_for('message',
                                              check=check,
                                              timeout=300)
            difficulty = msg.content

            if self.ctx.author not in self.cog.aigames:
                if difficulty.lower() in ('antonio', 'easy', 'one', '1', "a"):
                    difficulty = 1
                elif difficulty.lower() in ('charles', 'normal', 'two', '2',
                                            "b"):
                    difficulty = 2
                elif difficulty.lower() in ('reily', 'medium', 'three', '3',
                                            "c"):
                    difficulty = 3
                elif difficulty.lower() in ('seth', 'hard', 'four', '4', "d"):
                    difficulty = 4
                elif difficulty.lower() in ('joyce lu', 'expert', 'five', '5',
                                            "e"):
                    difficulty = 5
                elif difficulty.lower() in ('gmf', 'impossible', 'six', '6',
                                            "f"):
                    difficulty = 6
                else:
                    await self.ctx.send('Please select a valid difficulty.')
                    continue
                break

        if self.ctx.author not in self.cog.aigames:
            game_theme = await database.get_settings(self.cog.bot.database,
                                                     self.ctx.author,
                                                     'c4gametheme')
            theme_map = {
                'Default': ':blue_square:',
                'Sakura': '<:THEME_sakura:1065929561419825162>',
                'Pink-Blue': '<a:THEME_colorful:1065931156685606973>',
                'Anika In Space': '<:THEME_anika:1073873897360982076>',
                'Galaxy': '<:THEME_galaxy:1073875133925699624>',
                'Charles': '<:THEME_charles:1073876973824266351>'
            }
            self.cog.aigames[self.ctx.author] = ConnectFourAI(
                theme_map[game_theme], difficulty)
            self.cog.aigames[self.ctx.author].bot = self.cog.bot
            self.cog.aigames[self.ctx.author].channel = self.ctx.channel
            self.cog.aigames[self.ctx.author].user = self.ctx.author
            self.cog.aigames[self.ctx.author].turn = self.ctx.author

            embed = discord.Embed(
                title=f'{self.ctx.author.display_name}\'s AI game:',
                description=
                f'🔴 ― {self.ctx.author.mention}\n🟡 ― AI\n\n Game:\n{self.cog.aigames[self.ctx.author].print_board()}',
                color=0xff0000)
            if self.cog.aigames[self.ctx.author].difficulty == 6:
                embed.set_footer(text='Difficulty: Impossible (6)')
            if self.cog.aigames[self.ctx.author].difficulty == 7:
                embed.set_footer(text='Difficulty: 7 (Experimental!)')
            else:
                difficulty_mapping = {
                    1: 'Easy',
                    2: 'Normal',
                    3: 'Medium',
                    4: 'Hard',
                    5: 'Expert',
                    6: 'Impossible'
                }
                embed.set_footer(
                    text=
                    f'Difficulty: {difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty]}'
                )
            await self.ctx.send(
                content=self.cog.aigames[self.ctx.author].turn.mention,
                embed=embed)

        while True:

            def check(m):
                return m.author in self.cog.aigames and m.channel == self.cog.aigames[
                    m.author].channel and self.cog.aigames[
                        self.ctx.author].turn == m.author

            try:
                msg = await self.cog.bot.wait_for('message',
                                                  check=check,
                                                  timeout=300)
            except:
                self.cog.aigames.pop(msg.author)
                return

            if msg.content in ['1', '2', '3', '4', '5', '6', '7']:
                if self.cog.aigames[msg.author].is_full(int(msg.content)):
                    await msg.channel.send(
                        f'{msg.author.mention}, you are not allowed to place anything in that column anymore.'
                    )
                    continue
                mover = 'player'
                self.cog.aigames[msg.author].turn = None
                self.cog.aigames[msg.author].place(int(msg.content), 1)

                if self.cog.aigames[msg.author].win_check(1):
                    if difficulty == 1:
                      coins = random.randint(0, 10)
                      gems = 0
                    elif difficulty == 2:
                      coins = random.randint(10, 15)
                      gems = 0
                    elif difficulty == 3:
                      coins = random.randint(20, 30)
                      gems = 0
                    elif difficulty == 4:
                      coins = random.randint(50, 60)
                      gems = 0  
                    elif difficulty == 5:
                      coins = random.randint(100, 200)
                      gems = random.randint(0, 5)
                    elif difficulty == 6:
                      coins = random.randint(200, 400)
                      gems = random.randint(0, 10)
                    coin_text = ''
                    gem_text = ''
                    if coins > 0:
                      coin_text += f'\n{coins} :coin: has been added to your account.'
                    if gems > 0:
                      gem_text += f'\n{gems} :gem: has been added to your account.'
                    embed = discord.Embed(
                        title=f'{msg.author.display_name}\'s game:',
                        description=
                        f'{msg.author.display_name} has **won!**{coin_text}{gem_text}\n\nGame:\n{self.cog.aigames[self.ctx.author].print_board()}',
                        color=0xff0000)
                    await msg.channel.send(embed=embed)
                    difficulty_mapping = {
                        1: 'Easy',
                        2: 'Normal',
                        3: 'Medium',
                        4: 'Hard',
                        5: 'Expert',
                        6: 'Impossible'
                    } 
                    diff = f'{difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty].lower()}_ai_count'
                    diff_win = f'{difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty].lower()}_ai_win'
                    diff_streak = f'{diff_win}_streak'
                    await database.set_attribute(self.cog.bot.database, msg.author, 1, diff)
                    await database.set_attribute(self.cog.bot.database, msg.author, 1, diff_win)
                    await database.set_attribute(self.cog.bot.database, msg.author, 1, diff_streak)
                    await database.set_coins(self.cog.bot.database, msg.author, coins)
                    await database.set_attribute(self.cog.bot.database, msg.author, coins, 'ai_coin_count')
                    await database.set_attribute(self.cog.bot.database, msg.author, gems, 'ai_gem_count') 
                    await database.set_gems(self.cog.bot.database, msg.author, gems)

                    self.cog.aigames.pop(msg.author)
                    return

                if self.cog.aigames[msg.author].all_full():
                    embed = discord.Embed(
                        title=f'{msg.author.display_name}\'s game:',
                        description=
                        f'🔴 ― {msg.author.display_name}\n🟡 ― AI\nThe game has ended in a tie.\n\nGame:\n{self.cog.aigames[self.ctx.author].print_board()}',
                        color=0xff0000)
                    await msg.channel.send(embed=embed)

                    self.cog.aigames.pop(msg.author)
                    return

                if self.cog.aigames[msg.author].difficulty >= 5:
                    message = await self.ctx.send(
                        '**The AI is thinking...**\n> Other commands may not respond.'
                    )
                else:
                    message = None
                mover = 'ai'
                col = self.cog.aigames[msg.author].ai_place()
                self.cog.aigames[msg.author].place(col + 1, 2)

                if self.cog.aigames[msg.author].win_check(2):
                    embed = discord.Embed(
                        title=f'{msg.author.display_name}\'s game:',
                        description=
                        f'> The AI placed on column {col + 1} and has **won!**\n\nGame:\n{self.cog.aigames[self.ctx.author].print_board()}',
                        color=0xff0000)
                    diff = f'{difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty].lower()}_ai_count'
                    diff_streak = f'{difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty].lower()}_ai_win_streak'
                    await database.set_attribute(self.cog.bot.database, msg.author, 1, diff)
                    await database.set_attribute(self.cog.bot.database, msg.author, 0, diff_streak, increment=False)
                    if message is None:
                        await msg.channel.send(embed=embed)
                    else:
                        await message.edit(content='', embed=embed)

                    self.cog.aigames.pop(msg.author)
                    return

                if self.cog.aigames[msg.author].all_full():
                    embed = discord.Embed(
                        title=f'{msg.author.display_name}\'s game:',
                        description=
                        f'🔴 ― {msg.author.display_name}\n🟡 ― AI\nThe game has ended in a tie.\n\nGame:\n{self.cog.aigames[self.ctx.author].print_board()}',
                        color=0xff0000)
                    diff = f'{difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty].lower()}_ai_count'
                    await database.set_attribute(self.cog.bot.database, msg.author, 1, diff)
                    if message is None:
                        await msg.channel.send(embed=embed)
                    else:
                        await message.edit(content='', embed=embed)

                    self.cog.aigames.pop(msg.author)
                    return

                self.cog.aigames[msg.author].turn = msg.author
            elif msg.content.lower(
            ) in ('forfeit', 'resign',
                  'mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry. mommy? sorry.'
                  ):
                embed = discord.Embed(
                    title=f'{msg.author.display_name}\'s game:',
                    description=
                    f'> The AI has **won!**\n\nGame:\n{self.cog.aigames[self.ctx.author].print_board()}',
                    color=0xff0000)
                await msg.channel.send(embed=embed)
                diff = f'{difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty].lower()}_ai_count'
                diff_streak = f'{difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty].lower()}_ai_win_streak'
                await database.set_attribute(self.cog.bot.database, msg.author, 1, diff)
                await database.set_attribute(self.cog.bot.database, msg.author, 0, diff_streak, increment=False)

                self.cog.aigames.pop(msg.author)
                return
            elif msg.content not in [
                    '1', '2', '3', '4', '5', '6', '7'
            ] and self.cog.aigames[
                    msg.author].turn == msg.author and self.cog.aigames[
                        msg.author].channel == msg.channel:
                await msg.channel.send(
                    f'{msg.author.mention}, please type anything from 1 to 7.')
                continue

            if mover == 'player':
                color = 0xff0000
            else:
                color = 0xffff00
            embed = discord.Embed(
                title=f'{msg.author.display_name}\'s game:',
                description=
                f'> The AI placed on column {col + 1}.\n\nGame:\n{self.cog.aigames[self.ctx.author].print_board()}',
                color=color)
            difficulty_mapping = {
                1: 'Easy',
                2: 'Normal',
                3: 'Medium',
                4: 'Hard',
                5: 'Expert',
                6: 'Impossible'
            }
            embed.set_footer(
                text=
                f'Difficulty: {difficulty_mapping[self.cog.aigames[self.ctx.author].difficulty]}'
            )
            if message is None:
                await msg.channel.send(content=msg.author.mention, embed=embed)
            else:
                await message.edit(content=msg.author.mention, embed=embed)

    @discord.ui.button(label="Multiplayer",
                       style=discord.ButtonStyle.secondary)
    async def multi(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        embed = self.embed
        embed.description = 'Select your opponent.'
        await interaction.response.edit_message(embed=embed,
                                                view=SelectMemberView(
                                                    self.cog, self.ctx))


class Minigames(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.colors = {}
        self.hexes = {}
        self.coinflips = []
        self.aigames = {}

    async def database_operations(self, winner, loser, rng, gamemode):
        await database.set_attribute(self.bot.database, winner, 1,
                                     f'{gamemode}_c4_win_count')
        await database.set_attribute(self.bot.database, winner, 1,
                                     f'{gamemode}_c4_win_streak')
        await database.set_attribute(self.bot.database, winner, rng,
                                     f'{gamemode}_c4_coin_count')
        await database.set_attribute(self.bot.database,
                                     loser,
                                     0,
                                     f'{gamemode}_c4_win_streak',
                                     increment=False)
        if gamemode == 'swift':
            await database.set_xp(self.bot.database, winner, 20)
            await database.set_xp(self.bot.database, loser, 15)
        else:
            await database.set_xp(self.bot.database, winner, 50)
            await database.set_xp(self.bot.database, loser, 30)
        await database.set_coins(self.bot.database, winner, rng)
        await database.set_attribute(self.bot.database, loser, 1,
                                     f'{gamemode}_c4_count')
        await database.set_attribute(self.bot.database, winner, 1,
                                     f'{gamemode}_c4_count')
        await database.set_attribute(self.bot.database, winner, 1,
                                     'command_count')
        await database.set_attribute(self.bot.database, loser, 1,
                                     'command_count')

    async def bet_selection(self, ctx, member):
        while True:
            await ctx.send(
                f'How much would you want to bet, {member.display_name}?')

            def check(m):
                return m.author == member and m.channel == ctx.channel and member in self.coinflips

            try:
                msg = await self.bot.wait_for('message',
                                              check=check,
                                              timeout=300)
            except asyncio.TimeoutError:
                self.coinflips.remove(ctx.author)
                self.coinflips.remove(member)
                return

            try:
                bet = int(msg.content)
                assert bet > 0
            except (ValueError, AssertionError):
                if msg.content.lower() == 'end':
                    return None
                else:
                    await msg.channel.send('You need to bet a valid amount!')
                    continue
            else:
                coin_amount = await database.get_attribute(
                    self.bot.database, member, 'coins')
                if bet > coin_amount:
                    await msg.channel.send(
                        'You don\'t have enough coins on your balance to bet this amount.'
                    )
                    continue
                elif bet > 2500:
                    await msg.channel.send('You cannot bet over 2500 coins.')
                    continue
                else:
                    return bet

    @commands.command(aliases=('connect4', 'c4'))
    async def connectfour(self, ctx):
        embed = discord.Embed(
            title='Connect Four: Gamemode Selection',
            description=
            'Select a gamemode by clicking on the buttons below. Click on singleplayer if you want to compete against an AI and click on multiplayer if you want to compete against others.',
            color=discord.Color.random())
        await ctx.send(embed=embed,
                       view=RelationshipStatusView(self, ctx, embed))

    @commands.command(aliases=('cf', 'candace', 'coinfuck'))  #LOL
    async def coinflip(self, ctx, member: discord.Member):
        if ctx.channel.id not in (994580160219201606, 994580255446671371,
                                  994580274216181810):
            await ctx.send(
                '> To lessen the spam, minigame commands have been **disabled** in this channel. Please try it in a bot channel.'
            )
            return
        if member.bot:
            await ctx.send(
                f'{ctx.author.mention}, the right command is \"j.cf {{your opponent}}.\"'
            )
            return
        elif member == ctx.author:
            await ctx.send(
                f'{ctx.author.mention}, your opponent cannot be yourself.')
            return
        elif member in self.coinflips:
            await ctx.send(
                f'{ctx.author.mention}, your opponent, {member.display_name}, is currently in another game.'
            )
            return

        embed = discord.Embed(
            title=
            f'{ctx.author.display_name} is challenging you to a coinflip game!',
            description='Do you accept?',
            color=discord.Colour.random())
        to_edit = await ctx.send(embed=embed)
        await to_edit.add_reaction('✅')
        await to_edit.add_reaction('❌')

        def check(r, u):
            return u == member and r.message == to_edit and str(
                r.emoji) in ('✅', '❌')

        reaction, user = await self.bot.wait_for('reaction_add',
                                                 timeout=300,
                                                 check=check)
        if str(reaction.emoji) == '❌':
            await ctx.send(
                f'{ctx.author.display_name} and {member.display_name}\'s game has been ended by {ctx.author.display_name}'
            )
            return

        self.coinflips.append(ctx.author)
        self.coinflips.append(member)

        bet1 = await self.bet_selection(ctx, ctx.author)
        if bet1 is None:
            await ctx.send(
                f'{ctx.author.display_name} and {member.display_name}\'s game has been ended by {ctx.author.display_name}'
            )
            self.coinflips.remove(ctx.author)
            self.coinflips.remove(member)
            return
        bet2 = await self.bet_selection(ctx, member)
        if bet2 is None:
            await ctx.send(
                f'{ctx.author.display_name} and {member.display_name}\'s game has been ended by {member.display_name}'
            )
            self.coinflips.remove(ctx.author)
            self.coinflips.remove(member)
            return

        while True:
            await ctx.send(
                f'What do you predict it will land on, {ctx.author.display_name}?'
            )

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.author in self.coinflips

            try:
                msg = await self.bot.wait_for('message',
                                              check=check,
                                              timeout=300)
            except asyncio.TimeoutError:
                self.coinflips.remove(ctx.author)
                self.coinflips.remove(member)
                return

            if msg.content.lower() not in ('heads', 'tails'):
                await msg.channel.send('Please pick "Heads" or "Tails" only.')
            elif msg.content.lower() == 'end':
                await msg.channel.send(
                    f'{ctx.author.display_name} and {member.display_name}\'s game has been ended by {msg.author.display_name}'
                )
                self.coinflips.remove(ctx.author)
                self.coinflips.remove(member)
                return
            else:
                choice = msg.content.lower()
                break

        embed = discord.Embed(
            title='Coin Flip',
            description=
            ':coin: **Are you ready?**\nClick on the :white_check_mark: when you are ready to start, and click on the :x: to cancel.',
            color=0xffd580)
        to_react = await ctx.send(embed=embed)
        await to_react.add_reaction('✅')
        await to_react.add_reaction('❌')

        while True:

            def check(r, u):
                return u in (ctx.author, member) and r.message == to_react

            try:
                reaction, user = await self.bot.wait_for('reaction_add',
                                                         timeout=300,
                                                         check=check)
            except asyncio.TimeoutError:
                self.coinflips.remove(ctx.author)
                self.coinflips.remove(member)
                return

            reaction_list = [user async for user in reaction.users()]
            if str(reaction.emoji) == '❌':
                await msg.channel.send(
                    f'{ctx.author.display_name} and {member.display_name}\'s game has been ended by {msg.author.display_name}'
                )
                self.coinflips.remove(ctx.author)
                self.coinflips.remove(member)
                return
            if ctx.author in reaction_list and member in reaction_list and str(
                    reaction.emoji) == '✅':
                break
            else:
                continue

        coin_flip_result = random.choice(('heads', 'tails'))
        if choice == coin_flip_result:
            winner, loser = ctx.author, member
            losing_bet = bet2
        else:
            winner, loser = member, ctx.author
            losing_bet = bet1
        embed.description = f':coin: It landed on **{coin_flip_result}**!\n{winner.mention} has won the bet! {losing_bet:,} coins has been added to your account!'

        if not winner.bot:
            await database.set_coins(self.bot.database, winner, losing_bet)
            await database.set_attribute(self.bot.database, winner, losing_bet,
                                         'cf_coin_count')
            await database.set_attribute(self.bot.database, winner, 1,
                                         'cf_win_count')
        if not loser.bot:
            await database.set_coins(self.bot.database, loser, losing_bet * -1)
        total_winner_coins = await database.get_attribute(
            self.bot.database, winner, 'coins')
        embed.description += f'\nYou now have a total of {total_winner_coins:,} :coin: coins.'
        await to_react.edit(embed=embed)

        self.coinflips.remove(winner)
        self.coinflips.remove(loser)
        await database.set_attribute(self.bot.database, winner, 1, 'cf_count')
        await database.set_attribute(self.bot.database, winner, 1,
                                     'cf_win_count')
        await database.set_attribute(self.bot.database, winner, 1,
                                     'cf_win_streak')
        await database.set_attribute(self.bot.database, winner, 1,
                                     'command_count')
        await database.set_xp(self.bot.database, winner, 20)
        await database.set_attribute(self.bot.database, loser, 1, 'cf_count')
        await database.set_attribute(self.bot.database,
                                     loser,
                                     0,
                                     'cf_win_streak',
                                     increment=False)
        await database.set_attribute(self.bot.database, loser, 1,
                                     'command_count')
        await database.set_xp(self.bot.database, loser, 15)


async def setup(bot):
    await bot.add_cog(Minigames(bot))
