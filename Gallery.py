import os
import inspect
import ctypes
import urllib.parse
import time

from mutagen import File

from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from urllib.request import urlretrieve
from PIL import Image, ImageDraw


class Core(object):
    def __init__(self):
        pass

    @staticmethod
    def source_scan(paths: list) -> list:
        """
        对设置中选择的路径进行扫描，获取音乐的路径列表（目前只支持mp3）
        :param paths: 需要扫描的路径
        :return: 所有音乐的路径组成的列表
        """

        music_list = []
        try:
            for path in paths:
                for root, dirs, files in os.walk(path):
                    for name in files:
                        assert isinstance(name, str), 'TypeError: name is not instance of str'
                        if name.endswith('.mp3') or name.endswith('.aac') or name.endswith('.flac'):
                            assert isinstance(root, str), 'TypeError: variable root is not instance of str!'
                            root = root.replace('\\', '/')
                            music_list.append(f'{root}/{name}')
        except TypeError:
            pass
        return music_list

    @staticmethod
    def get_mp3_info(path: str) -> tuple:
        """
        获取一首歌的相关信息
        :param path: 这一首歌的路径
        :return: 返回一个元组(歌曲标题, 歌手, 歌曲所在专辑)
        """

        assert path.endswith('.mp3'), 'MusicTypeError: function get_mp3_info takes in mp3 file'
        file = File(path)
        try:
            mp3_title = file.tags['TIT2'].text[0]
        except KeyError:
            mp3_title = ''
        try:
            mp3_artist = file.tags['TPE1'].text[0]
        except KeyError:
            mp3_artist = ''
        try:
            mp3_album = file.tags['TALB'].text[0]
        except KeyError:
            mp3_album = ''
        return mp3_title, mp3_artist, mp3_album

    @staticmethod
    def save_cover(filepath, filename):
        """
        将指定的歌曲的封面保存下来
        :param filepath: 歌曲所在路径
        :param filename: 想要将封面图片保存至的路径
        :return: None
        """

        file = File(filepath)
        if '.' not in filename:
            filename = f'{filename}.jpg'
        with open(filename, "wb") as f:
            f.write(file.tags['APIC:'].data)
            f.close()

    @staticmethod
    def get_artist_page_url(artist):
        # Parse the artist name to use in the URL
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # chrome_options.add_experimental_option('detach', True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # initialize the Chrome driver
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        url = '/artist/7vk5e3vY1uw9plTHJAMwjN'
        artist_parsed = urllib.parse.quote(artist)

        # Fetch the content of the webpage
        driver.get(f"https://open.spotify.com/search/{artist_parsed}/artists")

        # Extract the URL from the first result on the page
        url_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[2]/div/div/div/div[1]/div[1]/div/div[2]/a'))
        )
        if url_element:
            url = url_element.get_attribute('href')
            return url
        else:
            print('failed')

    @staticmethod
    def get_artist_info(url):
        style = 'failed'

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # chrome_options.add_experimental_option('detach', True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # initialize the Chrome driver
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        # Fetch the content of the webpage
        driver.get(url)

        # /html/body/div[4]/div/div[2]/div[3]/div[1]/div[1]/div/div[1]
        style_element_parent = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'under-main-view'))
        )
        time.sleep(5)
        style_element_son = style_element_parent.find_element(By.XPATH, 'div')
        style_element = style_element_son.find_element(By.XPATH, 'div')

        audience = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'Ydwa1P5GkCggtLlSvphs'))
        )

        if audience:
            audience = audience.text
        else:
            audience = 'error'

        if style_element:
            style = style_element.get_attribute('style')
            print(style.split('("')[1].split('")')[0])
            return style.split('("')[1].split('")')[0], audience
        else:
            print('failed')

    @staticmethod
    def image_down(url):
        urlretrieve(url, 'tmp/background.jpeg')

    @staticmethod
    def get_artist_ins_name(artist):
        assert isinstance(artist, str)
        return artist.replace(' ', '').lower()
        # # Parse the artist name to use in the URL
        # chrome_options = Options()
        # # chrome_options.add_argument('--headless')
        # chrome_options.add_experimental_option('detach', True)
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # # initialize the Chrome driver
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        # driver.get('https://www.instagram.com/')
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, '_aauy'))
        # )
        # driver.find_element(By.CLASS_NAME, '_aauy').send_keys(artist)
        # ins_name_element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/nav/div[2]/div/div/div[2]/div[3]/div/div[2]/div/div[1]/div/a/div/div[2]/div[1]/div/div/div[1]'))
        # )
        #
        # if ins_name_element:
        #     ins_name = ins_name_element.text
        #     return ins_name
        # else:
        #     print('fatal error!')

    @staticmethod
    def get_artist_ins_avatar(ins_name):
        url = f'https://www.instagram.com/{ins_name}/'
        # Parse the artist name to use in the URL
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # chrome_options.add_experimental_option('detach', True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # initialize the Chrome driver
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(url)

        avatar_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/header/div/div/span/img'))
        )

        avatar_src = avatar_element.get_attribute('src')
        return avatar_src

    @staticmethod
    def circle_corner(src, percentage, filename):
        image = Image.open(src)
        length = image.size[0]
        radii = int(length * percentage)
        circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建黑色方形
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形

        image = image.convert("RGBA")
        w, h = image.size

        # 创建一个alpha层，存放四个圆角，使用透明度切除圆角外的图片
        alpha = Image.new('L', image.size, 255)
        alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
        alpha.paste(circle.crop((radii, 0, radii * 2, radii)),
                    (w - radii, 0))  # 右上角
        alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),
                    (w - radii, h - radii))  # 右下角
        alpha.paste(circle.crop((0, radii, radii, radii * 2)),
                    (0, h - radii))  # 左下角
        image.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见

        # 添加圆角边框
        # draw = ImageDraw.Draw(img)
        # draw.rounded_rectangle(img.getbbox(), outline="black", width=3, radius=radii)
        image.save(filename, 'png', quality=100)

    @staticmethod
    # 圆形头像
    def circle(img_path, cir_path):
        ima = Image.open(img_path).convert("RGBA")
        size = ima.size
        # print(size)
        # 因为是要圆形，所以需要正方形的图片
        r2 = min(size[0], size[1])
        if size[0] != size[1]:
            ima = ima.resize((r2, r2), Image.ANTIALIAS)
        # 最后生成圆的半径
        r3 = int(r2 / 2)
        imb = Image.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 0))
        pima = ima.load()  # 像素的访问对象
        pimb = imb.load()
        r = float(r2 / 2)  # 圆心横坐标

        for i in range(r2):
            for j in range(r2):
                lx = abs(i - r)  # 到圆心距离的横坐标
                ly = abs(j - r)  # 到圆心距离的纵坐标
                l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径
                if l < r3:
                    pimb[i - (r - r3), j - (r - r3)] = pima[i, j]

        imb.save(cir_path)
        return cir_path


def _async_raise(tid, ex_ctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(ex_ctype):
        ex_ctype = type(ex_ctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(ex_ctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
