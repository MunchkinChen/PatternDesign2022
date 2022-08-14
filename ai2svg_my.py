#!/usr/bin/python
import sys
import os
import re
import getopt
import string
import chardet

color_set = 'cmyk'



class Path:
    def __init__(self,css_color=None):
        self.fill = css_color
        self.d = ""


def color_to_css(*color_tuple):
    if len(color_tuple) == 4:
        (c,m,y,k) = color_tuple
        r = int(max(1 - (k + c), 0) * 255)
        g = int(max(1 - (k + m), 0) * 255)
        b = int(max(1 - (k + y), 0) * 255)
        return "#%02X%02X%02X" % (r, g, b)
    if len(color_tuple) == 3:
        (r,g,b) = color_tuple
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        return "#%02X%02X%02X" % (r, g, b)

def process_fill_color(paths, match, color=color_set):
    if color == 'cmyk':
        cmyk = tuple([float(match.group(i)) for i in range(1,5)])
        css_color = color_to_css(*cmyk)

    if color == 'rgb':
        rgb = tuple(float(match.group(i)) for i in range(5,8))
        css_color = color_to_css(*rgb)

    if css_color != "#7AA1AC":
        path = Path(css_color)
        paths.append(path)


def process_fill_color_k(paths, match):
    # print('in process_fill_color_k')
    cmyk = [float(match.group(i)) for i in range(1,5)]
    css_color = color_to_css(*cmyk)
    # if css_color != "#7AA1AC": # bug color
    if 1:
        path = Path(css_color)
        paths.append(path)


def process_move(paths, match):
    # print('in process_move')
    path = paths[-1]
    (x, y) = (match.group(1), match.group(2))
    x = float(x)
    y = float(y)
    path.d += ' M%f,%f ' % (x, y)

def process_lineto(paths, match):
    # print('in process_lineto')
    path = paths[-1]
    (x, y) = (match.group(1), match.group(2))
    x = float(x)
    y = float(y)
    path.d += ' L%f,%f ' % (x, y)


def process_curveto(paths, match):
    # print('in process_curveto')
    path = paths[-1]
    cs = [float(i) for i in match.groups()]

    p = ' C%f,%f,%f,%f,%f,%f ' % tuple(cs)
    path.d += p

def process_end_path(paths, match):
    # print('in process_end_path')
    path = paths[-1]
    path.d += 'z'



dispatch_table = {
    r'^ *([-\d\.]+) -([-\d\.]+) m$': process_move,
    r'^ *([-\d\.]+) -([-\d\.]+) [lL]$': process_lineto,
    r'^ *([-\d\.]+) -([-\d\.]+) ([-\d\.]+) -([-\d\.]+) ([-\d\.]+) -([-\d\.]+) [cC]$': process_curveto,
    r'^ *([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) Xa$': process_fill_color,
    r'^ *([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) [kK]$': process_fill_color_k,
    r'^ *([nNBbfFsS])': process_end_path,
}

dispatch_list = [(re.compile(k), v) for (k, v) in dispatch_table.items()]



def process_line(paths, l):
    # print('processing line :',l)

    found = 0
    for (regex, proc) in dispatch_list: # match到谁就执行谁对应的函数 proc是对应的函数
        m = regex.match(l)
        if m != None:
            found = 1
            proc(paths, m)
            break

    if not found:
        pass
        # print('ignoring ', l)




def ai2svg(ai_filename, svg_filename):
    # open a first time to check if compressed
    inf = open(ai_filename, encoding='latin1')

    find_EndSetUp = re.compile(r'%%EndSetup')
    res = find_EndSetUp.findall(inf.read())
    if len(res) == 0:
        print('.ai保存时压缩了，导出svg失败！')
        return -1
    inf.close()

    # open a second time to parse
    inf = open(ai_filename, encoding='latin1')

    artbox_regexp = r'^(.*)%%BoundingBox: ([-\d\.]+) -([-\d\.]+) ([-\d\.]+) -([-\d\.]+)(.*)$'
        # r'^(.*)CropBox\[([\d\.]+) ([\d\.]+) ([\d\.]+) ([\d\.]+)\](.*)$'


    (x1,y1,x2,y2,w,h) = (None,None,None,None,None,None)

    l = inf.readline()

    while not re.match("%%EndSetup", l):
        l = inf.readline()

        artbox_obj = re.match(artbox_regexp, l)

        if artbox_obj:
            (x1, y2, x2, y1) = tuple(artbox_obj.groups()[1:5])
            # (x1, y1, x2, y2) = tuple(artbox_obj.groups()[1:5])
            w = float(float(x2) - float(x1))
            h = float(float(y2) - float(y1))


    paths = []

    rest_lines = inf.readlines()

    i = 0
    while i < len(rest_lines):
        l = rest_lines[i]
        l = l[:-1]  # eliminate \n

        if re.match("%%EOF",l):
            break

        if re.match("endstream", l):
            last_l = rest_lines[i - 1][:-1]
            i += 4
            l = last_l + rest_lines[i][:-1]

        process_line(paths, l)
        i += 1

    def dump_output(paths, filename):
        outf = open(filename, 'w')
        outf.write(
            ''' <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x1} {y1} {w} {h}" width="{w}"  height="{h}">\n''' \
            .format(x1=x1, x2=x2, y1=y1, y2=y2, w=w, h=h))
        for path in paths:
            outf.write('''\n <path style="fill:{fill_color};" d="{d}" /> \n'''.format(fill_color=path.fill, d=path.d))
        outf.write('</svg>')

    dump_output(paths, svg_filename)
    return 1


#
ai_filename = '/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/elephant.ai'
svg_filename = '/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/elephant.svg'

ret = ai2svg(ai_filename,svg_filename)
print(ret)