# coding=utf-8



languages = {
    "1": {
        "name": "c",
        "code": 1,
        "compile_command": "gcc -DONLINE_JUDGE  -O2 -Wall -std=c99 -pipe {src_path} -lm -o {exe_path}",
        "execute_command": "{exe_path}"
    },
    "2": {
        "name": "cpp",
        "code": 2,
        "compile_command": "g++ -DONLINE_JUDGE -O2 -Wall -std=c++11 -pipe {src_path} -lm -o {exe_path}",
        "execute_command": "{exe_path}"
    },
    "3": {
        "name": "java",
        "code": 3,
        "compile_command": "javac {src_path} -d {exe_path}",
        "execute_command": "java {exe_path}"
    }
}


