import tkinter as tk
import tkinter.messagebox as tk_mb
from tkinter import ttk
from tkinter import filedialog
from tkinter.colorchooser import askcolor
from PIL import ImageTk,Image
import os
import sys

import mysvg
import utility
import ai2svg_my as ai2svg


IS_CAIRO = True
LARGEFONT = ("Verdana", 20)
try:
    BASE_DIR = sys._MEIPASS
except:
    BASE_DIR = os.path.dirname(__file__)


def svg2png(svg_path,dpi=None,w=None,h=None):
    if IS_CAIRO:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=svg_path.replace('svg', 'png'), dpi=dpi)
    else:
        utility.my_svg2png(svg_path, svg_path.replace('svg', 'png'), w, h, BASE_DIR)



class tkinterApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('600x430+10+10')

        self.container = ttk.Frame(self)

        # create canvas and a scrollable frame inside to adopt a scroll bar
        canvas = tk.Canvas(self.container)
        scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set,borderwidth=0)

        self.container.pack(side="top", fill="both", expand=True)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.init_params()

        # self.frames = {}
        #
        # for F in (SelectPattern, SelectPatternUp, SelectPatternInclined, SelectPatternRandom, SetParams, AddTiles):
        #     frame = F(self.scrollable_frame, self)
        #     self.frames[F] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SelectPattern)

    # to display the current frame passed as parameter
    def show_frame(self, cont):
        frame = cont(self.scrollable_frame, self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
        # frame = self.frames[cont]
        # frame.tkraise()

    def show_frame2(self, cont):
        frame = cont(self.scrollable_frame, self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def init_params(self):
        self.pattern_select1 = tk.StringVar()
        self.pattern_select2 = tk.StringVar()
        self.canvas_h = None
        self.canvas_w = None
        self.tile_h = None
        self.tile_w = None
        self.pattern_interval_x = None
        self.pattern_interval_y = None
        self.bg_color = None
        self.save_path = None
        self.save_name = None
        self.save_file_svg = None
        self.save_file_svg_tmp = None
        self.tile_paths = []
        self.tiles = []
        self.dpi = tk.StringVar()
        self.is_dense_pattern = None
        self.column_n = None
        self.param_dict = None
        self.all_colors = None
        self.reduced_colors = None
        self.color_labels = None
        self.changed_colors = None
        self.edited_colors = None
        self.color_edited = False




class SelectPattern(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.controller.geometry('600x360+10+10')

        label = ttk.Label(self, text="请选择排版样式", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='W')

        self.image_file1 = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, "./ui_imgs/up_up.png")))
        canvas1 = tk.Canvas(self,width=150,height=150)
        canvas1.create_image(0,0,anchor='nw',image=self.image_file1)
        canvas1.grid(row=1, column=0, padx=16, pady=24)
        rb1 = ttk.Radiobutton(self,text='垂直排列',value='up_up',variable=controller.pattern_select1)
        rb1.grid(row=2, column=0, padx=16, pady=5, sticky='N')

        self.image_file2 = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, "./ui_imgs/inclined.png")))
        canvas2 = tk.Canvas(self, width=150, height=150)
        canvas2.create_image(0,0,anchor='nw', image=self.image_file2)
        canvas2.grid(row=1, column=1, padx=16, pady=24)
        rb2 = ttk.Radiobutton(self, text='倾斜排列', value='inclined', variable=controller.pattern_select1)
        rb2.grid(row=2, column=1, padx=16, pady=5, sticky='N')

        self.image_file3 = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, "./ui_imgs/random.png")))
        canvas3 = tk.Canvas(self, width=150, height=150)
        canvas3.create_image(0,0,anchor='nw', image=self.image_file3)
        canvas3.grid(row=1, column=2, padx=16, pady=24)
        rb3 = ttk.Radiobutton(self, text='随机排列', value='random', variable=controller.pattern_select1)
        rb3.grid(row=2, column=2, padx=16, pady=5, sticky='N')

        if self.controller.pattern_select1.get():
            self.controller.pattern_select1.set(self.controller.pattern_select1.get())

        button1 = ttk.Button(self, text="下一步", command=self.next_step)
        button1.grid(row=3, column=2, padx=10, pady=20, sticky='E')


    def next_step(self):
        selected_pattern1 = self.controller.pattern_select1.get()
        # print(selected_pattern1)
        if not selected_pattern1:
            tk_mb.showwarning(message='请选择花型')
        if selected_pattern1 == 'up_up':
            self.controller.show_frame(SelectPatternUp)
        if selected_pattern1 == 'inclined':
            self.controller.show_frame(SelectPatternInclined)
        if selected_pattern1 == 'random':
            self.controller.show_frame(SelectPatternRandom)

# abstract class, heritated by subclasses 垂直，斜，随机
class SelectPattern2(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.patterns = [] # sub-categories in each category
        self.rb_texts = []
        self.rb_vals = []


    def set_layout(self, title):
        ttk.Label(self, text=title, font=LARGEFONT).grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='W')

        for i in range(len(self.patterns)):
            row = i // 3 * 2 + 1
            col = i % 3
            tmp = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, './ui_imgs/' + self.patterns[i])))
            self.__setattr__('image_file'+str(i),tmp)
            locals()['canvas'+str(i)] = tk.Canvas(self,width=150,height=150)
            locals()['canvas'+str(i)].create_image(0,0,anchor='nw',image=self.__getattribute__('image_file'+str(i)))
            locals()['canvas'+str(i)].grid(row=row, column=col, padx=16, pady=5)

            ttk.Radiobutton(self, text=self.rb_texts[i], value=self.rb_vals[i], variable=self.controller.pattern_select2)\
                        .grid(row=row + 1, column=col, padx=16, pady=5, sticky='N')

        if self.controller.pattern_select2.get():
            self.controller.pattern_select2.set(self.controller.pattern_select2.get())

        button1 = ttk.Button(self, text="上一步",
                             command=lambda: self.controller.show_frame(SelectPattern))
        button1.grid(row=row + 2, column=1, padx=10, pady=10, sticky='E')

        button2 = ttk.Button(self, text="下一步", command=self.next_step)
        button2.grid(row=row + 2, column=2, padx=10, pady=10, sticky='W')

    def next_step(self):
        selected_pattern2 = self.controller.pattern_select2.get()
        if not selected_pattern2:
            tk_mb.showwarning(message='请选择花型')
        else:
            self.controller.show_frame(SetParams)

    def prev_step(self):
        self.controller.show_frame(SelectPattern)


class SelectPatternUp(SelectPattern2):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller.geometry('600x740+10+10')
        self.rb_texts = ['错位', '上下', '同排同图', '同排镜像', '同排错位', '同排同方向', '同排对称']
        self.rb_vals = ['up_up', 'up_down', 'up_up_flower', 'up_up_house','up_up_zebra', 'left_right_shrimp', 'left_right']
        self.patterns = [i + '.png' for i in self.rb_vals]
        super().set_layout('请选择垂直排列样式')

class SelectPatternInclined(SelectPattern2):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.rb_texts = ['向右倾斜', '向左倾斜']
        self.rb_vals = ['inclined_right', 'inclined_left']
        self.patterns = [i + '.png' for i in self.rb_vals]
        super().set_layout('请选择斜排样式')

class SelectPatternRandom(SelectPattern2):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.rb_texts = ['随机旋转', '随机垂直']
        self.rb_vals = ['random','random_up']
        self.patterns = [i + '.png' for i in self.rb_vals]
        super().set_layout('请选择随机排列样式')



class SetParams(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.controller.geometry('600x500+10+10')

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=3)
        self.columnconfigure(4, weight=3)

        label = ttk.Label(self, text="请设置花型参数", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='W')

        canvas_w_label = ttk.Label(self, text='画布尺寸 (px)')
        canvas_w_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.canvas_w_entry = ttk.Entry(self,width=10)
        self.canvas_w_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        self.canvas_w_entry.insert(0,'300')
        if self.controller.canvas_w:
            self.canvas_w_entry.delete(0, 'end')
            self.canvas_w_entry.insert(0, self.controller.canvas_w)

        canvas_h_label = ttk.Label(self, text='×')
        canvas_h_label.grid(row=1, column=2, sticky=tk.W, pady=10)
        self.canvas_h_entry = ttk.Entry(self,width=10)
        self.canvas_h_entry.grid(row=1, column=2, sticky=tk.E, padx=20, pady=10)
        self.canvas_h_entry.insert(0,'300')
        if self.controller.canvas_h:
            self.canvas_h_entry.delete(0, 'end')
            self.canvas_h_entry.insert(0, self.controller.canvas_h)

        tile_w_label = ttk.Label(self, text='图案尺寸 (px)')
        tile_w_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.tile_w_entry = ttk.Entry(self,width=10)
        self.tile_w_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        self.tile_w_entry.insert(0,'40')
        if self.controller.tile_w:
            self.tile_w_entry.delete(0, 'end')
            self.tile_w_entry.insert(0, self.controller.tile_w)

        # tile_h_label = ttk.Label(self, text='×')
        # tile_h_label.grid(row=2, column=2, sticky=tk.W, pady=10)
        # self.tile_h_entry = ttk.Entry(self,width=10)
        # self.tile_h_entry.grid(row=2, column=3, sticky=tk.W, padx=10, pady=10)

        interval_x_label = ttk.Label(self, text='图案左右间距 (px)')
        interval_x_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self.interval_x_entry = ttk.Entry(self, width=10)
        self.interval_x_entry.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        self.interval_x_entry.insert(0,'100')
        if self.controller.pattern_interval_x:
            self.interval_x_entry.delete(0, 'end')
            self.interval_x_entry.insert(0, self.controller.pattern_interval_x)

        interval_y_label = ttk.Label(self, text='图案上下间距 (px)')
        interval_y_label.grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)
        self.interval_y_entry = ttk.Entry(self, width=10)
        self.interval_y_entry.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)
        self.interval_y_entry.insert(0,'100')
        if self.controller.pattern_interval_y:
            self.interval_y_entry.delete(0, 'end')
            self.interval_y_entry.insert(0, self.controller.pattern_interval_y)

        bg_label = ttk.Label(self, text='是否有背景色')
        bg_label.grid(row=5, column=0, sticky=tk.W, padx=10, pady=10)
        bg_color_button = ttk.Button(self, text='选择颜色', width=7, command=self.choose_bg_color)
        has_bg = tk.StringVar()
        def show_color_picker():
            if has_bg.get() == 'yes':
                bg_color_button.grid(row=5, column=2, sticky=tk.W, padx=10)
            else:
                self.controller.bg_color = None
                bg_color_button.grid_forget()
        rb4 = ttk.Radiobutton(self, text='否', value='no', variable=has_bg, width=3, command=show_color_picker)
        rb5 = ttk.Radiobutton(self, text='是', value='yes', variable=has_bg, width=3, command=show_color_picker)
        rb4.grid(row=5, column=1, sticky=tk.W, padx=10, pady=10)
        rb5.grid(row=5, column=1, sticky=tk.E, padx=10, pady=10)
        has_bg.set('no')


        save_path_label = ttk.Label(self, text='花型存储地址')
        save_path_label.grid(row=6, column=0, sticky=tk.W, padx=10, pady=10)
        self.save_path_entry = ttk.Entry(self,width=30)
        self.save_path_entry.grid(row=6, column=1, columnspan=3, sticky=tk.W, padx=10, pady=10)
        save_path_button = ttk.Button(self, text='选择', width=4, command=self.choose_save_path)
        save_path_button.grid(row=6, column=3, sticky=tk.W, padx=10)
        # self.save_path_entry.insert(0,'/Users/xiangyichen/PycharmProjects/Pattern_Design/output') # to delete
        if self.controller.save_path:
            self.save_path_entry.delete(0, 'end')
            self.save_path_entry.insert(0, self.controller.save_path)

        save_name_label = ttk.Label(self, text='花型存储名称')
        save_name_label.grid(row=7, column=0, sticky=tk.W, padx=10, pady=10)
        self.save_name_entry = ttk.Entry(self, width=30)
        self.save_name_entry.grid(row=7, column=1, columnspan=3, sticky=tk.W, padx=10, pady=10)
        # self.save_name_entry.insert(0,'test2') # to delete
        if self.controller.save_name:
            self.save_name_entry.delete(0, 'end')
            self.save_name_entry.insert(0, self.controller.save_name)


        dpi_label = ttk.Label(self, text='PNG保存分辨率')
        dpi_label.grid(row=8, column=0, sticky=tk.W, padx=10, pady=10)
        rb1 = ttk.Radiobutton(self, text='150', value=150, variable=self.controller.dpi,width=3)
        rb2 = ttk.Radiobutton(self, text='300', value=300, variable=self.controller.dpi,width=3)
        rb3 = ttk.Radiobutton(self, text='600', value=600, variable=self.controller.dpi,width=3)
        self.controller.dpi.set('150')
        rb1.grid(row=8, column=1, sticky=tk.W, padx=10, pady=10)
        rb2.grid(row=8, column=1, sticky=tk.E, padx=10, pady=10)
        rb3.grid(row=8, column=2, sticky=tk.W, padx=10, pady=10)


        button1 = ttk.Button(self, text="上一步",command=self.prev_step)
        button1.grid(row=9, column=1, columnspan=2, padx=10, pady=10, sticky='E')

        button2 = ttk.Button(self, text="下一步",command=self.next_step)
        button2.grid(row=9, column=3, padx=10, pady=10, sticky='W')

    def prev_step(self):
        selected_pattern1 = self.controller.pattern_select1.get()
        if selected_pattern1 == 'up_up':
            self.controller.show_frame(SelectPatternUp)
        if selected_pattern1 == 'inclined':
            self.controller.show_frame(SelectPatternInclined)
        if selected_pattern1 == 'random':
            self.controller.show_frame(SelectPatternRandom)

    def next_step(self):
        if (not self.canvas_h_entry.get()) or (not self.canvas_w_entry.get()) or (not self.controller.dpi.get())\
                or (not self.tile_w_entry.get()) or (not self.interval_x_entry.get()) \
                or (not self.interval_y_entry.get()) or (not self.save_path_entry.get()):
            tk_mb.showwarning(message='请填写全部参数')
        else:
            self.controller.canvas_h = int(self.canvas_h_entry.get())
            self.controller.canvas_w = int(self.canvas_w_entry.get())
            # self.controller.tile_h = int(self.tile_h_entry.get())
            self.controller.tile_w = int(self.tile_w_entry.get())
            self.controller.pattern_interval_x = int(self.interval_x_entry.get())
            self.controller.pattern_interval_y = int(self.interval_y_entry.get())
            self.controller.save_path = self.save_path_entry.get()
            self.controller.save_name = self.save_name_entry.get()

            self.controller.show_frame(AddTiles)

    def choose_save_path(self):
        chosen_path = filedialog.askdirectory(title="选择保存花型路径")
        self.save_path_entry.delete(0, 'end')
        self.save_path_entry.insert(tk.END,str(chosen_path))

    def choose_bg_color(self):
        colors = askcolor(title="请选择颜色")
        chosen_color = colors[1].upper()
        self.controller.bg_color = chosen_color


# third window frame page2
class AddTiles(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.controller.geometry('600x400+10+10')

        self.added_tile_rows = 0 # number of rows shown on window

        label = ttk.Label(self, text="请添加元素", font=LARGEFONT, width=30)
        label.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='W')

        self.add_tile_button = ttk.Button(self, text='添加一行', width=8, command=self.add_add_tile_row)

        self.button1 = ttk.Button(self, text="上一步",
                             command=lambda: controller.show_frame(SetParams))
        self.button2 = ttk.Button(self, text="生成花型",command=self.next_step)

        if len(self.controller.tile_paths)>0:
            for tile_path in self.controller.tile_paths:
                self.add_add_tile_row(tile_path)
        else:
            self.add_add_tile_row()

    def del_row(self,row_i):
        def del_row_i():
            if row_i < self.added_tile_rows:
                for i in range(row_i+1, self.added_tile_rows + 1):
                    next_row_val = self.__getattribute__('tiled_entry'+str(i)).get()
                    self.__getattribute__('tiled_entry' + str(i-1)).delete(0, 'end')
                    self.__getattribute__('tiled_entry' + str(i-1)).insert(tk.END, next_row_val)

            self.__getattribute__('tiled_label' + str(self.added_tile_rows)).destroy()
            self.__getattribute__('tiled_entry' + str(self.added_tile_rows)).destroy()
            self.__getattribute__('del_btn' + str(self.added_tile_rows)).destroy()
            self.__getattribute__('sel_btn' + str(self.added_tile_rows)).destroy()

            self.added_tile_rows -= 1

        return del_row_i

    def sel_pattern(self,row_i):
        def sel_pattern_i():
            while 1:
                chosen_path = filedialog.askopenfilename(title="选择元素") #,filetypes=[("Svg file","*.svg"),("AI file", "*.ai")])
                if chosen_path.split('.')[-1] == 'ai':
                    answer = tk_mb.askyesno(title='.ai格式转换要求', message='请确保选择的ai格式文件符合以下的要求（确认后开始自动开始svg转化）：'
                                                                       '\n 1. 保存时未勾选压缩 '
                                                                       '\n 2. 仅有色块（无边框）'
                                                                       '\n 3. 未使用渐变色'
                                                                       '\n 4. 单个花型尺寸尽量保持在200px之内')
                    if answer:
                        ret = ai2svg.ai2svg(chosen_path, chosen_path.replace('.ai', '.svg'))
                        if ret==1: # format transform success
                            chosen_path = chosen_path.replace('.ai', '.svg')
                        elif ret==-1:
                            tk_mb.showwarning(message='.ai保存时压缩了，格式转换失败，请重试！')
                            continue
                        else:
                            tk_mb.showwarning(message='格式转换失败，请选择其他.ai格式文件！')

                        break
                    if not answer:
                        continue
                else:
                    break
            self.__getattribute__('tiled_entry' + str(row_i)).delete(0, 'end')
            self.__getattribute__('tiled_entry' + str(row_i)).insert(tk.END, str(chosen_path))

        return sel_pattern_i



    def add_add_tile_row(self, selected_path = None):
        self.added_tile_rows += 1

        self.__setattr__('tiled_label' + str(self.added_tile_rows), ttk.Label(self, text='元素' + str(self.added_tile_rows)))
        self.__getattribute__('tiled_label' + str(self.added_tile_rows)).grid(row=self.added_tile_rows, column=0, sticky=tk.W, padx=10, pady=10)
        self.__setattr__('tiled_entry' + str(self.added_tile_rows), ttk.Entry(self, width=25))
        if selected_path:
            self.__getattribute__('tiled_entry' + str(self.added_tile_rows)).insert(0,selected_path)
        self.__getattribute__('tiled_entry' + str(self.added_tile_rows)).grid(row=self.added_tile_rows, column=1, sticky=tk.W, padx=10, pady=10)
        self.__setattr__('sel_btn' + str(self.added_tile_rows), ttk.Button(self, text='选择', width=5, command=self.sel_pattern(self.added_tile_rows)))
        self.__getattribute__('sel_btn' + str(self.added_tile_rows)).grid(row=self.added_tile_rows, column=2, sticky=tk.W, padx=1, pady=10)
        self.__setattr__('del_btn' + str(self.added_tile_rows), ttk.Button(self, text='删除', width=5, command=self.del_row(self.added_tile_rows)))
        self.__getattribute__('del_btn' + str(self.added_tile_rows)).grid(row=self.added_tile_rows, column=3, sticky=tk.W, padx=1, pady=10)

        self.add_tile_button.grid(row=self.added_tile_rows + 1, column=1, sticky=tk.W, padx=10)
        self.button1.grid(row=self.added_tile_rows + 2, column=1, columnspan=2, padx=10, pady=10, sticky='E')
        self.button2.grid(row=self.added_tile_rows + 2, column=3, padx=10, pady=10, sticky='W')

    def next_step(self):
        for i in range(1, self.added_tile_rows + 1):
            tile_path = self.__getattribute__('tiled_entry'+str(i)).get()
            if tile_path and (tile_path not in self.controller.tile_paths):
                self.controller.tile_paths.append(tile_path)
            # print(self.controller.tile_paths)

        my_tiles = []
        for tile_path in self.controller.tile_paths:
            my_tile = mysvg.Mysvg(tile_path)
            resize = self.controller.tile_w / my_tile.width
            self.controller.tile_h = self.controller.tile_w / my_tile.width * my_tile.height
            my_tile.resize(resize)
            my_tiles.append(my_tile)
        self.controller.tiles = my_tiles

        save_file = os.path.join(self.controller.save_path,self.controller.save_name+'.svg')
        self.controller.save_file_svg = save_file


        layout_svg = mysvg.Layout_svg(h=self.controller.canvas_h, w=self.controller.canvas_w, mysvg_list=self.controller.tiles,
                                pattern_interval_x=self.controller.pattern_interval_x, pattern_interval_y=self.controller.pattern_interval_x)
        layout_svg.do_layout(style=self.controller.pattern_select2.get(), savepath=self.controller.save_file_svg, save_params=True,
                             bg_color=self.controller.bg_color)

        self.controller.param_dict = layout_svg.save_dict
        print('花型生成完成，花型参数：', self.controller.param_dict)

        self.controller.is_dense_pattern = layout_svg.is_dense_pattern
        self.controller.column_n = layout_svg.column_n

        svg2png(save_file,dpi=float(self.controller.dpi.get()))

        self.controller.show_frame(PreviewPattern)



class PreviewPattern(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        w = self.controller.canvas_w + 250
        h = self.controller.canvas_h + 500
        self.controller.geometry(str(w)+"x"+str(h)+"+10+10")

        label = ttk.Label(self, text="生成花型预览和微调", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10, columnspan=4, sticky='W')

        button4 = ttk.Button(self, text="重新生成随机花型",command=self.random_again)
        if self.controller.pattern_select1.get() == 'random':
            button4.grid(row=1, column=3, columnspan=2, sticky='E', padx=10, pady=10)

        # test
        # png_path = './ui/test.png'
        # self.controller.canvas_w = 500
        # self.controller.canvas_h = 500
        # self.controller.tile_paths = ['aaaa','bbbb','ccc']


        png_path = self.controller.save_file_svg.replace('svg', 'png')
        self.image_file = ImageTk.PhotoImage(Image.open(png_path))
        self.canvas = tk.Canvas(self, width=self.controller.canvas_w, height=self.controller.canvas_h,bg='white')
        self.canvas.create_image(0,0,anchor='nw',image=self.image_file)
        self.canvas.grid(row=2, column=0, columnspan=8, padx=10, pady=10)

        instruction_label = ttk.Label(self, text='请选择微调图案位置')
        instruction_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)

        tile_i_label = ttk.Label(self, text='第几行')
        tile_i_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=10)
        self.tile_i_entry = ttk.Entry(self, width=4)
        self.tile_i_entry.grid(row=3, column=2, sticky=tk.W, padx=5, pady=10)
        tile_j_label = ttk.Label(self, text='第几列')
        tile_j_label.grid(row=3, column=3, sticky=tk.W, pady=5)
        self.tile_j_entry = ttk.Entry(self, width=4)
        self.tile_j_entry.grid(row=3, column=4, sticky=tk.W, padx=5, pady=10)

        instruction_label2 = ttk.Label(self, text='请选择微调图案参数')
        instruction_label2.grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)


        tile_path_label = ttk.Label(self, text='图案')
        tile_path_label.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)
        self.tile_path_entry = tk.StringVar(self)
        # self.tile_path_entry.set(self.controller.tile_paths[0])
        self.tile_path_entry.set('请选择更改图案')
        tmp = ['请选择更改图案'] + self.controller.tile_paths
        tile_path_options = ttk.OptionMenu(self, self.tile_path_entry, *tmp)
        tile_path_options.config(width=15)
        tile_path_options.grid(row=4, column=2, columnspan=3, sticky=tk.W, padx=10, pady=10)

        translate_x_l_label = ttk.Label(self, text='左移')
        translate_x_l_label.grid(row=5, column=1, sticky=tk.W, padx=5, pady=10)
        self.translate_x_l_entry = ttk.Entry(self, width=4)
        self.translate_x_l_entry.grid(row=5, column=2, sticky=tk.W, padx=5, pady=10)
        self.translate_x_l_entry.insert(0, '0')

        translate_x_r_label = ttk.Label(self, text='右移')
        translate_x_r_label.grid(row=5, column=3, sticky=tk.W, padx=5, pady=10)
        self.translate_x_r_entry = ttk.Entry(self, width=4)
        self.translate_x_r_entry.grid(row=5, column=4, sticky=tk.W, padx=5, pady=10)
        self.translate_x_r_entry.insert(0, '0')

        translate_y_u_label = ttk.Label(self, text='上移')
        translate_y_u_label.grid(row=6, column=1, sticky=tk.W, padx=5, pady=10)
        self.translate_y_u_entry = ttk.Entry(self, width=4)
        self.translate_y_u_entry.grid(row=6, column=2, sticky=tk.W, padx=5, pady=10)
        self.translate_y_u_entry.insert(0, '0')

        translate_y_d_label = ttk.Label(self, text='下移')
        translate_y_d_label.grid(row=6, column=3, sticky=tk.W, padx=5, pady=10)
        self.translate_y_d_entry = ttk.Entry(self, width=4)
        self.translate_y_d_entry.grid(row=6, column=4, sticky=tk.W, padx=5, pady=10)
        self.translate_y_d_entry.insert(0, '0')


        rotate_label = ttk.Label(self, text='旋转')
        rotate_label.grid(row=7, column=1, sticky=tk.W, padx=5, pady=10)
        self.rotate_entry = ttk.Entry(self, width=4)
        self.rotate_entry.grid(row=7, column=2, sticky=tk.W, padx=5, pady=10)
        self.rotate_entry.insert(0,'0')

        flip_label = ttk.Label(self, text='翻折')
        flip_label.grid(row=7, column=3, sticky=tk.W, padx=5, pady=10)
        self.flip_entry = tk.StringVar(self)
        self.flip_entry.set('无')
        tmp2 = ['无','无','上下','左右']
        flip_options = ttk.OptionMenu(self, self.flip_entry, *tmp2)
        flip_options.config(width=4)
        flip_options.grid(row=7, column=4, sticky=tk.W, padx=5, pady=10)


        button3 = ttk.Button(self, text="修改",
                             command=self.finetune)
        button3.grid(row=8, column=0, columnspan=2, sticky='E', padx=10, pady=10)

        button1 = ttk.Button(self, text="上一步",
                             command=self.prev_step)
        button1.grid(row=8, column=2, columnspan=2, sticky='E', padx=10, pady=10)

        button2 = ttk.Button(self, text="下一步",
                             command=self.next_step)
        button2.grid(row=8, column=4, sticky='W', padx=10, pady=10)

    def random_again(self):
        layout_svg = mysvg.Layout_svg(h=self.controller.canvas_h, w=self.controller.canvas_w,
                                      mysvg_list=self.controller.tiles,
                                      pattern_interval_x=self.controller.pattern_interval_x,
                                      pattern_interval_y=self.controller.pattern_interval_x)
        layout_svg.do_layout(style=self.controller.pattern_select2.get(), savepath=self.controller.save_file_svg,
                             save_params=True,
                             bg_color=self.controller.bg_color)

        self.controller.param_dict = layout_svg.save_dict
        print('花型生成完成，花型参数：', self.controller.param_dict)

        self.controller.is_dense_pattern = layout_svg.is_dense_pattern
        self.controller.column_n = layout_svg.column_n

        svg2png(self.controller.save_file_svg, dpi=float(self.controller.dpi.get()))

        self.controller.show_frame(PreviewPattern)



    def finetune(self):

        new_tile_path = self.tile_path_entry.get()
        new_rotate = int(self.rotate_entry.get())
        new_flip_entry = self.flip_entry.get()
        translate_x = int(self.translate_x_r_entry.get()) - int(self.translate_x_l_entry.get())
        translate_y = int(self.translate_y_d_entry.get()) - int(self.translate_y_u_entry.get())

        # if new_tile_path == '请选择更改图案':
        #     tk_mb.showwarning(message='请选择更改图案')
        #     return

        new_dict = self.controller.param_dict.copy()

        i = int(self.tile_i_entry.get())
        j = int(self.tile_j_entry.get())

        length = len(self.controller.param_dict['pattern_select_saved'])

        # 计算选中的图案在列花型的矩阵中排第几个
        if self.controller.is_dense_pattern:
            num_in_row = int(self.controller.column_n / 2)
            if (i-1)%2 == 0:
                selected_index = num_in_row*int((i-1)/2) + j-1
            else:
                selected_index = length/2 + num_in_row*int((i-2)/2) + j-1
        else:
            num_in_row = self.controller.column_n
            selected_index = num_in_row*(i-1) + (j-1)
        selected_index = int(selected_index)

        flip_dict = {'无':0,'左右':1,'上下':2}
        new_flip = flip_dict[new_flip_entry]

        if new_tile_path != '请选择更改图案':
            new_tile_index = self.controller.tile_paths.index(new_tile_path)
            new_dict['pattern_select_saved'][selected_index] = new_tile_index

        old_pos = new_dict['positions_saved'][selected_index]
        new_dict['positions_saved'][selected_index] = (old_pos[0]+translate_x,old_pos[1]+translate_y)

        new_dict['rotate_saved'][selected_index] = (new_dict['rotate_saved'][selected_index]+new_rotate) % 360
        new_dict['flip_saved'][selected_index] = new_flip

        self.controller.param_dict = new_dict

        new_layout_svg = mysvg.Layout_svg(h=self.controller.canvas_h, w=self.controller.canvas_w, mysvg_list=self.controller.tiles,
                                      pattern_interval_x=self.controller.pattern_interval_x,
                                      pattern_interval_y=self.controller.pattern_interval_x)
        new_layout_svg.do_layout(style=self.controller.pattern_select2.get(), savepath=self.controller.save_file_svg, load_params_dict=new_dict)

        svg2png(self.controller.save_file_svg,int(self.controller.dpi.get()))

        self.controller.show_frame(PreviewPattern)

    def prev_step(self):
        self.controller.show_frame(AddTiles)

    def next_step(self):
        answer = tk_mb.askyesno(title='是否进入下一步', message='一旦进入下一步（颜色编辑），不可再返回进行微调，是否进入下一步？')

        if answer:
            self.controller.all_colors = utility.find_all_color(*self.controller.tile_paths)
            self.controller.show_frame(EditColor)




class EditColor(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('600x650+10+10')

        self.reduce_color_time = 0
        self.change_color_time = 0
        self.edit_color_time = 0
        self.controller.edited_colors = self.controller.all_colors.copy()

        label = ttk.Label(self, text="颜色信息和颜色编辑", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='W')

        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, columnspan=5, sticky=tk.W, padx=10, pady=10)

        button = ttk.Button(self, text="跳过颜色编辑", command=lambda : self.controller.show_frame(CollagePattern))
        button.grid(row=3, column=4, padx=10, pady=10, sticky='E')

        self.frame1 = ttk.Frame(notebook)
        self.frame2 = ttk.Frame(notebook)
        self.frame3 = ttk.Frame(notebook)
        self.frame1.pack(fill='both', expand=True)
        self.frame2.pack(fill='both', expand=True)
        self.frame3.pack(fill='both', expand=True)

        color_num = len(self.controller.all_colors)
        ############################################ frame 1 ########################################################

        label_color_num = ttk.Label(self.frame1, text="花型颜色数量：" + str(color_num))
        label_color_num.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky='W')

        for i in range(min(color_num, 100)):
            locals()['label' + str(i)] = tk.Label(self.frame1, text=self.controller.all_colors[i])
            locals()['label' + str(i)].grid(row=1 + i, column=0, padx=10, pady=3)
            locals()['canvas' + str(i)] = tk.Canvas(self.frame1, width=100, height=15, bg=self.controller.all_colors[i])
            locals()['canvas' + str(i)].grid(row=1 + i, column=1, padx=10, pady=3)

        self.i = i

        reduce_color_label = ttk.Label(self.frame1, text='保留颜色数量')
        reduce_color_label.grid(row=i+2, column=0, sticky=tk.W, padx=10, pady=10)
        self.reduce_color_entry = ttk.Entry(self.frame1,width=7)
        self.reduce_color_entry.grid(row=i+2, column=1, sticky=tk.W, padx=10, pady=10)
        button2 = ttk.Button(self.frame1, text="预览减后颜色", command=self.reduce_color_preview)
        button2.grid(row=i+2, column=2, padx=10, pady=10, sticky='W')
        self.button4 = ttk.Button(self.frame1, text="生成减色花型", command=self.replace_color('reduce'))

        notebook.add(self.frame1, text='减少颜色数量')

        ############################################ frame 2 ########################################################

        label_color_num2 = ttk.Label(self.frame2, text="原本颜色：")
        label_color_num2.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky='W')

        for i2 in range(min(color_num, 100)):
            locals()['label2' + str(i2)] = tk.Label(self.frame2, text=self.controller.all_colors[i2])
            locals()['label2' + str(i2)].grid(row=1 + i2, column=0, padx=10, pady=3)
            locals()['canvas2' + str(i2)] = tk.Canvas(self.frame2, width=100, height=15, bg=self.controller.all_colors[i2])
            locals()['canvas2' + str(i2)].grid(row=1 + i2, column=1, padx=10, pady=3)

        change_color_label = ttk.Label(self.frame2, text='变换色系角度')
        change_color_label.grid(row=2+i2, column=0,columnspan=2, sticky=tk.W, padx=10, pady=5)
        self.change_color_entry = ttk.Entry(self.frame2,width=7)
        self.change_color_entry.insert(0,'0')
        self.change_color_entry.grid(row=2+i2, column=1,columnspan=2, sticky=tk.W, padx=10, pady=5)
        change_lightness_label = ttk.Label(self.frame2, text='变换亮度')
        change_lightness_label.grid(row=3 + i2, column=0,columnspan=2, sticky=tk.W, padx=10, pady=5)
        self.change_lightness_entry = ttk.Entry(self.frame2, width=7)
        self.change_lightness_entry.insert(0,'1')
        self.change_lightness_entry.grid(row=3 + i2, column=1,columnspan=2, sticky=tk.W, padx=10, pady=5)
        change_brightness_label = ttk.Label(self.frame2, text='变换明度')
        change_brightness_label.grid(row=4 + i2, column=0,columnspan=2, sticky=tk.W, padx=10, pady=10)
        self.change_brightness_entry = ttk.Entry(self.frame2, width=7)
        self.change_brightness_entry.insert(0,'1')
        self.change_brightness_entry.grid(row=4 + i2, column=1,columnspan=2, sticky=tk.W, padx=10, pady=10)

        button3 = ttk.Button(self.frame2, text="变换色系预览", command=self.change_color_preview)
        button3.grid(row=5+i2, column=1, padx=10, pady=10, sticky='W')
        self.button5 = ttk.Button(self.frame2, text="生成换色花型", command=self.replace_color('change'))

        label_color_change_instruction = ttk.Label(self.frame2, text="变换色系角度：请输入0到360间的整数，表示色盘上旋转角度\n "
                                                                     "变换亮度和变换色度：请输入0.5到2间的小数，越接近1变化越小")
        label_color_change_instruction.grid(row=6+i2, column=0, padx=10, pady=10, columnspan=4, sticky='W')

        notebook.add(self.frame2, text='变换色系')

        ############################################ frame 3 ########################################################

        label_color_num3 = ttk.Label(self.frame3, text="原本颜色：" )
        label_color_num3.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky='W')

        label_changed_colors = ttk.Label(self.frame1, text="调整后颜色：")
        label_changed_colors.grid(row=0, column=2, padx=10, pady=10, columnspan=2, sticky='W')

        for i3 in range(min(color_num, 100)):
            locals()['label3' + str(i3)] = tk.Label(self.frame3, text=self.controller.all_colors[i3])
            locals()['label3' + str(i3)].grid(row=1 + i3, column=0, padx=10, pady=3)
            locals()['canvas3' + str(i3)] = tk.Canvas(self.frame3, width=100, height=15,
                                                      bg=self.controller.all_colors[i3])
            locals()['canvas3' + str(i3)].grid(row=1 + i3, column=1, padx=10, pady=3)

        for i3 in range(min(color_num, 100)):
            self.__setattr__('color_change_label' + str(i3), tk.Label(self.frame3, text=''))

            self.__setattr__('color_change_canvas'+ str(i3),tk.Canvas(self.frame3, width=100, height=15))

            self.__setattr__('color_change_button' + str(i3), ttk.Button(self.frame3, width=7, text='选择颜色', command=self.edit_color_preview(i3)))
            self.__getattribute__(('color_change_button' + str(i3))).grid(row=1 + i3, column=2, columnspan=2, padx=3, pady=3)

        button6 = ttk.Button(self.frame3, text="确认颜色修改并重新生成花型", command=self.replace_color('edit'))
        button6.grid(row=2 + i2, column=1, columnspan=3, padx=10, pady=10, sticky='W')

        notebook.add(self.frame3, text='精准变色')

    # def prev_step(self):
    #     if self.controller.color_edited:
    #         tk_mb.showwarning('您已进行过颜色编辑，不可再返回微调')
    #         return
    #     self.controller.show_frame(PreviewPattern)

    def reduce_color_preview(self):
        if self.controller.reduced_colors:
            try:
                self.__getattribute__('label_reduced_color0')
                for j in range(len(self.controller.reduced_colors)):
                    self.__getattribute__('label_reduced_color' + str(j)).destroy()
                    self.__getattribute__('canvas_reduced_color' + str(j)).destroy()
            except:
                pass

        num = int(self.reduce_color_entry.get())
        if num >= len(self.controller.all_colors):
            tk_mb.showwarning(message='减少后颜色总数必须小于原来颜色总数')
            return
        label, center = utility.reduce_color(self.controller.all_colors,num)

        self.controller.color_labels = label
        self.controller.reduced_colors = center

        label_reduced_colors = ttk.Label(self.frame1, text="减色后颜色：")
        label_reduced_colors.grid(row=0, column=2, padx=10, pady=10, columnspan=2, sticky='W')

        for j in range(len(center)):
            self.__setattr__('label_reduced_color' + str(j), tk.Label(self.frame1, text=self.controller.reduced_colors[j]))
            self.__getattribute__('label_reduced_color' + str(j)).grid(row=1 + j, column=2, padx=10, pady=3)
            self.__setattr__('canvas_reduced_color' + str(j), tk.Canvas(self.frame1, width=100, height=15, bg=self.controller.reduced_colors[j]))
            self.__getattribute__('canvas_reduced_color' + str(j)).grid(row=1 + j, column=3, padx=10, pady=3)

        self.button4.grid(row=2 + self.i, column=3, padx=10, pady=10, sticky='W')


    def change_color_preview(self):

        color_num = len(self.controller.all_colors)
        angle = int(self.change_color_entry.get())
        brightness = float(self.change_brightness_entry.get())
        lightness = float(self.change_lightness_entry.get())

        label_color_num = ttk.Label(self.frame2, text="变换色系后对应颜色：" )
        label_color_num.grid(row=0, column=2, padx=10, pady=10, columnspan=2, sticky='W')

        self.controller.changed_colors = []
        for k in range(min(color_num,100)):
            new_color = utility.change_color(self.controller.all_colors[k], a=angle, l=lightness, b=brightness)
            self.controller.changed_colors.append(new_color)
            locals()['label' + str(k)] = tk.Label(self.frame2, text=new_color)
            locals()['label' + str(k)].grid(row=1 + k, column=2, padx=10, pady=3)
            locals()['canvas' + str(k)] = tk.Canvas(self.frame2, width=100, height=15, bg=new_color)
            locals()['canvas' + str(k)].grid(row=1 + k, column=3, padx=10, pady=3)

        self.button5.grid(row=5 + self.i, column=2, columnspan=2, padx=10, pady=10, sticky='W')

    def edit_color_preview(self, index):
        def edit_this_color():
            colors = askcolor(title="请选择颜色")
            chosen_color = colors[1].upper()

            self.controller.edited_colors[index] = chosen_color

            self.__getattribute__('color_change_button' + str(index)).configure(text='修改颜色')
            self.__getattribute__('color_change_button' + str(index)).grid(row=1 + index, column=4, padx=10, pady=3)

            self.__getattribute__('color_change_label' + str(index)).configure(text=chosen_color)
            self.__getattribute__('color_change_label' + str(index)).grid(row=1 + index, column=2, padx=10, pady=3)

            self.__getattribute__('color_change_canvas' + str(index)).configure(bg=chosen_color)
            self.__getattribute__('color_change_canvas' + str(index)).grid(row=1 + index, column=3, padx=10, pady=3)

        return edit_this_color

    def replace_color(self,method):
        def do_replace_color():
            self.controller.color_edited = method
            self.__setattr__(method+'_color_time', self.__getattribute__(method+'_color_time')+1)
            old_path = self.controller.save_file_svg
            new_path = old_path.replace('.svg', '_'+method + str(self.__getattribute__(method+'_color_time')) + '.svg')

            labels = [i for i in range(len(self.controller.all_colors))]

            if method == 'edit':
                utility.replace_color(old_path, self.controller.all_colors, labels,
                                      self.controller.edited_colors, new_path)
            if method == 'change':
                utility.replace_color(old_path, self.controller.all_colors, labels,
                                  self.controller.changed_colors, new_path)
            if method == 'reduce':
                labels = self.controller.color_labels
                utility.replace_color(old_path, self.controller.all_colors, labels,
                                      self.controller.reduced_colors, new_path)

            self.controller.save_file_svg_tmp = new_path

            svg2png(new_path,dpi=float(self.controller.dpi.get()))

            self.controller.show_frame(PreviewPatternColor)

        return do_replace_color






class PreviewPatternColor(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        w = self.controller.canvas_w + 50
        h = self.controller.canvas_h + 200
        self.controller.geometry(str(w)+"x"+str(h)+"+10+10")

        label = ttk.Label(self, text="改色后花型预览", font=LARGEFONT)

        label.grid(row=0, column=0, padx=10, pady=10, columnspan=4, sticky='W')

        png_path = self.controller.save_file_svg_tmp.replace('svg', 'png')
        self.image_file = ImageTk.PhotoImage(Image.open(png_path))
        self.canvas = tk.Canvas(self, width=self.controller.canvas_w, height=self.controller.canvas_h,bg='white')
        self.canvas.create_image(0,0,anchor='nw',image=self.image_file)
        self.canvas.grid(row=1, column=0, columnspan=8, padx=10, pady=10)

        button1 = ttk.Button(self, text="取消",
                             command = self.cancel)
        button1.grid(row=7, column=2, sticky='E', padx=10, pady=10)
        button2 = ttk.Button(self, text="确定",
                             command=self.confirm)
        button2.grid(row=7, column=3, sticky='W', padx=10, pady=10)

    def cancel(self):
        os.remove(self.controller.save_file_svg_tmp)
        os.remove(self.controller.save_file_svg_tmp.replace('svg','png'))
        self.controller.show_frame(EditColor)


    def confirm(self):
        new_save_file_svg = filedialog.asksaveasfilename(title="选择保存花型路径",defaultextension='.svg')

        if new_save_file_svg:

            os.rename(self.controller.save_file_svg_tmp, new_save_file_svg)
            os.rename(self.controller.save_file_svg_tmp.replace('svg', 'png'), new_save_file_svg.replace('svg', 'png'))

            self.controller.save_file_svg = new_save_file_svg
            self.controller.save_file_svg_tmp = None

            if self.controller.color_edited == 'reduce':
                self.controller.all_colors = self.controller.reduced_colors
                self.controller.reduced_colors = None
                self.controller.color_labels = None
            if self.controller.color_edited == 'change':
                self.controller.all_colors = self.controller.changed_colors
                self.controller.changed_colors = None
            if self.controller.color_edited == 'edit':
                self.controller.all_colors = self.controller.edited_colors
                self.controller.edited_colors = None

            answer = tk_mb.askyesno(message='是否进入下一步（无缝拼接）？\n选择否则返回上一步颜色编辑')
            if answer:
                self.controller.show_frame(CollagePattern)
            else:
                self.controller.show_frame(EditColor)





class CollagePattern(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.controller.geometry('600x300+10+10')

        label = ttk.Label(self, text="无缝拼接花型预览", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='W')

        num_w_label = ttk.Label(self, text='横向重复次数')
        num_w_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.num_w_entry = ttk.Entry(self, width=4)
        self.num_w_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        num_h_label = ttk.Label(self, text='纵向重复次数')
        num_h_label.grid(row=2, column=2, sticky=tk.W, padx=10, pady=10)
        self.num_h_entry = ttk.Entry(self, width=4)
        self.num_h_entry.grid(row=2, column=3, sticky=tk.W, padx=10, pady=10)

        button = ttk.Button(self, text='生成拼接花型', command=self.collage)
        button.grid(row=3, column=0, columnspan=2, sticky='W', padx=10, pady=10)

        button2 = ttk.Button(self, text="上一步", command=lambda: self.controller.show_frame(EditColor))
        button2.grid(row=3, column=3, padx=10, pady=10, sticky='E')

    def collage(self):
        num_w = int(self.num_w_entry.get())
        num_h = int(self.num_h_entry.get())

        dx = int(self.controller.pattern_interval_x * (1 + int(self.controller.is_dense_pattern) * 0.4))
        dy = int(self.controller.pattern_interval_y * (1 + int(self.controller.is_dense_pattern) * 0.4))

        decent_w = int((self.controller.canvas_w // dx + 1) * dx)
        decent_h = int((self.controller.canvas_h // dy + 1) * dy)


        collage = mysvg.Mysvg(self.controller.save_file_svg)
        self.controller.save_file_svg_tmp = self.controller.save_file_svg.replace('.svg','_collage.svg')
        collage.self_collage(decent_w,decent_h,num_w,num_h,self.controller.save_file_svg_tmp)

        svg2png(self.controller.save_file_svg_tmp, dpi=float(self.controller.dpi.get()))

        png_path = self.controller.save_file_svg_tmp.replace('.svg','.png')
        self.image_file = ImageTk.PhotoImage(Image.open(png_path))
        canvas = tk.Canvas(self, width=decent_w * num_w, height=decent_h * num_h, bg='white')
        canvas.create_image(0, 0, anchor='nw', image=self.image_file)
        canvas.grid(row=1, column=0, columnspan=8, padx=10, pady=10)

        w = decent_w * num_w + 50
        h = decent_h * num_h + 250
        self.controller.geometry(str(w)+'x'+str(h)+'+10+10')



# Driver Code
app = tkinterApp()
app.mainloop()
