from flask import Flask, json, request
import secret
import funx
import archives
app = Flask(__name__)


@app.route('/', methods=['POST'])
def processing():
    confirmation_token = '248551e0'
    confirmation_token_for_archives = 'bf2ef536'
    session = secret.session()
    reasons = ['другое"', 'спам', 'оскорбление участников', 'нецензурные выражения', 'сообщения не по теме']
    # Распаковываем json из пришедшего POST-запроса
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    if data['secret'] == secret.imp_key():
        if data['type'] == 'confirmation':
            return confirmation_token
        obj = data['object']
        if data['type'] == 'wall_post_new':
            return funx.add_post('wall', obj)
        elif data['type'] == 'wall_reply_new':
            return funx.add_post('comment_new', obj)
        elif data['type'] == 'wall_reply_edit':
            return funx.add_post('comment_edit', obj)
        elif data['type'] == 'board_post_new':
            return funx.add_post('board_comment_new', obj)
        elif data['type'] == 'board_post_edit':
            return funx.add_post('board_comment_edit', obj)
        # Защита Императора и Левина от бана
        elif data['type'] == 'group_officers_edit':
            return funx.check_permissions(obj['user_id'], obj['admin_id'], obj)
        elif data['type'] == 'wall_reply_delete':
            ident = obj['id']
            values = {'version': 5.85, 'from_group': 1, 'group_id': '169839935', 'topic_id': 39703400,
                      'guid': ident, 'message': 'Комментарий к записи с id %s был удалён пользователем @id%s' %
                                                (obj['post_id'], obj['deleter_id'])}
            session.method('board.createComment', values)
            return 'ok'
        elif data['type'] == 'user_block':
            values = {'version': 5.92, 'from_group': 1, 'group_id': '169839935', 'topic_id': 39707065,
                      'guid': obj['unblock_date'],
                      'message': 'Пользователь @id%s был заблокирован админом @id%s по причине "%s" с пометкой "%s"'
                                 % (obj['user_id'], obj['admin_id'], reasons[obj['reason']], obj['comment'])}
            session.method('board.createComment', values)
            return 'ok'
        elif data['type'] == 'user_unblock':
            text = ('Пользователь @id%s был разблокирован по истечении срока бана' % (obj['user_id']) if
                    obj['by_end_date'] else 'Пользователь @id%s был разблокирован администратором @id%s'
                                            % (obj['user_id'], obj['admin_id']))
            values = {'version': 5.92, 'from_group': 1, 'group_id': '169839935', 'topic_id': 39707065, 'message': text}
            session.method('board.createComment', values)
            return 'ok'

    elif data['secret'] == secret.archives_key():
        if data['type'] == 'confirmation':
            return confirmation_token_for_archives
        obj = data['object']
        if data['type'] == 'message_new':
            ans = archives.set_permission(obj['from_id'], obj)
            return ans


if __name__ == "__main__":
    app.run(port=4444)
