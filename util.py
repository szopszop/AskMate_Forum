from flask import redirect, url_for
import data_handler


def sort_by(items, key=None, order=None):
    if key is None:  # default sort by most recent
        key = 'time'
    if order is None:
        order = 'desc'
    order = False if order == 'asc' else True
    match key:
        case 'title':
            return sorted(items, key=lambda x: x['title'], reverse=order)
        case 'time':
            return sorted(items, key=lambda x: int(x['submission_time']), reverse=order)
        case 'message':
            return sorted(items, key=lambda x: x['message'], reverse=order)
        case 'views':
            return sorted(items, key=lambda x: int(x['view_number']), reverse=order)
        case 'votes':
            return sorted(items, key=lambda x: int(x['vote_number']), reverse=order)


def vote_on(file, id_, headers, endpoint):
    data = data_handler.get_data_from_file(f'sample_data/{file}.csv')
    for element in data:
        if element['id'] == str(id_):
            if endpoint.endswith('vote-up'):
                element['vote_number'] = int(element['vote_number']) + 1
            elif endpoint.endswith('vote-down'):
                element['vote_number'] = int(element['vote_number']) - 1
            data_handler.update_data_in_file(data, f'sample_data/{file}.csv', headers)
            if file == 'question':
                return redirect(url_for('list'))
            else:
                return redirect(f"/question/{element['question_id']}")
