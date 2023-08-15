
def parse_txt(path):
    links = []
    with open(path, 'r') as file:
        for i,line in enumerate(file):
            if i == 0 or i == 1 or i == 2:
                continue
            links.append(line.strip())
    return links

