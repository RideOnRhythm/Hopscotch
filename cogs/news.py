import math
from discord.ext import commands
from discord.ext import tasks
import aiohttp
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import geopy.distance


async def get_quake_info():
    async with aiohttp.ClientSession() as session:
        # Make GET requests to PHIVOLCS latest earthquake information
        async with session.get('https://earthquake.phivolcs.dost.gov.ph/') as resp:
            text = await resp.text()
            soup = BeautifulSoup(text, features='html5lib')
            # This will select the latest earthquake <tr> element
            quake_tr = soup.select_one('div.auto-style94 > table:nth-child(4) > tbody:nth-child(1) > tr:nth-child(2)')

            quake_tds = quake_tr.find_all('td')
            # Gets the quake info by navigating each <td> element in the <tr>
            try:
                date = quake_tds[0].find_all('span')[1].find_all('a')[0].find_all('span')[0]
            except IndexError:  # Workaround as the website can either put the text inside the <a> directly or in a <span>
                date = quake_tds[0].find_all('span')[1].find_all('a')[0]
            quake_info = {
                'date': date.text,
                'latitude': quake_tds[1].text.strip(),
                'longitude': quake_tds[2].text,
                'depth': quake_tds[3].text,
                'magnitude': quake_tds[4].text
            }
            return quake_info


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quake_refresh.start()
        self.latest_quake = None

    @tasks.loop(seconds=10)
    async def quake_refresh(self):
        quake_info = await get_quake_info()

        # Return if no new quake has occurred
        if self.latest_quake is None or quake_info == self.latest_quake:
            return
        self.latest_quake = quake_info
        
        # Calculate distance in kilometers
        coords_1 = (float(quake_info['latitude']), float(quake_info['longitude']))
        coords_2 = (14.5995, 120.9842)
        km_distance = geopy.distance.geodesic(coords_1, coords_2).km
        # Formula to estimate the intensity of the earthquake in Modified Mercalli Intensity Scale
        # ty chatgpt
        if 1/2 * float(quake_info['magnitude']) + math.log10(km_distance/10) < 3:
            return
        
        # Get epicenter address
        geolocator = Nominatim(user_agent='Hopscotch Quake Info')
        location = geolocator.reverse(f'{quake_info["latitude"].strip()} {quake_info["longitude"]}')
        description = f'''<@&1090514249564033114>
        
An earthquake has recently occurred near **{location.address}** with magnitude **{quake_info['magnitude']}**. You are expected to feel shaking in your area soon.

- **DROP** down onto your hands and knees before the earthquake knocks you down. This position protects you from falling but allows you to still move if necessary.
- **COVER** your head and neck (and your entire body if possible) underneath a sturdy table or desk. If there is no shelter nearby, get down near an interior wall or next to low-lying furniture that won't fall on you, and cover your head and neck with your arms and hands.
- **HOLD ON** to your shelter (or to your head and neck) until the shaking stops. Be prepared to move with your shelter if the shaking shifts it around.'''

        # Make a post in the #server-forums channel
        forum_channel = self.bot.get_channel(1085469323952402442)
        news_tag = next(tag for tag in forum_channel.available_tags if tag.name == 'News')
        await forum_channel.create_thread(name='Earthquake Warning', content=description, applied_tags=[news_tag])


async def setup(bot):
    await bot.add_cog(News(bot))
