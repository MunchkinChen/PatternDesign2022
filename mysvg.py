#%%
from svgutils.compose import *
from copy import deepcopy
import random
import xml.etree.ElementTree as ET
import re
import math
import numpy as np

def preprocess_svg_hw(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    if 'viewBox' in root.attrib.keys():
        boundaries = root.attrib['viewBox']
        searchObj = re.search(r'(.*) (.*) (.*) (.*)', boundaries)
        searchObj_groups = searchObj.groups()
    elif 'enable-background' in root.attrib.keys():
        boundaries = root.attrib['enable-background']
        regexp = r'^(.*)([-\d\.]+) ([-\d\.]+) ([-\d\.]+) ([-\d\.]+)'
        searchObj = re.search(regexp, boundaries)
        searchObj_groups = searchObj.groups()[1:]
    else:
        return 0, 0

    x1 = float(searchObj_groups[0])
    y1 = float(searchObj_groups[1])
    width = searchObj_groups[2]
    height = searchObj_groups[3]
    root.attrib['width'] = width
    root.attrib['height'] = height
    # del root.attrib['viewBox']
    # del root.attrib['style']
    tree.write(svg_path)
    return x1, y1






class Mysvg(SVG):
    def __init__(self,fname=None, fix_mpl=False):
        (x1,y1) = preprocess_svg_hw(fname)
        self.x1 = x1
        self.y1 = y1

        super(Mysvg,self).__init__(fname, fix_mpl)
        self.unresized_width = self.width
        self.unresized_height = self.height

        super(Mysvg, self).move(-x1,-y1)


    def save(self,pathname):
        h_str = str(self.height)
        w_str = str(self.width)
        Figure(w_str, h_str, self).save(pathname)

    def rotate(self,angle=0):
        rotate_center = (self.unresized_width//2, self.unresized_height//2)
        super(Mysvg,self).rotate(angle,x=rotate_center[0], y=rotate_center[1])
        return self

    def flip(self,flip_val=1): # flip_val=1:左右  flip_val=2:上下
        if flip_val==1:
            super(Mysvg, self).scale(x=-1, y=1)
            super(Mysvg, self).move(self.width,0)
        if flip_val==2:
            super(Mysvg, self).scale(x=1, y=-1)
            super(Mysvg, self).move(0, self.height)
        return self

    def resize(self,size):
        self.unresized_width = self.width
        self.unresized_height = self.height
        super(Mysvg,self).scale(x=size,y=size)
        self._height = self._height * size
        self._width = self._width * size
        return self

    def move_center_to(self,x,y): #把中心点和(x,y)重合
        #左上角应该和以下坐标重合
        left_top_x = x - self.width // 2
        left_top_y = y - self.height // 2
        super(Mysvg, self).move(left_top_x,left_top_y)
        return self



# mysvg = Mysvg('/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/goat.svg')
# mysvg.resize(0.5)
# mysvg.save("/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/dog_editted_resized.svg")


# for i in range(7):
#     rotate_val = i*60
#     mysvg.save("/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/monkey_editted" + str(rotate_val) + ".svg")
#     mysvg.rotate(60)

# mysvg.move_center_to(mysvg.x1+mysvg.width//2,mysvg.y1+mysvg.height//2)
# mysvg.save("/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/monkey_editted_unchanged.svg")


# tiled_svgs = []
# for i in range(6):
#
#     curr = deepcopy(mysvg)
#     curr.rotate(i*60)
#     curr.move_center_to(100*i,50)
#     tiled_svgs.append(curr)
#
#
# Figure(3000, 500, *tiled_svgs).save("/Users/xiangyichen/PycharmProjects/Pattern_Design/input_ai/test4.svg")

#%%
class Layout:
    def __init__(self,h,w,pattern_interval_x,pattern_interval_y = None):
        if pattern_interval_y is None:
            pattern_interval_y = pattern_interval_x
        self.pattern_interval_x = pattern_interval_x
        self.pattern_interval_y = pattern_interval_y
        self.h = h
        self.w = w
        self.is_dense_pattern = None
        self.column_n = None

    def cal_pattern_pos(self, is_dense_pattern, shift=(0,0)):
        # dx dy 表示pattern grid (is_dense_pattern=False时) 的间距，而不是实际上的元素间距
        dx = int(self.pattern_interval_x * (1 + int(is_dense_pattern) * 0.4))
        dy = int(self.pattern_interval_y * (1 + int(is_dense_pattern) * 0.4))

        # default value for shift
        if not isinstance(shift, tuple):
            shift = (0,0)
        shift = (dx//2 + shift[0], dy//2 + shift[1])

        pos = [(dx*i+shift[0], dy*j+shift[1]) for j in range(-1,self.h//dy+1) for i in range(-1,self.w//dx+1)]

        if not is_dense_pattern:
            return pos

        else:
            pos_more = [(x + dx // 2, y + dy // 2) for (x, y) in pos]
            return pos + pos_more

    def cal_img_pos(self, imgs_len,
                    is_dense_pattern=False, shift=(0,0),
                    rotate=False, random_shift=False, flip=False,
                    pattern_select='random', first_pattern_i = 0,
                    use_position=[], use_rotate=[], use_pattern_select=[]):

        self.is_dense_pattern = is_dense_pattern

        # dx dy 表示pattern grid (is_dense_pattern=False时) 的间距，而不是实际上的元素间距
        dx = int(self.pattern_interval_x * (1 + int(is_dense_pattern) * 0.4))
        dy = int(self.pattern_interval_y * (1 + int(is_dense_pattern) * 0.4))

        pattern_select_save = []
        positions_save = []
        rotate_save = []
        flip_save = []

        positions = self.cal_pattern_pos(is_dense_pattern, shift=shift)

        if not isinstance(shift, tuple):
            shift = (0,0)
        shift = (dx//2 + shift[0], dy//2 + shift[1])


        iter = 0
        pattern_i = first_pattern_i % imgs_len
        flip_val = 0

        column_n = (self.w // dx + 2) * (1+int(is_dense_pattern))  # total number of columns
        self.column_n = column_n

        for position in positions:
            if not is_dense_pattern:
                column_i = round((position[0] - shift[0]) / dx)
                row_i = round((position[1] - shift[1]) / dy)

            else:
                position_i = positions.index(position)
                if position_i < len(positions)/2:
                    column_i = round((position[0] - shift[0]) / dx) * 2
                    row_i = round((position[1] - shift[1]) / dy) * 2
                else:
                    ref_position = positions[position_i - int(len(positions)/2)]
                    column_i = round((ref_position[0] - shift[0]) / dx) * 2 + 1
                    row_i = round((ref_position[1] - shift[1]) / dy) * 2 + 1

            # print(position,row_i,column_i)

            # decide which pattern to use in list imgs
            if len(use_pattern_select) > 0:
                pattern_i = use_pattern_select[iter % len(use_pattern_select)]
            elif pattern_select == 'random':
                pattern_i = random.randint(0,imgs_len-1)
            elif pattern_select == 'sequential':
                if not is_dense_pattern:
                    if column_n % imgs_len != 0:
                        pattern_i = (pattern_i + 1) % imgs_len
                    else:  # 如果列数能被元素数整除，为了避免排成一列一元素，每列再加一个额外的位移
                        pattern_i = ((column_i % imgs_len) + row_i) % imgs_len
                    # pattern_i = ((column_i % imgs_len) + row_i) % imgs_len
                else:
                    pattern_i = (pattern_i + 1) % imgs_len

            elif pattern_select == 'sequential_inclined_left':
                # pattern_i = (((column_i // 2) % imgs_len - int(row_i % 2 == 1)) + row_i) % imgs_len
                first_pattern_in_row = - (row_i//2) % imgs_len
                pattern_i = (first_pattern_in_row + column_i//2) % imgs_len
            elif pattern_select == 'sequential_inclined_right':
                first_pattern_in_row = ( (row_i+1) // 2) % imgs_len
                pattern_i = (first_pattern_in_row + column_i//2) % imgs_len
            elif pattern_select == 'row':
                pattern_i = row_i % imgs_len
            elif pattern_select == 'column':
                pattern_i = column_i % imgs_len

            pattern_select_save.append(int(pattern_i))

            # decide rotation value
            random_rotate_val = 0
            if len(use_rotate) > 0:
                random_rotate_val = use_rotate[iter % len(use_rotate)]
            elif rotate == 'random':
                random_rotate_val = random.randrange(-180,180)
            elif isinstance(rotate, int):
                random_rotate_val = rotate

            rotate_save.append(random_rotate_val)

            # decide position to move the pattern
            if len(use_position) > 0:
                new_position = use_position[iter % len(use_position)]
            elif random_shift:
                random_x = random.randrange(round(-dx/random_shift), round(dx/random_shift))
                random_y = random.randrange(round(-dy/random_shift), round(dy/random_shift))
                new_position = (position[0]+random_x,position[1]+random_y)
            else:
                new_position = position

            positions_save.append(new_position)

            # decide flip value
            if flip:
                # flip_val=0:不翻  flip_val=1:左右  flip_val=2:上下
                if flip=='left':
                    if not is_dense_pattern:
                        flip_val = (row_i + column_i) % 2 #10101... 01010...
                    else:
                        flip_val = (flip_val+1) % 2
                if flip=='up':
                    if not is_dense_pattern:
                        flip_val = ((row_i + column_i) % 2)*2 #2020.. 0202...
                    else:
                        flip_val = ((flip_val+1) % 2) * 2
                if flip=='left_column': # 一列左右翻一列不翻
                    flip_val = [1, 0][(column_i % 2) == 1]
                if flip=='up_column': # 一列上下翻一列不翻
                    flip_val = [2, 0][(column_i % 2) == 1]
                if flip=='left_row': # 一列左右翻一列不翻
                    flip_val = [1, 0][(row_i % 2) == 1]
                if flip=='up_row': # 一列上下翻一列不翻
                    flip_val = [2, 0][(row_i % 2) == 1]

            flip_save.append(flip_val)

            iter += 1

        self.positions_save = positions_save
        self.pattern_select_save = pattern_select_save
        self.rotate_save = rotate_save
        self.flip_save = flip_save

    def layout_up_up(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         pattern_select='row')

    def layout_up_up_house(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=False,
                         flip = 'left_row',
                         pattern_select='sequential')

    def layout_up_up_flower(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=False,
                         pattern_select='row')

    def layout_up_up_zebra(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         flip='left_row',
                         pattern_select='row')

    def layout_up_down(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         flip='up_column',
                         pattern_select='column')

    def layout_left_right(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=False,
                         flip='left',
                         pattern_select='sequential')

    def layout_left_right_shrimp(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         pattern_select='sequential')

    def layout_inclined_right(self, imgs_len):
        tan_angle = - self.pattern_interval_y / self.pattern_interval_x
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         pattern_select='sequential_inclined_right',
                         rotate=int(math.atan(tan_angle)/math.pi*180))

    def layout_inclined_left(self, imgs_len):
        tan_angle = - self.pattern_interval_y / self.pattern_interval_x
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         pattern_select='sequential_inclined_left',
                         rotate=int(-math.atan(tan_angle)/math.pi*180))

    def layout_random(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         rotate='random', random_shift = False,
                         pattern_select='random')

    def layout_random_up(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         random_shift=14,
                         pattern_select='random')

    def layout_overlap(self, imgs_len):
        self.cal_img_pos(imgs_len=imgs_len,
                         is_dense_pattern=True,
                         pattern_select='sequential')

        dy = int(self.pattern_interval_y * 1.4)
        row_n = (self.h // dy + 2) * 2

        new_pos = []
        for i in range(-1, row_n-1):
            new_pos += [e for e in self.positions_save if e[1] == i*(dy//2) or e[1] == i/2*dy]

        self.positions_save = new_pos



class Layout_svg(Layout):
    def __init__(self,mysvg_list,h,w,pattern_interval_x,pattern_interval_y=None):

        super(Layout_svg,self).__init__(h,w,pattern_interval_x,pattern_interval_y)
        self.mysvg_list = mysvg_list
        self.save_dict = None


    def do_layout(self,savepath, style = None, DIY_params = None, save_params = False, load_params_dict = None):
        imgs_len = len(self.mysvg_list)

        if style:
            if style == 'DIY':
                self.cal_img_pos(imgs_len=imgs_len, **DIY_params)
                # todo DIY_params: {'is_dense_pattern':False,...}

            else:
                super_layout_func = eval('self.layout_'+style)
                super_layout_func(imgs_len=imgs_len)

            if save_params:
                save_dict = {}
                save_dict['positions_saved'] = self.positions_save
                save_dict['pattern_select_saved'] = self.pattern_select_save
                save_dict['rotate_saved'] = self.rotate_save
                save_dict['flip_saved'] = self.flip_save

                self.save_dict = save_dict

                # np.savez('outfile.npz', **save_dict)

        if load_params_dict:
            self.positions_save = load_params_dict['positions_saved']
            self.pattern_select_save = load_params_dict['pattern_select_saved']
            self.rotate_save = load_params_dict['rotate_saved']
            self.flip_save = load_params_dict['flip_saved']

        positions_use = self.positions_save
        pattern_select_use = self.pattern_select_save
        rotate_use = self.rotate_save
        flip_use = self.flip_save

        tiled_svg = []
        for i in range(len(positions_use)):
            curr_svg = deepcopy(self.mysvg_list[pattern_select_use[i]])
            curr_svg = curr_svg.move_center_to(*positions_use[i])
            curr_svg = curr_svg.rotate(rotate_use[i])
            curr_svg = curr_svg.flip(flip_use[i])

            tiled_svg.append(curr_svg)

        Figure(str(self.w), str(self.h), *tiled_svg).save(savepath)

#%%
# lion = Mysvg('./svg_imgs/lion.svg')
# goat = Mysvg('./svg_imgs/goat.svg')
# pig = Mysvg('./svg_imgs/pig.svg')
# monkey = Mysvg('./svg_imgs/monkey.svg')
# animals = [lion,goat,pig,monkey]

#
# flower = Mysvg('./tiles/flower.svg')
# flower.resize(0.25)
#
# flower1 = Mysvg('./tiles/flower1.svg')
# flower1.resize(float(1/7))
# flower2 = Mysvg('./tiles/flower2.svg')
# flower2.resize(float(1/7))
# flower3 = Mysvg('./tiles/flower3.svg')
# flower3.resize(float(1/7))
# flower4 = Mysvg('./tiles/flower4.svg')
# flower4.resize(float(1/7))

# flo1 = Mysvg('./tiles/flo1.svg')
# flo1.resize(float(1/30))
# flo2 = Mysvg('./tiles/flo2.svg')
# flo2.resize(float(1/30))
# flo4 = Mysvg('./tiles/flo4.svg')
# flo4.resize(float(1/30))
# flo6 = Mysvg('./tiles/flo6.svg')
# flo6.resize(float(1/30))

# zebra = Mysvg('./tiles/zebra.svg')
# zebra.resize(float(1/20))
#
# fish1 = Mysvg('./tiles/fish1.svg').scale(-1,1)
# fish1.resize(float(1/4))
# fish2 = Mysvg('./tiles/fish2.svg').scale(-1,1)
# fish2.resize(float(1/8))
# fish3 = Mysvg('./tiles/fish3.svg').scale(-1,1)
# fish3.resize(float(1/8))

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=120, pattern_interval_y=75, mysvg_list=[flower])
# layout_svg.do_layout(style='up_up', savepath='./svg_layout/up_up.svg')

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=150, pattern_interval_y=150, mysvg_list=[goat.resize(0.7),pig.resize(0.7),monkey.resize(0.7)])
# layout_svg.do_layout(style='up_up_house', savepath='./svg_layout/up_up_house.svg')

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=100, pattern_interval_y=150, mysvg_list=[flower1,flower2,flower3,flower4])
# layout_svg.do_layout(style='up_up_flower', savepath='./svg_layout/up_up_flower.svg')

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=150, pattern_interval_y=150, mysvg_list=[zebra])
# layout_svg.do_layout(style='up_up_zebra', savepath='./svg_layout/up_up_zebra.svg')

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=120, pattern_interval_y=74, mysvg_list=[flower])
# layout_svg.do_layout(style='up_down', savepath='./svg_layout/up_down.svg')

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=200, pattern_interval_y=150, mysvg_list=[zebra])
# layout_svg.do_layout(style='left_right', savepath='./svg_layout/left_right2.svg')

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=150, pattern_interval_y=150, mysvg_list=[zebra])
# layout_svg.do_layout(style='left_right_shrimp', savepath='./svg_layout/left_right_shrimp.svg')

# layout_svg = Layout_svg(h=600, w=1000, pattern_interval_x=130, pattern_interval_y=130, mysvg_list=[fish1,fish2,fish3])
# layout_svg.do_layout(style='inclined_left', savepath='./svg_layout/inclined3.svg')




#%% 细调间距
# layout_svg = Layout_svg(h=1500, w=1000, pattern_interval_x=280, pattern_interval_y=280, mysvg_list=animals)
# layout_svg.do_layout(style='random', savepath='./ui/random_test.svg',save_params=True)
#
# npzfile = np.load('outfile.npz')
# new_npzfile = dict(npzfile).copy()
#
# layout_svg_load = Layout_svg(h=1500, w=1000, pattern_interval_x=280, pattern_interval_y=280, mysvg_list=animals)
# layout_svg_load.do_layout(savepath='./svg_layout/random6_load.svg',load_params_dict=npzfile)
#
# new_npzfile['pattern_select_saved'][6] = 1
# new_npzfile['rotate_saved'][6] = -20
#
# new_npzfile['pattern_select_saved'][9] = 0
# new_npzfile['rotate_saved'][9] = 0
#
# new_npzfile['pattern_select_saved'][14] = 0
# new_npzfile['rotate_saved'][14] = 70
#
#
# layout_svg_load = Layout_svg(h=1500, w=1000, pattern_interval_x=280, pattern_interval_y=280, mysvg_list=animals)
# layout_svg_load.do_layout(savepath='./svg_layout/random6_load_2.svg',load_params_dict=new_npzfile)


