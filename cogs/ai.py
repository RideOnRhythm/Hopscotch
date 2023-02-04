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
                                            prompt=f'\n\nFriend: {prompt}',
                                            temperature=0.9,
                                            max_tokens=150,
                                            top_p=1,
                                            frequency_penalty=0.0,
                                            presence_penalty=0.6)
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                os.getenv('webhook'),
                session=session)
            await webhook.send(content=response['choices'][0]['text'])

    @commands.hybrid_command()
    async def aitype(self, ctx, type='chat', *, prompt):
        if type == 'chat':
            response = openai.Completion.create(
                model='text-davinci-003',
                prompt=
                f'The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: {prompt}\nAI:',
                temperature=0.9,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                stop=["AI:"])
        elif type == 'friend':
            response = openai.Completion.create(
                model='text-davinci-003',
                prompt=f'\n\nFriend: {prompt}\nYou:',
                temperature=0.5,
                max_tokens=60,
                top_p=1.0,
                frequency_penalty=0.5,
                presence_penalty=0.0,
                stop=["You:"])
        elif type == 'python':
            response = openai.Completion.create(model='code-davinci-002',
                                                prompt=prompt,
                                                temperature=0,
                                                max_tokens=64,
                                                top_p=1.0,
                                                frequency_penalty=0.0,
                                                presence_penalty=0.0)
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(
                    'https://discord.com/api/webhooks/1069966968108626031/dOzeEiWCh016hjKsw0fNh_L-foKYYIxyFV_HQgFGNeltoOmRTXnSxUkxxA6kILUQHcQB',
                    session=session)
                await webhook.send(content=response['choices'][0]['text'])


async def setup(bot):
    await bot.add_cog(Ai(bot))
