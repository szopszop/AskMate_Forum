import csv
import os

BASEPATH = os.path.dirname(os.path.abspath(__file__)) + '/'
DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']


def get_data_from_file(filename):
    with open(BASEPATH + filename) as data_file:
        read_data_file = csv.DictReader(data_file)
        return list(read_data_file)


def build_headers():
    headers = []
    for header in DATA_HEADER:
        if '_' in header:
            header = ' '.join([header.capitalize() for header in header.split('_')])
            headers.append(header)
        else:
            headers.append(header.capitalize())
    return headers


def append_new_data_to_file(new_data, filename):
    with open(BASEPATH + filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=DATA_HEADER)
        writer.writerow(new_data)


def update_data_in_file(data, filename):
    with open(BASEPATH + filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=DATA_HEADER)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
