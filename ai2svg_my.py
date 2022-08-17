#!/usr/bin/python
# import sys
# import os
import re
# import getopt
# import string
# import chardet
from mysvg import Mysvg

COLOR_SET = 'cmyk'

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

def process_fill_color(paths, match, has_minus_sign):
    if COLOR_SET == 'cmyk':
        cmyk = tuple([float(match.group(i)) for i in range(1,5)])
        css_color = color_to_css(*cmyk)

    if COLOR_SET == 'rgb':
        rgb = tuple(float(match.group(i)) for i in range(5,8))
        css_color = color_to_css(*rgb)

    path = Path(css_color)
    paths.append(path)


def process_fill_color_k(paths, match, has_minus_sign):
    # print('in process_fill_color_k')
    cmyk = [float(match.group(i)) for i in range(1,5)]
    css_color = color_to_css(*cmyk)
    path = Path(css_color)
    paths.append(path)


def process_move(paths, match, has_minus_sign):
    # print('in process_move')
    path = paths[-1]
    (x, y) = (match.group(1), match.group(2))
    x = float(x)
    y = float(y)
    if not has_minus_sign:
        y = -y
    path.d += ' M%f,%f ' % (x, y)

def process_lineto(paths, match, has_minus_sign):
    # print('in process_lineto')
    path = paths[-1]
    (x, y) = (match.group(1), match.group(2))
    x = float(x)
    y = float(y)
    if not has_minus_sign:
        y = -y
    path.d += ' L%f,%f ' % (x, y)


def process_curveto(paths, match, has_minus_sign):
    # print('in process_curveto')
    path = paths[-1]
    cs = [float(i) for i in match.groups()]
    if has_minus_sign:
        p = ' C%f,%f,%f,%f,%f,%f ' % tuple(cs)
    if not has_minus_sign:
        p = ' C%f,-%f,%f,-%f,%f,-%f ' % tuple(cs)
    path.d += p

def process_end_path(paths, match, has_minus_sign):
    # print('in process_end_path')
    path = paths[-1]
    path.d += 'z'

# (?:re) match re but dont remembre in group
dispatch_table = {
    r'^ *([-\d\.]+) (?:|-)([\d\.]+) m$': process_move,
    r'^ *([-\d\.]+) (?:|-)([\d\.]+) [lL]$': process_lineto,
    r'^ *([-\d\.]+) (?:|-)([\d\.]+) ([-\d\.]+) (?:|-)([\d\.]+) ([-\d\.]+) (?:|-)([\d\.]+) [cC]$': process_curveto,
    r'^ *([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) Xa$': process_fill_color,
    r'^ *([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+) [kK]$': process_fill_color_k,
    r'^ *([nNBbfFsS])': process_end_path,
}

dispatch_list = [(re.compile(k), v) for (k, v) in dispatch_table.items()]

# l = '145.749352007915 39.8603481716 m'
# found=0
# for (regex, proc) in dispatch_list:  # match到谁就执行谁对应的函数 proc是对应的函数
#     m = regex.match(l)
#     if m != None:
#         print(m.groups())


def process_line(paths, l, has_minus_sign):
    # print('processing line')
    # print(l)

    found = 0
    for (regex, proc) in dispatch_list: # match到谁就执行谁对应的函数 proc是对应的函数
        m = regex.match(l)
        if m != None:
            found = 1
            proc(paths, m, has_minus_sign)
            break

    if not found:
        pass
        # print('ignoring \n', l)


#%%
def ai2svg(ai_filename, svg_filename):
    # open a first time to check if compressed
    inf = open(ai_filename, encoding='latin1')
    inf_read = inf.read()

    find_EndSetUp = re.compile(r'%%EndSetup')
    res = find_EndSetUp.findall(inf_read)

    has_minus_sign = True
    re_curve = r'\n([-\d\.]+) (|-)([\d\.]+) ([-\d\.]+) (|-)([\d\.]+) ([-\d\.]+) (|-)([\d\.]+) [cC]\n'
    find_C = re.compile(re_curve)
    res_C = find_C.findall(inf_read)[-1]
    # print(res_C)
    if res_C[1] == res_C[4] == res_C[7] == '':
        has_minus_sign = False
    # print(has_minus_sign)



    if len(res) == 0:
        print('.ai保存时压缩了，导出svg失败！')
        return -1
    inf.close()

    # open a second time to parse
    inf = open(ai_filename, encoding='latin1')
    bbox_regexp = r'^(.*)%%BoundingBox: ([-\d\.]+) (?:|-)([\d\.]+) ([-\d\.]+) (?:|-)([\d\.]+)(.*)$'
        # r'^(.*)CropBox\[([\d\.]+) ([\d\.]+) ([\d\.]+) ([\d\.]+)\](.*)$'

    (x1,y1,x2,y2,w,h) = (None,None,None,None,None,None)

    l = inf.readline()

    while not re.match("%%EndSetup", l):
        l = inf.readline()

        bbox_obj = re.match(bbox_regexp, l)

        if bbox_obj:
            (x1, y2, x2, y1) = tuple(bbox_obj.groups()[1:5])
            if not has_minus_sign:
                y2 = '-'+y2
                y1 = '-'+y1
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


        process_line(paths, l, has_minus_sign)
        i += 1

    def dump_output(paths, filename):
        outf = open(filename, 'w')
        if not has_minus_sign:
            y1_here = abs(float(y1))
        else:
            y1_here = y1
        outf.write(
            ''' <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x1} {y1} {w} {h}" width="{w}"  height="{h}">\n''' \
            .format(x1=x1, x2=x2, y1=y1_here, y2=y2, w=w, h=h))
        for path in paths:
            outf.write('''\n <path style="fill:{fill_color};" d="{d}" /> \n'''.format(fill_color=path.fill, d=path.d))
        outf.write('</svg>')
        outf.close()

    dump_output(paths, svg_filename)

    if not has_minus_sign:
        tmpsvg = Mysvg(svg_filename)
        tmpsvg.move(0,2*abs(float(y1)))
        tmpsvg.save(svg_filename)

    inf.close()
    return 1


#
ai_filename = '/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/bear.ai'
svg_filename = '/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/bear.svg'
#
ret = ai2svg(ai_filename,svg_filename)

