import csv
import os

BASEPATH = os.path.dirname(os.path.abspath(__file__)) + '/'
DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']


def get_data_file(filename):
    data_file = open(BASEPATH + filename)
    read_data_file = csv.DictReader(data_file)
    return read_data_file


def build_headers():
    headers = []
    for header in DATA_HEADER:
        if '_' in header:
            header = ' '.join([header.capitalize() for header in header.split('_')])
            headers.append(header)
        else:
            headers.append(header.capitalize())
    return headers
