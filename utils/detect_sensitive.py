import html
import os

import jieba
import redis
from bs4 import BeautifulSoup

from readingforum.settings import BASE_DIR


class Sensitive:
    _sensitive_words_set_key = 'sensitive_words'
    _sensitive_words_dir = BASE_DIR / 'utils/sensitive-words'
    for filename in os.listdir(_sensitive_words_dir):
        print("jieba加载" + filename)
        jieba.load_userdict(os.path.join(_sensitive_words_dir, filename))

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        if not self.redis_client.exists(Sensitive._sensitive_words_set_key):
            self._read_sensitive_words()

    def _read_sensitive_words(self):
        sensitive_words_files = os.listdir(Sensitive._sensitive_words_dir)
        print("读取敏感词到redis")
        for filename in sensitive_words_files:
            with open(os.path.join(Sensitive._sensitive_words_dir, filename), 'r', encoding='utf-8') as f:
                sensitive_w = f.read().splitlines()
                for word in sensitive_w:
                    self.redis_client.sadd(Sensitive._sensitive_words_set_key, word)
        print("读取结束，redis中的敏感词数量：", self.redis_client.scard(Sensitive._sensitive_words_set_key))

    @classmethod
    def detect_sensitive_words(cls, text: str) -> tuple[str, bool]:
        """

        :param text:
        :return: 过滤后的html，是否含有敏感词
        """
        instance = cls()
        soup = BeautifulSoup(text, 'html.parser')
        for element in soup.find_all(string=True):
            if element.parent.attrs.get('class') == ["sensitive-word"]:
                continue
            new_element = element
            for word in jieba.lcut(element):
                if instance.redis_client.sismember(Sensitive._sensitive_words_set_key, word):
                    new_element = new_element.replace(word, f'<span class="sensitive-word">{word}</span>')
            element.replace_with(new_element)

        for element in soup.find_all('span', attrs={'class': 'sensitive-word'}):
            if element.text == "":
                element.extract()
            if element.has_attr('style'):
                del element['style']

        text = html.unescape(str(soup))
        # filtered_text = text.replace('<span class="sensitive-word"></span>', "")
        return text, '<span class="sensitive-word"' in text


if __name__ == '__main__':
    html_text = """
        <p>这是一个<b>兼职</b>例子。</p>
        <p>更多文本内容...</p>
        <p>我想要招聘你和兼职我<p>
        这段文字包含敏感词汇如：兼职、淘宝内容等。但已经有了<span class="sensitive-word">兼职</span>。还有一个空标记<span class="sensitive-word"></span>。
    """
    for i in range(5):
        print(i)
        html_text, has_sensitive = Sensitive.detect_sensitive_words(html_text)
        print(html_text, has_sensitive)

# import os
# import re
# from typing import List, Union, Tuple
#
# from bs4 import BeautifulSoup
#
# from readingforum.settings import BASE_DIR
#
#
# class Sensitive:
#     _sensitive_words = set()
#     _sensitive_words_dir = BASE_DIR / 'utils/sensitive-words'
#     _sensitive_words_loaded = False
#
#     def __init__(self):
#         if not Sensitive._sensitive_words_loaded:
#             self._read_sensitive_words()
#             Sensitive._sensitive_words_loaded = True
#
#     def _read_sensitive_words(self):
#         sensitive_words_files = os.listdir(Sensitive._sensitive_words_dir)
#         for sensitive_words_file in sensitive_words_files:
#             with open(os.path.join(Sensitive._sensitive_words_dir, sensitive_words_file), 'r', encoding='utf-8') as f:
#                 sensitive_w = f.read().splitlines()
#                 Sensitive._sensitive_words.update(sensitive_w)
#         print("词典中的敏感词数量：", len(Sensitive._sensitive_words))
#
#     @classmethod
#     def detect_sensitive_words(cls, text: str) -> tuple[str, bool]:
#         """
#
#         :param text:
#         :return: 过滤后的html，是否含有敏感词
#         """
#         instance = cls()
#         filtered_text = text
#         for sensi_word in instance._sensitive_words:
#             pattern = re.compile(r'(?<!<span class="sensitive-word">)' + re.escape(sensi_word) + r'(?!</span>)',
#                                  re.IGNORECASE)
#             replacement = f'<span class="sensitive-word">{sensi_word}</span>'
#             filtered_text = re.sub(pattern, replacement, filtered_text)
#         filtered_text = filtered_text.replace("<span class='sensitive-word'></span>", "")
#         # print(filtered_text, '<span class="sensitive-word"' in filtered_text)
#         return filtered_text, '<span class="sensitive-word"' in filtered_text
#
#
# if __name__ == '__main__':
#     html_text = """
#     <head><title>测试页面</title></head>
#     <body>
#         <p>这是一个<b>兼职</b>例子。</p>
#         <p>更多文本内容...</p>
#         <p>我想要招聘你和兼职我<p>
#         这段文字包含敏感词汇如：兼职、淘宝内容等。但已经有了<span class="sensitive-word">兼职</span>。还有一个空标记<span class="sensitive-word"></span>。
#     </body>
#     """
#     for _ in range(5):
#         html_text, _ = Sensitive.detect_sensitive_words(html_text)
#         print(html_text)
#         print(_)
