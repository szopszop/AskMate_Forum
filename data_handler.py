import csv
import os

BASEPATH = os.path.dirname(os.path.abspath(__file__)) + '/'
ALLOWED_EXTENSIONS = {'jpg', 'png'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_data_from_file(filename):
    with open(BASEPATH + filename) as data_file:
        read_data_file = csv.DictReader(data_file)
        return list(read_data_file)


def build_headers(data_headers):
    headers = []
    for header in data_headers:
        if '_' in header:
            header = ' '.join([header.capitalize() for header in header.split('_')])
            headers.append(header)
        else:
            headers.append(header.capitalize())
    return headers


def append_new_data_to_file(new_data, filename, headers):
    with open(BASEPATH + filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writerow(new_data)


def update_data_in_file(data, filename, headers):
    with open(BASEPATH + filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
