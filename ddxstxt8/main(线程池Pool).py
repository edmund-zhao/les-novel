import json
from math import ceil
import gc
import tracemalloc

from lxml import etree

import bot
import time
from multiprocessing import Pool, Manager
import sys, getopt, os


poolNum = 16

opts, args = getopt.getopt(sys.argv[1:], "hkc:o:", ["start=", "end=","single","sorted","bookshelf","stared",'epub','order','log','tagid=','max='])
for opt, arg in opts:
    if opt == "--start":
        start = int(arg)
    elif opt == '--end':
        end = int(arg)

# 加载进入队列
def initQueue(q):
    with open('./queue.json','r') as f:
        for i in json.load(f)['urls']:
            q.put(i)
            print(i)


def splitList(l,n):
    u = len(l)/n
    t = []
    for i in range(n):
        t.append(l[ceil(u)*i:(i+1)*ceil(u)])
    if type(u) == float:
        t[-1].extend(l[ceil(u)*n:])
    return t

def maxRun(tags, q):
    print('第{}个线程开始'.format(tags))
    Bot = bot.Bot('12315')
    while not q.empty():
        url = q.get()
        print('第{}个线程正在进行: '.format(tags), url)
        Bot.__init__(url)
        Bot.run()
    print('-----------')
    return 0

if __name__ == '__main__':

    threads = []
    start_time = time.time()

    ### 以下是多进程
    '''
    for i in range(poolNum):
        th = threading.Thread(target=maxRun, args=(runList[i],i,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    '''

    ### 以下是多进程
    manager = Manager()
    queue = manager.Queue()
    initQueue(queue)
    p = Pool(poolNum)
    for i in range(poolNum + 1):
        p.apply_async(maxRun, args=(i,queue))
    p.close()
    p.join()
    print(time.time()-start_time,'s')
    # snapshot = tracemalloc.take_snapshot()
    # top_stats = snapshot.statistics('lineno')  # lineno,逐行统计；filename，统计整个文件内存
    # for stat in top_stats:
    #     print(stat)