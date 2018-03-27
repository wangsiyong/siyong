# coding:utf-8
import json


def join_duplicate_keys(ordered_pairs):
    """to load duplicate key json"""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            if isinstance(d[k], list):
                d[k].append(v)
            else:
                newlist = []
                newlist.append(d[k])
                newlist.append(v)
                d[k] = newlist
        else:
            d[k] = v
    return d


def load_duplicate_json(filename):
    with open(filename) as fp:
        data = json.load(fp, object_pairs_hook=join_duplicate_keys)
        return data


def dump_duplicate_json(obj, filename):
    json_str = pretty_json(json.dumps(DuplicateDict(obj), ensure_ascii=False).encode('utf-8'))
    with open(filename, 'w') as fp:
        fp.write(json_str)


def pretty_json(s, step_size=4, multi_line_strings=False, advanced_parse=False, tab=False):
    out = ''
    step = 0
    in_marks = False  # Are we in speech marks? What character will indicate we are leaving it?
    escape = False  # Is the next character escaped?

    if advanced_parse:
        # \x1D (group seperator) is used as a special character for the parser
        # \0x1D has the same effect as a quote ('") but will not be ouputted
        # Can be used for special formatting cases to stop text being processed by the parser
        s = re.sub(r'datetime\(([^)]*)\)', r'datetime(\x1D\g<1>\x1D)', s)
        s = s.replace('\\x1D', chr(0X1D))  # Replace the \x1D with the single 1D character

    if tab:
        step_char = '\t'
        step_size = 1  # Only 1 tab per step
    else:
        step_char = ' '
    for c in s:

        if step < 0:
            step = 0

        if escape:
            # This character is escaped so output it without looking at it
            escape = False
            out += c
        elif c in ['\\']:
            # Escape the next character
            escape = True
            out += c
        elif in_marks:
            # We are in speech marks
            if c == in_marks or (not multi_line_strings and c in ['\n', '\r']):
                # but we just got to the end of them
                in_marks = False
            if c not in ["\x1D"]:
                out += c
        elif c in ['"', "'", "\x1D"]:
            # Enter speech marks
            in_marks = c
            if c not in ["\x1D"]:
                out += c
        elif c in ['{', '[']:
            # Increase step and add new line
            step += step_size
            out += c
            out += '\n'
            out += step_char * step
        elif c in ['}', ']']:
            # Decrease step and add new line
            step -= step_size
            out += '\n'
            out += step_char * step
            out += c
        elif c in [':']:
            # Follow with a space
            out += c
            out += ' '
        elif c in [',']:
            # Follow with a new line
            out += c
            out += '\n'
            out += step_char * step
        elif c in [' ', '\n', '\r', '\t', '\x1D']:
            #Ignore this character
            pass
        else:
            # Character of no special interest, so just output it as it is
            out += c
    return out


class DuplicateDict(dict):
    '''
    to dump duplicate key(item) json\n
    only work in python2
    '''
    def __init__(self, data):
        self['who'] = '12sigma'     # need to have something in the dictionary
        self._data = data

    def __getitem__(self, key):
        return self._value

    def __iter__(self):
        def generator():
            for key, value in self._data.items():
                if isinstance(value, list) and key == 'item':
                    for i in value:
                        if isinstance(i, dict):
                            self._value = DuplicateDict(i)
                        else:
                            self._value = i
                        yield key
                elif isinstance(value, dict):
                    self._value = DuplicateDict(value)
                    yield key
                else:
                    self._value = value
                    yield key

        return generator()
