#!/usr/bin/python3
"""
File:       get_question_types.py
Author:     Martijn E.N.F.L. Schendstok
Date:       15 May 2020
"""

import sys
import spacy


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

            if parse[0].lemma_ == "where":
                # Where question:
                with open("where_question.txt", "a") as out_file:
                    out_file.write(line + "\n")
            elif parse[0].head.lemma_ == "be" and parse[0].head.dep_ == "ROOT":
                prep = False
                for t in parse[:-2]:
                    if t.dep_ == "prep" or (t.head.pos_ == "NOUN" and
                                            t.dep_ == "case"):  # -X of Y- or -X's Y-
                        prep = True
                if prep:
                    # X of Y question
                    with open("x_of_y_question.txt", "a") as out_file:
                        out_file.write(line + "\n")
                else:
                    if parse[0].lemma_ == "be":
                        # True/False question:
                        with open("true_false_question.txt", "a") as out_file:
                            out_file.write(line + "\n")
                    elif parse[1].lemma_ == "be":
                        # Description question:
                        with open("description_question.txt", "a") as out_file:
                            out_file.write(line + "\n")
            elif parse[0].lemma_ == "who":
                # Who question:
                with open("who_question.txt", "a") as out_file:
                    out_file.write(line + "\n")
            else:
                with open("other_question.txt", "a") as out_file:
                    out_file.write(line + "\n")


if __name__ == "__main__":
    main(sys.argv)
