#!/usr/bin/python3
"""
File:       get_question_types.py
Author:     Martijn E.N.F.L. Schendstok
Date:       26 May 2020
"""

from final_project import *


def main(argv):
    nlp = spacy.load('en_core_web_sm')
    open('where_question.txt', 'w').close()
    open('who_question.txt', 'w').close()
    open('x_of_y_question.txt', 'w').close()
    open('true_false_question.txt', 'w').close()
    open('description_question.txt', 'w').close()
    open('other_question.txt', 'w').close()

    with open("all_questions_sorted.txt", "r") as file:
        for line in file:
            line = line.strip()
            parse = nlp(line)

            if is_where_question(parse):
                # Where question:
                with open("where_question.txt", "a") as out_file:
                    out_file.write(line + "\n")

            elif is_xy_question(parse):
                # X of Y question
                with open("x_of_y_question.txt", "a") as out_file:
                    out_file.write(line + "\n")

            elif is_truefalse_question(parse):
                # True/False question:
                with open("true_false_question.txt", "a") as out_file:
                    out_file.write(line + "\n")

            elif is_description_question(parse):
                # Description question:
                with open("description_question.txt", "a") as out_file:
                    out_file.write(line + "\n")

            elif is_who_question(parse):
                # Who question:
                with open("who_question.txt", "a") as out_file:
                    out_file.write(line + "\n")

            else:
                with open("other_question.txt", "a") as out_file:
                    out_file.write(line + "\n")


if __name__ == "__main__":
    main(sys.argv)
