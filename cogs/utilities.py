from discord.ext import commands
import discord
import googleapiclient
import random
import aiohttp
import typing
import datetime
import requests
import time
import os
import tweepy
from googleapiclient.discovery import build
from assets import database
from bs4 import BeautifulSoup
from bs4 import NavigableString

cached_forecast = None
cache_time = None

auth = tweepy.OAuthHandler(os.getenv('ckey'), os.getenv('secret'))
auth.set_access_token(os.getenv('access'), os.getenv('atsecret'))
client = tweepy.API(auth)


def minigames_embed():
    embed = discord.Embed(title='Hopscotch Commands',
                          description='''**__Minigames__**
**Connect Four** - Connect four dots to win.
`j.connectfour`, `j.c4`, `j.connect4`

**Coinflip** - Make a bet with your opponent using a coin!
`j.coinflip`, `j.cf`''',
                          color=discord.Color.red())
    return embed


def statistics_embed():
    embed = discord.Embed(title='Hopscotch Commands',
                          description='''**__Statistics__**
**Profile** - shows if you are active, your level, messages, coins, gems, and games
`j.profile`,` j.p`

**Coins** - shows your total coins and gems
`j.coins`, `j.c`

**Leaderboard** - shows the top 10 members in the server (categories: coins, level, wins; defaults to coins)
`j.leaderboard`, `j.lb`, `j.top`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀example: j.leaderboard coins''',
                          color=discord.Color.red())
    return embed


def utilities_embed():
    embed = discord.Embed(title='Hopscotch Commands',
                          description='''**__Utilities__**
**Showimage** - shows an image according to your search
`j.showimage (text)`, `j.showpic (text)`, `j.sp (text)`

**Dictionary** - tells the definition of a word
`j.dictionary (word)`, `j.dict (word)`, `j.dic (word)`, `j.d (word)`

**Active Now** - shows the active members and what channel they are in
`j.activenow`, `j.active_now`, `j.active`, `j.acn`, `j.ac`

**Members** - shows the list of all the chit chatters and eggs and if they are active or not
`j.members`, `j.member`, `j.m`''',
                          color=discord.Color.red())
    return embed


class HelpButtons(discord.ui.View):

    def __init__(self,
                 author: typing.Union[discord.Member, discord.User],
                 timeout=180):
        self.author = author
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id

    @discord.ui.button(label="Minigames", style=discord.ButtonStyle.primary)
    async def minigames_button(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        await interaction.response.edit_message(embed=minigames_embed())

    @discord.ui.button(label="Statistics", style=discord.ButtonStyle.primary)
    async def statistics_button(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        await interaction.response.edit_message(embed=statistics_embed())

    @discord.ui.button(label="Utilities", style=discord.ButtonStyle.primary)
    async def utilities_button(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        await interaction.response.edit_message(embed=utilities_embed())


async def get_forecast_async():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'https://www.pagasa.dost.gov.ph/weather/') as resp:
            text = await resp.text()
            parsed_html = BeautifulSoup(text, features='html5lib')
            parsed_html = parsed_html.body.find('table',
                                                attrs={
                                                    'class': 'table'
                                                }).find('tbody')
            return parsed_html


def get_forecast():
    resp = requests.get('https://www.pagasa.dost.gov.ph/weather/')
    text = resp.text
    parsed_html = BeautifulSoup(text, features='html5lib')
    parsed_html = parsed_html.body.find('table', attrs={
        'class': 'table'
    }).find('tbody')
    return parsed_html


class WeatherView(discord.ui.View):

    def __init__(self, forecast, timeout=180):
        self.forecast = forecast
        super().__init__(timeout=timeout)

    @discord.ui.select(
        cls=discord.ui.Select,
        options=[
            discord.SelectOption(label=label.find_all('td')[0].text[:100])
            for label in get_forecast().find_all('tr')
        ])
    async def location_select(self, interaction: discord.Interaction,
                              select: discord.ui.Select):
        for i in self.forecast.find_all('tr'):
            if isinstance(i, NavigableString):
                continue
            if select.values[0] == i.find_all('td')[0].text[:100]:
                location_forecast = i
                break

        embed = discord.Embed(
            title='Forecast Weather Conditions',
            description=
            '*Data from [https://www.pagasa.dost.gov.ph/](https://www.pagasa.dost.gov.ph/)*',
            color=discord.Color.dark_teal())
        embed.add_field(name='Place',
                        value=location_forecast.find_all('td')[0].text)
        embed.add_field(name='Weather Condition',
                        value=location_forecast.find_all('td')[1].text)
        embed.add_field(name='Caused By',
                        value=location_forecast.find_all('td')[2].text)
        embed.add_field(name='Impacts',
                        value=location_forecast.find_all('td')[3].text)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Daily Forecast",
                       style=discord.ButtonStyle.primary)
    async def daily_forecast(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        global cached_forecast
        global cache_time
        if cached_forecast is None:
            forecast = await get_forecast_async()
            cached_forecast = forecast
            cache_time = time.time()
        else:
            if cache_time is not None:
                if time.time() - cache_time > 7200:
                    forecast = await get_forecast_async()
                    cached_forecast = forecast
                    cache_time = time.time()
                else:
                    forecast = cached_forecast
        for i in forecast.find_all('tr'):
            if isinstance(i, NavigableString):
                continue
            if 'Metro Manila' in i.find_all('td')[0].text:
                location_forecast = i
                break

        embed = discord.Embed(
            title='Forecast Weather Conditions',
            description=
            '*Data from [https://www.pagasa.dost.gov.ph/](https://www.pagasa.dost.gov.ph/)*',
            color=discord.Color.dark_teal())
        embed.add_field(name='Place',
                        value=location_forecast.find_all('td')[0].text)
        embed.add_field(name='Weather Condition',
                        value=location_forecast.find_all('td')[1].text)
        embed.add_field(name='Caused By',
                        value=location_forecast.find_all('td')[2].text)
        embed.add_field(name='Impacts',
                        value=location_forecast.find_all('td')[3].text)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Thunderstorm Advisory",
                       style=discord.ButtonStyle.primary)
    async def tstorm_advisory(self, interaction: discord.Interaction,
                              button: discord.ui.Button):
        tweets = client.user_timeline(user_id=202890266)
        tstm_tweet = None
        for tweet in tweets:
            if 'Thunderstorm' in tweet.text:
                tstm_tweet = tweet
                break

        embed = discord.Embed(title='Thunderstorm Advisory',
                              color=discord.Color.dark_teal())
        if tstm_tweet is None:
            embed.description = 'No recent Thunderstorm Advisory.'
        else:
            embed.description = tstm_tweet.text
            if 'media' in tweet.entities:
                embed.set_image(url=tweet.entities['media'][0]['media_url'])
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Rainfall Advisory",
                       style=discord.ButtonStyle.primary)
    async def rainfall_advisory(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        tweets = client.user_timeline(user_id=202890266)
        tstm_tweet = None
        for tweet in tweets:
            if 'RAINFALL ADVISORY' in tweet.text:
                tstm_tweet = tweet
                break

        embed = discord.Embed(title='Rainfall Advisory',
                              color=discord.Color.dark_teal())
        if tstm_tweet is None:
            embed.description = 'No recent Rainfall Advisory.'
        else:
            embed.description = tstm_tweet.text
            if 'media' in tweet.entities:
                embed.set_image(url=tweet.entities['media'][0]['media_url'])
        await interaction.response.edit_message(embed=embed)


class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(aliases=('sp', 'showimage', 'sendmeapicshawty'))
    async def showpic(self, ctx, *, query):
        rand = random.randint(0, 9)
        resource = build(
            'customsearch',
            'v1',
            developerKey='AIzaSyCb0AOgORJJc90al6H5_FjY2PwQA0ikOcM').cse()

        try:
            result = resource.list(q=f'{query}',
                                   cx='0f1a9f84529a968c1',
                                   searchType='image',
                                   safe='active',
                                   imgType='photo').execute()
        except googleapiclient.errors.HttpError:
            await ctx.send(
                'Sorry, due to Google’s API restrictions, I can no longer show pictures. Please try again later.'
            )
            return

        try:
            # Easter Eggs
            now = datetime.datetime.now(
                tz=datetime.timezone(datetime.timedelta(hours=8)))
            x = int(str(now.hour) + str(now.minute))
            if query == 'ylzfhf':
                url = 'https://media.discordapp.net/attachments/994945251565371606/1056173290508521552/tenor_6.gif'
                image_title = 'Halt - DOORS Wiki - Fandom'
            elif 'ed sheeran' in query.lower() and random.randint(1, 5) == 1:
                url = 'https://media.discordapp.net/attachments/858167284069302292/1056926496436006944/Screen_Shot_2022-09-08_at_9.30.31_PM.png'
                image_title = result['items'][rand]['title']
            elif query == str(x**2 - 3 * x + 2):
                url = 'https://media.discordapp.net/attachments/858167284069302292/1058755582900846672/image.png'
                image_title = '⠀'
            else:
                url = result['items'][rand]['link']
                image_title = result['items'][rand]['title']
        except (IndexError, KeyError):
            await ctx.send('No results found.')
            return
        random.seed(query)
        embed = discord.Embed(title=image_title,
                              color=discord.Colour.from_hsv(
                                  random.random(), 0.5, 1))
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        await database.set_attribute(self.bot.database, ctx.author, 1,
                                     'command_count')
        await database.set_xp(self.bot.database, ctx.author, 2)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=('d', 'dic', 'dict', 'dick'))
    async def dictionary(self, ctx, *, word):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
            ) as resp:
                result = await resp.json()

        if isinstance(result, dict):
            if result.get('title') == 'No Definitions Found':
                await ctx.send('No definitions found.')
                return

        embeds = []
        for word in result[:10]:
            random.seed(word['word'])
            embed = discord.Embed(title=word['word'],
                                  color=discord.Colour.from_hsv(
                                      random.random(), 0.5, 1))
            for meaning in word['meanings'][:10]:
                value = ''
                for definition in meaning['definitions'][:10]:
                    value += ' • ' + definition['definition'] + '\n'
                embed.add_field(name=meaning['partOfSpeech'],
                                value=value[:1024],
                                inline=False)
            embeds.append(embed)

        webhooks = await ctx.channel.webhooks()
        webhook = discord.utils.find(
            lambda w: w.name == 'Hopscotch Dictionary', webhooks)
        if not webhook:
            print('creating webhook')
            webhook = await ctx.channel.create_webhook(
                name='Hopscotch Dictionary')

        await webhook.send(embeds=embeds)
        await database.set_attribute(self.bot.database, ctx.author, 1,
                                     'command_count')
        await database.set_xp(self.bot.database, ctx.author, 2)

    @commands.command()
    async def ervin(self, ctx):
        await ctx.send('the ervin')

    @commands.command()
    async def nerf(self, ctx):
        await ctx.send('pew pew')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{int(self.bot.latency * 1000)}ms ― **Replit**')

    @commands.hybrid_command()
    async def help(self, ctx):
        await ctx.send(embed=minigames_embed(), view=HelpButtons(ctx.author))
        await database.set_attribute(self.bot.database, ctx.author, 1,
                                     'command_count')

    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.hybrid_command()
    async def weather(self, ctx):
        global cached_forecast
        global cache_time
        if cached_forecast is None:
            forecast = await get_forecast_async()
            cached_forecast = forecast
            cache_time = time.time()
        else:
            if cache_time is not None:
                if time.time() - cache_time > 7200:
                    forecast = await get_forecast_async()
                    cached_forecast = forecast
                    cache_time = time.time()
                else:
                    forecast = cached_forecast
        for i in forecast.find_all('tr'):
            if isinstance(i, NavigableString):
                continue
            if 'Metro Manila' in i.find_all('td')[0].text:
                location_forecast = i
                break

        embed = discord.Embed(
            title='Forecast Weather Conditions',
            description=
            '*Data from [https://www.pagasa.dost.gov.ph/](https://www.pagasa.dost.gov.ph/)*',
            color=discord.Color.dark_teal())
        embed.add_field(name='Place',
                        value=location_forecast.find_all('td')[0].text)
        embed.add_field(name='Weather Condition',
                        value=location_forecast.find_all('td')[1].text)
        embed.add_field(name='Caused By',
                        value=location_forecast.find_all('td')[2].text)
        embed.add_field(name='Impacts',
                        value=location_forecast.find_all('td')[3].text)
        await ctx.send(embed=embed, view=WeatherView(forecast))
        await database.set_attribute(self.bot.database, ctx.author, 1,
                                     'command_count')


async def setup(bot):
    await bot.add_cog(Utilities(bot))
