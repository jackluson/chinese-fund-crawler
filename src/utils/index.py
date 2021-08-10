
import time
import datetime
import os
from threading import Thread, Lock


def lock_process(func):
    lock = Lock()

    def wrapper(self, *args):
        lock.acquire()
        result = func(self, *args)
        lock.release()
        return result
    return wrapper


def debug(func):
    def wrapper(self, *args):  # 指定一毛一样的参数
        print("[DEBUG]: enter {}()".format(func.__name__))
        return func(self, *args)
    return wrapper  # 返回包装过函数


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


def get_last_quarter_str(last_index=1):
    last_quarter_time = time.localtime(
        time.time() - last_index * 3 * 30 * 24 * 3600)
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


def fisrt_match_condition_from_list(list, code):
    for item in list:
        stock_code = item.split('-', 1)[0]
        is_exist = code == stock_code
        if is_exist:
            return item


def dict_list_to_list_list(dict_list, key_sort_list):
    tuple_list = []
    for item in dict_list:
        temp_list = []
        for key in key_sort_list:
            temp_list.append(item.get(key))
        tuple_list.append(temp_list)
    return tuple_list


def find_from_list_of_dict(dict_list, match_key, value):
    res = None
    for sub in dict_list:
        if sub[match_key] == value:
            res = sub
            break
    return res


def bootstrap_thread(target_fn, total, thread_count=2):
    threaders = []
    start_time = time.time()
    # 如果少于10个，只开一个线程
    if total < 10:
        thread_count = 1
    step_num = total / thread_count
    for i in range(thread_count):
        # start = steps[i]['start']
        # end = steps[i]['end']
        start = i * step_num
        end = (i + 1) * step_num
        t = Thread(target=target_fn, args=(int(start), int(end)))
        t.setDaemon(True)
        threaders.append(t)
        t.start()
    for threader in threaders:
        threader.join()
    end_time = time.time()
    print(total, 'run time is %s' % (end_time - start_time))
