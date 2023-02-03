from discord.ext import commands
import discord
import asyncio


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
          organizer_roles[ind + 1]) - member.roles.index(organizer) == 1:
        await member.remove_roles(organizer_roles[ind + 1])
    # If the first organizer role is the first role of the member, remove the role
    if member.roles.index(organizer_roles[0]) == 1:
      await member.remove_roles(organizer_roles[0])

  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    if before.roles != after.roles and not after.bot:
      await self.update_roles(after)


async def setup(bot):
  await bot.add_cog(RoleOrganizer(bot))
