#!/usr/bin/python3
"""
File:       get_question_types.py
Author:     Martijn E.N.F.L. Schendstok
Date:       26 May 2020
"""

from final_project import *


def main(argv):
    nlp = spacy.load('en_core_web_sm')

    where_file = open('questions/where_question.txt', 'w')
    who_file = open('questions/who_question.txt', 'w')
    xy_file = open('questions/x_of_y_question.txt', 'w')
    truefalse_file = open('questions/true_false_question.txt', 'w')
    description_file = open('questions/description_question.txt', 'w')
    count_file = open('questions/count_questions.txt', 'w')
    how_file = open('questions/how_questions.txt', 'w')
    in_file = open('questions/in_questions.txt', 'w')
    what_do_file = open('questions/what_do_questions.txt', 'w')
    other_file = open('questions/other_question.txt', 'w')

    with open("all_questions_formatted.txt", "r") as file:
        for line in file:
            line = line.strip().split("\t")
            n = line[0]
            question = line[1]
            parse = nlp(question)

            if is_where_question(parse):
                # Where question:
                where_file.write("{0}\t{1}\n".format(n, question))

            elif is_xy_question(parse):
                # X of Y question
                xy_file.write("{0}\t{1}\n".format(n, question))

            elif is_truefalse_question(parse):
                # True/False question:
                truefalse_file.write("{0}\t{1}\n".format(n, question))

            elif is_description_question(parse):
                # Description question:
                description_file.write("{0}\t{1}\n".format(n, question))

            elif is_who_question(parse):
                # Who question:
                who_file.write("{0}\t{1}\n".format(n, question))

            elif is_count_question(parse):
                # Count question:
                count_file.write("{0}\t{1}\n".format(n, question))

            elif is_how_question(parse):
                # How question:
                how_file.write("{0}\t{1}\n".format(n, question))

            elif is_in_question(parse):
                # In question:
                in_file.write("{0}\t{1}\n".format(n, question))

            elif is_what_do_question(parse):
                # In question:
                what_do_file.write("{0}\t{1}\n".format(n, question))

            else:
                other_file.write("{0}\t{1}\n".format(n, question))

    where_file.close()
    who_file.close()
    xy_file.close()
    truefalse_file.close()
    description_file.close()
    count_file.close()
    how_file.close()
    in_file.close()
    what_do_file.close()
    other_file.close()


if __name__ == "__main__":
    main(sys.argv)
