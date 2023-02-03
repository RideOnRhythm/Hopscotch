import asyncio
import time
from assets import database
import discord
from discord.ext import commands
from assets.connectfour import ConnectFour
from assets.connectfour import ConnectFourAI
from assets.connectfour import Gamemode
import random


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
    await database.set_attribute(self.bot.database, winner, rng,
                                 f'{gamemode}_c4_coin_count')
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
    await database.set_attribute(self.bot.database, winner, 1, 'command_count')
    await database.set_attribute(self.bot.database, loser, 1, 'command_count')

  async def gamemode_selection(self, ctx, member):
    embed = discord.Embed(
      title=
      f'{ctx.author.display_name} is challenging you to a connect four game!',
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
      return 'refusal'

    embed = discord.Embed(
      title='Select a Gamemode',
      description=
      'A - Normal\nB - Extreme\nC - Invisible\nD - Swiftplay\n\nType "A", "B", "C", or "D" in chat to select your gamemode.',
      color=discord.Colour.random())
    await to_edit.edit(embed=embed)

    while True:

      def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

      msg = await self.bot.wait_for('message', check=check, timeout=300)

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

  async def bet_selection(self, ctx, member):
    while True:
      await ctx.send(f'How much would you want to bet, {member.display_name}?')

      def check(m):
        return m.author == member and m.channel == ctx.channel and member in self.coinflips

      try:
        msg = await self.bot.wait_for('message', check=check, timeout=300)
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
        coin_amount = await database.get_attribute(self.bot.database, member,
                                                   'coins')
        if bet > coin_amount:
          await msg.channel.send(
            'You don\'t have enough coins on your balance to bet this amount.')
          continue
        elif bet > 2500:
          await msg.channel.send('You cannot bet over 2500 coins.')
          continue
        else:
          return bet

  @commands.command(aliases=('connect4', 'c4'))
  async def connectfour(self, ctx, member: discord.Member):
    if member.bot:
      await ctx.send(
        f'{ctx.author.mention}, the right command is \"j.c4 {{your opponent}}.\"'
      )
      return
    elif member == ctx.author:
      await ctx.send(f'{ctx.author.mention}, your opponent cannot be yourself.'
                     )
      return
    elif member in self.games:
      await ctx.send(
        f'{ctx.author.mention}, your opponent, {member.display_name}, is currently in another game.'
      )
      return

    gamemode = await self.gamemode_selection(ctx, member)
    if gamemode is None:
      await ctx.send(
        f'{ctx.author.display_name} and {member.display_name}\'s game has been ended by {ctx.author.display_name}'
      )
      return
    elif gamemode == 'refusal':
      await ctx.send(
        f'{ctx.author.display_name} and {member.display_name}\'s game has been ended by {member.display_name}'
      )
      return
    if gamemode == Gamemode.EXTREME:
      self.colors[ctx.author] = ':blue_circle:'
      self.colors[member] = ':yellow_circle:'
      self.hexes[':blue_circle:'] = 0x0000ff
      self.hexes[':yellow_circle:'] = 0xffff00
    else:
      self.colors[ctx.author] = ':red_circle:'
      self.colors[member] = ':yellow_circle:'
      self.hexes[':red_circle:'] = 0xff0000
      self.hexes[':yellow_circle:'] = 0xffff00

    if ctx.author not in self.games:
      if gamemode in (Gamemode.NORMAL, Gamemode.INVISIBLE, Gamemode.SWIFTPLAY):
        self.games[ctx.author] = ConnectFour(':blue_square:',
                                             [ctx.author, member])
      elif gamemode == Gamemode.EXTREME:
        self.games[ctx.author] = ConnectFour(
          str(discord.utils.get(self.bot.emojis, name='c4_fire')),
          [ctx.author, member])
      self.games[ctx.author].gamemode = gamemode
      self.games[ctx.author].channel = ctx.channel
      self.games[member] = self.games[ctx.author]
      self.games[member].channel = ctx.channel
      self.games[member].gamemode = gamemode
      self.games[ctx.author].turn = self.games[ctx.author].players[0]

      if self.games[ctx.author].gamemode == Gamemode.INVISIBLE:
        embed = discord.Embed(
          title=f'{ctx.author.display_name} and {member.display_name}\'s game:',
          color=self.hexes[self.colors[self.games[ctx.author].turn]])
        embed.add_field(name='Game:',
                        value=((':black_large_square:' * 7) + '\n') * 6)
      elif self.games[ctx.author].gamemode == Gamemode.EXTREME:
        embed = discord.Embed(
          title=f'{ctx.author.display_name} and {member.display_name}\'s game:',
          description=
          f'🔵 ― {self.games[ctx.author].red.mention}\n🟡 ― {self.games[ctx.author].yellow.mention}\n\n**Game:**\n{self.games[ctx.author].print_board()}',
          color=self.hexes[self.colors[self.games[ctx.author].turn]])
      else:
        embed = discord.Embed(
          title=f'{ctx.author.display_name} and {member.display_name}\'s game:',
          description=
          f'🔴 ― {self.games[ctx.author].red.mention}\n🟡 ― {self.games[ctx.author].yellow.mention}',
          color=self.hexes[self.colors[self.games[ctx.author].turn]])
        if self.games[ctx.author].gamemode == Gamemode.SWIFTPLAY:
          embed.description += f'\n**TIME LEFT:** {str(discord.utils.get(self.bot.emojis, name="5secondtimer"))}'
        embed.add_field(name='Game:',
                        value=self.games[ctx.author].print_board())
      embed.set_footer(text='type "end" to end the game')
      await ctx.send(content=self.games[ctx.author].turn.mention, embed=embed)

      while True:

        def check(m):
          return m.author in self.games and self.games[
            m.author].turn == m.author and m.channel == self.games[
              m.author].channel

        try:
          if self.games[ctx.author].gamemode == Gamemode.SWIFTPLAY:
            msg = await self.bot.wait_for('message', check=check, timeout=5)
          else:
            msg = await self.bot.wait_for('message', check=check, timeout=300)
        except:
          if self.games[ctx.author].gamemode == Gamemode.SWIFTPLAY:
            rng = random.randint(100, 200)
            embed = discord.Embed(
              title=
              f'{self.games[ctx.author].players[0].display_name} and {self.games[ctx.author].players[1].display_name}\'s game:',
              description=
              f'You ran out of time! {self.games[ctx.author].players[1]} wins the game!\n{rng:,} :coin: has been added to your account.',
              color=self.hexes[self.colors[self.games[ctx.author].turn]])
            await self.database_operations(self.games[ctx.author].players[1],
                                           self.games[ctx.author].players[0],
                                           rng, 'swift')
            embed.add_field(name='Game:',
                            value=self.games[ctx.author].print_board())
            await ctx.send(embed=embed)
          temp = self.games[ctx.author]
          gamemode = self.games[ctx.author].gamemode
          loser = temp.players[0]
          self.games.pop(temp.players[0])
          self.games.pop(temp.players[1])
          if gamemode == Gamemode.SWIFTPLAY:

            def check(m):
              return m.author.id == loser.id and 'lag' in m.content.lower()

            for _ in range(5):
              try:
                msg = await self.bot.wait_for('message',
                                              check=check,
                                              timeout=20)
              except asyncio.TimeoutError:
                return
              else:
                await msg.channel.send(
                  'https://media.discordapp.net/attachments/1055814810459193426/1059658024689614928/unknown.png'
                )
                return
          return

        if msg.content in ['1', '2', '3', '4', '5', '6', '7']:
          if self.games[msg.author].is_full(int(msg.content)):
            await msg.channel.send(
              f'{msg.author.mention}, you are not allowed to place anything in that column anymore.'
            )
            continue
          self.games[msg.author].players = self.games[msg.author].players[::-1]
          self.games[msg.author].turn = self.games[msg.author].players[0]
          self.games[msg.author].place(int(msg.content),
                                       self.colors[msg.author])
          if self.games[msg.author].win_check(self.colors[msg.author]):
            rng = random.randint(800, 1200)
            if self.games[ctx.author].gamemode == Gamemode.INVISIBLE:
              embed = discord.Embed(
                title=
                f'{self.games[msg.author].players[0].display_name} and {self.games[msg.author].players[1].display_name}\'s game:',
                description=
                f'🔴 ― {self.games[ctx.author].red.mention}\n🟡 ― {self.games[ctx.author].yellow.mention}\n\n{msg.author.display_name} has **won!**\n{rng:,} :coin: has been added to your account.',
                color=self.hexes[self.colors[self.games[ctx.author].turn]])
              embed.add_field(name='Game:',
                              value=self.games[ctx.author].print_board())
              await self.database_operations(self.games[msg.author].players[1],
                                             self.games[msg.author].players[0],
                                             rng, 'invisible')
            elif self.games[ctx.author].gamemode == Gamemode.EXTREME:
              embed = discord.Embed(
                title=
                f'{ctx.author.display_name} and {member.display_name}\'s game:',
                description=
                f'{msg.author.display_name} has **won!**\n{rng:,} :coin: has been added to your account.\n\n**Game:**\n{self.games[ctx.author].print_board()}',
                color=self.hexes[self.colors[self.games[ctx.author].turn]])
              await self.database_operations(self.games[msg.author].players[1],
                                             self.games[msg.author].players[0],
                                             rng, 'extreme')
            else:
              rng = random.randint(100, 200)
              embed = discord.Embed(
                title=
                f'{self.games[msg.author].players[0].display_name} and {self.games[msg.author].players[1].display_name}\'s game:',
                description=
                f'{msg.author.display_name} has **won!**\n{rng:,} :coin: has been added to your account.',
                color=self.hexes[self.colors[self.games[ctx.author].turn]])
              if self.games[ctx.author].gamemode == Gamemode.SWIFTPLAY:
                await self.database_operations(
                  self.games[msg.author].players[1],
                  self.games[msg.author].players[0], rng, 'swift')
              else:
                await self.database_operations(
                  self.games[msg.author].players[1],
                  self.games[msg.author].players[0], rng, 'normal')
              embed.add_field(name='Game:',
                              value=self.games[msg.author].print_board())
            await msg.channel.send(embed=embed)

            temp = self.games[msg.author]
            self.games.pop(temp.players[0])
            self.games.pop(temp.players[1])
            return

          if self.games[msg.author].all_full():
            embed = discord.Embed(
              title=
              f'{self.games[msg.author].players[0].display_name} and {self.games[msg.author].players[1].display_name}\'s game:',
              description=
              f'🔴 ― {self.games[ctx.author].red.mention}\n🟡 ― {self.games[ctx.author].yellow.mention}\n\nThe game has ended in a tie.',
              color=self.hexes[self.colors[self.games[ctx.author].turn]])
            embed.add_field(name='Game:',
                            value=self.games[ctx.author].print_board())
            await msg.channel.send(embed=embed)

            temp = self.games[msg.author]
            self.games.pop(temp.players[0])
            self.games.pop(temp.players[1])
            return

          embed = discord.Embed(
            title=
            f'{self.games[msg.author].players[0].display_name} and {self.games[msg.author].players[1].display_name}\'s game:',
            color=self.hexes[self.colors[self.games[msg.author].turn]])
          if self.games[ctx.author].gamemode == Gamemode.INVISIBLE:
            embed.add_field(name='Game:',
                            value=((':black_large_square:' * 7) + '\n') * 6)
          elif self.games[ctx.author].gamemode == Gamemode.EXTREME:
            embed.description = f'**Game:**\n{self.games[ctx.author].print_board()}'
          else:
            embed.add_field(name='Game:',
                            value=self.games[ctx.author].print_board())
          embed.set_footer(text='type "end" to end the game')
          if self.games[ctx.author].gamemode == Gamemode.SWIFTPLAY:
            embed.description = f'**TIME LEFT:** {str(discord.utils.get(self.bot.emojis, name="5secondtimer"))}'
            explosion_event = await msg.channel.send(
              content=f'{self.games[msg.author].turn.mention}', embed=embed)
          else:
            explosion_event = await msg.channel.send(
              content=self.games[msg.author].turn.mention, embed=embed)
          if self.games[msg.author].gamemode == Gamemode.EXTREME:
            if time.time() - self.games[msg.author].last > 60:
              rng = random.randint(1, 125)
              if self.games[msg.author].guaranteed:
                rng = 1
              if rng in range(1, 101):
                coords_list = [self.games[msg.author].extreme_explosion()]
                if self.games[msg.author].guaranteed:
                  coords_list.append(
                    self.games[msg.author].extreme_explosion())
                embed.description = f'**Game:**\n{self.games[ctx.author].print_board()}'
                await explosion_event.edit(embed=embed)
                await asyncio.sleep(4.8)
                for coord in coords_list:
                  self.games[msg.author].extreme_petrify(coord)
                embed.description = f'**Game:**\n{self.games[ctx.author].print_board()}'
                await explosion_event.edit(embed=embed)
                self.games[msg.author].guaranteed = False
              else:
                self.games[msg.author].guaranteed = True
              self.games[msg.author].last = time.time() + 28800
        elif msg.content.lower() in (
            'forfeit', 'resign',
            'Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry. Mommy? Sorry.'
            .lower()):
          rng = random.randint(800, 1200)
          if self.games[ctx.author].gamemode == Gamemode.SWIFTPLAY:
            rng = random.randint(100, 200)
          if self.games[ctx.author].gamemode == Gamemode.INVISIBLE:
            embed = discord.Embed(
              title=
              f'{self.games[msg.author].players[0].display_name} and {self.games[msg.author].players[1].display_name}\'s game:',
              description=
              f'🔴 ― {self.games[ctx.author].red.mention}\n🟡 ― {self.games[ctx.author].yellow.mention}\n\n{self.games[msg.author].players[1].display_name} has **won!**\n{rng:,} :coin: has been added to your account.',
              color=self.hexes[self.colors[self.games[ctx.author].turn]])
            embed.add_field(name='Game:',
                            value=self.games[ctx.author].print_board())
            await self.database_operations(self.games[msg.author].players[1],
                                           self.games[msg.author].players[0],
                                           rng, 'invisible')
          elif self.games[ctx.author].gamemode == Gamemode.EXTREME:
            embed = discord.Embed(
              title=
              f'{ctx.author.display_name} and {member.display_name}\'s game:',
              description=
              f'{self.games[msg.author].players[1].display_name} has **won!**\n{rng:,} :coin: has been added to your account.\n\n**Game:**\n{self.games[ctx.author].print_board()}',
              color=self.hexes[self.colors[self.games[ctx.author].turn]])
            await self.database_operations(self.games[msg.author].players[1],
                                           self.games[msg.author].players[0],
                                           rng, 'extreme')
          else:
            embed = discord.Embed(
              title=
              f'{self.games[msg.author].players[0].display_name} and {self.games[msg.author].players[1].display_name}\'s game:',
              description=
              f'{self.games[msg.author].players[1].display_name} has **won!**\n{rng:,} :coin: has been added to your account.',
              color=self.hexes[self.colors[self.games[ctx.author].turn]])
            if self.games[ctx.author].gamemode == Gamemode.SWIFTPLAY:
              await self.database_operations(self.games[msg.author].players[1],
                                             self.games[msg.author].players[0],
                                             rng, 'swift')
            else:
              await self.database_operations(self.games[msg.author].players[1],
                                             self.games[msg.author].players[0],
                                             rng, 'normal')
            embed.add_field(name='Game:',
                            value=self.games[msg.author].print_board())
          await msg.channel.send(embed=embed)

          temp = self.games[msg.author]
          self.games.pop(temp.players[0])
          self.games.pop(temp.players[1])
          return
        elif msg.content not in [
            '1', '2', '3', '4', '5', '6', '7'
        ] and self.games[msg.author].turn == msg.author and self.games[
            msg.author].channel == msg.channel:
          await msg.channel.send(
            f'{msg.author.mention}, please type anything from 1 to 7.')
          continue

  @commands.command(aliases=('cf', 'candace', 'coinfuck'))
  async def coinflip(self, ctx, member: discord.Member):
    if member.bot:
      await ctx.send(
        f'{ctx.author.mention}, the right command is \"j.cf {{your opponent}}.\"'
      )
      return
    elif member == ctx.author:
      await ctx.send(f'{ctx.author.mention}, your opponent cannot be yourself.'
                     )
      return
    elif member in self.coinflips:
      await ctx.send(
        f'{ctx.author.mention}, your opponent, {member.display_name}, is currently in another game.'
      )
      return

    embed = discord.Embed(
      title=f'{ctx.author.display_name} is challenging you to a coinflip game!',
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
        f'What do you predict it will land on, {ctx.author.display_name}?')

      def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.author in self.coinflips

      try:
        msg = await self.bot.wait_for('message', check=check, timeout=300)
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
    total_winner_coins = await database.get_attribute(self.bot.database,
                                                      winner, 'coins')
    embed.description += f'\nYou now have a total of {total_winner_coins:,} :coin: coins.'
    await to_react.edit(embed=embed)

    self.coinflips.remove(winner)
    self.coinflips.remove(loser)
    await database.set_attribute(self.bot.database, winner, 1, 'cf_count')
    await database.set_attribute(self.bot.database, winner, 1, 'command_count')
    await database.set_xp(self.bot.database, winner, 20)
    await database.set_attribute(self.bot.database, loser, 1, 'cf_count')
    await database.set_attribute(self.bot.database, loser, 1, 'command_count')
    await database.set_xp(self.bot.database, loser, 15)

  @commands.command(aliases=('c4ai', 'cfourai', 'cfour_ai'))
  async def c4_ai(self, ctx):
    if ctx.author not in self.aigames:
      self.aigames[ctx.author] = ConnectFourAI(':blue_square:')
      self.aigames[ctx.author].channel = ctx.channel
      self.aigames[ctx.author].turn = ctx.author

      embed = discord.Embed(title=f'{ctx.author.display_name}\'s AI game:',
                            description=f'🔴 ― {ctx.author.mention}\n🟡 ― AI',
                            color=0xff0000)
      embed.add_field(name='Game:',
                      value=self.aigames[ctx.author].print_board())
      embed.set_footer(text='type "end" to end the game')
      await ctx.send(content=self.aigames[ctx.author].turn.mention,
                     embed=embed)

    while True:

      def check(m):
        return m.author in self.aigames and m.channel == self.aigames[
          m.author].channel

      try:
        msg = await self.bot.wait_for('message', check=check, timeout=300)
      except:
        self.aigames.pop(msg.author)
        return

      if msg.content in ['1', '2', '3', '4', '5', '6', '7']:
        if self.aigames[msg.author].is_full(int(msg.content)):
          await msg.channel.send(
            f'{msg.author.mention}, you are not allowed to place anything in that column anymore.'
          )
          continue
        mover = 'player'
        self.aigames[msg.author].turn = None
        self.aigames[msg.author].place(int(msg.content), ':red_circle:')

        if self.aigames[msg.author].win_check(':red_circle:'):
          embed = discord.Embed(
            title=f'{msg.author.display_name}\'s game:',
            description=f'{msg.author.display_name} has **won!**',
            color=0xff0000)
          embed.add_field(name='Game:',
                          value=self.aigames[msg.author].print_board())
          await msg.channel.send(embed=embed)

          self.aigames.pop(msg.author)
          return

        if self.aigames[msg.author].all_full():
          embed = discord.Embed(
            title=f'{msg.author.display_name}\'s game:',
            description=
            f'🔴 ― {msg.author.display_name}\n🟡 ― AI\nThe game has ended in a tie.',
            color=0xff0000)
          embed.add_field(name='Game:',
                          value=self.aigames[ctx.author].print_board())
          await msg.channel.send(embed=embed)

          self.aigames.pop(msg.author)
          return

        mover = 'ai'
        col, minimax_score = self.aigames[msg.author].ai_place()
        self.aigames[msg.author].place(col, ':yellow_circle:')

        if self.aigames[msg.author].win_check(':yellow_circl'):
          embed = discord.Embed(title=f'{msg.author.display_name}\'s game:',
                                description='The AI has **won!**',
                                color=0xff0000)
          embed.add_field(name='Game:',
                          value=self.aigames[msg.author].print_board())
          await msg.channel.send(embed=embed)

          self.aigames.pop(msg.author)
          return

        if self.aigames[msg.author].all_full():
          embed = discord.Embed(
            title=f'{msg.author.display_name}\'s game:',
            description=
            f'🔴 ― {msg.author.display_name}\n🟡 ― AI\nThe game has ended in a tie.',
            color=0xff0000)
          embed.add_field(name='Game:',
                          value=self.aigames[ctx.author].print_board())
          await msg.channel.send(embed=embed)

          self.aigames.pop(msg.author)
          return

        self.aigames[msg.author].turn = msg.author
      elif msg.content.lower() in ('forfeit', 'resign'):
        pass
      elif msg.content not in [
          '1', '2', '3', '4', '5', '6', '7'
      ] and self.aigames[msg.author].turn == msg.author and self.aigames[
          msg.author].channel == msg.channel:
        await msg.channel.send(
          f'{msg.author.mention}, please type anything from 1 to 7.')
        continue

      if mover == 'player':
        color = 0xff0000
      else:
        color = 0xffff00
      embed = discord.Embed(title=f'{msg.author.display_name}\'s game:',
                            color=color)
      embed.add_field(name='Game:',
                      value=self.aigames[ctx.author].print_board())
      embed.set_footer(text='type "end" to end the game')
      await msg.channel.send(content=msg.author.mention, embed=embed)


async def setup(bot):
  await bot.add_cog(Minigames(bot))
