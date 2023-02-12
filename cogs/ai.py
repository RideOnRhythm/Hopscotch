from discord.ext import commands
import os
import discord
import aiohttp
import time
import asyncio
from dotenv import load_dotenv
from chatgpt_wrapper import ChatGPT

load_dotenv()


class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ai_list = []
        self.gpt = ChatGPT()

    @commands.hybrid_command()
    async def enable_ai(self, ctx):
        self.ai_list.append(ctx.author)
        await ctx.send(f'Started a conversation with ChatGPT for {ctx.author.mention}.')
        
        while ctx.author in self.ai_list:

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author and m.author in self.ai_list

            try:
                msg = await client.wait_for('message', check=check, timeout=300.0)
            except asyncio.TimeoutError:
                await ctx.send('No messages have been sent within 5 minutes. Ending conversation.')
                return
            else:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(os.getenv('webhook'),
                                                    session=session)
                    response = ''
                    temp = await webhook.send(content='> Generating response...')
                    timer = time.time()

                    for chunk in self.gpt.ask_stream(msg.content):
                        response += chunk
                        if time.time() - timer >= 5:
                            await temp.edit(content=f'> Generating response...\n\n{response}')
                    
                    await temp.edit(content=response)

    @commands.hybrid_command()
    async def disable_ai(self, ctx):
        if ctx.author in self.ai_list:
            self.ai_list.remove(ctx.author)
            await ctx.send(f'Ended the conversation with ChatGPT for {ctx.author.mention}.')
        else:
            await ctx.send('You are not currently in a conversation.')
    

async def setup(bot):
    await bot.add_cog(Ai(bot))
