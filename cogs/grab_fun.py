from discord.ext import commands
import random
from assets import database


class Subject:

  def __init__(self, name, gender):
    self.name = name
    self.gender = gender
    self.subject_pronoun = {'m': 'he', 'f': 'she', 'n': 'they'}[gender]
    self.object_pronoun = {'m': 'him', 'f': 'her', 'n': 'them'}[gender]
    self.possessive_pronoun = {'m': 'his', 'f': 'her', 'n': 'their'}[gender]

  def apply_action(self, action):
    songs = [
      'Atlantis by Seafret', 'Sunshine Rainbow White Pony by Wowkie Zhang',
      'The N-Word Song', 'Shinunoga E-Wa', 'Ed Sheeran'
      'NGGUP', 'Jepoy D', 'Unhinged', 'Here I Come'
    ]
    subject2 = random.choice(subjects)
    while subject2.name == self.name:
      subject2 = random.choice(subjects)
    return action.format(
      subject=self.name,
      subject2=subject2.name,
      subject_pronoun=self.subject_pronoun,
      object_pronoun=self.object_pronoun,
      possessive_pronoun=self.possessive_pronoun,
      cap_subject_pronoun=self.subject_pronoun.capitalize(),
      cap_object_pronoun=self.object_pronoun.capitalize(),
      cap_possessive_pronoun=self.possessive_pronoun.capitalize(),
      song=random.choice(songs))


subjects = [
  Subject('Ervin', 'm'),
  Subject('Mickel', 'm'),
  Subject('Prince', 'm'),
  Subject('Turtleguuy', 'm'),
  Subject('TTguy', 'n'),
  Subject('Hazzy', 'f'),
  Subject('Ervin the Bean Murderer', 'm'),
  Subject('Antonio', 'm'),
  Subject('Aliosio', 'm'),
  Subject('Charles', 'm'),
  Subject('Karim Agha', 'm'),
  Subject('Seth', 'm'),
  Subject('Joyce Lu', 'f'),
  Subject('Ketplane', 'm'),
  Subject('Li Shu Shu', 'm'),
  Subject('林怡平(GMF)', 'f'),
  Subject('Ulysses Yu', 'm'),
  Subject('Mr. No Belt-on', 'm'),
  Subject('Mrs. Belton', 'f'),
  Subject('Halt', 'n'),
  Subject('Hopscotch', 'n'),
  Subject('你的媽媽', 'f'),
  Subject('Nate Higgers', 'm'),
  Subject('Barry McCockiner', 'm'),
  Subject('Don Schoendorfer', 'm'),
  Subject('Joyce Piap-Go', 'f'),
  Subject('Reily', 'm'),
  Subject('Denise', 'f'),
  Subject('A phoque', 'n'),
  Subject('Prince', 'm'),
  Subject('Jet', 'm'),
  Subject('Kenzo', 'm'),
  Subject('Mr Cua', 'm'),
  Subject('Ms. Liwanag', 'f')
]


def generate_message():
  actions = [
    '{subject} has dropped {possessive_pronoun} coins! Quick, type the command `j.grab` to steal them!',
    'While {subject} was spamming the raise hand button, {subject_pronoun} did not realize that {possessive_pronoun} gadget fell on the road, QUICK!! Type the command `j.grab` before anyone else steals it!',
    '{subject} cooked carbonara! Quick, type the command `j.grab` to eat it before anyone else does!',
    '{subject} died of hypothermia! Quick, type the command `j.grab` to steal {possessive_pronoun} belongings!',
    '{subject} has a gift! Quick, type the command `j.grab` to receive {possessive_pronoun} gift!',
    'The FBI is investigating {subject} for terrorism. The FBI offers you a monetary reward for information leading to {possessive_pronoun} arrest. Quick, type the command `j.grab` to claim your money!',
    '{subject} has committed tax fraud. {cap_subject_pronoun} offers you money to prevent {object_pronoun} from getting caught by the IRS. Quick, type the command `j.grab` to help {object_pronoun}!',
    'While {subject} and {subject2} were fighting each other, {subject}\'s wallet fell. Quick, type the command `j.grab` to steal it!',
    '{subject} pulls a halt gameplay, and everyone goes crazy. Amidst the chaos, someone drops their credit card. Quick, type the command `j.grab` to steal it!',
    'While {subject} was listening to {song}, {subject2} sets the building on fire. {subject} ran so quickly that {subject_pronoun} forgot {possessive_pronoun} belongings. Quick, type the command `j.grab` to steal them!',
    '{subject} was pole dancing, and everyone threw money at {object_pronoun}. Quick, type the command `j.grab` to steal them!',
    '{subject} fell on the auditorium stairs. Quick, type the command `j.grab` to steal {possessive_pronoun} wallet!',
    "{subject} got scolded by the librarian for dragging the chair. Quick, type `j.grab` to steal the librarian's wallet!"    
  ]
  return random.choice(subjects).apply_action(random.choice(actions))


class GrabFun(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.message_count = 0
    self.grab_flag = False
    self.add_coins = True

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.channel.id != 858167284069302292 or message.author.bot:
      return
    self.message_count += 1
    if self.message_count >= 200:
      self.message_count = 0
      await message.channel.send(generate_message())
      self.grab_flag = True

  @commands.command(aliases=('g', 'collect'))
  async def grab(self, ctx):
    if not self.grab_flag:
      await ctx.send('**Too slow, better luck next time!**')
    else:
      self.grab_flag = False
      rng = random.randint(500, 800  )
      if not self.add_coins:
        rng = 0
      await ctx.send(f'{ctx.author.mention} was able to grab {rng} :coin:! ')
      await database.set_xp(self.bot.database, ctx.author, 150)
      await database.set_coins(self.bot.database, ctx.author, rng)
      self.add_coins = True

  @commands.command()
  async def grab_message(self, ctx):
    await ctx.send(generate_message())


async def setup(bot):
  await bot.add_cog(GrabFun(bot))
