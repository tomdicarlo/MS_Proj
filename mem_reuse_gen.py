import math
import os
from itertools import islice
import time
from collections import defaultdict, deque

#import heartrate 
#heartrate.trace(browser=True)


# Page size in bytes
PAGE_SIZE = 4096
MASK_SIZE = math.log(PAGE_SIZE, 2)
MASK = int("0xfffffffff000",16)
# MAX NUM OF BYTES TO BE READ AT A SINGLE TIME
MAX_READ_SIZE = 10000000
#@profile
def get_mem_reuse(filename):
    start_time = time.perf_counter()
    with open(filename, 'rb') as f:
        access_count = 0
        page_counts = defaultdict(int)
        reuse_size_counts = defaultdict(int)
        page_accesses = deque()
        cumulative_reuse_distance = 0
        bad_access_counts = 0
        file_size = os.path.getsize(filename)
        num_bytes_read = 0
        for lines in iter(lambda: tuple(islice(f, MAX_READ_SIZE)), ()):
            access_count += len(lines)

            for line in lines:

                    instance = line.split()
                    num_bytes_read += len(line)
                    try:
                        page = int(instance[2], 16) & MASK
                    except:
                        bad_access_counts += 1
                        continue
                    if page_counts[page] < 2:
                        page_counts[page] += 1
                    if page in page_accesses:
                        reuse_distance = page_accesses.index(page)
                        reuse_size_counts[reuse_distance] += 1
                        page_accesses.remove(page)
                    
                    page_accesses.appendleft(page)

            print("Starting new batch")
            percent = num_bytes_read/file_size*100
            print(str(percent) + "% of bytes read so far")
            curr_time = time.perf_counter()
            print(str(((curr_time-start_time)/(percent/100))*(1-(percent/100))) + " estimated seconds remaining\n")

    reuse_sizes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    # We are pre-calculating these values since they are fixed to save time
    reuse_barriers = [2**0, 2**1, 2**2, 2**3, 2**4, 2**5, 2**6, 2**7, 2**8, 2**9, 2**10, 2**11, 2**12, 2**13, 2**14, 2**15, 2**16, 2**17, 2**18, 2**19]
    reaccessed = 0
    accessed = 0

    true_access_count = access_count - bad_access_counts

    for page in page_counts:
        accessed+=1
        if page_counts[page] >1:
            reaccessed += 1
    # for key, value in reused_pages.items():
    #     if value:
    #         reaccessed += 1
    #     accessed += 1
    page_reuse_percentage = reaccessed/accessed

    for val in reuse_size_counts:
        cumulative_reuse_distance += val*reuse_size_counts[val]
        i = 0
        for barrier in reuse_barriers:
            if val >= barrier:
                reuse_sizes[i] += reuse_size_counts[val]
            else:
                break
            i+=1

    avg_reuse_distance = cumulative_reuse_distance/true_access_count


    cdfs = [(true_access_count-num) / true_access_count for num in reuse_sizes]

    print("Stats for " + filename[0:len(filename)-3])
    print("Total Seconds Elapsed: " + str(time.perf_counter()-start_time) + "\n")
    print("Average Reuse Distance:" + str(avg_reuse_distance))
    print("Page Reuse Percentage:" + str(page_reuse_percentage))
    print("CDFS:" + str(cdfs))
    print("Percentage of Bad Memory Addressed Provided By Tool:" + str(bad_access_counts/(bad_access_counts + access_count)))
    return avg_reuse_distance, page_reuse_percentage, cdfs