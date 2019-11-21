# -*- encoding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class News:
    title = ""
    source_url = ""
    source = ""

    def __init__(self, title, author, url):
        self.title = title
        self.source = author
        self.source_url = url

    def print_all(self):
        print("{}\n{}\t{}".format(self.title, self.source, self.source_url))

    def print_title(self):
        print(self.title)

    def print_detail(self):
        print("{}\t{}", self.source, self.source_url)
