from discord.ext import commands
import os
import discord
import time
import asyncio
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('openai')


class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ai_list = []

    @commands.hybrid_command()
    async def enable_ai(self, ctx):
        self.ai_list.append(ctx.author)
        await ctx.send(f'Started a conversation with ChatGPT for {ctx.author.mention}.')
        
        while ctx.author in self.ai_list:

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author and m.author in self.ai_list

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            except asyncio.TimeoutError:
                await ctx.send('No messages have been sent within 5 minutes. Ending conversation.')
                return
            else:
                response = ''
                temp = await ctx.send(content='> Generating response...')

                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'user', 'content': msg.content}
                    ]
                )
                await temp.edit(content=response['choices'][0]['message']['content'])

    @commands.hybrid_command()
    async def disable_ai(self, ctx):
        if ctx.author in self.ai_list:
            self.ai_list.remove(ctx.author)
            await ctx.send(f'Ended the conversation with ChatGPT for {ctx.author.mention}.')
        else:
            await ctx.send('You are not currently in a conversation.')
    
    @commands.hybrid_command()
    async def ai(self, ctx, *, prompt):
        response = ''
        temp = await ctx.send(content='> Generating response...')

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        await temp.edit(content=response['choices'][0]['message']['content'])
    

async def setup(bot):
    await bot.add_cog(Ai(bot))
