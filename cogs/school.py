from discord.ext import commands
from discord.ext import tasks
import discord
from assets import database
from itertools import groupby
import datetime
import time


class RemindersView(discord.ui.View):

    def __init__(self, cog, timeout=180):
        self.cog = cog
        super().__init__(timeout=timeout)

    @discord.ui.select(
        cls=discord.ui.Select,
        options=[
            discord.SelectOption(label=label)
            for label in ('8 - Violet', '8 - Aqua', 'Chinese Go: 600A',
                          'Chinese Go: 500B', 'Chinese Go: 500A')
        ])
    async def section_select(self, interaction: discord.Interaction,
                             select: discord.ui.Select):
        sections = {
            '8 - Violet': 'violet',
            '8 - Aqua': 'aqua',
            'Chinese Go: 600A': '600a',
            'Chinese Go: 500B': '500b',
            'Chinese Go: 500A': '500a'
        }
        embed = await section_reminders(self.cog, sections[select.values[0]])
        await interaction.response.edit_message(embed=embed)


async def section_reminders(self, section):
    titles = {
        'violet': 'Reminders — 8 - Violet',
        'aqua': 'Reminders — 8 - Aqua',
        '500a': 'Reminders — Chinese Go: 500A',
        '500b': 'Reminders — Chinese Go: 500B',
        '600a': 'Reminders — Chinese Go: 600A'
    }
    colors = {
        'violet': 0x8f00ff,
        'aqua': 0x00ffff,
        '500a': 0xeded09,
        '500b': 0x000080,
        '600a': 0xff6961
    }
    embed = discord.Embed(title=titles[section], color=colors[section])
    reminders = await database.get_other_attribute(self.bot.database,
                                                   'reminders')
    reminders = list(filter(lambda r: r['section'] == section, reminders))
    reminders.sort(key=lambda r: r['unix'], reverse=True)
    dates = {}
    for key, group in groupby(
            reminders, lambda r: datetime.date.fromtimestamp(r['unix'])):
        dates[key] = list(group)

    for group in dates:
        saved_unix = int(time.mktime(group.timetuple()))
        if saved_unix - int(time.time()) <= 86400 and saved_unix - int(
                time.time()) > 0:
            when = ' — __**TOMORROW**__'
        else:
            when = ''
        if int(time.mktime(group.timetuple())) == 9999993600:
            field_name = 'Unknown'
        else:
            field_name = f'<t:{int(time.mktime(group.timetuple()))}:D>{when}'
        embed.add_field(name=field_name,
                        value='\n'.join(
                            [reminder['text'] for reminder in dates[group]]),
                        inline=False)
    if len(dates) == 0:
        fancy = {
            'violet': '8 - Violet',
            'aqua': '8 - Aqua',
            '500a': '500A',
            '500b': '500B',
            '600a': '600A'
        }
        embed.description = f'There are currently no school reminders for {fancy[section]}.'
    return embed


class Schedule(discord.ui.View):

    def __init__(self, cog, timeout=180):
        self.cog = cog
        super().__init__(timeout=timeout)

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('8 - Violet', '8 - Aqua')
                       ])
    async def section_select(self, interaction: discord.Interaction,
                             select: discord.ui.Select):
        sections = {'8 - Violet': 'violet', '8 - Aqua': 'aqua'}
        embed = await schedule(self.cog, sections[select.values[0]])
        await interaction.response.edit_message(embed=embed)


async def schedule(self, section):
    titles = {
        'violet': 'Reminders — 8 - Violet',
        'aqua': 'Reminders — 8 - Aqua'
    }
    colors = {'violet': 0x8f00ff, 'aqua': 0x00ffff}
    image = {
        'violet':
        "https://media.discordapp.net/attachments/1015572867267707024/1038797451311722549/unknown.png?width=1188&height=701",
        'aqua':
        "https://media.discordapp.net/attachments/1015572867267707024/1038797487445655602/unknown.png?width=1051&height=701"
    }
    embed = discord.Embed(title=titles[section], color=colors[section])
    embed.set_image(url=image[section])
    return embed


async def contacts(category):
    strs = {
        'Admins': '**Alimpolo, Merriam**: meriamalimpolo1217@sshs.edu.ph\n**Belton, Margaret**: mbelton@sshs.edu.ph\n**Belton, James**: jbelton@sshs.edu.ph\n**Chen, Jane**: jpc@sshs.edh.ph\n**Chu, Jocelyn**: jpchu@sshs.edu.ph\n**Chua, Lilan**: lanpchua@sshs.edu.ph\n**Dueñas, Joy**: jmduenas@sshs.edu.ph\n**Endo, Milagros**: maendo@sshs.edu.ph\n**Gutierrez, Antonio Angelo**: agutierrez@sshs.esu.ph\n**Keng, Elizabeth**: eckeeng@sshs.edu.ph\n**Lim, Conchita**: conchitalim@sshs.edu.ph / clim@sshs.edu.ph\n**Lim, Natalie**: lizalim@sshs.edu.ph\n**Lim, Liza Lynn**: nlim@sshs.edu.ph\n**Ngo, Wilson**: coachwngo@sshs.edu.ph\n**Recosana, Ma. Christina**: trecosana@sshs.edu.ph\n**So, Freddie**: coachfso@sshs.edu.ph\n**Sy, Judith**: juoungsy@sshs.edu.ph\n**Tacus, Josie**: jo_tacus@sshs.edu.ph\n**Tan, Judy**: jtan@sshs.edu.ph\n**Yu, Brenda**: brendsyu@sshs.edu.ph\n**Yu, Ulysses**: dr.ulyyu@sshs.edu.ph',
        'HS English': '**\\*Adonis, Abigail Elinor N.**: aeadonis@sshs.edu.ph\n**\\*Aguila, Alan Betuel O.**: abaguila@sshs.edu.ph\n**Barbo, Randy B.**: rbarbo@sshs.edu.ph\n**Berdan, Rene Daniel**: daniel.berdan.kr@gmail.com\n**Bonifacio, Renz Hector**: troysophia5@gmail.com\n**Briones, Chariza A.**: cbriones@sshs.edu.ph\n**Bunagan, Ferlie**: fbunagan@sshs.edu.ph\n**\\*Cabansag, Henry**: hcabansag@sshs.edu.ph\n**\\*Ching, Elwin B.**: eching@sshs.edu.ph\n**Dela Cruz, Maribeth**: mdelacruz@sshs.edu.ph\n**Dy. Kathleen Dianne K.**: kddy@sshs.edu.ph\n**\\*Garcia, Isaiah F.**: igarcia@sshs.edu.ph\n**\\*Gayares, Joseph D.**: igayares@sshs.edu.ph\n**Ibasco, Anna Paula A.**: apibasco@sshs.edu.ph\n**\\*Laude, Sherylou Dela Torre**: slaude@sshs.edu.ph\n**Lee, Chester Howard**: leechesterhoward@gmail.com\n**\\*Liwanag, Katrine S.**: kliwanag@sshs.edu.ph\n**\\*Lopez, Ramon**: rlopez@sshs.edu.ph\n**\\*Lumbang, Geenross Ashley**: galumbang@sshs.edu.ph\n**\\*Mallari, Rosalita O.**: rmallari@sshs.edu.ph\n**Manalili, Trina Arrianne C.**: tmanalili@sshs.edu.ph\n**\\*Ong. Stefhanie Kaye**: skong@sshs.edu.ph\n**\\*Panes, Agnes C.**: apanes@sshs.edu.ph\n**Ping, Arniel V.**: aping@sshs.edu.ph\n**\\*Ramos, Jonah Leigh**: jlramos@sshs.edu.ph\n**\\*Recosana Jr. Leonardo P.**: lirecosana@sshs.edu.ph\n**Romo, Anne-Louie Chua Dy**: alromo@sshs.edu.ph\n**Roncal, James**: jroncal@sshs.edu.ph \n**\\*Serrato, Jamielyn**: jserrato@sshs.edu.ph\n**Simon, Rhenish**: rcsimon@sshs.edu.ph\n**Sy, Jiko Aldrei**: jsy@sshs.edu.ph\n**Sy, Marie Ann Michelle B.**: msy@sshs.edu.ph\n**Tabuclao, Criselda O.**: ctabuclao@sshs.edu.ph\n**Tan. Anne Carleen**: atan@sshs.edu.ph\n**Torres, Eleazar**: etorres@sshs.edu.ph\n**\\*Yap. Sharmagne Alison**: syap@sshs.edu.ph\n**Albano, Menelyn**: menelynalbano@sshs.edu.ph\n**Sablaya, Mylene M**: mylenesablaya@sshs.edu.ph',
        'ELEM Chinese': '**Cham, Aniceto**: acham@sshs.edu.ph\n**Chia, Susan**: schia@sshs.edu.ph\n**Choi, Man Ngar**: ichoi@sshs.edu.ph\n**Chong, Getheline**: gchong@sshs.edu.ph\n**Lim, Mimi**: mlim@sshs.edu.ph\n**Malubag, Colleene**: cmalubag@sshs.edu.ph\n**Ong, Chun Chun Sally**: song@sshs.edu.ph\n**Tao, Ling**: tling@sshs.edu.ph\n**Yu, Ming Lai**: ymlai@sshs.edu.ph',
        'HS Chinese': '**Chong, Ellen**: echong@sshs.edu.ph\n**Dy Un Hua**: uhdy@sshs.edu.ph\n**Francisco, Gabriel Marie**: gfrancisco@sshs.edu.ph\n**Liao Chiu Lan**: sliao@sshs.edu.ph\n**Sy, Henry**: hsy@sshs.edu.ph\n**Sy, Sally**: ssy@sshs.edu.ph\n**Wang Yang**: ywang@sshs.edu.ph\n**Yao, Liging**: Iqyao@sshs.edu.ph\n**Zhou Yue**: yzhou@sshs.edu.ph',
        'HS Chinese (Taiwan Teachers)': '**Yi-Shan Yang**: ysyang@sshs.edu.ph\n**Liang-Yu Chen**: lychen@sshs.edu.ph\n**Yi-Hsuan Lai**: yhlai@sshs.edu.ph\n**Feng Hsuan Liang**: fhliang@sshs.edu.ph\n**Cheh Yu Wu**: cywu@sshs.edu.ph\n**Hsi Mei Chiang**: hmchiang@sshs.edu.ph\n**Shing-Jen Tsai**: sjtsai@sshs.edu.ph'
    }
    embed = discord.Embed(title=category, description=strs[category], color=discord.Color.random(seed=category))
    return embed


class ContactsView(discord.ui.View):

    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('Admins', 'HS English', 'ELEM Chinese', 'HS Chinese', 'HS Chinese (Taiwan Teachers)')
                       ])
    async def category_select(self, interaction: discord.Interaction,
                             select: discord.ui.Select):
        embed = await contacts(select.values[0])
        await interaction.response.edit_message(embed=embed)


class School(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.auto_remove.start()
        self.nails_check.start()

    @tasks.loop(hours=1)
    async def auto_remove(self):
        reminders = await database.get_other_attribute(self.bot.database,
                                                       'reminders')
        for reminder in reminders:
            reminder_dt = datetime.datetime.fromtimestamp(
                reminder['unix'],
                tz=datetime.timezone(datetime.timedelta(hours=8)))
            now = datetime.datetime.now(
                tz=datetime.timezone(datetime.timedelta(hours=8)))
            total_seconds = now - reminder_dt
            total_seconds = total_seconds.total_seconds()
            if total_seconds > 86400 or now.timetuple(
            ).tm_yday > reminder_dt.timetuple().tm_yday:
                await database.remove_reminder(self.bot.database, reminder)

    @commands.command(aliases=('sc', 'sched'))
    async def schedule(self, ctx, section=None):
        violet = ctx.guild.get_role(858224685686325268)
        if section is None:
            if violet in ctx.author.roles:
                section = 'violet'
            else:
                section = 'aqua'
        embed = await schedule(self, section)
        await ctx.send(embed=embed, view=Schedule(self))
        await database.set_attribute(self.bot.database, ctx.author, 1,
                                     'command_count')
        await database.set_xp(self.bot.database, ctx.author, 1)

    @commands.command(aliases=('reminder', 'rm', 'rem'))
    async def reminders(self, ctx, section=None):
        violet = ctx.guild.get_role(858224685686325268)
        if section is None:
            if violet in ctx.author.roles:
                section = 'violet'
            else:
                section = 'aqua'
        embed = await section_reminders(self, section)
        await ctx.send(embed=embed, view=RemindersView(self))
        await database.set_attribute(self.bot.database, ctx.author, 1,
                                     'command_count')
        await database.set_xp(self.bot.database, ctx.author, 1)

    @commands.command(aliases=('arm', 'add rm'))
    async def add_reminder(self, ctx, unix, text, section):
        if ctx.author.id not in (748388929631289436, 556307832241389581,
                                 994223267462258688):
            return
        if unix == 'unknown':
            unix = 9999999999
        else:
            unix = int(unix) * 86400 + int(time.time())
        await database.add_reminder(
            self.bot.database,
            {
                'unix': unix,
                'text': text,
                'section': section
            },
        )
        await ctx.send('Reminder added.')

    @commands.command(aliases=('rrm', 'remove rm'))
    async def remove_reminder(self, ctx, section, text):
        if ctx.author.id not in (748388929631289436, 556307832241389581,
                                 994223267462258688):
            return
        reminders = await database.get_other_attribute(self.bot.database,
                                                       'reminders')
        for i in reminders:
            if text in i['text'] and section == i['section']:
                await database.remove_reminder(self.bot.database, i)
                await ctx.send('Reminder removed.')
                return

    @commands.command(aliases=('erm', 'edit rm'))
    async def edit_reminder(self, ctx, section, text, edit, value):
        if ctx.author.id not in (748388929631289436, 556307832241389581,
                                 994223267462258688):
            return
        reminders = await database.get_other_attribute(self.bot.database,
                                                       'reminders')
        for i in reminders:
            if text in i['text'] and section == i['section']:
                print('a')
                if 'unix' in edit:
                    await database.reminder_unix(
                        self.bot.database,
                        int(value) * 86400 + int(time.time()),
                        reminders.index(i))
                    await ctx.send('Reminder edited.')
                    return
                if 'text' in edit:
                    await database.reminder_text(self.bot.database, value,
                                                 reminders.index(i))
                    await ctx.send('Reminder edited.')
                    return
                if 'section' in edit:
                    await database.reminder_section(self.bot.database, value,
                                                    reminders.index(i))
                    await ctx.send('Reminder edited.')
                    return

    @commands.command(aliases=('tdl', 'todolist'))
    async def to_do_list(self, ctx, *, add=None):
        tdl = await database.get_attribute(self.bot.database, ctx.author,
                                           'to_do_list')
        embed = discord.Embed(title='To Do List', color=discord.Color.blue())
        embed.description = ''
        if add is None:
            for i in tdl:
                embed.description += f'- {i}\n'
            if len(tdl) == 0:
                embed.description += 'You have nothing to do. \n**Now go touch some grass instead of being on Discord all day.**'
            await ctx.send(embed=embed)
        else:
            await database.add_tdl(self.bot.database, ctx.author, add,
                                   'to_do_list')
            await ctx.send('Added.')
        await database.set_attribute(self.bot.database, ctx.author, 1,
                                     'command_count')
        await database.set_xp(self.bot.database, ctx.author, 1)

    @commands.command(aliases=('tdl_done', 'tdld', 'tdl_finish'))
    async def to_do_list_done(self, ctx, remove):
        tdl = await database.get_attribute(self.bot.database, ctx.author,
                                           'to_do_list')
        for i in tdl:
            if remove in i:
                await database.remove_tdl(self.bot.database, ctx.author, i,
                                          'to_do_list')
                await ctx.send('Removed.')
                return

    @commands.command(aliases=('liwanag_check_nails', 'nails'))
    async def nails_reminder(self, ctx):
        check = await database.get_attribute(self.bot.database, ctx.author,
                                             'nails_check')
        if check == True:
            await database.set_attribute(self.bot.database,
                                         ctx.author,
                                         False,
                                         'nails_check',
                                         increment=False)
            await ctx.send("Reminder disabled.")
        else:
            await database.set_attribute(self.bot.database,
                                         ctx.author,
                                         True,
                                         'nails_check',
                                         increment=False)
            await ctx.send("Reminder enabled")

    @tasks.loop(minutes=1)
    async def nails_check(self):
        last_nails = await database.get_other_attribute(
            self.bot.database, 'last_nails')
        if int(time.time()) < last_nails:
            return
        guild = self.bot.get_guild(763218643843678288)
        chit_chat = guild.get_channel(858167284069302292)
        chit_chatter_role = guild.get_role(910723707578753074)
        egg_role = guild.get_role(1020889035901780018)
        chit_chatters = list(
            filter(lambda m: chit_chatter_role in m.roles, guild.members))
        eggs = list(filter(lambda m: egg_role in m.roles, guild.members))
        eggs = [x for x in eggs if x not in chit_chatters]
        nails_list = []
        for member in chit_chatters + eggs:
            nails = await database.get_attribute(self.bot.database, member,
                                                 'nails_check')
            if nails == True:
                nails_list.append(member.id)
        if int(time.time()) >= last_nails:
            nails_mention = ' '.join([f'<@{i}>' for i in nails_list])
            await database.set_other_attribute(self.bot.database,
                                               last_nails + 604800,
                                               'last_nails')
            await chit_chat.send(f'{nails_mention} Reminder: cut nails')

    @commands.command(aliases=('ci', 'cinfo', 'contactinfo', 'c_info', 'contact_info'))
    async def contact_information(self, ctx):
        embed = await contacts('Admins')
        await ctx.send(embed=embed, view=ContactsView())


async def setup(bot):
    await bot.add_cog(School(bot))
