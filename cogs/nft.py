from discord.ext import commands
import discord
import aiohttp
import random


class Nft(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nft(self, ctx):
        with open('../assets/nft_list.txt', 'r') as f:
            urls = f.read().split('\n')
            url = random.choice(urls)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file: 
                    await ctx.send(file=discord.File(file, "generated_nft.png"))



async def setup(bot):
    await bot.add_cog(Nft(bot))

