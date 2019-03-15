# @param type: тип события в группе.
# @param date: объект события в группе, полученный через callback api
# @param session: активная сессия вконтакте, через которую выполняются действия
# @param main: id основной группы, в которой происходят события
# @param rez: id группы архива, куда добавляются копии постов из основной группы
import secret
import json
from templates import get_date, levin, full_permissions

session = secret.levin_session()
session_t = secret.session_t()
rez = secret.archives_id
main = secret.main_id


def update_topic_dict():
    with open('topic_dict.json', 'tw') as f:
        f.write(json.dumps(secret.boardvalues))


def add_post(event_type, data):
    global session, rez

    def create_comment(comment_type):
        global session, rez
        nonlocal data

        values_search = {'v': 5.92, 'owner_id': rez, 'query': str(data['post_id'])}
        post_object = session.method('wall.search', values_search)

        if post_object['count'] != 0:
            sms = '@id' + str(data['from_id']) + '\n' + str(data['text'])
            if comment_type == 'edit':
                date = get_date()
                sms = 'edit at ' + date + '\n' + '@id'+str(data['from_id']) + '\n' + str(data['text'])

            val = {'v': 5.92, 'owner_id': rez, 'from_group': rez[1:], 'post_id': post_object['items'][0]['id'],
                   'message': sms}
            session.method('wall.createComment', val)

    def create_board_comment(comment_type):
        global session, rez
        nonlocal data

        d = secret.boardvalues
        if str(data['topic_id']) in d:
            topic_archive = d[str(data['topic_id'])]
        else:                                                    # If topic_id isn`t in dict
            req = session.method('board.getTopics', {'v': 5.92, 'group_id': main, 'topic_ids': data['topic_id']})
            values = {'v': 5.92, 'group_id': int(rez[1:]), 'title': req['items'][0]['title'], 'from_group': 1,
                      'text': 'text'}
            topic_id = session.method('board.addTopic', values)
            secret.boardvalues[str(data['topic_id'])] = topic_id
            update_topic_dict()
            topic_archive = topic_id

        sms = str(data['id']) + ' @id' + str(data['from_id']) + '\n' + str(data['text'])
        if comment_type == 'edit':
            date = get_date()
            sms = 'edit at ' + date + '\n' + sms

        val = {'v': 5.92, 'group_id': rez[1:], 'topic_id': topic_archive, 'guid': data['id'],
               'message': sms, 'from_group': 1}
        session.method('board.createComment', val)

    if event_type == 'wall':
        values = {'v': 5.92, 'owner_id': rez, 'from_group': 1,
                  'message': str(data['id']) + '\n' + '@id' + str(data['from_id']) + '\n' + str(data['text'])}
        session.method('wall.post', values)

    elif event_type == 'comment_new':
        create_comment('new')
    elif event_type == 'comment_edit':
        create_comment('edit')

    elif event_type == 'board_comment_new':
        create_board_comment('new')
    elif event_type == 'board_comment_edit':
        create_board_comment('edit')

    return 'ok'


def check_permissions(id_banned_user, admin, data):
    global session, main, rez

    if data['level_new'] != 3 and id_banned_user in full_permissions and admin not in full_permissions:
        ban_values = {'v': 5.92, 'group_id': main, 'user_id': admin}
        values = {'v': 5.92, 'group_id': main, 'user_id': str(id_banned_user), 'role': 'administrator'}
        banval = {'v': 5.92, 'group_id': main, 'owner_id': admin, 'reason': 0,
                  'comment': 'Наказан за покушение на Императора', 'comment_visible': 1}
        if id_banned_user == levin:
            session_t.method('groups.editManager', ban_values)
            session_t.method('groups.editManager', values)
            session_t.method('groups.ban', banval)
        else:
            session.method('groups.editManager', ban_values)
            session.method('groups.editManager', values)
            session.method('groups.ban', banval)
    else:
        levels = ['нет полномочий', 'модератор', 'редактор', 'администратор']
        text = ('Администратор @id%s изменил статус пользователя @id%s с "%s" на "%s"' %
                (data['admin_id'], data['user_id'], levels[data['level_old']], levels[data['level_new']]))
        values = {'v': 5.92, 'from_group': 1, 'group_id': rez[1:], 'topic_id': 39707149, 'message': text}
        session.method('board.createComment', values)

    return 'ok'
