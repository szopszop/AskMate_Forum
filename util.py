def sort_by(key, items):
    match key:
        case 'title':
            return sorted(items, key=lambda x: x['title'])
        case 'time':
            return sorted(items, key=lambda x: x['submission_time'])
        case 'message':
            return sorted(items, key=lambda x: x['message'])
        case 'views':
            return sorted(items, key=lambda x: x['view_number'])
        case 'votes':
            return sorted(items, key=lambda x: x['vote_number'])
