def division(x, y):
    if y == 0:
        raise ZeroDivisionError('div by zero')
    return x/y

if __name__ == '__main__':
    try:
        division(1, 0)
    except ZeroDivisionError as e:
        print(e)
