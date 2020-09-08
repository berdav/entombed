#!/usr/bin/env python3

import sys
import random
import getopt

NO_WALL       = 0
WALL          = 1
RANDOM_CHOICE = 2

# Default row value
rows = 25
# Default column value
columns = 39
print_rules_opt = False
no_maze = False
no_symmetry = False

lut = [
        # Selection algorithm
        #    _ _ _
        #  _|c|d|e|
        # |a|b|X
        #
        # key, bits: edcba
        # edcba
        WALL,          WALL,       WALL,          RANDOM_CHOICE,
        NO_WALL,       NO_WALL,    RANDOM_CHOICE, RANDOM_CHOICE,
        WALL,          WALL,       WALL,          WALL,
        RANDOM_CHOICE, NO_WALL,    NO_WALL,       NO_WALL,
        WALL,          WALL,       WALL,          RANDOM_CHOICE,
        NO_WALL,       NO_WALL,    NO_WALL,       NO_WALL,
        RANDOM_CHOICE, NO_WALL,    WALL,          RANDOM_CHOICE,
        RANDOM_CHOICE, NO_WALL,    NO_WALL,       NO_WALL,
]

def randombit():
    return random.choice([0,1])

def print_row(r, specular=True):
    for item in r:
        if item:
            print('█', end ='')
        else:
            print(' ', end ='')
    # Create specular labyrinth
    if (not specular):
        print()
        return

    for item in r[::-1]:
        if item:
            print('█', end ='')
        else:
            print(' ', end ='')
    print()

def get_idx(a, b, c, d, e):
    return (a << 0) | (b << 1) | (c << 2) | (d << 3) | (e << 4)

def generate_row(r):
    out = [ 0 for _ in range(len(r))]

    for i in range(len(r)):
        if i == 0 or i == 1:
            a = 0
        else:
            a = out[i - 2]

        if i == 0:
            b = 0
        else:
            b = out[i - 1]

        if i == 0:
            c = 0
        else:
            c = r[i-1]

        d = r[i]

        if i == len(r) - 1:
            e = 0
        else:
            e = r[i+1]

        idx = get_idx(a,b,c,d,e)
        #print(a, b, c, d, e, idx)

        out[i] = lut[idx]
        if out[i] == RANDOM_CHOICE:
            out[i] = randombit()

    return out

def lut_to_str(lut):
    outs = ""
    for v in lut:
        outs+="{},".format(v)
    return outs

def lut_from_str(lutstr):
    return list(map(int, lutstr.split(",")))

def print_rules(rules):
    blocksize = 8
    cline = "│"
    nline = "│"
    nextline=""
    print("┌────"+"┬────"*(blocksize-1)+"┐")
    for rule_idx in range(len(rules)):
        out = ''
        a = '.'
        if (rule_idx & 1) >> 0:
            a = '█'
        b = '.'
        if (rule_idx & 2) >> 1:
            b = '█'
        c = '.'
        if (rule_idx & 4) >> 2:
            c = '█'
        d = '.'
        if (rule_idx & 8) >> 3:
            d = '█'
        e = '.'
        if (rule_idx & 16) >> 4:
            e = '█'
        if rules[rule_idx] == RANDOM_CHOICE:
            out = '?'
        if rules[rule_idx] == NO_WALL:
            out = ' '
        if rules[rule_idx] == WALL:
            out = '█'

        sep1 = "│"
        if (((rule_idx + 1) % blocksize)!=0):
            sep1 = "│"
        sep2 = "│ "
        if (((rule_idx + 1) % blocksize)!=0):
            sep2 = "│"

        cline += (" {}{}{}{}".format(c, d, e, sep1))
        nline += ("{}{}{}{}{} {}".format(a, b, "\x1b[0;35;40m", out,
            "\x1b[0m", sep2))

        if (((rule_idx + 1) % blocksize)==0):
            print(nextline, end ='')
            print(cline)
            cline = "│"
            print(nline)
            nline = "│"
            if (rule_idx < (len(rules) - 1)):
                nextline = "├────"+"┼────"*(blocksize-1)+"┤\n"
    print("└────"+"┴────"*(blocksize-1)+"┘")

optlist, args = getopt.getopt(sys.argv[1::], 'R:hr:c:pMS', [
    'help',
    'print-rules',
    'no-maze',
    'no-simmetry',
    'rules=',
    'rows=',
    'colums='])

def usage():
    print("Open Entombed")
    print("Generate maze with entombed algorithm")
    print("options:")
    print(" -p --print-rules : Print rules in pretty format")
    print(" -M --no-maze :     Do not generate maze")
    print(" -h --help:         This help")
    print(" -S --no-symmetry:  Disable maze symmetry")
    print(" -r --rows:         Number of rows to generate, default {}".format(rows))
    print(" -c --columns:      Number of columns to generate, default {}".format(columns))
    print(" -R --rules:        Load different rules for the maze generation")
    print("                    The rules should be an array of 32 items:")
    print("                    {} -> No wall".format(NO_WALL))
    print("                    {} -> Wall".format(WALL))
    print("                    {} -> Random value".format(RANDOM_CHOICE))
    print("                        ┌───┬───┬───┐")
    print("                        │ c │ d │ e │")
    print("                    ┌───┼───┼───┼───┘")
    print("                    │ a │ b │ V │    ")
    print("                    └───┴───┴───┘    ")
    print("                    with V as the resultant value")
    print("                                edcba bits       ecdba            ecdba            ecdba")
    print("                    value_for_00000,value_for_00001,value_for_00010,value_for_00011,...");
    print("                    default value is {}".format(lut_to_str(lut)))

for optname,optval in optlist:
    if optname == '-R' or optname == '--rules':
        lut = lut_from_str(optval)
    if optname == '-h' or optname == '--help':
        usage()
        sys.exit(0)
    if optname == '-r' or optname == '--rows':
        rows = int(optval)
    if optname == '-c' or optname == '--colums':
        columns = int(optval)
    if optname == '-M' or optname == '--no-maze':
        no_maze = True
    if optname == '-S' or optname == '--no-symmetry':
        no_symmetry = True
    if optname == '-p' or optname == '--print-rules':
        print_rules_opt = True

if not no_maze:
    initial_state = [randombit() for _ in range(columns)]
    current_row = initial_state

    print_row(initial_state, specular = not no_symmetry)

    for i in range(rows):
        row = generate_row(current_row)
        print_row(row, specular = not no_symmetry)
        current_row = row

if print_rules_opt:
    print()
    print("Rules")
    print(" ",lut_to_str(lut))
    print_rules(lut)
