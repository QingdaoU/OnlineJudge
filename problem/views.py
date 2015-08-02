# coding=utf-8
from django.shortcuts import render


def problem_page(request, problem_id):
    # todo
    return render(request, "problem/problem.html")
