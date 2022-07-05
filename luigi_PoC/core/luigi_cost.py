import math
import re
import time

import jieba
import luigi
import urllib


def calculate_similarity(text1, text2):
    s1_cut = [i for i in jieba.cut(text1, cut_all=True) if i != '']
    s2_cut = [i for i in jieba.cut(text2, cut_all=True) if i != '']
    word_set = set(s1_cut).union(set(s2_cut))
    # print(word_set)

    word_dict = dict()
    i = 0
    for word in word_set:
        word_dict[word] = i
        i += 1

    s1_cut_code = [word_dict[word] for word in s1_cut]
    s1_cut_code = [0] * len(word_dict)

    for word in s1_cut:
        s1_cut_code[word_dict[word]] += 1

    s2_cut_code = [word_dict[word] for word in s2_cut]
    s2_cut_code = [0] * len(word_dict)
    for word in s2_cut:
        s2_cut_code[word_dict[word]] += 1

    # 计算余弦相似度
    sum = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(s1_cut_code)):
        sum += s1_cut_code[i] * s2_cut_code[i]
        sq1 += pow(s1_cut_code[i], 2)
        sq2 += pow(s2_cut_code[i], 2)

    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0
    return result


record = dict()


class MemoryTarget(luigi.Target):
    def __init__(self, key):
        self.key = key
        super().__init__()

    def exists(self):
        return record.get(self.key, False)

    def touch(self, value):
        record[self.key] = value


class ParseArgs(luigi.Task):

    def output(self):
        return MemoryTarget("keyword")

    def run(self):
        keyword = "nihao"
        m = MemoryTarget("keyword")
        m.touch(keyword)


class GenerateUrls(luigi.Task):
    def requires(self):
        return ParseArgs()

    def run(self):
        keyword = urllib.parse.quote(record.get(self.input().key))
        urls_dict = dict(
            biying=f"https://cn.bing.com/search?q={keyword}",
            s_360=f"https://www.so.com/s?ie=utf-8&fr=none&src=home_none&nlpv=basesc&q={keyword}",
            sougou=f"https://www.sogou.com/web?query={keyword}"
        )
        m = MemoryTarget("urls_dict")
        m.touch(urls_dict)

    def output(self):
        return MemoryTarget("urls_dict")


class ParsePage(luigi.Task):
    def requires(self):
        return GenerateUrls()

    def run(self):
        html_string_dict = {}
        with open("biying.txt", 'r', encoding='UTF8') as f:
            biying = f.read()
        with open("s_360.txt", 'r', encoding='UTF8') as f:
            s_360 = f.read()
        with open("sougou.txt", 'r', encoding='UTF8') as f:
            sougou = f.read()
        html_string_dict.update({"biying": biying, "s_360": s_360, "sougou": sougou})
        m = MemoryTarget("html_string_dict")
        m.touch(html_string_dict)

    def output(self):
        return MemoryTarget("html_string_dict")


class CalculateBiyingAnd360(luigi.Task):
    def requires(self):
        return ParsePage()

    def run(self):
        string_dict = record.get(self.input().key)
        t1 = string_dict.get('biying')
        t2 = string_dict.get('s_360')
        biying_360_result = calculate_similarity(t1, t2)
        m = MemoryTarget("biying_360_result")
        m.touch(biying_360_result)

    def output(self):
        return MemoryTarget("biying_360_result")


class CalculateBiyingSogou(luigi.Task):
    def requires(self):
        return ParsePage()

    def run(self):
        string_dict = record.get(self.input().key)
        t1 = string_dict.get('biying')
        t2 = string_dict.get('sougou')
        biying_sougou_result = calculate_similarity(t1, t2)
        m = MemoryTarget("biying_sougou_result")
        m.touch(biying_sougou_result)

    def output(self):
        return MemoryTarget("biying_sougou_result")


class Join(luigi.Task):
    def requires(self):
        return {"biying_360": CalculateBiyingAnd360(), "biying_sougou": CalculateBiyingSogou()}

    def run(self):
        result_360 = record.get(self.input()["biying_360"].key)
        result_sougou = record.get(self.input()["biying_sougou"].key)
        final_result = f"biying and 360 is {result_360}; biying and sougou result is {result_sougou}"
        m = MemoryTarget("final_result")
        m.touch(final_result)

    def output(self):
        return MemoryTarget("final_result")