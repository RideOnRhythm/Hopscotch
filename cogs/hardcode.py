from discord.ext import commands
import discord


async def function_1():
    embed = discord.Embed(title='Events', color=discord.Color.orange())
    embed.description = '''Welcome to **Events**! Here we list the active and upcoming events for the server as well as the requirements to participate.

**__Ongoing Events__**
**GRADE COMPETITION (2nd Quarter - Grade 8)**
Event Duration: October 24, 2022 - February 6, 2023
Requirements: Must be a Chit Chatter.
Chit Chatter with the best grades in their report card wins a mystery prize!

**__Upcoming Events__**
**-** There are no upcoming events.
    '''
    return embed

async def function_2():
    embed = discord.Embed(title='Grade Competition', color=discord.Color.orange())
    embed.description = '''**__Event Details__**
**Grade Competition** is an event hosted every school quarter to make studies more fun and encouraging! The member who has the best card grade will win a mystery prize provided and contributed by anonymous chit-chatters! 
*English and Chinese are two separate categories but the point system will be the same for both. 

**Point System:**
A    5 points
A-  4 points
B+  3 points
B    2 points
C   .5 points

**Grade 8**
**Winner of 1st Quarter Competition:** NOT COUNTED!

**Winner of 2nd Quarter Competition:**
English Winner: Denise
CHINESE GO 600 Winner: Daniah
CHINESE GO 500 Winner: Mckylle, Denise
https://discord.com/channels/763218643843678288/858167489799520269/1073906795975807070

**Winner of 3rd Quarter Competition:** ---
**Winner of 4th Quarter Competition:** --- 
    '''
    return embed


class EventsView(discord.ui.View):

    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('Event Summary', 'Grade Competition')
                       ])
    async def function(self, interaction: discord.Interaction,
                              select: discord.ui.Select):
        if select.values[0] == 'Event Summary':
            embed = await function_1()
        elif select.values[0] == 'Grade Competition':
            embed = await function_2()
        await interaction.response.edit_message(embed=embed)


class Hardcode(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def events(self, ctx):
        embed = await function_1()
        await ctx.send(embed=embed, view=EventsView())


async def setup(bot):
    await bot.add_cog(Hardcode(bot))
