# -*- encoding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class News:
    title = ""
    source_url = ""
    source = ""

    def __init__(self, title, author,url):
        self.title = title
        self.source = author
        self.source_url = url

    def print(self):
        print("title:" + self.title + " source" + self.source + " source_url:" + self.source_url)
