import os
import inspect
import ctypes

from mutagen import File


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
