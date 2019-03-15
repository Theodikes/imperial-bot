from secret import technical_token
from vk_api import VkApi
from random import randint
from templates import create_throttle_decorator, theo, emperor, levin, VkBot

bot = VkBot(VkApi(token=technical_token))
player_dict_throttle = {}


def get_technologist():
    new_technologist = bot.method('messages.search', {'v': 5.92, 'q': 'Технолог', 'peer_id': levin})
    return int(new_technologist['items'][0]['text'][9:])


technologist = get_technologist()
full_permission = [theo, levin, emperor, technologist]

throttle = create_throttle_decorator(player_dict_throttle, full_permission)
send_message = bot.send_message


def roll_dice(s: str):
    lst = s.split()
    print(lst)
    try:
        num1 = int(lst[-2])
        num2 = int(lst[-1])
    except:
        return 'Были поданы неверные значения'
    return randint(num1, num2)


@throttle
def processing(user_id, obj):

    what = obj['text']

    if user_id not in full_permission:
        send_message(str(roll_dice(what)), user_id)

    else:
        if what == 'commands':
            send_message(
                'Кинуть дайс на страну можно по соответствующей форме:\n\nДайс:\nНазвание страны:\nНазвание ветки: очки\
                \nНазвание ветки: очки\nНазвание ветки: очки\nНазвание ветки: очки\nНазвание ветки: очки', user_id)

        if what.startswith('дайс') or what.startswith('Дайс'):
            lst = what.splitlines()[1:]
            answer = lst[0] + '\n'

            for line in lst[1:]:
                templist = line.split()
                answer += ' '.join(templist[:-1])
                number = int(templist[-1])
                if randint(1, 100) <= number:
                    answer += ' Технология выпала!'
                else:
                    answer += ' Неудача...'
                answer += '\n'

            send_message(answer, user_id)

    return 'ok'
