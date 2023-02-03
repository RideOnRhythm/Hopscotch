from discord.ext import commands
from assets import database
import discord
import random


class ShopView(discord.ui.View):

    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.select(
        cls=discord.ui.Select,
        options=[discord.SelectOption(label=label) for label in ('Usables')])
    async def category_select(self, interaction: discord.Interaction,
                              select: discord.ui.Select):
        pass


class Inventory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.items = {
            'lottery_ticket': {
                'name': 'Lottery Ticket',
                'id': 'lottery_ticket',
                'description': 'A lottery ticket. I wish I had a car.',
                'icon': ':ticket:',
                'category': 'usable',
                'price': 200,
                'quantity': None,
                'special': []
            }
        }

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title='Shop', color=discord.Color.yellow())
        member_items = await database.get_items(self.bot.database, ctx.author)
        lottery_amount = ''
        for item in member_items:
            if item["id"] == 'lottery_ticket':
                lottery_amount += f'*- You have **{item["quantity"]}** of this item.*\n'
        for item in self.items:
            embed.add_field(
                name=f'{self.items[item]["icon"]} {self.items[item]["name"]}',
                value=
                f'`ID: {item}`\n{lottery_amount}{self.items[item]["description"]}'
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, member: discord.Member = None):
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

        member_items = await database.get_items(self.bot.database, member)
        for item in member_items:
            embed.add_field(
                name=
                f'{item["icon"]} {item["name"]} (Quantity: {item["quantity"]})',
                value=f'`ID: {item["id"]}`\n{item["description"]}')

        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, item, quantity=1):
        item = self.items[item]
        coins = await database.get_attribute(self.bot.database, ctx.author,
                                             'coins')
        price = item['price'] * quantity
        if coins < price:
            await ctx.send('You don\'t have enough coins to buy this item.')
            return
        if item['id'] == 'lottery_ticket':
            original_q = await database.get_items(self.bot.database,
                                                  ctx.author)
            ticket = None
            for i in original_q:
                if i['id'] == 'lottery_ticket':
                    ticket = i
                    break
            if ticket is not None:
                if ticket['quantity'] + quantity > 100:
                    await ctx.send('You have too many of this item.')
                    return
            item['special'] = [
                random.randint(0, 999999) for _ in range(quantity)
            ]
        await database.set_coins(self.bot.database, ctx.author, -1 * price)
        await database.add_item(self.bot.database, ctx.author, item, quantity)
        await ctx.send(f'Bought **{item["name"]}** for **{price}** :coin:.')

    # @commands.command()
    # async def fix_inventory(self, ctx, quantity):
    #   if ctx.author.id not in (748388929631289436, 556307832241389581,
    #                          994223267462258688):
    #     return
    #   participants = [
    #     member for member in filter(
    #       lambda m: next(
    #         (item['id'] for item in self.bot.database['members'][m]['inventory']
    #          ), None) == 'lottery_ticket', self.bot.database['members'])
    #   ]
    #   for member in participants:
    #     item = await database.get_items(self.bot.database, member)
    #     if item['id'] == 'lottery_ticket':
    #       item['special'] = [random.randint(0, 999999) for _ in range(int(quantity))
    #       await database.add_item(self.bot.database, member, special, quantity)


async def setup(bot):
    await bot.add_cog(Inventory(bot))
