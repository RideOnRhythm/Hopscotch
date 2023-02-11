from discord.ext import commands
from assets import database
import discord
import random


async def category_shop(ctx, cog, category):
    embed = discord.Embed(title='Shop', color=discord.Color.yellow())

    member_items = await database.get_items(cog.bot.database, ctx.author)
    category_items = filter(lambda x: cog.items[x]['category'] == category,
                            cog.items)
    for item in category_items:
        for member_item in member_items:
            if item == member_item['id']:
                if member_item['category'] == 'C4 Themes':
                    amount = '- ***You own this theme.***\n'
                    break
                else:
                    quantity = member_item['quantity']
                    amount = f'\n*- You have **{quantity}** of this item.*\n'
                    break
        else:
            amount = ''

        if item == 'charles':
            wins = []
            for attribute in ('normal_c4_win_count', 'extreme_c4_win_count',
                              'invisible_c4_win_count', 'swift_c4_win_count',
                              'cf_win_count', 'easy_ai_win', 'normal_ai_win',
                              'medium_ai_win', 'hard_ai_win', 'expert_ai_win',
                              'impossible_ai_win'):
                wins.append(await
                            database.get_attribute(cog.bot.database,
                                                   ctx.author, attribute))
            if sum(wins) < 100:
                embed.add_field(
                    name=
                    f'{cog.items[item]["icon"]} {cog.items[item]["name"]} - Unavailable!',
                    value=
                    f'`ID: {item}`\nWin {100 - sum(wins)} more games to unlock this in the shop.'
                )
        else:
            embed.add_field(
                name=
                f'{cog.items[item]["icon"]} {cog.items[item]["name"]} - {cog.items[item]["price"]:,} :coin:',
                value=f'`ID: {item}`\n{amount}{cog.items[item]["description"]}'
            )

    return embed


async def category_inventory(ctx, cog, member, category):
    if member is None:
        member = ctx.author
    if member.bot:
        await ctx.send(
            f'{ctx.author.mention}, the right command is \"j.inventory {{user (optional)}}.\"'
        )
        return

    embed = discord.Embed(color=discord.Color.gold())
    if member.avatar is not None:
        embed.set_author(name=f'{member.display_name}\'s inventory',
                         icon_url=member.avatar.url)
    else:
        embed.set_author(name=f'{member.display_name}\'s inventory')

    member_items = await database.get_items(cog.bot.database, member)
    category_items = filter(lambda x: x['category'] == category, member_items)
    for item in category_items:
        if item['category'] == 'C4 Themes':
            embed.add_field(name=f'{item["icon"]} {item["name"]}',
                            value=f'`ID: {item["id"]}`\n{item["description"]}')
        else:
            embed.add_field(
                name=
                f'{item["icon"]} {item["name"]} (Quantity: {item["quantity"]})',
                value=f'`ID: {item["id"]}`\n{item["description"]}')
    if len(embed.fields) == 0:
        embed.description = 'You do not have any items in this category.'

    return embed


class ShopView(discord.ui.View):

    def __init__(self, ctx, cog, timeout=180):
        self.ctx = ctx
        self.cog = cog
        super().__init__(timeout=timeout)

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('Items', 'C4 Themes')
                       ])
    async def category_select(self, interaction: discord.Interaction,
                              select: discord.ui.Select):
        embed = await category_shop(self.ctx, self.cog, select.values[0])
        await interaction.response.edit_message(embed=embed,
                                                view=ShopView(
                                                    self.ctx, self.cog))


class InventoryView(discord.ui.View):

    def __init__(self, ctx, cog, member, timeout=180):
        self.ctx = ctx
        self.cog = cog
        self.member = member
        super().__init__(timeout=timeout)

    @discord.ui.select(cls=discord.ui.Select,
                       options=[
                           discord.SelectOption(label=label)
                           for label in ('Items', 'C4 Themes')
                       ])
    async def category_select(self, interaction: discord.Interaction,
                              select: discord.ui.Select):
        embed = await category_inventory(self.ctx, self.cog, self.member,
                                         select.values[0])
        await interaction.response.edit_message(embed=embed,
                                                view=InventoryView(
                                                    self.ctx, self.cog,
                                                    self.member))


class Inventory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.items = {
            'lottery_ticket': {
                'name': 'Lottery Ticket',
                'id': 'lottery_ticket',
                'description': 'A lottery ticket.',
                'icon': ':ticket:',
                'category': 'Items',
                'price': 200,
                'quantity': None,
                'special': []
            },
            'anikainspace': {
                'name': 'Anika In Space',
                'id': 'anikainspace',
                'description': 'Its time to go on an adventure!',
                'icon': '<:THEME_anika:1073873897360982076>',
                'category': 'C4 Themes',
                'price': 5000,
                'quantity': None
            },
            'galaxy': {
                'name': 'Galaxy',
                'id': 'galaxy',
                'description':
                'Held together by gravity, a beautiful purple galaxy theme for your C4 games!',
                'icon': '<:THEME_galaxy:1073875133925699624>',
                'category': 'C4 Themes',
                'price': 10000,
                'quantity': None
            },
            'sakura': {
                'name': 'Sakura',
                'id': 'sakura',
                'description': 'A pink sakura theme for your C4 games!',
                'icon': '<:THEME_sakura:1065929561419825162>',
                'category': 'C4 Themes',
                'price': 15000,
                'quantity': None
            },
            'colorchanging': {
                'name': 'Pink-Blue',
                'id': 'pinkblue',
                'description': 'Why are the colors changing?',
                'icon': '<a:THEME_colorful:1065931156685606973>',
                'category': 'C4 Themes',
                'price': 20000,
                'quantity': None
            },
            'charles': {
                'name': 'Charles',
                'id': 'charles',
                'description': 'ummm...',
                'icon': '<:THEME_charles:1073876973824266351>',
                'category': 'C4 Themes',
                'price': 69420,
                'quantity': None
            }
        }

    @commands.command()
    async def shop(self, ctx):
        embed = await category_shop(ctx, self, 'Items')
        await ctx.send(embed=embed, view=ShopView(ctx, self))

    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, member: discord.Member = None):
        embed = await category_inventory(ctx, self, member, 'Items')
        await ctx.send(embed=embed, view=InventoryView(ctx, self, member))

    @commands.command()
    async def buy(self, ctx, item, quantity=1):
        item = self.items[item]
        coins = await database.get_attribute(self.bot.database, ctx.author,
                                             'coins')
        price = item['price'] * quantity
        if item['id'] == 'charles':
            wins = []
            for attribute in ('normal_c4_win_count', 'extreme_c4_win_count',
                              'invisible_c4_win_count', 'swift_c4_win_count',
                              'cf_win_count', 'easy_ai_win', 'normal_ai_win',
                              'medium_ai_win', 'hard_ai_win', 'expert_ai_win',
                              'impossible_ai_win'):
                wins.append(await
                            database.get_attribute(self.bot.database,
                                                   ctx.author, attribute))
            if sum(wins) < 100:
                await ctx.send('You are currently unworthy of this item.')
                return
        if coins < price:
            await ctx.send('You don\'t have enough coins to buy this item.')
            return

        item_limits = {
            'lottery_ticket': 100,
            'sakura': 1,
            'colorchanging': 1,
            'anikainspace': 1,
            'galaxy': 1,
            'charles': 1
        }
        original_q = await database.get_items(self.bot.database, ctx.author)
        existing = None
        for i in original_q:
            if i['id'] == item['id']:
                existing = i
                break
        if existing is not None:
            existing = existing['quantity']
        else:
            existing = 0
        if existing + quantity > item_limits[item['id']]:
            if item['category'] == 'C4 Themes':
                await ctx.send(
                    'You already own this theme! Please buy another one.')
            else:
                await ctx.send('You can\'t buy too many of this item.')
            return

        if item['id'] == 'lottery_ticket':
            item['special'] = [
                random.randint(0, 999999) for _ in range(quantity)
            ]

        await database.set_coins(self.bot.database, ctx.author, -1 * price)
        await database.add_item(self.bot.database, ctx.author, item, quantity)
        await ctx.send(f'Bought **{item["name"]}** for **{price}** :coin:.')


async def setup(bot):
    await bot.add_cog(Inventory(bot))
