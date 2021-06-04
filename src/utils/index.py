
import time
import datetime
import os


def get_star_count(morning_star_url):
    import numpy as np
    import requests
    from PIL import Image
    module_path = os.getcwd() + '/src'
    temp_star_url = module_path + '/assets/star/tmp.gif'
    r = requests.get(morning_star_url)
    with open(temp_star_url, "wb") as f:
        f.write(r.content)
    f.close()
    path = module_path + '/assets/star/star'

    # path = './assets/star/star'
    try:
        for i in range(6):
            p1 = np.array(Image.open(path + str(i) + '.gif'))
            p2 = np.array(Image.open(temp_star_url))
            if (p1 == p2).all():
                return i
    except:
        print('morning_star_url', morning_star_url)


def parse_csv(datafile):
    data = []
    with open(datafile, "r") as f:
        header = f.readline().split(",")  # 获取表头
        counter = 0
        for line in f:
            if counter == 10:
                break
            fields = line.split(",")
            entry = {}
            for i, value in enumerate(fields):
                entry[header[i].strip()] = value.strip()  # 用strip方法去除空白
            data.append(entry)
            counter += 1

    return data


def get_quarter_index(input_date):
    year = time.strftime("%Y", time.localtime())
    boundary_date_list = ['03-31', '06-30', '09-30', '12-31']

    input_date_strptime = datetime.datetime.strptime(
        year + '-' + input_date, '%Y-%m-%d')
    index = 1
    for idx in range(len(boundary_date_list)):
        join_date = year + '-' + boundary_date_list[idx]
        season_date_strptime = datetime.datetime.strptime(
            join_date, '%Y-%m-%d')
        if input_date_strptime <= season_date_strptime:
            index = idx + 1
            break
    return index


def get_last_quarter_str():
    last_quarter_time = time.localtime(time.time() - 3 * 30 * 24 * 3600)
    year = time.strftime("%Y", last_quarter_time)
    date = time.strftime("%m-%d", last_quarter_time)
    index = get_quarter_index(date)
    quarter_index_str = year + '-Q' + str(index)
    return quarter_index_str

def get_quarter_date(quarter_index_str):
    year = quarter_index_str.split('-')[0]
    boundary_date_list = ['03-31', '06-30', '09-30', '12-31']
    quarter_index = quarter_index_str.split('-')[1][1:]
    return year + '-' + boundary_date_list[int(quarter_index) - 1]
