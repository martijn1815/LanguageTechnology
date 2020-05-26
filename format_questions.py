#!/usr/bin/python3
"""
File:       format_questions.py
Author:     Martijn E.N.F.L. Schendstok
Date:       26 May 2020
"""

import sys


def main(argv):
    with open("all_questions_formatted.txt", "w") as write_file:
        with open("all_questions_sorted.txt", "r") as file:
            for n, line in enumerate(file):
                line = line.strip()
                write_file.write("{0}\t{1}\n".format(n, line))


if __name__ == "__main__":
    main(sys.argv)
