import json
from urllib.request import urlopen
import urllib
import re
import _thread
import logging
import time

search_string = 'Apocalyptron'
urlstub = "https://web.archive.org/web/"
CHUNK_SIZE = 500
SLEEP_TIMER_PER_RETRY = 0.75
resultURL = []
global done_lock
countChecksPerTID = []


def processurl(argurl):
    try:
        page = urlopen(argurl)
    except urllib.error.URLError:
        return -1,-1
    html = page.read().decode('utf-8')
    return 0,html

# search a chunk for the string
def search_chunk_of_urls(threadID,datachunk):
    global search_string
    global urlstub
    global CHUNK_SIZE
    global SLEEP_TIMER_PER_RETRY
    global resultURL
    global done_lock
    global countChecksPerTID

    logging.debug('TID %d Searching from %s to %s', threadID, datachunk[0], datachunk[CHUNK_SIZE - 1])
    countChecksPerTID.append(0)

    for line in datachunk:
        if (done_lock.locked() == True):
            return
        url = urlstub + line[0] + "/" + line[1]

        errCode,html = processurl(url)
        while (errCode != 0):
            time.sleep(SLEEP_TIMER_PER_RETRY)
            errCode,html = processurl(url)

        matches = re.findall(search_string, html)
        logging.debug('TID %d Checking %s',threadID,line)
        countChecksPerTID[threadID] = countChecksPerTID[threadID]+1
        if len(matches) != 0:
            done_lock.acquire()
            resultURL = line
            return

def main():
    global done_lock
    global countChecksPerTID

    done_lock = _thread.allocate_lock()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(relativeCreated)6d %(message)s"
    )

    file = open("C:\\Users\\oteod\\Desktop\\urls\\urlseuw.txt", "rt")
    data = json.load(file)

    print("Number of entries: ",len(data))
    nbThreads = 20
    print("Spawning", nbThreads, "threads")

    i = 0
    while (i < nbThreads):
        _thread.start_new_thread(search_chunk_of_urls, (i, data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]))
        i = i+1

    while (done_lock.locked() != True):
        time.sleep(5)

    totalcount = 0
    i=0
    for idx in countChecksPerTID:
        print('TID', i, 'checked', idx, 'entries')
        totalcount = totalcount + idx
        i=i+1

    print('Total entries checkd:',totalcount)

    print(resultURL)

if __name__ == "__main__":
    main()