#!/usr/bin/python3
"""
File:       test.py
Author:     Martijn E.N.F.L. Schendstok
Date:       15 May 2020
"""

import sys
import random
from s2688174 import *


def main(argv):
    questions = list()
    with open("all_questions_sorted.txt", "r") as file:
        for line in file:
            questions.append(line.strip())
    random.shuffle(questions)

    open('questions_no_answer.txt', 'w').close()
    count_total = 0
    count_answered = 0
    for question in questions:
        count_total += 1
        answer = create_and_fire_query(question)
        if answer:
            if answer[0] == "Could not find an answer":
                with open("questions_no_answer.txt", "a") as f:
                    f.write(question + "\n")
            else:
                count_answered += 1
        else:
            with open("questions_no_answer.txt", "a") as f:
                f.write(question + "\n")

        print("{0} - {1} ({2:0.1f}%) answered".format(count_total,
                                                      count_answered,
                                                      count_answered / count_total * 100))

    print("Results:")
    print("{0} quesions".format(count_total))
    print("{0} ({1:0.1f}%) answered".format(count_answered, count_answered/count_total*100))


if __name__ == "__main__":
    main(sys.argv)
