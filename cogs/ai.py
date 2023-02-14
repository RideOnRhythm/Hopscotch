from discord.ext import commands
import os
import discord
import time
import asyncio
import openai
from dotenv import load_dotenv
from chatgpt_wrapper import ChatGPT

load_dotenv()
openai.api_key = os.getenv('openai')


class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ai_list = []
        self.gpt = ChatGPT()
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.gpt.async_init()

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
                timer = time.time()

                try:
                    async for chunk in self.gpt.ask_stream(msg.content):
                        response += chunk
                        if time.time() - timer >= 3:
                            timer = time.time()
                            await temp.edit(content=f'> Generating response...\n\n{response}')
                    await temp.edit(content=response)
                except:
                    response = openai.Completion.create(
                        model='text-davinci-003'.
                        prompt=f'The following is a conversation with an AI chatbot. The chatbot is helpful, creative, clever, very friendly, and also humorous.\n\nHuman: {prompt}\nAI:',
                        temperature=0.9,
                        max_tokens=150,
                        top_p=1,
                        frequency_penalty=0.0,
                        presence_penalty=0.6,
                        stop=['AI:']
                    )
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
