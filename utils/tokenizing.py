import os

import jieba
import redis
from bs4 import BeautifulSoup
from readingforum.settings import BASE_DIR


class Tokenizer:
    _stop_words_set_key = 'stop_words'
    stop_words_dir = BASE_DIR / 'utils/stopwords'

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        if not self.redis_client.exists(Tokenizer._stop_words_set_key):
            self._read_stop_words()

    def _read_stop_words(self):
        print("加载停用词表")
        stop_words_files = os.listdir(self.stop_words_dir)
        for stop_word_file in stop_words_files:
            with open(os.path.join(self.stop_words_dir, stop_word_file), "r", encoding='utf-8') as f:
                stop_words = f.read().splitlines()
                for stop_word in stop_words:
                    self.redis_client.sadd(Tokenizer._stop_words_set_key, stop_word)
        print("停用词数量：", self.redis_client.scard(Tokenizer._stop_words_set_key))

    @classmethod
    def tokenize(cls, text: str) -> str:
        instance = cls()
        text = instance._remove_html(text)
        words_all = []
        words = jieba.cut_for_search(text)
        for word in words:
            if not instance.redis_client.sismember(Tokenizer._stop_words_set_key, word):
                words_all.append(word)
        return " ".join(words_all)

    def _remove_html(self, sentence: str) -> str:
        soup = BeautifulSoup(sentence, "html.parser")
        text = soup.get_text()
        lines = text.splitlines()
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        return " ".join(non_empty_lines)


if __name__ == '__main__':
    html_text = """
        <p>这是一个 <b>测试</b> 例子。</p>
        <p>更多文本内容...</p>
    """
    print(Tokenizer.tokenize(html_text))
    # 可以多次调用 tokenize 方法
    print(Tokenizer.tokenize(html_text))

# import os
# from typing import List
#
# import jieba
# from bs4 import BeautifulSoup
# from readingforum.settings import BASE_DIR
#
#
# class Tokenizer:
#     stop_words = set()
#     stop_words_dir = BASE_DIR / 'utils/stopwords'
#     stop_words_loaded = False
#
#     def __init__(self):
#         if not Tokenizer.stop_words_loaded:
#             self._read_stop_words()
#             Tokenizer.stop_words_loaded = True
#
#     def _read_stop_words(self):
#         stop_words_files = os.listdir(self.stop_words_dir)
#         for stop_word_file in stop_words_files:
#             with open(os.path.join(self.stop_words_dir, stop_word_file), "r", encoding='utf-8') as f:
#                 stop_words = f.read().splitlines()
#                 Tokenizer.stop_words.update(stop_words)
#         print("停用词数量：", len(Tokenizer.stop_words))
#
#     @classmethod
#     def tokenize(cls, sentence: str) -> str:
#         instance = cls()
#         sentences = instance._remove_html(sentence)
#         words_all = []
#         for s in sentences:
#             words = jieba.cut_for_search(s)
#             words = filter(lambda w: w not in instance.stop_words, words)
#             words_all.extend(list(words))
#         return " ".join(words_all)
#
#     def _remove_html(self, sentence: str) -> List[str]:
#         soup = BeautifulSoup(sentence, "html.parser")
#         text = soup.get_text()
#         lines = text.splitlines()
#         non_empty_lines = [line.strip() for line in lines if line.strip()]
#         return non_empty_lines
#
#
# if __name__ == '__main__':
#     html_text = """
#     <html>
#     <head><title>测试页面</title></head>
#     <body>
#         <p>这是一个 <b>测试</b> 例子。</p>
#         <p>更多文本内容...</p>
#     </body>
#     </html>
#     """
#     print(Tokenizer.tokenize(html_text))
#     # 可以多次调用 tokenize 方法
#     print(Tokenizer.tokenize(html_text))
