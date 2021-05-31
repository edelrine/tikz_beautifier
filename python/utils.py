def gap(a, b):
    """return abs(b-a)"""
    return abs(a - b)


def is_float(token):
    """check if the token can be convert in float"""
    try:
        _ = float(token)
        return True
    except Exception:
        return False


def is_int(token):
    """check if the token can be convert in int"""
    try:
        return float(token).is_integer()
    except Exception:
        return False


def get_color_name(data_colors, red, green, blue):
    """return a color name corresponding to the r,g,b"""
    minn = float("inf")
    minn_name = "no name"
    for name, (r, g, b) in data_colors.items():
        score = (
            gap(red, r)**2 +
            gap(green, g)**2 +
            gap(blue, b)**2
        )

        if score < minn:
            minn = score
            minn_name = name

    return minn_name

def stripped(token):
    '''
    return a striped token

    >>> stripped(' test ')
    'test'
    >>> stripped([' test '])
    [' test ']
    '''
    if isinstance(token, str) and token != '\n':
        return token.strip()
    return token


def get_path(index):
    '''
    return path to element to run in exec function

    >>> get_path([0,1])
    '[0][1]'
    >>> array = [['a','b'], ['c', 'd']]
    '''
    return ''.join([f'[{i}]' for i in index])


def space_beetwen(last, new):
    '''
    return True if the two token need to be separete with espace'''
    OPEN = ('(', '[', '{')
    CLOSE = (')', ']', '}')

    if last is None:
        return False

    if True in (  # without space
            # opened brackets before
            last.endswith((
                *OPEN,
                '\\',
                '='
            )),
            # closing bracket after
            new.startswith((
                *CLOSE,
                '='
            )),
            # no space beetwen command and parameters
            last.startswith('\\') and new.startswith(OPEN)
    ):
        return False

    if True in (  # with espace
            # end with comma or --
            last.endswith((
                '--',
                ',',
                '.'
            )),
            # begin with --
            new.startswith('--'),
            # space beetwen text and brackets
            (new[0:1].isalpha() and last.endswith(CLOSE)),
            (last[-1:].isalpha() and new.startswith(OPEN))
    ):
        return True

    # default
    return False

