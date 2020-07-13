#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author: lpx
@Date: 2020-07-13 17:56:13
@LastEditTime: 2020-07-13 19:04:58
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /baseline/rouge_eval.py
'''
from rouge import Rouge
from config import Params as p
import jieba
from collections import Counter
from predict import Predict
from utils import timer


class RougeEval():
    def __init__(self, path):
        self.path = path
        self.scores = None
        self.rouge = Rouge()
        self.sources = []
        self.hypos = []
        self.refs = []
        self.process()

    def process(self):
        print('Reading from ', self.path)
        with open(self.path, 'r') as test:
            for line in test:
                source, ref = line.strip().split(',')
                ref = ''.join(list(jieba.cut(ref))).replace('。', '.')
                self.sources.append(source)
                self.refs.append(ref)
        print('Evaluating.')
        print(f'Test set contains {len(self.sources)} samples.')

    @timer('building hypotheses')
    def build_hypos(self, predict):
        print('Building hypotheses.')
        count = 0
        for source in self.sources:
            if count % 50 == 0: print(count)
            self.hypos.append(predict.predict(source.split()))
            count += 1

    def get_average(self):
        assert len(self.hypos) > 0, 'Build hypotheses first!'
        print('Calculating average rouge scores.')
        return self.rouge.get_scores(self.hypos, self.refs, avg=True)

    def one_sample(self, hypo, ref):
        return self.rouge.get_scores(hypo,ref)[0]

rouge_eval = RougeEval(p.test_data_path)
predict = Predict()
rouge_eval.build_hypos(predict)
result = rouge_eval.get_average()
print('rouge1: ',result['rouge-1'])
print('rouge2: ',result['rouge-2'])
print('rougeL: ',result['rouge-l'])
with open('evaluation/rouge_result.txt', 'w') as file:
    for r, metrics in result.items():
        file.write(r+'\n')
        for metric, value in metrics.items():
            file.write(metric+': '+str(value*100))
            file.write('\n')
