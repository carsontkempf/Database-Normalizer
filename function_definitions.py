# normalization_functions.py

def First(relation):
    relations_after_1NF = [relation]
    return relations_after_1NF


def Second(relation):
    relations_after_1NF = First(relation)
    relations_after_2NF = relations_after_1NF
    return relations_after_2NF


def Third(relation):
    relations_after_2NF = Second(relation)
    relations_after_3NF = relations_after_2NF
    return relations_after_3NF


def Boyce(relation):
    relations_after_3NF = Third(relation)
    relations_after_BCNF = relations_after_3NF
    return relations_after_BCNF


def Fourth(relation):
    relations_after_BCNF = Boyce(relation)
    relations_after_4NF = relations_after_BCNF
    return relations_after_4NF


def Fifth(relation):
    relations_after_4NF = Fourth(relation)
    relations_after_5NF = relations_after_4NF
    return relations_after_5NF
