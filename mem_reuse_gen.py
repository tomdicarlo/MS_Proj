import math
import os
from itertools import islice
import time
#import heartrate 
#heartrate.trace(browser=True)


# Page size in bytes
PAGE_SIZE = 4096
MASK_SIZE = math.log(PAGE_SIZE, 2)
MASK = "0xfffffffff000"
# MAX NUM OF BYTES TO BE READ AT A SINGLE TIME
MAX_READ_SIZE = 100000

#@profile
def get_mem_reuse(filename):
    start_time = time.perf_counter()
    with open(filename, 'rb') as f:
        access_count = 0
        reuse_sizes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # We are pre-calculating these values since they are fixed to save time
        reuse_barriers = [2**0, 2**1, 2**2, 2**3, 2**4, 2**5, 2**6, 2**7, 2**8, 2**9, 2**10, 2**11, 2**12, 2**13, 2**14, 2**15, 2**16, 2**17, 2**18, 2**19]
        reused_pages = {}
        page_accesses = []
        cumulative_reuse_distance = 0
        bad_access_counts = 0
        file_size = os.path.getsize(filename)
        num_bytes_read = 0
        for lines in iter(lambda: tuple(islice(f, MAX_READ_SIZE)), ()):
            
            for line in lines:
            
                if(line != "#eof" and line!=""):
                    
                    instance = line.split()
                    if(len(instance) == 3):
                            page = -1
                            num_bytes_read += len(instance)
                            try:
                                page = int(instance[2], 16) & int(MASK, 16)
                            except:
                                bad_access_counts += 1
                            if(page !=-1):
                                access_count += 1
                                if page in reused_pages:
                                    if not reused_pages[page]:
                                        reused_pages[page] = True
                                else:
                                    reused_pages[page] = False
                                if page in page_accesses:
                                    reuse_distance = page_accesses.index(page)
                                    cumulative_reuse_distance += reuse_distance
                                    i = 0
                                    for val in reuse_barriers:
                                        if reuse_distance >= val:
                                            reuse_sizes[i] += 1
                                        else:
                                            break
                                        i+=1
                                    page_accesses.remove(page)

                                
                                
                                #REUSE SIZES
                                
                                page_accesses.insert(0, page)

            print("Starting new batch")
            percent = num_bytes_read/file_size*1000
            print(str(percent) + "% of bytes read so far")
            curr_time = time.perf_counter()
            print(str(((curr_time-start_time)/(percent/100))*(1-(percent/100))) + " estimated seconds remaining\n")

    avg_reuse_distance = cumulative_reuse_distance/access_count
    reaccessed = 0
    accessed = 0
    for key, value in reused_pages.items():
        if value:
            reaccessed += 1
        accessed += 1
    page_reuse_percentage = reaccessed/accessed

    cdfs = [(access_count-num) / access_count for num in reuse_sizes]

    print("Stats for " + filename[0:len(filename)-3])
    print("Average Reuse Distance:" + str(avg_reuse_distance))
    print("Page Reuse Percentage:" + str(page_reuse_percentage))
    print("CDFS:" + str(cdfs))
    print("Percentage of Bad Memory Addressed Provided By Tool:" + str(bad_access_counts/(bad_access_counts + access_count)))
    print("Total Seconds Elapsed: " + str(time.perf_counter()-start_time) + "\n")
    return avg_reuse_distance, page_reuse_percentage, cdfs