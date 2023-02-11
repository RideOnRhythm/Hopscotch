from discord.ext import commands
import os
import openai
import discord
import aiohttp
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('openai')


class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def ai(self, ctx, *, prompt):
        response = openai.Completion.create(model='text-davinci-003',
                                            prompt=prompt,
                                            temperature=0.8,
                                            max_tokens=60,
                                            top_p=1.0,
                                            frequency_penalty=0.5,
                                            presence_penalty=0.0)
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(os.getenv('webhook'),
                                               session=session)
            await webhook.send(content=response['choices'][0]['text'])


async def setup(bot):
    await bot.add_cog(Ai(bot))
