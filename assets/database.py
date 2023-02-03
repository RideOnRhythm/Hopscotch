import json


async def initialize_member(database, member):
  if str(member.id) not in database['members']:
    database['members'][str(member.id)] = {
      'hopscotch_level': 1,
      'current_xp': 0,
      'total_messages': 0,
      'total_vc_hours': 0,
      'command_count': 0,
      'coins': 0,
      'gems': 0,
      'positive_coin_count': 0,
      'negative_coin_count': 0,
      'positive_gem_count': 0,
      'negative_gem_count': 0,
      'normal_c4_count': 0,
      'normal_c4_win_count': 0,
      'normal_c4_coin_count': 0,
      'extreme_c4_count': 0,
      'extreme_c4_win_count': 0,
      'extreme_c4_coin_count': 0,
      'invisible_c4_count': 0,
      'invisible_c4_win_count': 0,
      'invisible_c4_coin_count': 0,
      'swift_c4_count': 0,
      'swift_c4_win_count': 0,
      'swift_c4_coin_count': 0,
      'cf_count': 0,
      'cf_win_count': 0,
      'cf_coin_count': 0,
      'total_vc_minutes': 0,
      'last_message_unix': None,
      'last_message_channel_id': None,
      'roles': [],
      'last_saved_roles_unix': None
    }


async def create_nonexistent_keys(database):
  # Creates keys that are not found in each member's user data
  presets = {
    'hopscotch_level': 1,
    'current_xp': 0,
    'total_messages': 0,
    'total_vc_hours': 0,
    'command_count': 0,
    'coins': 0,
    'gems': 0,
    'positive_coin_count': 0,
    'negative_coin_count': 0,
    'positive_gem_count': 0,
    'negative_gem_count': 0,
    'normal_c4_count': 0,
    'normal_c4_win_count': 0,
    'normal_c4_coin_count': 0,
    'extreme_c4_count': 0,
    'extreme_c4_win_count': 0,
    'extreme_c4_coin_count': 0,
    'invisible_c4_count': 0,
    'invisible_c4_win_count': 0,
    'invisible_c4_coin_count': 0,
    'swift_c4_count': 0,
    'swift_c4_win_count': 0,
    'swift_c4_coin_count': 0,
    'cf_count': 0,
    'cf_win_count': 0,
    'cf_coin_count': 0,
    'total_vc_minutes': 0,
    'last_message_unix': None,
    'last_message_channel_id': None,
    'roles': [],
    'last_saved_roles_unix': None
  }
  for member in database['members']:
    for key in presets:
      if key not in database['members'][member]:
        database['members'][member][key] = presets[key]


async def set_coins(database, member, value, increment=True):
  await initialize_member(database, member)
  if increment:
    database['members'][str(member.id)]['coins'] = database['members'][str(
      member.id)]['coins'] + value
    # Update positive and negative coin counts
    if value >= 0:
      database['members'][str(
        member.id)]['positive_coin_count'] = database['members'][str(
          member.id)]['positive_coin_count'] + value
    else:
      database['members'][str(
        member.id)]['negative_coin_count'] = database['members'][str(
          member.id)]['negative_coin_count'] + -1 * value
  else:
    database['members'][str(member.id)]['coins'] = value


async def set_attribute(database, member, value, attribute, increment=True):
  await initialize_member(database, member)
  if increment:
    database['members'][str(member.id)][attribute] = database['members'][str(
      member.id)][attribute] + value
  else:
    database['members'][str(member.id)][attribute] = value


async def set_xp(database, member, value, increment=True):
  await initialize_member(database, member)
  if increment:
    database['members'][str(
      member.id)]['current_xp'] = database['members'][str(
        member.id)]['current_xp'] + value
  else:
    database['members'][str(member.id)]['current_xp'] = value
  current_xp = database['members'][str(member.id)]['current_xp']
  xp_needed = 5 * database['members'][str(member.id)]['hopscotch_level']**2
  while current_xp > xp_needed:
    database['members'][str(member.id)]['current_xp'] = current_xp - xp_needed
    database['members'][str(
      member.id)]['hopscotch_level'] = database['members'][str(
        member.id)]['hopscotch_level'] + 1
    current_xp = database['members'][str(member.id)]['current_xp']
    xp_needed = 5 * database['members'][str(member.id)]['hopscotch_level']**2


async def get_attribute(database, member, attribute):
  await initialize_member(database, member)
  return database['members'][str(member.id)][attribute]


async def get_other_attribute(database, attribute):
  return database[attribute]


async def add_reminder(database, value):
  database['reminders'].append(value)


async def remove_reminder(database, value):
  database['reminders'].remove(value)


async def reminder_unix(database, value, index):
  database['reminders'][index]['unix'] = value


async def reminder_text(database, value, index):
  database['reminders'][index]['text'] = value


async def reminder_section(database, value, index):
  database['reminders'][index]['section'] = value


async def save_json(data):
  with open('database.json', 'w') as f:
    json.dump(data, f, indent=4)


async def load_json():
  with open('database.json', 'r') as f:
    return json.load(f)
