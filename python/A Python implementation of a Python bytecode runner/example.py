a = 1


def other_func():
    global a
    a = 1
    return a


var = 10


def example_func(a, b):
    d = {"v": 2}
    ret = ""
    if a in [1, 2]:
        ret = (other_func() + a + b) * var
    else:
        ret = False
    d["v"] += 3
    return f"{d} , ret={ret}"
