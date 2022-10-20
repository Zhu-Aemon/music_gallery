import os
from mutagen import File


class Core:
    def __init__(self):
        pass

    @staticmethod
    def source_scan(paths: list) -> list:
        music_list = []
        for path in paths:
            for root, dirs, files in os.walk(path):
                for name in files:
                    assert isinstance(name, str), 'TypeError: name is not instance of str'
                    if name.endswith('.mp3') or name.endswith('.aac') or name.endswith('.flac'):
                        assert isinstance(root, str), 'TypeError: variable root is not instance of str!'
                        root = root.replace('\\', '/')
                        music_list.append(f'{root}/{name}')
        return music_list

    @staticmethod
    def get_mp3_info(path: str) -> list:
        assert path.endswith('.mp3'), 'MusicTypeError: function get_mp3_info takes in mp3 file'
        file = File(path)
        mp3_title = file.tags['TIT2'].text[0]
        mp3_artist = file.tags['TPE1'].text[0]
        try:
            mp3_cover_data = file.tags['APIC:Cover'].data
        except KeyError:
            try:
                mp3_cover_data = file.tags['APIC:'].data
            except KeyError:
                mp3_cover_data = None
        try:
            mp3_album = file.tags['TALB'].text[0]
        except KeyError:
            mp3_album = ''
        return mp3_title, mp3_artist, mp3_album, mp3_cover_data
