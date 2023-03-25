import datetime
import time
from discord.ext import commands
from discord import app_commands
import discord
from discord.ext import tasks
import bcrypt
from assets import database


# These will store the last unix timestamps of each user
# when they sent a message or unmuted
timers = {}
# When a member uses the /login command, it will add their original roles back
# This dictionary will store their roles before removing them
cached_roles = {}
# This will prevent double locking of members
locked = []

async def user_password(cog, password, security_level, interaction, og_embed):
    # Store the hashed password, salt, and security level in the member's database
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    
    hash = hash.decode('utf-8')
    await database.set_attribute(cog.bot.database, interaction.user, hash, 'hash', increment=False)
    await database.set_attribute(cog.bot.database, interaction.user, security_level, 'security_level', increment=False)

    embed = og_embed
    embed.description = '2FA has been enabled.'
    await interaction.response.edit_message(embed=embed, view=None)


async def lock_user(guild, member):
    locked.append(member)
    cc_role = guild.get_role(910723707578753074)
    mini_cc = guild.get_role(1020889035901780018)
    smp_player = guild.get_role(1085464616018120744)
    mc_player = guild.get_role(1085463856995913819)
    tr_player = guild.get_role(1085463960133840948)
    dev_team = guild.get_role(934678477825802270)
    mod = guild.get_role(1059763760056782858)
    # A list of the permission roles the member has
    member_roles = [role for role in [cc_role, mini_cc, smp_player, mc_player, tr_player, dev_team, mod] if role in member.roles]
    cached_roles[member] = member_roles

    _2fa_role = guild.get_role(1089032862461857893)
    # Removing these roles removes the member's access to all channels
    # The 2FA role will give the member access to a single channel
    await member.remove_roles(*member_roles)
    await member.add_roles(_2fa_role)


class RegisterView(discord.ui.View):
    def __init__(self, cog, password, og_embed, timeout=180):
        self.cog = cog
        self.password = password
        self.og_embed = og_embed
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label='Normal', style=discord.ButtonStyle.secondary)
    async def normal(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        await user_password(self.cog, self.password, 'normal', interaction, self.og_embed)

    @discord.ui.button(label='Medium', style=discord.ButtonStyle.secondary)
    async def medium(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        await user_password(self.cog, self.password, 'medium', interaction, self.og_embed)

    @discord.ui.button(label='High', style=discord.ButtonStyle.secondary)
    async def high(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        await user_password(self.cog, self.password, 'high', interaction, self.og_embed)

    @discord.ui.button(label='Super Secure', style=discord.ButtonStyle.secondary)
    async def super_secure(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        await user_password(self.cog, self.password, 'super_secure', interaction, self.og_embed)


class TwoFactor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_detector.start()
        self._2fa_checker.start()
    
    @tasks.loop(seconds=5)
    async def mute_detector(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(763218643843678288)
        non_bot_members = [member for member in guild.members if not member.bot]
        for member in non_bot_members:
            if member.voice is None:
                continue
            if not member.voice.self_mute:
                # Reset the timer of the member if they are unmuted
                timers[member] = time.time()

    @tasks.loop(seconds=5)
    async def _2fa_checker(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(763218643843678288)
        # Only members with 2FA enabled will have a security level
        _2fa_members = [member for member in guild.members if await database.get_attribute(self.bot.database, member, 'security_level') is not None]
        for member in _2fa_members:
            if member not in timers or member in locked:
                continue
            
            security_level = await database.get_attribute(self.bot.database, member, 'security_level')
            time_limits = {
                'normal': 7200,
                'medium': 3600,
                'high': 1800,
                'super_secure': 600
            }
            # Check if the member has been inactive for an amount of time specified by their security level
            if time.time() - timers[member] >= time_limits[security_level]:
                await lock_user(guild, member)

    @commands.hybrid_command(name='2fa')  # Workaround to have a command that starts with a number
    async def _2fa(self, ctx):
        embed = discord.Embed(title='2FA Setup', color=discord.Color.random())
        embed.description = '''Welcome to the 2FA Setup! This will increase the security of your account in this server. After enabling 2FA, you will have to enter your 2FA password that you registered in order to get access to channels. Make sure the password you used to register is a password you have not used in any of your previous accounts to make it more unique and harder to obtain.

**Setup Command**: `/2fa_register <password> <password>`
To register, send the command above. Take note if the password you input there and make sure you don't forget it.

Once you send that command, the bot will ask you for the level of security. There are 4 levels of security: **Normal, Medium, High, and Super Secure**. 
The normal security removes your server permissions after **2 hours** of being inactive. 
The medium security removes your server permissions after **an hour** of being inactive. 
The high security removes your server permissions after **30 minutes** of being inactive.
The super secure security removes your server permissions after **10 minutes** of being inactive.

Additionally, there will be a `/lock` command if you want the bot to log you out automatically.
Stay safe!'''
        embed.timestamp = datetime.datetime.now()
        await ctx.send(embed=embed)
    
    @app_commands.command(name='2fa_register')
    async def _2fa_register(self, interaction: discord.Interaction, password: str, confirm: str):
        if password != confirm:
            await interaction.response.send_message('> The password you inputted are not the same. Please try again.', ephemeral=True)
            return
        try:
            if await database.get_attribute(self.bot.database, interaction.user, 'security_level') is not None:
                await interaction.response.send_message('> You have already registered. If you want to change your password, contact a developer.', ephemeral=True)
                return
        except KeyError:  # Ignore KeyError as it means the user has not registered
            pass
        
        embed = discord.Embed(title='2FA Setup', color=discord.Color.random())
        embed.description = '''**Please select the level of security**:
Normal
Medium (Recommended)
High
Super Secure
        '''
        embed.timestamp = datetime.datetime.now()
        await interaction.response.send_message(embed=embed, view=RegisterView(self, password, embed), ephemeral=True)
    
    @app_commands.command(name='login')
    async def login(self, interaction: discord.Interaction, password: str):
        _2fa_role = interaction.guild.get_role(1089032862461857893)
        if _2fa_role not in interaction.user.roles:
            await interaction.response.send_message('> You are already logged in.', ephemeral=True)
            return
        
        # Check the inputted password with the user's hash
        hash = await database.get_attribute(self.bot.database, interaction.user, 'hash')
        hash = hash.encode('utf-8')
        bytes = password.encode('utf-8')
        result = bcrypt.checkpw(bytes, hash)

        if not result:
            await interaction.response.send_message('> The password you inputted is incorrect. Please contact a Developer if you forgot your password.', ephemeral=True)
            return
        
        # Remove the 2FA role from the user and give them back their original roles
        await interaction.user.remove_roles(_2fa_role)
        await interaction.user.add_roles(*cached_roles[interaction.user])

        await interaction.response.send_message('Successfuly logged in.', ephemeral=True)
    
    @app_commands.command(name='lock')
    async def lock(self, interaction: discord.Interaction):
        try:
            if await database.get_attribute(self.bot.database, interaction.user, 'security_level') is None:
                await interaction.response.send_message('> You have not registered. Do `/2fa` for information on how to enable 2FA.', ephemeral=True)
                return
        except KeyError:  # Ignore KeyError as it means the user has not registered
            return
       
        await lock_user(interaction.guild, interaction.user)
        await interaction.response.send_message('Locked.', ephemeral=True)
    
    @app_commands.command(name='disable_2fa')
    async def disable_2fa(self, interaction: discord.Interaction, password: str):
        hash = await database.get_attribute(self.bot.database, interaction.user, 'hash')
        hash = hash.encode('utf-8')
        bytes = password.encode('utf-8')
        result = bcrypt.checkpw(bytes, hash)

        if not result:
            await interaction.response.send_message('> The password you inputted is incorrect. Please contact a Developer if you forgot your password.', ephemeral=True)
            return
        
        # Disable the user's 2FA by setting their 'hash' and 'security_level' to None
        await database.set_attribute(self.bot.database, interaction.user, None, 'hash', increment=False)
        await database.set_attribute(self.bot.database, interaction.user, None, 'security_level', increment=False)

        await interaction.response.send_message('Successfuly disabled 2FA.', ephemeral=True)


    @_2fa_register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('> The correct format is `/2fa_register <password> <password>`')
        else:
            raise error
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Delete messages sent in 2FA channel
        if message.channel.id == 1089029172879433938:
            await message.delete()

        # Reset the timer of the user when they send a message
        timers[message.author] = time.time()


async def setup(bot):
    await bot.add_cog(TwoFactor(bot))
