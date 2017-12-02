
from multiprocessing import Pool


def doit(article):
    while(True):
        print('YES ')
    

if __name__ == '__main__':
    p = Pool(10)
    # iterator
    p.map(doit, iterator)

