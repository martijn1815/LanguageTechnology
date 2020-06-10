#!/usr/bin/python3
"""
File:       evaluation_score.py
Authors:    Martijn E.N.F.L. Schendstok (s2688174)
Date:       10 June 2020
"""

import sys

def main(argv):
    with open(argv[1]) as file:
        score = 0
        total = 0
        for line in file:
            line = line.strip().split()
            if len(line) == 2:
                score += int(line[1])
                total += 1

    print("Score: {0}/{1}".format(score, total))


if __name__ == "__main__":
    main(sys.argv)
