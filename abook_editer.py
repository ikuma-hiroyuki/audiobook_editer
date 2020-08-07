# import glob
import os
import subprocess

import mutagen
from mutagen.easyid3 import EasyID3

root = input("pleas input target root folder path." + "\n")
print()


def division_and_remove(root):
    """
    指定したフォルダのサブフォルダ内のmp3ファイルを対象に
    mp3DirectCutでファイルを分割し、元ファイルを削除します。
    """
    for folder, subfolders, files in os.walk(root):
        # if folder != root:
        print(folder, subfolders)
        for file in files:
            print(file)
            file_path = os.path.join(folder, file)
            subprocess.run(["mp3DirectCut", file_path, "/autocue", folder], shell=True)
            os.remove(file_path)


def all_edit(root):
    """
    指定したフォルダのサブフォルダにあるmp3ファイルにタグをつけ、ファイル名を編集します
    """
    for folder, subfolders, files in os.walk(root):
        # if folder != root:
        target = AudioBook(folder, subfolders, files)
        target.edit_audiobook()


class AudioBook:
    def __init__(self, folder, subfolders, files):
        self.__folder = folder
        self.__files = files
        self.__folder_base_name = os.path.basename(self.__folder)
        self.__under_score_position = self.__folder_base_name.rfind("_")
        self.__bookname = None
        self.__set_bookname()
        self.__author = None
        self.__authorlist = []
        self.__set_author()

    def __set_bookname(self):
        if self.__under_score_position > 0:
            self.__bookname = self.__folder_base_name[: self.__under_score_position]
        else:
            self.__bookname = self.__folder_base_name

    def __get_bookname(self):
        return self.__bookname

    def __set_author(self):
        if self.__under_score_position > 0:
            # フォルダ名の_より後ろの文字を取得する (著者名)
            buf = self.__folder_base_name[self.__under_score_position + 1 :]
            # 著者名の空白文字を削除する (表記揺れをなくすため)
            replace_table = str.maketrans({" ": "", "　": ""})
            author_string = buf.translate(replace_table)
            # 著者リスト作成 リスト[0]はアーティスト。アルバムアーティストはリストを;で連結した文字列
            self.__authorlist = [
                author_string for author_string in author_string.split(",")
            ]
            self.__author = ";".join(self.__authorlist)
        else:
            self.__author = None

    def __get_author(self):
        return self.__author

    def edit_audiobook(self):
        if self.__under_score_position > 0:
            for i, file in enumerate(self.__files):
                extension = os.path.splitext(file)[1]
                if extension == ".MP3":
                    track_title = self.__bookname + "_" + str(i + 1).zfill(3)
                    filepath = os.path.join(self.__folder, file)
                    print(track_title)

                    # mp3タグの編集
                    try:
                        tags = EasyID3(filepath)
                    except mutagen.id3.ID3NoHeaderError:
                        tags = mutagen.File(filepath, easy=True)
                        tags.add_tags()

                    tags["title"] = track_title
                    tags["genre"] = "Book"
                    tags["album"] = self.__bookname
                    tags["artist"] = self.__author
                    tags["albumartist"] = self.__authorlist[0]
                    tags["tracknumber"] = "{}/{}".format(i + 1, len(self.__files))
                    tags.save()

                # ファイル名のリネーム
                # extension = os.path.splitext(file)[1]
                old_file_path = os.path.join(self.__folder, file)
                new_file_path = os.path.join(self.__folder, track_title + extension)
                os.rename(old_file_path, new_file_path)

            # フォルダ名のリネーム
            new_folder_path = os.path.join(
                os.path.dirname(self.__folder), self.__bookname
            )
            os.rename(self.__folder, new_folder_path)

            print(f"書名: {self.__bookname} / 著者: {self.__author}\n")

    bookname = property(__get_bookname)
    author = property(__get_author)


division_and_remove(root)
all_edit(root)

input("\nComplete")
