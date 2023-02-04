from discord.ext import commands
import discord


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
        exclusive_roles = [1064445950992597042, 1052103824346710056, 858166817145880587, 957799704660439041, 1044612642599358475, 957803140864950302, 858222265098174474, 858228707767877632, 1026064526698889286, 1067326246867980318, 1036568309501526026, 1036842427622903878, 1063688787722522666, 1055792475245129759, 1058290811835531304, 1045704861783695450]
        added_role = next((role for role in after.roles if role not in before.roles), None)
        hops_dev = after.guild.get_role(934678477825802270)
        if added_role is not None:
            if added_role.id in exclusive_roles:
                entries = [entry async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update)]
                role_entry = next((entry for entry in entries if (hops_dev in entry.user.roles or entry.user.bot)
                     and entry.target == after), None)
                if not role_entry:
                    await after.remove_roles(added_role)
        else:
            removed_role = next((role for role in before.roles if role not in after.roles), None)
            if removed_role is None:
                return
            if removed_role.id in exclusive_roles:
                entries = [entry async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update)]
                role_entry = next((entry for entry in entries if (hops_dev in entry.user.roles or entry.user.bot)
                     and entry.target == after), None)
                if not role_entry:
                    await after.add_roles(removed_role)
        await self.update_roles(after)



async def setup(bot):
    await bot.add_cog(RoleOrganizer(bot))
