"""
Project : Smart_Bourse

File : news_analyzer.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
News Analyzer
"""


class NewsAnalyzer:

    def __init__(self):

        self.news = []

    # --------------------------------------------------

    def add_news(self, title, source, score=0):

        self.news.append({

            "title": title,

            "source": source,

            "score": score

        })

    # --------------------------------------------------

    def positive_news(self):

        return [

            n for n in self.news

            if n["score"] > 0

        ]

    # --------------------------------------------------

    def negative_news(self):

        return [

            n for n in self.news

            if n["score"] < 0

        ]

    # --------------------------------------------------

    def neutral_news(self):

        return [

            n for n in self.news

            if n["score"] == 0

        ]

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 60)

        print("NEWS ANALYZER")

        print("=" * 60)

        for item in self.news:

            print(item)

        print("=" * 60)
