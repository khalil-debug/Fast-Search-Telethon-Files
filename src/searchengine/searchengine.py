from collections import defaultdict
from math import log
import string


def update_username_scores(old: dict[str, float], new: dict[str, float]):
    for username, score in new.items():
        if username in old:
            old[username] += score
        else:
            old[username] = score
    return old


def normalize_string(input_string: str) -> str:
    translation_table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    string_without_punc = input_string.translate(translation_table)
    string_without_double_spaces = " ".join(string_without_punc.split())
    return string_without_double_spaces.lower()


class SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self._index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._documents: dict[str, tuple[str, str]] = {}
        self.k1 = k1
        self.b = b

    @property
    def posts(self) -> list[str]:
        return list(self._documents.keys())

    @property
    def number_of_documents(self) -> int:
        return len(self._documents)

    @property
    def avdl(self) -> float:
        if not hasattr(self, "_avdl"):
            self._avdl = sum(len(d) for d in self._documents.values()) / len(self._documents)
        return self._avdl

    def idf(self, kw: str) -> float:
        N = self.number_of_documents
        n_kw = len(self.get_usernames(kw))
        return log((N - n_kw + 0.5) / (n_kw + 0.5) + 1)

    def bm25(self, kw: str) -> dict[str, float]:
        result = {}
        idf_score = self.idf(kw)
        avdl = self.avdl
        for url, freq in self.get_usernames(kw).items():
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (
                1 - self.b + self.b * len(self._documents[url]) / avdl
            )
            result[url] = idf_score * numerator / denominator
        return result

    def search(self, query: str) -> dict[str, float]:
        keywords = normalize_string(query).split(" ")
        username_scores: dict[str, float] = {}
        for kw in keywords:
            kw_urls_score = self.bm25(kw)
            username_scores = update_username_scores(username_scores, kw_urls_score)
        return username_scores

    def index(self, username: str,filename: str, password: str) -> None:
        self._documents[filename] = (username, password)
        words = normalize_string(password).split(" ")
        for word in words:
            self._index[word][filename] += 1
        self._index[filename][filename] += 1
        if hasattr(self, "_avdl"):
            del self._avdl

    def bulk_index(self, documents: list[tuple[str, str, str]]):
        for username, filename, password in documents:
            self.index(username, filename, password)

    def get_usernames(self, keyword: str) -> dict[str, int]:
        keyword = normalize_string(keyword)
        return self._index[keyword]

    def print_index(self):
        for word, usernames in self._index.items():
            print(f"Word: {word}")
            for username, count in usernames.items():
                print(f"    Username: {username}, Count: {count}")

    @property
    def documents(self):
        return self._documents
