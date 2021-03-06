from secret import archive_token
import vk_api
from templates import create_throttle_decorator, get_unixtime, levin, emperor, VkBot
from time import sleep

bot = VkBot(vk_api.VkApi(token=archive_token))
player_dict_throttle = {}
margrave = 133540023
full_permissions = [levin, emperor, margrave]

throttle = create_throttle_decorator(player_dict_throttle, full_permissions)
send = bot.send_message
search = bot.search_message


def set_judges():
    string = search('Список судий:', margrave)['items'][0]['text']
    d = get_user(','.join(string[14:].split()))
    return [el['id'] for el in d]


@throttle
def justis(who, obj):

    if obj['text'] == '' and 'attachments' in obj:

        if 'sticker' in obj['attachments'][0]:

            if obj['attachments'][0]['sticker']['sticker_id'] == 163:
                send('', who, False, 163)
                return True

    return False


def check_margrave():
    new_margrave = bot.method('messages.search', {'v': 5.92, 'q': 'Маркграф', 'peer_id': levin})
    return int(new_margrave['items'][0]['text'][9:])


def get_user(ids):
    return bot.method('users.get', {'v': 5.92, 'user_ids': ids})


def check_permissions(user, method):

    if user in judges or user in full_permissions:
        return True
    else:
        send('Вы не являетесь военным судьей - метод "%s" вам недоступен' % method, user)


def put_player_in_throttle_list(who):
        player_dict_throttle[who] = {'messages': 0, 'last_message_time': get_unixtime()}


def get_war(who, what, offset, caller='', peer_id=''):

    if what:
        what = ' ' + what

    values = {'v': 5.92, 'offset': offset, 'q': 'set%s' % what}

    if caller.startswith('get'):
        values['peer_id'] = peer_id

    messages = bot.method('messages.search', values)
    count = len(messages['items'])
    sms_ids = []

    if count == 0:
        send('Нет приказов по запрошенному вами конфликту. Возможно, они ещё не присланы, или вы ошиблись \
        в названии конфликта', who)

    for i in range(count):
        if messages['items'][i]['from_id'] != -169839935:
            sms_ids.append(str(messages['items'][i]['id']))

    return ','.join(sms_ids)


judges = set_judges()


@throttle
def get_battle_order(who, what):

    if what.startswith('help') or what.startswith('помощь'):
        send('Команды:\n 1) Если войны нет: set + документы для оборонки\n\
        2) Если война идёт: set + название_войны + приложенные документы - сдать оборонку\n\
        3) Для военников: введите commands для получения списка команд. Если вы не военник - даже не пытайтесь. \n\n\
        Примечание: давайте войне ТОЧНОЕ название, иначе судья не сможет получить ваши обронки! \n\
        Кроме того, не пишите вместе с командой set ничего лишнего, просто прикладывайте документы или текст оборонки. \
        Если вы поняли, что не доложили какие-либо документы - редактировать сообщения можно, \
        однако при отправке сообщения с новой информацией всегда используйте команду set.\
        Другие сообщения, за исключением комманд, боту писать не надо. Он будет отвечать, что вас не понимает, \
        но при этом может потерять вашу оборонку или я просто дам вам бан за флуд.', who)

    elif what.startswith('set'):
        send('Ваш оборонительный приказ принят', who)

    elif what.startswith('getwar'):
        if check_permissions(who, 'getWar'):
            try:
                conflicts = search('setWar %s' % who, margrave)['items'][0]['text']
                if ~conflicts.find(what[7:]):
                    messages = search('set %s' % what[7:], '')
                    count = messages['count']
                    ids = ''
                    for i in range(0, count, 20):
                        ids += get_war(who, what[7:], i)
                    send('', who, ids)
            except IndexError:
                send('Вы не были установлены ни на одну войну', who)

    elif what.startswith('get'):
        if check_permissions(who, 'get'):
            what = ','.join(','.join(what[4:].split('-')).split())
            try:
                what = get_user(what)
                judge = search('set %s' % who, margrave)['items']
                if len(judge):

                    judge = judge[0]['text']
                    indictee = get_user(','.join(judge[len('set %s' % who):].split()))
                    indictee_id = [el['id'] for el in indictee]

                    for user in what:

                        if user['id'] in indictee_id or who in full_permissions:

                            messages = search('set', user['id'])
                            count = messages['count']
                            ids = ''

                            for i in range(0, count, 20):
                                ids += get_war(who, '', i, 'get', user['id'])
                            send('', who, ids)

                        else:
                            send(
                                'Игрока "%s %s" нет в списке ваших подсудимых. \
                                Его оборонительный приказ вам недоступен.' %
                                (user['first_name'], user['last_name']), who)

                else:
                    send('Данного игрока нет в списке ваших подсудимых', who)

            except vk_api.exceptions.ApiError:
                send('Вы неверно указали краткую ссылку и/или id игрока (-ов)', who)

    elif what.startswith('userid'):
        if check_permissions(who, 'userid'):
            try:
                if ~what.find('vk.com'):
                    user = get_user(what[24:]) if ~what.find('m.vk.com') else get_user(what[22:])
                else:
                    user = get_user(what[7:])
            except vk_api.exceptions.ApiError as e:
                send('Ошибка "%s" - неправильно указана ссылка или такого юзера не существует' % e, who)
            else:
                send(str(user[0]['id']), who)

    elif what.startswith('commands'):
        if check_permissions(who, 'commands'):
            send('1) get id или get краткая_ссылка* - получить оборонку человека\n\
                  2) Получить приказы по названию войны: getWar название_войны\n\
                    3) Получить оборонку сразу нескольких людей - get id id id id, либо же get краткая_ссылка \
                    краткая_ссылка краткая_ссылка. Вместо пробелов могут быть как дефисы, так и запятые\n\
                    4) Получить id игрока - userid полная_ссылка, может быть как мобильная, так и компьютерная\n\n\
                * Для примера - моей краткой ссылкой является @id202195616 (levinnelevin)', who)

    else:
        send('Я не понял, что вы написали. Чтобы узнать поддерживаемые команды,\
         отправьте сообщение с текстом "help" или "помощь"', who)

    return True


def set_permission(who, obj):
    global margrave

    what = obj['text'].lower()

    if who not in player_dict_throttle:
        put_player_in_throttle_list(who)

    if who in full_permissions:

        if what == 'start' or what == 'начать':
            send('Проверка статуса...', who)
            sleep(2)
            send('Подтверждение получено. Статус: Mаркграф', who)
            send('Инициализация функционала...', who)
            sleep(2)
            send('Готово. Введите commands для получения команд', who)

        elif what == 'commands':
            send('Для установки игроку статуса военного судьи измените последнее сообщение со списками военных судей, \
            если его ещё можно изменить, или опубликуйте новое сообщение в формате (без кавычек): \n\n\
            "Списoк судий: id_судьи id_судьи id_сульи id_судьи"\n\nКоличество судий может быть любым, \
            вместо кавычек могут быть краткие ссылки\n\n\n\
            Чтобы дать судье доступ к оборонительным приказам определенных игроков, \
            следует использовать команду "set id_судьи id_игрока id_игрока id_игрока". Можно использовать краткие \
            ссылки вместо id игроков, но не вместо id судий.\
            \n\nЧтобы дать судье доступ ко всем приказам по войне с определенным названием, следует \
            использовать команду "setWar id_судьи название_войны".\n\n\
            Чтобы сдать оборонку как игрок, используйте "игрок set + документы_для_приказа"', who)

        elif who == levin and what.startswith('маркграф'):
            margrave = check_margrave()
            user = get_user(margrave)[0]
            send('Установлен новый мaркграф - %s %s' % (user['first_name'], user['last_name']), who)

        elif what.startswith('setwar'):
            try:
                s = what.split()  # разбиваем предложение на части
                j = get_user(s[1])[0]  # судья
                send('Судья %s %s успешно установлен на регион %s' % (j['first_name'], j['last_name'], s[2]), who)
            except vk_api.exceptions.ApiError as e:
                send('Ошибка "%s" - неправильно указана ссылка или такого юзера не существует' % e, who)

        elif what.startswith('set'):
            try:
                judge = bot.method('users.get', {'v': 5.92, 'user_ids': what.split()[1], 'name_case': 'gen'})[0]
                send('Подсудимые %s %s успешно установлены' % (judge['first_name'], judge['last_name']), who)
            except vk_api.exceptions.ApiError as e:
                send('Ошибка "%s" - неправильно указана ссылка или такого юзера не существует' % e, who)

        elif what.startswith('список судий:'):
            global judges
            judges = set_judges()
            send('Списoк судий успешно установлен!', who)

        elif what.startswith('игрок'):
            get_battle_order(who, what[6:])

        else:
            get_battle_order(who, what)

    else:
        if not justis(who, obj):
            get_battle_order(who, what)

    return 'ok'
