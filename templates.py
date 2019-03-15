import time
from random import random


def get_unixtime():
    return int(time.time())


def get_date():
    return time.ctime(get_unixtime())


def create_throttle_decorator(throttle_dict, full_permission: list):
    def throttle(f):
        def put_player_in_throttle_dict(who):
            throttle_dict[who] = {'messages': 0, 'last_message_time': get_unixtime()}

        def wrapper(*args):
            now = get_unixtime()
            who = args[0]

            if who not in throttle_dict:
                put_player_in_throttle_dict(who)

            if throttle_dict[who]['messages'] > 4 and who not in full_permission:

                if now - throttle_dict[who]['last_message_time'] < 300:
                    return 'ok'

                else:
                    throttle_dict[who]['messages'] = 0

            else:
                result = f(*args)

                if result:
                    throttle_dict[who]['messages'] += 1
                    throttle_dict[who]['last_message_time'] = now

                return result

        return wrapper
    return throttle


class VkBot:

    def __init__(self, bot):
        self.bot = bot
        self.method = bot.method

    def send_message(self, text, who, forward=0, sticker=0):

        values = {'v': 5.92, 'user_id': who, 'random_id': int(random() * 100000000000000), 'message': text}

        if forward:
            values['forward_messages'] = forward
        if sticker and not text:
            del values['message']
            values['sticker_id'] = sticker

        self.bot.method('messages.send', values)

    def search_message(self, q, user_id):
        return self.bot.method('messages.search', {'v': 5.92, 'q': q, 'peer_id': user_id})


levin = 202195616
emperor = 154943011
theo = 445103876

full_permissions = [levin, emperor, theo]
