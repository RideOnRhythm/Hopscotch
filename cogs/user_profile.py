import time
from discord.ext import commands
import discord
import aiohttp
import typing
from assets import database


async def get_mee6_level(member):
  async with aiohttp.ClientSession() as session:
    async with session.get(
        f'https://mee6.xyz/api/plugins/levels/leaderboard/{member.guild.id}'
    ) as resp:
      players_json = await resp.json()
      players_json = players_json['players']
      player_level = [i for i in players_json
                      if i['id'] == str(member.id)][0]['level']
      return player_level


class FirstPageView(discord.ui.View):

  def __init__(self,
               author: typing.Union[discord.Member, discord.User],
               member,
               cog,
               timeout=180):
    self.author = author
    self.member = member
    self.cog = cog
    super().__init__(timeout=timeout)

  @discord.ui.button(label="← Back", style=discord.ButtonStyle.primary)
  async def first_button(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
    embed = await UserProfile.first_page(self.cog, self.member)
    await interaction.response.edit_message(embed=embed,
                                            view=SecondPageView(
                                              self.author, self.member,
                                              self.cog))


class SecondPageView(discord.ui.View):

  def __init__(self,
               author: typing.Union[discord.Member, discord.User],
               member,
               cog,
               timeout=180):
    self.author = author
    self.member = member
    self.cog = cog
    super().__init__(timeout=timeout)

  @discord.ui.button(label="Next Page →", style=discord.ButtonStyle.primary)
  async def second_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
    embed = await UserProfile.second_page(self.cog, self.member)
    await interaction.response.edit_message(embed=embed,
                                            view=FirstPageView(
                                              self.author, self.member,
                                              self.cog))


class UserProfile(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.member_last_message = {}

  async def first_page(self, member):
    embed = discord.Embed(color=discord.Colour.random(
      seed=member.display_name))
    if member.avatar is not None:
      embed.set_author(name=f'{member.display_name}\'s profile',
                       icon_url=member.avatar.url)
    else:
      embed.set_author(name=f'{member.display_name}\'s profile')

    guild = self.bot.get_guild(763218643843678288)
    dev = guild.get_role(934678477825802270)
    mod = guild.get_role(1059763760056782858)
    chit = guild.get_role(910723707578753074)
    egg = guild.get_role(1020889035901780018)
    if dev in member.roles:
      rank = 'Developer'
    elif mod in member.roles:
      rank = 'Moderator'
    elif chit in member.roles:
      rank = 'Chit-Chatter'
    elif egg in member.roles:
      rank = 'Egg'
    else:
      rank = 'Peasant'
    icons = {
      1036842427622903878:
      str(discord.utils.get(self.bot.emojis, name='ICON_4')),
      1052103824346710056:
      str(discord.utils.get(self.bot.emojis, name='ICON_2')),
      1063688787722522666:
      str(discord.utils.get(self.bot.emojis, name='ICON_3')),
      1048233290143907900:
      str(discord.utils.get(self.bot.emojis, name='ICON_1'))
    }
    icon = ''
    for role in icons:
      if role in [role.id for role in member.roles]:
        icon += f'{icons[role]} '
    if icon == '':
      icon = 'None'
    last_saved = await database.get_attribute(self.bot.database, member,
                                              'last_saved_roles_unix')
    last_message_unix = await database.get_attribute(self.bot.database, member,
                                                     'last_message_unix')
    last_message_channel_id = await database.get_attribute(
      self.bot.database, member, 'last_message_channel_id')
    last_message_channel = self.bot.get_channel(last_message_channel_id)
    if last_message_unix is None and member.voice is None:
      active_string = '**Inactive** (Last active: Unknown)'
    elif member.voice is None and time.time() - last_message_unix > 180:
      active_string = f'**Inactive** (Last Active: - <t:{int(last_message_unix)}:R>)'
    elif last_message_unix is None and member.voice is not None:
      active_string = f'**Active Now** ― in {member.voice.channel.mention}'
    if last_message_unix is not None:
      if time.time(
      ) - last_message_unix <= 180 and member.voice is None:  # Last message sent within 3 minutes and not in voice
        active_string = f'**Active Now** ― in {last_message_channel.mention}'
      elif time.time(
      ) - last_message_unix > 180 and member.voice is not None:  # Last message not sent within 3 minutes and in voice
        active_string = f'**Active Now** ― in {member.voice.channel.mention}'
      elif time.time(
      ) - last_message_unix <= 180 and member.voice is not None:  # Last message sent within 3 minutes and in voice
        active_string = f'**Active Now** ― in {last_message_channel.mention} and {member.voice.channel.mention}'

    await database.initialize_member(self.bot.database, member)
    hopscotch_level = await database.get_attribute(self.bot.database, member,
                                                   'hopscotch_level')
    try:
      mee6_level = await get_mee6_level(member)
    except IndexError:
      mee6_level = 0
    current_xp = await database.get_attribute(self.bot.database, member,
                                              'current_xp')
    total_messages = await database.get_attribute(self.bot.database, member,
                                                  'total_messages')
    if total_messages >= 1000:
      total_messages = f'{total_messages // 1000}K+'
    total_vc_hours = await database.get_attribute(self.bot.database, member,
                                                  'total_vc_hours')
    command_count = await database.get_attribute(self.bot.database, member,
                                                 'command_count')

    embed.description = f'**Rank**: {rank}\n**Icons**: {icon}\n'
    embed.description += f'''{active_string}
        
**__Levels__**
**HOPS LEVEL**: Level {hopscotch_level} ({current_xp}XP/{5 * hopscotch_level ** 2}XP)
**MEE6 LEVEL**: Level {mee6_level}

**__Server Statistics__**
- You have sent approximately **{total_messages}** messages. (6/26/2021 onwards)
- You have spent a total of **{total_vc_hours}** hours in voice channels. (1/7/2023 onwards)
- You have sent a total of **{command_count}** Hopscotch commands. (1/7/2023 onwards)

**Roles Last Saved**: <t:{int(last_saved)}>'''
    embed.set_footer(text='Page 1/2')
    return embed

  async def second_page(self, member):
    embed = discord.Embed(color=discord.Colour.random(
      seed=member.display_name))
    if member.avatar is not None:
      embed.set_author(name=f'{member.display_name}\'s profile',
                       icon_url=member.avatar.url)
    else:
      embed.set_author(name=f'{member.display_name}\'s profile')

    await database.initialize_member(self.bot.database, member)
    positive_coin_count = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'positive_coin_count')
    negative_coin_count = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'negative_coin_count')
    positive_gem_count = await database.get_attribute(self.bot.database,
                                                      member,
                                                      'positive_gem_count')
    negative_gem_count = await database.get_attribute(self.bot.database,
                                                      member,
                                                      'negative_gem_count')
    normal_c4_count = await database.get_attribute(self.bot.database, member,
                                                   'normal_c4_count')
    normal_c4_win_count = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'normal_c4_win_count')
    normal_c4_coin_count = await database.get_attribute(
      self.bot.database, member, 'normal_c4_coin_count')
    extreme_c4_count = await database.get_attribute(self.bot.database, member,
                                                    'extreme_c4_count')
    extreme_c4_win_count = await database.get_attribute(
      self.bot.database, member, 'extreme_c4_win_count')
    extreme_c4_coin_count = await database.get_attribute(
      self.bot.database, member, 'extreme_c4_coin_count')
    invisible_c4_count = await database.get_attribute(self.bot.database,
                                                      member,
                                                      'invisible_c4_count')
    invisible_c4_win_count = await database.get_attribute(
      self.bot.database, member, 'invisible_c4_win_count')
    invisible_c4_coin_count = await database.get_attribute(
      self.bot.database, member, 'invisible_c4_coin_count')
    swift_c4_count = await database.get_attribute(self.bot.database, member,
                                                  'swift_c4_count')
    swift_c4_win_count = await database.get_attribute(self.bot.database,
                                                      member,
                                                      'swift_c4_win_count')
    swift_c4_coin_count = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'swift_c4_coin_count')
    cf_count = await database.get_attribute(self.bot.database, member,
                                            'cf_count')
    cf_win_count = await database.get_attribute(self.bot.database, member,
                                                'cf_win_count')
    cf_coin_count = await database.get_attribute(self.bot.database, member,
                                                 'cf_coin_count')

    embed.description = f'''**__Hopscotch Statistics__**
- You have earned a total of **{positive_coin_count}** :coin:. 
- You have earned a total of **{positive_gem_count}** :gem:
------------------
- You have used/lost a total of **{negative_coin_count}** :coin:. 
- You have used/lost a total of **{negative_gem_count}** :gem:.

**__Hopscotch C4 Statistics__**
- You have played a total of **{normal_c4_count}** normal games.
- You have won **{normal_c4_win_count}** normal games.
- You have earned a total of **{normal_c4_coin_count}** :coin: from normal games.
------------------
- You have played a total of **{extreme_c4_count}** extreme games.
- You have won **{extreme_c4_win_count}** extreme games.
- You have earned a total of **{extreme_c4_coin_count}** :coin: from extreme games.
------------------
- You have played a total of **{invisible_c4_count}** invisible games.
- You have won **{invisible_c4_win_count}** invisible games.
- You have earned a total of **{invisible_c4_coin_count}** :coin: from invisible games.
------------------
- You have played a total of **{swift_c4_count}** swiftplay games.
- You have won **{swift_c4_win_count}** swiftplay games.
- You have earned a total of **{swift_c4_coin_count}** :coin: from swiftplay games.

**__Hopscotch CF Statistics__**
- You have played a total of **{cf_count}** games.
- You have won **{cf_win_count}** games.
- You have earned a total of **{cf_coin_count}** :coin:.'''
    embed.set_footer(text='Page 2/2')
    return embed

  @commands.command(aliases=tuple('p'))
  async def profile(self,
                    ctx,
                    member: typing.Union[discord.Member, int] = None):
    if member is None:
      member = ctx.author
    if isinstance(member, discord.Member):
      if member.bot:
        await ctx.send(
          f'{ctx.author.mention}, the right command is \"j.profile {{user (optional)}}/{{page}}.\"'
        )
        return

    if member == 2:
      member = ctx.author
      embed = await self.second_page(member)
      await ctx.send(embed=embed, view=FirstPageView(ctx.author, member, self))
    else:
      embed = await self.first_page(member)
      await ctx.send(embed=embed,
                     view=SecondPageView(ctx.author, member, self))
    await database.set_attribute(self.bot.database, ctx.author, 1,
                                 'command_count')
    await database.set_xp(self.bot.database, ctx.author, 1)

  @commands.command(aliases=('coin', 'c', 'balance', 'bal', 'b', 'gems'))
  async def coins(self, ctx, member: discord.Member = None):
    if member is None:
      member = ctx.author
    if member.bot:
      await ctx.send(
        f'{ctx.author.mention}, the right command is \"j.coins {{user (optional)}}.\"'
      )
      return

    coins = await database.get_attribute(self.bot.database, member, 'coins')
    gems = await database.get_attribute(self.bot.database, member, 'gems')
    embed = discord.Embed(description=f'**{coins}** :coin:\n**{gems}** :gem:',
                          color=discord.Colour.random())
    if member.avatar is not None:
      embed.set_author(name=f'{member.display_name}\'s balance',
                       icon_url=member.avatar.url)
    else:
      embed.set_author(name=f'{member.display_name}\'s balance')
    await ctx.send(embed=embed)
    await database.set_attribute(self.bot.database, ctx.author, 1,
                                 'command_count')
    await database.set_xp(self.bot.database, ctx.author, 1)

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot or message.guild.id != 763218643843678288:
      return
    await database.save_json(self.bot.database)


async def setup(bot):
  await bot.add_cog(UserProfile(bot))
