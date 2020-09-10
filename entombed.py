#!/usr/bin/env python3

# Copyright (c) 2020 Davide Berardi <berardi.dav@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import random
import getopt
import itertools

from functools import reduce

NO_WALL       = 0
WALL          = 1
RANDOM_CHOICE = 2

# Default row value
rows                    = 25
# Default column value
columns                 = 39
# Do not print rules by default
print_rules_opt         = False
# Print maze by default
no_maze                 = False
# Print a symmetrical maze
no_symmetry             = False
# Do not print probabilities by default
print_probabilities_opt = False
# How much rules to print in one row
rules_blocks            = 8
# Save the maze to print it to a file
saved_maze              = None
# Truecolor
truecolor               = False
# Output file
output                  = None
# Default output background color
output_bg               = 0x3f3f3f
# Default output foreground color
output_fg               = 0x775577
# Default output scale when outputting to image
output_scale            = 10

# Default rules
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

def hex_to_truecolor(c, fg=True):
    red   = (c&0xff0000) >> 16
    green = (c&0x00ff00) >> 8
    blue  = (c&0x0000ff) >> 0

    if fg:
        return "\x1b[38;2;{};{};{}m".format(red,green,blue)
    return "\x1b[48;2;{};{};{}m".format(red,green,blue)

def randombit():
    return random.choice([0,1])

def print_row(r, specular=True, truecolors=False, foreground=0x0, background=0x0):
    start_color_fg = ""
    start_color_bg = ""
    reset_color = ""
    if truecolors:
        start_color_fg = hex_to_truecolor(foreground, True)
        start_color_bg = hex_to_truecolor(background, False)
        reset_color = "\x1b[0m"

    wallitem = "{}█{}".format(start_color_fg, reset_color)
    nowallitem = "{} {}".format(start_color_bg, reset_color)

    for item in r:
        if item:
            print(wallitem, end ='')
        else:
            print(nowallitem, end ='')
    # Create specular labyrinth
    if (not specular):
        print()
        return

    for item in r[::-1]:
        if item:
            print(wallitem, end ='')
        else:
            print(nowallitem, end ='')
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

def print_rules(rules, blocksize=8):
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

def probselect(V, cell):
    # Probability to have a 1 in A
    if V:
        return cell
    return 1 - cell

def probabilities(rows, cols, start_row = 0, start_col = 0):
    # Matrix of probabilities
    prob = [ [0, 0]+ [ 0 for c in range(cols) ] + [0,0] for _ in range(rows + 1)]
    for k in range(len(prob[0]) - 2):
        prob[0][k + 2] = .5
    scan = 0 + 2

    for r in range(start_row + 1, rows + 1):
        for c in range(start_col + 2, cols + 2):
            psum = 0

            # Calculate conditioned probabilities
            for A,B,C,D,E in itertools.product([0,1], repeat=5):
                probabilities = [
                    probselect(A, prob[r][c-2]),
                    probselect(B, prob[r][c-1]),
                    probselect(C, prob[r-1][c-1]),
                    probselect(D, prob[r-1][c]),
                    probselect(E, prob[r-1][c+1])
                ]

                p = reduce(lambda x,y: x*y, probabilities)

                idx = (A << 0) | (B << 1) | (C << 2) | (D << 3) | (E << 4)
                if (lut[idx] == RANDOM_CHOICE):
                    psum += (.5 * p)
                else:
                    psum += (lut[idx] * p)
            prob[r][c]=psum

    return prob


optlist, args = getopt.getopt(sys.argv[1::], 'bB:c:F:hMpPr:R:tsSO:', [
    'rules-blocks=',
    'columns='
    'help',
    'no-maze',
    'no-simmetry',
    'print-rules',
    'print-prob',
    'rules=',
    'rows=',
    'colors=',
    'output=',
    'output-scale=',
    'output-bg=',
    'output-fg=',
])

def usage():
    print("Open Entombed")
    print("Generate maze with entombed algorithm")
    print("options:")
    print(" -b --rules-blocks: How much rules to print on a single line".format(rules_blocks))
    print(" -h --help:         This help")
    print(" -p --print-rules:  Print rules in pretty format")
    print(" -P --print-prob:   Print calculated probability")
    print(" -M --no-maze :     Do not generate maze")
    print(" -S --no-symmetry:  Disable maze symmetry")
    print(" -O --output:       Output to an image")
    print(" -s --output-scale: Output image scale")
    print(" -B --output-bg:    Output background color, default RGB:#{:06x}".format(output_bg))
    print(" -F --output-fg:    Output foreground color, default RGB:#{:06x}".format(output_fg))
    print(" -t --colors:       Colorize the output using truecolors")
    print(" -c --columns:      Number of columns to generate, default {}".format(columns))
    print(" -r --rows:         Number of rows to generate, default {}".format(rows))
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
    if optname == '-b' or optname == '--rules-blocks':
        rules_blocks = int(optval)
    if optname == '-r' or optname == '--rows':
        rows = int(optval)
    if optname == '-c' or optname == '--colums':
        columns = int(optval)
    if optname == '-M' or optname == '--no-maze':
        no_maze = True
    if optname == '-t' or optname == '--colors':
        truecolor = True
    if optname == '-S' or optname == '--no-symmetry':
        no_symmetry = True
    if optname == '-p' or optname == '--print-rules':
        print_rules_opt = True
    if optname == '-P' or optname == '--print-prob':
        print_probabilities_opt = True
    if optname == '-B' or optname == '--output-bg':
        output_bg = int(optval,16)
    if optname == '-F' or optname == '--output-fg':
        output_fg = int(optval,16)
    if optname == '-O' or optname == '--output':
        output = optval
    if optname == '-s' or optname == '--output-scale':
        output_scale = int(optval)

if not no_maze:
    initial_state = [randombit() for _ in range(columns)]
    current_row = initial_state

    print_row(initial_state, specular = not no_symmetry,
            truecolors=truecolor,
            background=output_bg, foreground=output_fg)
    saved_maze = [ initial_state ]

    for i in range(rows):
        row = generate_row(current_row)
        print_row(row, specular = not no_symmetry,
            truecolors=truecolor,
            background=output_bg, foreground=output_fg)
        # Save the maze for the output to image
        if output != None:
            saved_maze.append(row)

        current_row = row

if print_rules_opt:
    print()
    print("Rules")
    print(" ",lut_to_str(lut))
    print_rules(lut, blocksize=rules_blocks)

if print_probabilities_opt:
    print()
    print("Probabilities")
    for r in probabilities(rows, columns)[1::]:
        for c in r[2:-2]:
            print("{:.3f} ".format(c), end ='')
        print()

if output != None and saved_maze != None:
    # Place import here to require them only if output is required
    from PIL import Image
    import numpy

    print("Saving to {}".format(output))

    fg = ((output_fg&0xff0000)>>16, (output_fg&0xff00)>>8, (output_fg&0xff))
    bg = ((output_bg&0xff0000)>>16, (output_bg&0xff00)>>8, (output_bg&0xff))

    output_maze = []
    for row in saved_maze:
        r = []
        for el in row:
            if el:
                for i in range(output_scale):
                    r.append(fg)
            else:
                for i in range(output_scale):
                    r.append(bg)
        for el in row[::-1]:
            if el:
                for i in range(output_scale):
                    r.append(fg)
            else:
                for i in range(output_scale):
                    r.append(bg)
        for i in range(output_scale):
            output_maze.append(r)

    npimg = numpy.array(output_maze)

    PIL_img = Image.fromarray(numpy.uint8(npimg)).convert("RGB")

    PIL_img.save(output)
    # Save the image
