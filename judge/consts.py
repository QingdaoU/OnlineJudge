# coding=utf-8
class Result(object):
    ACCEPTED = 0
    RUNTIME_ERROR = 1
    TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    COMPILE_ERROR = 4
    FORMAT_ERROR = 5
    WRONG_ANSWER = 6
    SYSTEM_ERROR = 7
    WAITING = 8


class Language(object):
    C = 1
    CPP = 2
    JAVA = 3
