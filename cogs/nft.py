from discord.ext import commands
import discord
import aiohttp
import random
import os.path
import io


class Nft(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nft(self, ctx, amount=1):
        files = []
        for i in range(amount):
            with open(
                    os.path.dirname(__file__) + '/../assets/nft_list.txt',
                    'r') as f:
                urls = f.read().split('\n')
                url = random.choice(urls)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    img = await resp.read()
                    with io.BytesIO(img) as file:
                        files.append(discord.File(file, 'generated_nft.png'))
        await ctx.send(files=files)
    
    @commands.command()
    async def add_nft(self, ctx, image: typing.Union[str, discord.Attachment]):
        with open(os.path.dirname(__file__) + '/../assets/nft_list.txt',
                  'a') as f:
            if isinstance(image, str):
                f.write(f'{image}\n')
            else:
                f.write(f'{image.url}\n')
        await ctx.send('Added image.')



async def setup(bot):
    await bot.add_cog(Nft(bot))
