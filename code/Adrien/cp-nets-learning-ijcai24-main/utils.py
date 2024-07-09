import math

# « Elias gamma encoding » (Elias, 1975)
def code_length_integer_2(n): # encode aussi les 0
    return 2 * math.floor(math.log2(n + 1)) + 1

# "universal code for the integers", Rissanen, 1983
def code_length_integer(n): # for n>=0
    n += 1
    out = math.log2(2.865064)
    while n > 0:
        out += math.log2(n)
        n = math.log2(n)
    return out

def instantiate(instance, variables, value):
    for i in range(len(variables)):
        instance[variables[i]] = value[i]

