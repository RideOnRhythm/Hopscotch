from discord.ext import commands
from discord.ext import tasks
from assets import database
import discord
import time


class Stats(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.member_last_message = {}
    self.global_last_message = None
    self.vc_times = {}

  @commands.command(aliases=('active', 'acn', 'ac', 'active_now'))
  async def activenow(self, ctx):
    if ctx.author.bot:
      return
    await self.bot.wait_until_ready()
    guild = self.bot.get_guild(763218643843678288)
    chit_chatter_role = guild.get_role(910723707578753074)
    egg_role = guild.get_role(1020889035901780018)
    chit_chatters = list(
      filter(lambda m: chit_chatter_role in m.roles, guild.members))
    eggs = list(filter(lambda m: egg_role in m.roles, guild.members))

    online_members = list(
      filter(
        lambda c: c.status in
        (discord.Status.online, discord.Status.idle, discord.Status.dnd),
        chit_chatters + eggs))
    active_members = []
    for member in chit_chatters + eggs:
      last_message_unix = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'last_message_unix')
      if member.voice is not None:
        active_members.append(member)
      elif last_message_unix is not None:
        if time.time() - last_message_unix <= 180:
          active_members.append(member)

    embed = discord.Embed(
      title='**Active Now**',
      description=
      f'**{len(online_members)}** are online, ** {len(active_members)}** are active\n',
      color=0x2ecc71)

    for member in chit_chatters + eggs:  # s + eggs (real)
      last_message_unix = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'last_message_unix')
      last_message_channel_id = await database.get_attribute(
        self.bot.database, member, 'last_message_channel_id')
      last_message_channel = self.bot.get_channel(last_message_channel_id)
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
      for i in icons:
        if i in [role.id for role in member.roles]:
          icon = f'{icons[i]} '
          break
      if last_message_unix is not None:
        if time.time(
        ) - last_message_unix <= 180 and member.voice is None:  # Last message sent within 3 minutes and not in voice
          embed.description += f'\n**{icon}{member.display_name}** ― in {last_message_channel.mention}'
        elif time.time(
        ) - last_message_unix > 180 and member.voice is not None:  # Last message not sent within 3 minutes and in voice
          embed.description += f'\n**{icon}{member.display_name}** ― in {member.voice.channel.mention}'
        elif time.time(
        ) - last_message_unix <= 180 and member.voice is not None:  # Last message sent within 3 minutes and in voice
          embed.description += f'\n**{icon}{member.display_name}** ― in {last_message_channel.mention} and {member.voice.channel.mention}'
      elif member.voice is not None:
        embed.description += f'\n**{icon}{member.display_name}** ― in {member.voice.channel.mention}'

    await ctx.send(embed=embed)
    await database.set_attribute(self.bot.database, ctx.author, 1,
                                 'command_count')
    await database.set_xp(self.bot.database, ctx.author, 1)

  @commands.command(aliases=('member', 'users', 'user', 'm'))
  async def members(self, ctx):
    await self.bot.wait_until_ready()
    guild = self.bot.get_guild(763218643843678288)
    chit_chatter_role = guild.get_role(910723707578753074)
    egg_role = guild.get_role(1020889035901780018)  # egg roll?!?!?!?!?!
    chit_chatters = list(
      filter(lambda m: chit_chatter_role in m.roles, guild.members))
    eggs = list(filter(lambda m: egg_role in m.roles, guild.members))

    online_members = list(
      filter(
        lambda c: c.status in
        (discord.Status.online, discord.Status.idle, discord.Status.dnd),
        chit_chatters + eggs))
    active_members = []
    for member in chit_chatters + eggs:
      last_message_unix = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'last_message_unix')
      if member.voice is not None:
        active_members.append(member)
      elif last_message_unix is not None:
        if time.time() - last_message_unix <= 180:
          active_members.append(member)

    embed = discord.Embed(
      title='**Members**',
      description=
      f'**{len(chit_chatters + eggs)} total members, {len(online_members)}** are online, ** {len(active_members)}** are active\n\nActive:',
      color=0x2ecc71)

    for member in chit_chatters + eggs:  # s + eggs (real)
      last_message_unix = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'last_message_unix')
      last_message_channel_id = await database.get_attribute(
        self.bot.database, member, 'last_message_channel_id')
      last_message_channel = self.bot.get_channel(last_message_channel_id)
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
      for i in icons:
        if i in [role.id for role in member.roles]:
          icon = f'{icons[i]} '
      if last_message_unix is not None:
        if time.time(
        ) - last_message_unix <= 180 and member.voice is None:  # Last message sent within 3 minutes and not in voice
          embed.description += f'\n**{icon}{member.display_name}** ― in {last_message_channel.mention}'
        elif time.time(
        ) - last_message_unix > 180 and member.voice is not None:  # Last message not sent within 3 minutes and in voice
          embed.description += f'\n**{icon}{member.display_name}** ― in {member.voice.channel.mention}'
        elif time.time(
        ) - last_message_unix <= 180 and member.voice is not None:  # Last message sent within 3 minutes and in voice
          embed.description += f'\n**{icon}{member.display_name}** ― in {last_message_channel.mention} and {member.voice.channel.mention}'
      elif member.voice is not None:
        embed.description += f'\n**{icon}{member.display_name}** ― in {member.voice.channel.mention}'

    embed.description += '\n\nInactive:'
    inactive_hit_list = []
    for member in chit_chatters + eggs:
      last_message_unix = await database.get_attribute(self.bot.database,
                                                       member,
                                                       'last_message_unix')
      if last_message_unix is not None:
        if time.time() - last_message_unix > 180 and member.voice is None:
          inactive_hit_list.append((member, last_message_unix))
      elif member.voice is None:
        inactive_hit_list.append((member, 0))
    inactive_hit_list = sorted(inactive_hit_list,
                               key=lambda t: t[1],
                               reverse=True)
    for i in inactive_hit_list:
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
      for a in icons:
        if a in [role.id for role in i[0].roles]:
          icon = f'{icons[a]} '
          break
      if i[1] == 0:
        embed.description += f'\n**{icon}{i[0].display_name} ** ― Last Active: Unknown'
      else:
        embed.description += f'\n**{icon}{i[0].display_name}** ― Last Active: <t:{int(i[1])}:R>'

    await ctx.send(embed=embed)
    await database.set_attribute(self.bot.database, ctx.author, 1,
                                 'command_count')
    await database.set_xp(self.bot.database, ctx.author, 1)

  @commands.command(aliases=('top', 'lb'))
  async def leaderboard(self, ctx, sort='coins'):
    await self.bot.wait_until_ready()
    guild = self.bot.get_guild(763218643843678288)
    chit_chatter_role = guild.get_role(910723707578753074)
    egg_role = guild.get_role(1020889035901780018)  # egg roll?!?!?!?!?!
    chit_chatters = list(
      filter(lambda m: chit_chatter_role in m.roles, guild.members))
    eggs = list(filter(lambda m: egg_role in m.roles, guild.members))
    eggs = [x for x in eggs if x not in chit_chatters]
    embed = discord.Embed(title='**Leaderboard — **',
                          description='',
                          color=discord.Color.blue())
    if sort in ('coins', 'coin', 'balance', 'bal'):
      embed.title += 'coins'
      coin_list = [(member, await
                    database.get_attribute(self.bot.database, member, 'coins'))
                   for member in chit_chatters + eggs]
      coin_list = sorted(coin_list, key=lambda t: t[1], reverse=True)
      coin_list = coin_list[:10]
      for member in coin_list:
        if coin_list.index(member) + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[coin_list.index(member) + 1]
        else:
          honour_string = str(coin_list.index(member) + 1) + '. '
        embed.description += f'\n{honour_string} **{member[0].display_name}** ― {member[1]} :coin:'
    elif sort in ('level', 'lvl', 'lv', 'levels'):
      embed.title += 'level'
      level_list = [(member, await
                     database.get_attribute(self.bot.database, member,
                                            'hopscotch_level'))
                    for member in chit_chatters + eggs]
      exp_list = [(member, await
                   database.get_attribute(self.bot.database, member,
                                          'current_xp'))
                  for member in chit_chatters + eggs]
      total_list = [(level_list[i][0],
                     sum(5 * n**2
                         for n in range(1, level_list[i][1])) + exp_list[i][1])
                    for i in range(len(level_list))]
      total_list = sorted(total_list, key=lambda t: t[1], reverse=True)
      total_list = total_list[:10]
      for i in range(len(total_list)):
        if i + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[i + 1]
        else:
          honour_string = str(i + 1) + '. '
        member = total_list[i][0]
        all_members = chit_chatters + eggs
        embed.description += f'\n{honour_string} **{total_list[i][0].display_name}** ― Level {level_list[all_members.index(member)][1]} ({exp_list[all_members.index(member)][1]}XP/{5 * level_list[all_members.index(member)][1] ** 2}XP)'
    elif sort in ('gems', 'gem'):
      embed.title += 'gems'
      gem_list = [(member, await
                   database.get_attribute(self.bot.database, member, 'gems'))
                  for member in chit_chatters + eggs]
      gem_list = sorted(gem_list, key=lambda t: t[1], reverse=True)
      gem_list = gem_list[:10]
      for member in gem_list:
        if gem_list.index(member) + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[gem_list.index(member) + 1]
        else:
          honour_string = str(gem_list.index(member) + 1) + '. '
        embed.description += f'\n{honour_string} **{member[0].display_name}** ― {member[1]} 💎'
    elif sort in ('wins', 'win'):
      embed.title += 'wins'
      total_win_list = [
        (member, await database.get_attribute(self.bot.database, member,
                                              'normal_c4_win_count') +
         await database.get_attribute(self.bot.database, member,
                                      'extreme_c4_win_count') +
         await database.get_attribute(self.bot.database, member,
                                      'invisible_c4_win_count') + await
         database.get_attribute(self.bot.database, member, 'cf_win_count') +
         await database.get_attribute(self.bot.database, member,
                                      'swift_c4_win_count'))
        for member in chit_chatters + eggs
      ]
      total_win_list = sorted(total_win_list, key=lambda t: t[1], reverse=True)
      total_win_list = total_win_list[:10]
      for member in total_win_list:
        if total_win_list.index(member) + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[total_win_list.index(member) + 1]
        else:
          honour_string = str(total_win_list.index(member) + 1) + '. '
        embed.description += f'\n{honour_string} **{member[0].display_name}** ― {member[1]} wins'
    elif sort in ('messages', 'msgs', 'msg' or sort in 'message'):
      embed.title += 'messages'
      message_list = [(member, await
                       database.get_attribute(self.bot.database, member,
                                              'total_messages'))
                      for member in chit_chatters + eggs]
      message_list = sorted(message_list, key=lambda t: t[1], reverse=True)
      message_list = message_list[:10]
      for member in message_list:
        if message_list.index(member) + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[message_list.index(member) + 1]
        else:
          honour_string = str(message_list.index(member) + 1) + '. '
        embed.description += f'\n{honour_string} **{member[0].display_name}** ― {member[1]} messages'
    elif sort in ('vc', 'vcs', 'voice channels', 'voice channel'):
      embed.title += 'voice channels'
      vc_list = [(member, await
                  database.get_attribute(self.bot.database, member,
                                         'total_vc_hours'))
                 for member in chit_chatters + eggs]
      vc_list = sorted(vc_list, key=lambda t: t[1], reverse=True)
      vc_list = vc_list[:10]
      for member in vc_list:
        if vc_list.index(member) + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[vc_list.index(member) + 1]
        else:
          honour_string = str(vc_list.index(member) + 1) + '. '
        embed.description += f'\n{honour_string} **{member[0].display_name}** ― {member[1]} hours'
    elif sort in ('command count', 'cmd count', 'commands count', 'cmds count',
                  'cmd', 'cmds', 'commands'):
      embed.title += 'command count'
      cmd_list = [(member, await
                   database.get_attribute(self.bot.database, member,
                                          'command_count'))
                  for member in chit_chatters + eggs]
      cmd_list = sorted(cmd_list, key=lambda t: t[1], reverse=True)
      cmd_list = cmd_list[:10]
      for member in cmd_list:
        if cmd_list.index(member) + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[cmd_list.index(member) + 1]
        else:
          honour_string = str(cmd_list.index(member) + 1) + '. '
        embed.description += f'\n{honour_string} **{member[0].display_name}** ― {member[1]} commands'
    else:
      embed.title += 'coins'
      coin_list = [(member, await
                    database.get_attribute(self.bot.database, member, 'coins'))
                   for member in chit_chatters + eggs]
      coin_list = sorted(coin_list, key=lambda t: t[1], reverse=True)
      coin_list = coin_list[:10]
      for member in coin_list:
        if coin_list.index(member) + 1 in (1, 2, 3):
          honour_string = {
            1: ':first_place:',
            2: ':second_place:',
            3: ':third_place:'
          }[coin_list.index(member) + 1]
        else:
          honour_string = str(coin_list.index(member) + 1) + '. '
        embed.description += f'\n{honour_string} **{member[0].display_name}** ― {member[1]} :coin:'
    await ctx.send(embed=embed)
    await database.set_attribute(self.bot.database, ctx.author, 1,
                                 'command_count')
    await database.set_xp(self.bot.database, ctx.author, 1)

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot:
      return
    self.global_last_message = message
    await database.set_attribute(self.bot.database,
                                 message.author,
                                 message.created_at.timestamp(),
                                 'last_message_unix',
                                 increment=False)
    await database.set_attribute(self.bot.database,
                                 message.author,
                                 message.channel.id,
                                 'last_message_channel_id',
                                 increment=False)
    await database.set_attribute(self.bot.database, message.author, 1,
                                 'total_messages')
    await database.set_xp(self.bot.database, message.author, 2)


async def setup(bot):
  await bot.add_cog(Stats(bot))
