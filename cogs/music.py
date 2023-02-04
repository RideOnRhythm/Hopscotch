from discord.ext import commands
import discord
import re
import lavalink
import datetime

url_rx = re.compile(r'https?://(?:www\.)?.+')


class LavalinkVoiceClient(discord.VoiceClient):

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node('localhost', 2333, 'youshallnotpass', 'us',
                                          'default-node')
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {'t': 'VOICE_SERVER_UPDATE', 'd': data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        lavalink_data = {'t': 'VOICE_STATE_UPDATE', 'd': data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self,
                      *,
                      timeout: float,
                      reconnect: bool,
                      self_deaf: bool = False,
                      self_mute: bool = False) -> None:
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel,
                                                    self_mute=self_mute,
                                                    self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        player = self.lavalink.player_manager.get(self.channel.guild.id)
        if not force and not player.is_connected:
            return
        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(1001668250951753738)
            bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'eu',
                                  'default-node')
        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

    @commands.command()
    async def play(self, ctx, *, query):
        if ctx.author.voice is None:
            await ctx.send('Please join a voice channel.')
            return
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        if not results or not results.tracks:
            await ctx.send('No results found.')
            return

        track = results.tracks[0]
        embed = discord.Embed(
            title='Added Track',
            description=
            f'Song: [{track.title}]({track.uri})\nDuration: {str(datetime.timedelta(seconds=track.duration // 1000))}',
            color=discord.Color.blurple())
        await ctx.send(embed=embed)

        player.add(requester=ctx.author.id, track=track)
        await player.play()

    @commands.command()
    async def stop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not ctx.voice_client:
            await ctx.send('Not connected.')
            return
        if not ctx.author.voice or (
                player.is_connected
                and ctx.author.voice.channel.id != int(player.channel_id)):
            await ctx.send('You\'re not in my voicechannel!')
            return

        await player.stop()

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not ctx.voice_client:
            await ctx.send('Not connected.')
            return
        if not ctx.author.voice or (
                player.is_connected
                and ctx.author.voice.channel.id != int(player.channel_id)):
            await ctx.send('You\'re not in my voicechannel!')
            return

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('*⃣ | Disconnected.')

    @commands.command()
    async def queue(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(title='Queue', color=discord.Color.fuchsia())
        for track in player.queue:
            embed.description += f'[{track.title}]({track.uri}) ({str(datetime.timedelta(seconds=track.duration // 1000))})\n'
        await ctx.send(embed=embed)

    @commands.command()
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not ctx.voice_client:
            await ctx.send('Not connected.')
            return
        if not ctx.author.voice or (
                player.is_connected
                and ctx.author.voice.channel.id != int(player.channel_id)):
            await ctx.send('You\'re not in my voicechannel!')
            return

        await player.skip()


async def setup(bot):
    await bot.add_cog(Music(bot))
