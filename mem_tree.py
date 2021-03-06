import math

def get_page_stats(pages):
    total_count = 0;
    page_counts = {}
    for page in pages:
        if page in page_counts:
            page_counts[page] += 1
        else:
            page_counts[page] = 1
        total_count += 1
        
    page_counts = {key: value for key, value in reversed(sorted(page_counts.items(), key=lambda item:item[1]))}
    page_percentages = {}

    for page in page_counts:
        page_percentages[page] = page_counts[page]/total_count

    return page_counts, page_percentages

def print_page_stats(page_counts, page_percentages):
    print("Total number of pages: " + str(len(page_counts)))
    print("Number of Accesses:")
    for page in page_counts:
        print("Page " + page + ": " + str(page_counts[page]))

    print("Percentage of Accesses:")
    for page in page_percentages:
        print("Page " + page + ": " + str(page_percentages[page]))

def get_page_reuse_distances(pages):
    page_accesses = {}
    reuse_distances = {}
    for page in pages:
        if not page in page_accesses:
            page_accesses[page] = []
        else:
            reuse_distance = len(page_accesses[page])
            if not page in reuse_distances:
                reuse_distances[page] = []

            reuse_distances[page].append(reuse_distance)
            page_accesses[page] = []

        for access_record in page_accesses:
            if access_record != page and page not in page_accesses[access_record]:
                page_accesses[access_record].append(page)

    return reuse_distances



# Page size in bytes
PAGE_SIZE = 4096
MASK_SIZE = math.log(PAGE_SIZE, 2)
MASK = "0xfffffffff000"
print(MASK_SIZE)
f = open("pinatrace.out", "r")
data = f.read().split("\n")

instructions = []
access_types = []
addresses = []
pages = []

for row in data:
    if(row != "#eof" and row!=""):
        instance = row.split(' ')
        instructions.append(instance[0][:-1])
        access_types.append(instance[1])
        addresses.append(instance[2])
        page = int(instance[2], 16) & int(MASK, 16)
        pages.append(hex(page))

page_counts, page_percentages = get_page_stats(pages)
print_page_stats(page_counts, page_percentages)

reuse_distances = get_page_reuse_distances(pages)

print(reuse_distances)
