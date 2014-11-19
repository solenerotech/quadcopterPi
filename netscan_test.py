# -*- coding: utf-8 -*-
from netscan2 import netscan
from logger_manager import setupLogger
from time import time, sleep
logger = setupLogger('myQ', True, 'netscan_log.txt')


myNetscan = netscan(ip='192.168.1.1')
myNetscan.start()
initTime = time()
try:
    for j in range(50):
        n = 0
        #do something...
        for i in range(10):
            n = n * (i + 1)
        sleep(0.2)
        #logger.debug("cycle done!")


finally:
    # shut down cleanly
    myNetscan.stop()

    logger.debug("time: " + str(time()-initTime)+ " conn: " + str(myNetscan.connectionUp))