import selenium
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import time
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sys
# import requests
import os
# import PIL
# from PIL import Image
# import urllib
import cv2
import numpy as np


try:
    BASE_DIR = sys._MEIPASS
except:
    BASE_DIR = os.path.dirname(__file__)

curr_num = 0


def remove_border(img_path, min_size=0):
    image = cv2.imread(img_path)
    binary_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges_y, edges_x = np.where(binary_image > 16)
    bottom = min(edges_y)
    top = max(edges_y)
    height = top - bottom

    left = min(edges_x)
    right = max(edges_x)
    width = right - left

    if width < min_size:
        return False

    pre1_picture = image[bottom:bottom + height, left:left + width]  # 图片截取
    cv2.imwrite(img_path, pre1_picture)
    return True


def download_url_screenshot(driver, url, save_folder, min_size=0):
    driver.set_window_size(2500, 2500)
    unique_img_name = url.split('/')[-1]  # 将图片以最后的数字+后缀命名，方便检查文件是否存在，全都是jpg
    filename = os.path.join(save_folder, unique_img_name)
    filename = filename.replace('.jpg', '.png')
    if os.path.isfile(filename):  # 如果文件已爬取，则不再重复爬取
        print("文件存在：", filename)
        return 1
    try:
        driver.get(url)
        driver.find_element(By.XPATH, "/html/body/img[1]")
    except selenium.common.exceptions.NoSuchElementException:
        url = url.replace('.jpg', '.png')
        driver.get(url)
    except Exception as e:
        print('下载失败：', url, '(失败原因: ', e, ')')
        return -2

    print('下载图片：', url)
    driver.save_screenshot(filename)
    ret = remove_border(filename, min_size)
    if ret:
        return 1
    else:
        print('图片尺寸太小，跳过了')
        os.remove(filename)
        return -1


def scraper(query, num_images, save_folder, min_size):
    global curr_num
    curr_num = 0

    # init chromedriver
    cr_options = ChromeOptions()
    cr_options.headless = True
    cr_options.add_argument('--ignore-certificate-errors')
    cr_options.add_argument('--ignore-ssl-errors')

    # first driver used to download img
    driver_ss = Chrome(options=cr_options, executable_path=os.path.join(BASE_DIR, 'chromedriver'))

    # second driver used to scrape source urls
    # # s = Service(os.path.join(base_dir, 'chromedriver.exe'))
    # # driver = Chrome(options=cr_options, service=s)
    cr_options.add_argument("--start-maximized")
    driver = Chrome(options=cr_options, executable_path=os.path.join(BASE_DIR, 'chromedriver'))


    if not os.path.exists(os.path.join(save_folder, query)):
        os.mkdir(os.path.join(save_folder, query))

    # load pinterest and scrape
    url_set = set()
    pinterest_url = f'https://www.pinterest.com/search/pins/?q={query}'
    driver.get(pinterest_url)
    time.sleep(3)

    last_urls = []

    i = -1
    while 1:
        i += 1

        all_elements = driver.find_elements(By.XPATH,
                                                 '//div[@data-test-id="pin-visual-wrapper"]/div[1]/div[1]/img')  # 查找全部的图片元素
        log = '第' + str(i + 1) + '次scroll，本次scroll共发现' + str(len(all_elements)) + '张图' + "\n"
        print(log)

        for element in all_elements:
            try:
                img_url = element.get_attribute('src')  # 获取图片链接
            except Exception as e:
                print(e)
                continue

            new_url = img_url.replace('236x', 'originals')  # 缩略图的尺寸只有236x，替换为originals才是原图尺寸高清
            last_url_set_len = len(url_set)
            url_set.add(new_url)
            last_url = img_url

            # 若图片没有重复并成功添加，则下载
            if len(url_set) > last_url_set_len:
                ret = download_url_screenshot(driver_ss, new_url, os.path.join(save_folder, query), min_size)
                if ret>0:
                    curr_num += 1
                # print(curr_num)

            if curr_num >= num_images:
                print(str(num_images) + '张图片已爬取完毕，爬取程序终止')
                break

        else: # if break + 外层else + 外层break 跳出二重循环（因为如果满足上面的if条件的话，else就不执行，就跳到外层循环的break了）
            last_urls.append(last_url)

            # 这一步操作是为了判断滑到了底部，以last来记录每一页的最后一个数据，如果连续3页数据的最后一个数据都相同，则代表滑到了底部，则停止循环
            if i >= 4 and last_urls[-1] == last_urls[-2] and last_urls[-1] == last_urls[-3]:
                log = '已达到页面底部，没有爬到预期数量的图片，共爬取到', str(len(url_set)), '张图片，爬取程序终止'
                print(log)
                break

            else:  # 如果没有滑到底部则继续循环
                driver.execute_script(f'window.scrollTo({i * 2400},{(i + 1) * 2400})')
                # 设置每次滑动的高度，我这里经调试后即使每次滑动2000，每页数据也还是会有重复，所以必须去重
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
            continue

        break

    driver.close()
    driver_ss.close()
    return 1


class Scraper_UI:
    def __init__(self):
        global curr_num

        self.win = tk.Tk()
        self.win.title('Pinterest 爬虫')
        self.win.geometry("500x350+10+10")

        query_label = tk.Label(self.win, text='请输入关键词')
        query_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        self.query_entry = tk.Entry(width=20)
        self.query_entry.grid(row=1, column=1, padx=10, pady=10)

        num_images_label = tk.Label(self.win, text='请输入爬取数量')
        num_images_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        self.num_images_entry = tk.Entry(width=20)
        self.num_images_entry.grid(row=2, column=1, padx=10, pady=10)

        min_size_label = tk.Label(self.win, text='请输入最小图片宽度')
        min_size_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.E)
        self.min_size_entry = tk.Entry(width=20)
        self.min_size_entry.grid(row=3, column=1, padx=10, pady=10)

        save_folder_label = tk.Label(self.win, text='图片存储地址')
        save_folder_label.grid(row=4, column=0, sticky=tk.E, padx=10, pady=10)
        self.save_folder_entry = tk.Entry(self.win, width=20)
        self.save_folder_entry.grid(row=4, column=1,  sticky=tk.W, padx=10, pady=10)
        save_folder_button = tk.Button(self.win, text='选择', width=4, command=self.choose_save_folder)
        save_folder_button.grid(row=4, column=2, padx=10, pady=10)

        start_button = tk.Button(self.win, text='开始爬虫', command=self.start_scraper)
        start_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        progress_label = tk.Label(self.win, text='图片下载进度')
        progress_label.grid(row=6, column=0, padx=10, pady=10, sticky=tk.E)
        self.progressbar = ttk.Progressbar(self.win)
        self.progressbar.grid(row=6, column=1, columnspan=3, padx=10, pady=10)
        self.progressbar['length'] = 240

        self.start_button = tk.Button(self.win, text='打开文件夹', command=self.open_folder)

    def choose_save_folder(self):
        chosen_path = filedialog.askdirectory(title="选择图片存储地址")
        self.save_folder_entry.delete(0, 'end')
        self.save_folder_entry.insert(tk.END, str(chosen_path))

    def start_scraper(self):
        self.progressbar['value'] = 0
        self.start_button.grid_forget()

        self.query = self.query_entry.get()
        self.num_images = int(self.num_images_entry.get())
        self.min_size = int(self.min_size_entry.get())
        self.save_folder = self.save_folder_entry.get()
        self.progressbar['maximum'] = self.num_images
        # scraper(query,num_images,save_folder)
        scraper_thread = threading.Thread(target=scraper,args=(self.query,self.num_images,
                                                               self.save_folder,self.min_size))
        scraper_thread.start()

        self.refresh_progressbar()

    def refresh_progressbar(self):
        self.progressbar['value'] = curr_num

        if curr_num < self.num_images:
            self.win.after(2, self.refresh_progressbar)
        if curr_num == self.num_images:
            self.start_button.grid(row=7, column=2, padx=10, pady=10)

    def open_folder(self):
        dir = self.save_folder
        os.system('start ' + dir)   # windows
        # os.system('open ' + dir)  # mac



mywin = Scraper_UI()
mywin.win.mainloop()

