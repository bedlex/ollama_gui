"""Load style sheet from file"""
from typing import List
from abc import ABC
import os
from random import choice
import re


class Style(ABC):
    current_theme_path = os.path.join("app", "style", "current.pss")

    @staticmethod
    def load(style_file: str) -> str | bool:
        """load style shit from file"""
        try:
            with open(style_file, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            print("Style sheet not found")
            return False

    @staticmethod
    def save(style_file: str, data: str) -> bool:
        try:
            with open(style_file, 'w', encoding='utf-8') as file:
                file.write(data)
                return True
        except Exception as error:
            print(error)

    @classmethod
    def __load_random(cls) -> str | bool:
        dir_path = os.path.join("app", "style", "themes")
        item = choice(os.listdir(dir_path))
        if item != "":
            theme_path = os.path.join(dir_path, item)
            return cls.load(theme_path)
        return False

    @classmethod
    def current(cls):

        if not os.path.exists(cls.current_theme_path):
            current_style = cls.__load_random()
            if current_style:
                cls.save(cls.current_theme_path, current_style)
                return current_style
            return False
        else:
            current_style = cls.load(cls.current_theme_path)
            return current_style

    @classmethod
    def change_theme(cls, theme: str) -> bool:
        new_theme_path = os.path.join("app", "style", "themes", theme)
        if os.path.exists(new_theme_path):
            new_theme = cls.load(new_theme_path)
            if new_theme:
                cls.save(cls.current_theme_path, new_theme)
                return True

        return False

    @classmethod
    def available_themes(cls) -> List[str]:
        dir_path = os.path.join("app", "style", "themes")
        return os.listdir(dir_path)

    @classmethod
    def get_font(cls) -> int | bool:
        current_theme = cls.current()
        pattern = r"font-size: (\d+)px;"
        match = re.search(pattern, current_theme)
        if match:
            return int(match.group(1))
        return False

    @classmethod
    def set_font(cls, font_size: str) -> bool:
        current_theme = cls.current()
        pattern = r"font-size: (\d+)px;"
        replacement = f"font-size: {font_size}px;"
        match = re.search(pattern, current_theme)
        if match:
            current_theme = re.sub(pattern, replacement, current_theme)
            cls.save(cls.current_theme_path, current_theme)
            return True
        return False