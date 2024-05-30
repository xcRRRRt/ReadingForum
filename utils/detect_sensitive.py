import os
import re
from typing import List, Union, Tuple

from bs4 import BeautifulSoup

from readingforum.settings import BASE_DIR


class Sensitive:
    _sensitive_words = set()
    _sensitive_words_dir = BASE_DIR / 'utils/sensitive-words'
    _sensitive_words_loaded = False

    def __init__(self):
        if not Sensitive._sensitive_words_loaded:
            self._read_sensitive_words()
            Sensitive._sensitive_words_loaded = True

    def _read_sensitive_words(self):
        sensitive_words_files = os.listdir(Sensitive._sensitive_words_dir)
        for sensitive_words_file in sensitive_words_files:
            with open(os.path.join(Sensitive._sensitive_words_dir, sensitive_words_file), 'r', encoding='utf-8') as f:
                sensitive_w = f.read().splitlines()
                Sensitive._sensitive_words.update(sensitive_w)
        print("词典中的敏感词数量：", len(Sensitive._sensitive_words))

    @classmethod
    def detect_sensitive_words(cls, text: str) -> tuple[str, bool]:
        """

        :param text:
        :return: 过滤后的html，是否含有敏感词
        """
        instance = cls()
        filtered_text = text
        for sensi_word in instance._sensitive_words:
            pattern = re.compile(r'(?<!<span class="sensitive-word">)' + re.escape(sensi_word) + r'(?!</span>)',
                                 re.IGNORECASE)
            replacement = f'<span class="sensitive-word">{sensi_word}</span>'
            filtered_text = re.sub(pattern, replacement, filtered_text)
        filtered_text = filtered_text.replace("<span class='sensitive-word'></span>", "")
        # print(filtered_text, '<span class="sensitive-word"' in filtered_text)
        return filtered_text, '<span class="sensitive-word"' in filtered_text


if __name__ == '__main__':
    html_text = """
    <html>
    <head><title>测试页面</title></head>
    <body>
        <p>这是一个<b>兼职</b>例子。</p>
        <p>更多文本内容...</p>
        <p>我想要招聘你和兼职我<p>
        这段文字包含敏感词汇如：兼职、淘宝内容等。但已经有了<span class="sensitive-word">兼职</span>。还有一个空标记<span class="sensitive-word"></span>。
    </body>
    </html>
    """
    for _ in range(5):
        html_text, _ = Sensitive.detect_sensitive_words(html_text)
        print(html_text)
        print(_)
