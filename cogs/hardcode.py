from discord.ext import commands
import discord


async def function_1():
    embed = discord.Embed(title='Events', color=discord.Color.orange())
    embed.description = '''Welcome to **Events**! Here we list the active and upcoming events for the server as well as the requirements to participate.

**__Ongoing Events__**
**GRADE COMPETITION (3rd Quarter - Grade 8)**
Event Duration: January 23, 2023 - March 24, 2023  (Results will be on April 14)
Requirements: Must be a Chit Chatter.
Chit Chatter with the best grades in their report card wins a mystery prize!

**[SP. EVT]: Mr. Cua "Thank You Letter" in HTML**
Event Duration: March 5, 2023 - March 11, 2023
Requirements: Must be a Chit-Chatter or Mini Chit-Chatter
Contribute as we create an HTML code for our previous computer teacher, Mr. Cua! 

**__Upcoming Events__**
**GRADE COMPETITION (4th Quarter - Grade 8)**
Event Duration: March 27, 2023 - June 2, 2023 
Requirements: Must be a Chit Chatter.
    '''
    return embed


async def function_2():
    embed = discord.Embed(title='Grade Competition',
                          color=discord.Color.orange())
    embed.description = '''**__Event Details__**
**Grade Competition** is an event hosted every school quarter to make studies more fun and encouraging! The member who has the best card grade will win a mystery prize provided and contributed by anonymous chit-chatters! 
*English and Chinese are two separate categories but the point system will be the same for both. 

**Point System:**
A is 5 points
A- is 4 points
B+ is 3 points
B is 2 points
C is .5 points

**Grade 8**
**Winner of 1st Quarter Competition:** NOT COUNTED!

**Winner of 2nd Quarter Competition:**
English Winner: Denise
CHINESE GO 600 Winner: Daniah
CHINESE GO 500 Winner: Mckylle, Denise
>  [Learn more](https://discord.com/channels/763218643843678288/858167489799520269/1073906795975807070)

**Winner of 3rd Quarter Competition:** ---
**Winner of 4th Quarter Competition:** --- 
    '''
    return embed

async def function_3():
    embed = discord.Embed(title='**[SP. EVENT] Mr. Cua "Thank You Letter" in HTML**',
                          color=discord.Color.orange())
    embed.description = '''**__Event Details__**
Contribute as we create an HTML code for our previous computer teacher, Mr. Cua! We will be using REPL so everyone who is interested can update the code real-time! In order to join us, you will have to create your own REPL account. To do that, visit the website https://replit.com/signup and register your own account. Afterwards, click the link below to start editing the code! The event will end on March 11, 2023 and the output will be saved and sent to him. Thanks!

__**Links**__
[REPL](https://replit.com/join/wzymckndww-jaydenis9)
[Canva](https://www.canva.com/design/DAFcYnpsdqs/jSRz5vVGSPDPjJWbF2aiSQ/edit?utm_content=DAFcYnpsdqs&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)
    '''
    return embed

class EventsView(discord.ui.View):

    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('Event Summary', 'Grade Competition', '[SP. EVENT] Mr. Cua "Thank You Letter" in HTML')
                       ])
    async def function(self, interaction: discord.Interaction,
                       select: discord.ui.Select):
        if select.values[0] == 'Event Summary':
            embed = await function_1()
        elif select.values[0] == 'Grade Competition':
            embed = await function_2()
        elif select.values[0] == '[SP. EVENT] Mr. Cua "Thank You Letter" in HTML':
            embed = await function_3()
        await interaction.response.edit_message(embed=embed)


class Hardcode(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=('event', 'evt'))
    async def events(self, ctx):
        embed = await function_1()
        await ctx.send(embed=embed, view=EventsView())


async def setup(bot):
    await bot.add_cog(Hardcode(bot))
