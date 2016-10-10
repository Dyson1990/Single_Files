# -*- coding:utf-8 -*-  
"""
@Version: ??
@Author: Dyson
@Contact: Weaver1990@163.com
@File: Markov_text.py
@Time: 2016/9/24 16:28
@Instruction：PASS
"""
import set_log #log_obj.debug(文本)  "\x1B[1;32;41m (文本)\x1B[0m"
import urllib2, bs4
import random
import re
log_obj = set_log.Logger('Markov_text.log', set_log.logging.WARNING, set_log.logging.DEBUG)
log_obj.cleanup('Markov_text.log', if_cleanup = True) # 是否需要在每次运行程序前清空Log文件

def build_dict(text):
    """
    效果：
     {word_a:{word_b:2,word_c:1,word_d:1}, word_e:{word_b:2}, ........}
    """
    # 过滤空单词
    text = text.replace('\n','')
    text = text.replace('\"','')
    text = re.sub(r'\r', '', text)
    # 保证每个标点符号都和前面的单词在一起
    # 这样不会被剔除，保留在马尔科夫链里
    punctuation = [',', '.', ';', ':', '?']
    for symbol in punctuation:
        text = text.replace(symbol, ' '+ symbol +' ')
    words = text.split(' ')
    # 过滤空单词
    words = [word for word in words if word != '']
    
    word_dict = {}
    for i in xrange(1, len(words)):
        if words[i-1] not in word_dict:
            # 为单词新建一个词典
            word_dict[words[i-1]] = {}
        if words[i] not in word_dict[words[i-1]]:
            word_dict[words[i-1]][words[i]] = 0
        word_dict[words[i-1]][words[i]] += 1
    return word_dict

def word_d1_sum(word_d1):
    sum = 0
    for word, value in word_d1.items():
        sum += value
    return sum

def retrieve_random_word(word_d1):
    rand_index = random.randint(1, word_d1_sum(word_d1)) # rand_index: 3
    log_obj.debug("rand_index: %d" %rand_index)
    log_obj.debug2(word_d1.items())
    for word, value in word_d1.items(): # [('over', 1), ('out', 1), ('from', 1), (',', 1), ('.', 2)]
        rand_index -= value
        if rand_index <= 0:
            log_obj.debug2("return: %s" %word)
            return word # return: from
        
if __name__ == '__main__':
    text = str(urllib2.urlopen(
            "http://novel.tingroom.com/novel_down.php?aid=1642&dopost=txt"
            "").read())
    word_dict = build_dict(text)
    length = 200 # 生成马尔科夫链的长度
    chain = ""
    current_word = "I"
    for i in xrange(0, length):
        chain += current_word + ' '
        current_word = retrieve_random_word(word_dict[current_word])
    print chain

