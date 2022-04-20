import csv
import os

BASEPATH = os.path.dirname(os.path.abspath(__file__)) + '/'


def get_data_file(filename):
    data_file = open(BASEPATH + filename)
    read_data_file = csv.DictReader(data_file)
    return list(read_data_file)


def build_headers(headers):
    headers = []
    for header in headers:
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
