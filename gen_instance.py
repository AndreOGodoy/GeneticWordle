#!/usr/bin/env python3

from argparse import ArgumentParser
from typing import List, Tuple
from random import randint
import sys

Instance = Tuple[List[str], str]

def generate_from_english_list(word_len: int = 5) -> Instance:
    with open('words.txt', 'r') as file:
        content = file.readlines()

    without_new_line = map(str.strip, content)
    without_numbers = filter(str.isalpha, without_new_line)
    with_desired_len = filter(lambda word: len(word) == 5, without_numbers)
    as_upper_case = map(str.upper, with_desired_len)
    without_duplicates = list(set(as_upper_case))

    words = list(without_duplicates)
    secret = words[randint(0, len(words)-1)]

    return words, secret

def generate_from_wordle_list(word_len: int = 5) -> Instance:
    with open('wordle_words.txt', 'r') as file:
        content = file.readlines()

    without_new_line = map(str.strip, content)
    as_upper_case = map(str.upper, without_new_line)

    words = list(as_upper_case)
    secret = words[randint(0, len(words)-1)]

    return words, secret

def generate_random(word_len: int = 5, dict_len: int = 10_000) -> Instance:
    ascii_upper_case_start = 65
    ascii_upper_case_end = 90

    gen_letter = lambda:  chr(randint(ascii_upper_case_start, ascii_upper_case_end))
    gen_word = lambda: ''.join([gen_letter() for _ in range(word_len)])

    words = [gen_word() for _ in range(dict_len)]
    secret = words[randint(0, dict_len-1)]

    return words, secret

def print_instance(instance: Instance):
    dictionary, secret = instance

    print(secret)
    print()
    for word in dictionary:
        print(word)

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-n', '--word_len', type=int, nargs=1)
    arg_parser.add_argument('-m', '--method', nargs=1)
    args = arg_parser.parse_args()

    if args.method == 'random':
        method = generate_random
    elif args.method == 'wordle':
        method = generate_from_wordle_list
    else:
        method = generate_from_english_list

    instance = method(word_len=args.word_len)
    print_instance(instance)

