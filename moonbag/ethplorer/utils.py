import numbers


def converter(num):
    if isinstance(num, numbers.Number):
        "{:.14f}".format(num)
