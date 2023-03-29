def get_loc() -> tuple[tuple[float, float], str]:
    """
    Return value like:
    ((123, 567), "xxx")
    """
    with open('../minic.log', encoding='gbk', errors='ignore') as f:
        for line in f.readlines():
            if line.startswith('+GTGIS'):
                if ',' in line:
                    loc = line[9:-2].split(',')
                    loc = loc[0], loc[1]
                else:
                    desc = line[9:-2]
    return loc, desc


if __name__ == "__main__":
    r = get_loc()
    print(r)
