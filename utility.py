#%%
import re
import cv2
import numpy as np
from matplotlib import pyplot as plt

# given a svg image, return all colors
def find_all_color(*svg_path_list):
    color_set_all = set([])
    for svg_path in svg_path_list:
        svg_content = open(svg_path, encoding='latin1').read()
        find_color = re.compile(r'#[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]')
        res = find_color.findall(svg_content)
        tmp_color_set = set(res)
        color_set = set([i.upper() for i in tmp_color_set])
        color_set_all = color_set_all.union(color_set)
    return list(color_set_all)

# given a set of colors and number of clusters, use kmeans to reduce
def reduce_color(colors, num):
    tmp = list(colors)[0]
    if isinstance(tmp, str):
        colors = [(int(i[1:3], base=16), int(i[3:5], base=16), int(i[5:7], base=16)) for i in colors]
    colors = np.array(colors).reshape((-1,3))
    colors = np.float32(colors)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = num
    ret, label, center = cv2.kmeans(colors, K, None, criteria, 10, cv2.KMEANS_PP_CENTERS )
    label = list(label.flatten())
    if isinstance(tmp, str):
        center_ret = ["#%02X%02X%02X" % (int(round(i[0])), int(round(i[1])), int(round(i[2]))) for i in center]
    else:
        center_ret = [(int(round(i[0])),int(round(i[1])),int(round(i[2]))) for i in center]
    return label, center_ret

# execute color reduction on a svg image
def replace_color(svg_path,initial_colors,label,center,save_path):
    svg_content = open(svg_path, encoding='latin1').read()

    for i in range(len(initial_colors)):
        initial_color = initial_colors[i]
        new_color = center[label[i]]
        svg_content = re.sub(initial_color, new_color, svg_content)
        svg_content = re.sub(initial_color.lower(), new_color, svg_content)

    new_f = open(save_path,'w')
    new_f.write(svg_content)
    new_f.close()



# svg_path = '/Users/xiangyichen/PycharmProjects/crawler/ai/ui/new_dog.svg'
# all_colors = list(find_all_color(svg_path))
# label,center = reduce_color(all_colors,5)
# replace_color(svg_path,all_colors,label,center,'/Users/xiangyichen/PycharmProjects/crawler/ai/ui/new_dog_reduced.svg')



#%%
index_dict = {0:'R',1:'G',2:'B'}
# zone_border = {(255,0,0):('R',2),(255,255,0):('G',1),(0,255,0):('G',2),
#                (0,255,255):('B',1),(0,0,255):('B',2),(255,0,255):('R',1)}

zone_border1 = {'G':('G',2),'R':('R',2),'B':('B',2)}
zone_border2 = {'RG':('G',1),'RB':('R',1),'GB':('B',1)}
zone_angles = {'R1':300,'R2':0,'G1':60,'G2':120,'B1':180,'B2':240}

class Color:
    def __init__(self,R,G,B):
        self.R = R
        self.G = G
        self.B = B

        # lightness normalization / cast max color to 255
        self.lightness = max(R,G,B) / 255
        self.R_l = R / self.lightness
        self.G_l = G / self.lightness
        self.B_l = B / self.lightness

        list_RGB_l = [self.R_l,self.G_l,self.B_l]
        sorted_RGB_l = sorted(list_RGB_l)

        # brightness normalization / cast min color to 0
        min_color_val = sorted_RGB_l[0]
        self.brightness = min_color_val / 255


        # find 1st and 2nd max colors
        max1_color_i = list_RGB_l.index(sorted_RGB_l[-1])
        if sorted_RGB_l[-1] == sorted_RGB_l[-2]:
            max2_color_i = list_RGB_l.index(sorted_RGB_l[-2],max1_color_i+1)
        else:
            max2_color_i = list_RGB_l.index(sorted_RGB_l[-2])

        self.max1_color = index_dict[max1_color_i]
        self.max2_color = index_dict[max2_color_i]

        # group into zone according to 1st and 2nd max colors
        # and compute normalized 2nd max color value
        max2_color_val = list_RGB_l[max2_color_i]

        if max2_color_val == 255:
            self.max2_color_normalized = 255
            (self.zone1, self.zone2) = zone_border2[self.max1_color + self.max2_color]

        elif max2_color_val == 0:
            self.max2_color_normalized = 0
            (self.zone1, self.zone2) = zone_border1[self.max1_color]

        else:
            self.max2_color_normalized = max2_color_val - (255 - max2_color_val) * self.brightness / (1 - self.brightness)
            self.zone1 = self.max1_color
            self.zone2 = [1, 2][max2_color_i - max1_color_i == 1 or max2_color_i - max1_color_i == -2]


        # compute color angle according to normalized 2nd max color value
        zone_angle = zone_angles[self.zone1+str(self.zone2)]

        if self.zone2 == 1:
            relative_angle = 60 * (255 - self.max2_color_normalized) / 255
        if self.zone2 == 2:
            relative_angle = 60 * (self.max2_color_normalized) / 255

        self.angle = zone_angle + relative_angle

    def __sub__(self, other):
        d_angle = self.angle - other.angle
        d_lightness = self.lightness - other.lightness
        d_brightness = self.brightness - other.brightness
        return (d_angle,d_lightness,d_brightness)

    def change_color(self,a=0,l=0,b=0): # angle, lightness, brightness

        # rotate
        balanced_a = self.balance_rotate(a)
        self.angle = (self.angle+balanced_a) % 360
        relative_angle = self.angle % 60
        zone_angle = int((self.angle // 60) * 60)
        zone_str = list(zone_angles.keys())[list(zone_angles.values()).index(zone_angle)]
        self.zone1 = zone_str[0]
        self.zone2 = int(zone_str[1])

        self.max1_color = self.zone1

        if self.zone2 == 1:
            self.max2_color = ['R','G','B'][(['R','G','B'].index(self.max1_color) - 1) % 3]
            self.max2_color_normalized = 255 - relative_angle * 255 / 60
        if self.zone2 == 2:
            self.max2_color = ['R','G','B'][(['R','G','B'].index(self.max1_color) + 1) % 3]
            self.max2_color_normalized = relative_angle * 255 / 60

        # brightness
        self.brightness += b
        min_color_val = 255 * self.brightness
        max2_color_val = self.max2_color_normalized * (1 - self.brightness) + 255 * self.brightness

        min_color = list({'R','G','B'}-{self.max1_color,self.max2_color})[0]
        self.__setattr__(min_color+'_l', min_color_val)
        self.__setattr__(self.max1_color + '_l', 255)
        self.__setattr__(self.max2_color + '_l', max2_color_val)

        # lightness
        self.lightness += l
        self.R = self.R_l * self.lightness
        self.G = self.G_l * self.lightness
        self.B = self.B_l * self.lightness

    # since red (warm color) occupies only ONE-THIRD of color map (whilst cold colors i.e. blue and green occupy TWO-THIRDS)
    # balanced_rotate doubles the warm color area / makes 1 degree of rotation in warm area equal to 2 degrees in cold area

    def balance_rotate(self,a):
        angle_n = self.angle
        if angle_n > 180:
            angle_n = angle_n - 360
        if a > 180:
            a = a - 360
        start = angle_n
        end = angle_n + a
        if end > 180:
            end = end - 360
        R_border1 = -45
        R_border2 = 75

        def in_R(x):
            res = (x>=R_border1 and x<=R_border2)
            return res

        if in_R(start) and in_R(end):
            return a/2

        if (not in_R(start)) and (not in_R(end)):
            if a>=120:
                return a - (R_border2 - R_border1) / 2
            if a<-120:
                return a + (R_border2 - R_border1) / 2
            else:
                return a

        if in_R(start) and (not in_R(end)):
            offset = [-(R_border2-start)/2, (start-R_border1)/2][a<0]
            return a + offset

        if in_R(end) and (not in_R(start)):
            offset = [-(end-R_border1)/2, (R_border2-end)/2][a>=0]
            return a + offset



    def change_color_as(self,color1,color2): # change self color the same way color1 changes to color2
        (d_angle,d_lightness,d_brightness) = color2 - color1
        self.change_color(a=d_angle,l=d_lightness,b=d_brightness)

    def show(self):
        h = 100
        w = 100
        tmp = np.zeros((h, w, 3), dtype=np.uint8)
        tmp[:, :, 0] = np.ones((h, w), dtype=np.uint8) * self.R
        tmp[:, :, 1] = np.ones((h, w), dtype=np.uint8) * self.G
        tmp[:, :, 2] = np.ones((h, w), dtype=np.uint8) * self.B
        fig, ax = plt.subplots(figsize=[10, 10])
        ax.imshow(tmp, cmap='gray', interpolation='bicubic')
        plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
        plt.show()


def change_color(color_RGB,a=180,b=0,l=0):
    if color_RGB in [(0,0,0),(255,255,255),'#000000','#FFFFFF','#ffffff']:
        return color_RGB
    # cast angel to [-180,180]
    a = a % 360
    if a>180:
        a = a-360

    tmp_bool = False
    if isinstance(color_RGB,str):
        tmp_bool = True
        color_RGB = (int(color_RGB[1:3], base=16), int(color_RGB[3:5], base=16), int(color_RGB[5:7], base=16))
    color = Color(color_RGB[0],color_RGB[1],color_RGB[2])

    b_max = 1 - color.brightness;   b_min = -color.brightness
    l_max = 1 - color.lightness;    l_min = -color.lightness

    if not (b<=b_max and b>=b_min and l<=l_max and l>=l_min):
        print('Wrong usage. b must be in range: [%d, %d]; l must be in range: [%d, %d]' %(b_min, b_max, l_min, l_max))
        return
    color.change_color(a,l,b)
    if tmp_bool:
        return "#%02X%02X%02X" % (int(color.R), int(color.G), int(color.B))

    return (int(color.R),int(color.G),int(color.B))

# res = change_color('#FF0000', a=144, l=-0.9, b=0.5)
# print(res)

#%%
# r = Color(255,0,0)
# res = r.balance_rotate(-170,50)
# print(res)

