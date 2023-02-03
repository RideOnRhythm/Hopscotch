from discord.ext import commands
from discord.ext import tasks
import discord
import time
import logging
from assets import database


class ChannelDesc(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.chit_description.start()
    self.vc_counter.start()
    self.role_saver.start()

  @tasks.loop(minutes=7)
  async def chit_description(self):
    await self.bot.wait_until_ready()
    guild = self.bot.get_guild(763218643843678288)
    chit_chat = self.bot.get_channel(858167284069302292)
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
    chit_description = f'''**{len(online_members)} ** are online, ** {len(active_members)}** are active now. │ **AD:** ---  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Chit-Chat is our main general channel in this server. This is where we usually hang-out to chat and talk about random stuff! There is just 1 rule and that is to have common sense. Try not to do anything stupid and have fun. That's what it's all about, right?
        '''
    await chit_chat.edit(topic=chit_description)
    logging.info('Edited Chit-Chat channel description')

  @tasks.loop(seconds=60)
  async def vc_counter(self):
    await self.bot.wait_until_ready()
    guild = self.bot.get_guild(763218643843678288)
    for member in guild.members:
      if member.voice is not None:
        await database.set_attribute(self.bot.database, member, 60,
                                     'total_vc_minutes')
        # ignore why it says minutes it should be seconds but am too lazy to change it
        member_vc_time = await database.get_attribute(self.bot.database,
                                                      member,
                                                      'total_vc_minutes')
        if member_vc_time >= 3600:
          logging.info(
            f'Added 1 hour to {member.display_name}\'s total VC hour count')
          await database.set_attribute(self.bot.database, member, 1,
                                       'total_vc_hours')
          await database.set_xp(self.bot.database, member, 400)
          await database.set_attribute(self.bot.database,
                                       member,
                                       0,
                                       'total_vc_minutes',
                                       increment=False)

  @tasks.loop(hours=1)
  async def role_saver(self):
    await self.bot.wait_until_ready()
    guild = self.bot.get_guild(763218643843678288)
    for member in guild.members:
      if time.time() - member.joined_at.timestamp() < 7200 or member.bot:
        continue
      await database.set_attribute(self.bot.database,
                                   member, [role.id for role in member.roles],
                                   'roles',
                                   increment=False)
      await database.set_attribute(self.bot.database,
                                   member,
                                   time.time(),
                                   'last_saved_roles_unix',
                                   increment=False)

  @commands.command()
  async def save_roles(self, ctx):
    if ctx.author.id not in (748388929631289436, 556307832241389581,
                             994223267462258688):
      return
    guild = self.bot.get_guild(763218643843678288)
    for member in guild.members:
      if member.bot:
        continue
      await database.set_attribute(self.bot.database,
                                   member, [role.id for role in member.roles],
                                   'roles',
                                   increment=False)
      await database.set_attribute(self.bot.database,
                                   member,
                                   time.time(),
                                   'last_saved_roles_unix',
                                   increment=False)
    await ctx.send('Saved')

  @commands.Cog.listener()
  async def on_member_join(self, member):
    guild = self.bot.get_guild(763218643843678288)
    chit = guild.get_channel(858167284069302292)
    saved_roles = await database.get_attribute(self.bot.database, member,
                                               'roles')
    last_saved = await database.get_attribute(self.bot.database, member,
                                              'last_saved_roles_unix')
    missing_roles = list(
      set(saved_roles) - set([role.id for role in member.roles]))
    await member.add_roles(
      *[guild.get_role(role_id) for role_id in missing_roles])
    await chit.send(
      f'[**SYS**]: Welcome back, {member.mention}! Your roles (saved from <t:{int(last_saved)}>) have been added back.'
    )

  @commands.command()
  async def return_roles(self, ctx, member: discord.Member):
    if ctx.author.id not in (748388929631289436, 556307832241389581,
                             994223267462258688):
      return
    guild = self.bot.get_guild(763218643843678288)
    chit = guild.get_channel(858167284069302292)
    saved_roles = await database.get_attribute(self.bot.database, member,
                                               'roles')
    last_saved = await database.get_attribute(self.bot.database, member,
                                              'last_saved_roles_unix')
    missing_roles = list(
      set(saved_roles) - set([role.id for role in member.roles]))
    await member.add_roles(
      *[guild.get_role(role_id) for role_id in missing_roles])
    await chit.send(
      f'> ADDED BACK ROLES TO {member.mention} (**LAST SAVE**: <t:{int(last_saved)}>)'
    )


async def setup(bot):
  await bot.add_cog(ChannelDesc(bot))
