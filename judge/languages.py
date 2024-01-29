from problem.models import ProblemIOMode


default_env = ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]

_c_lang_config = {
    "template": """//PREPEND BEGIN
#include <stdio.h>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // code
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  printf("%d\n", add(1, 2));
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.c",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 10000,
        "max_memory": 256 * 1024 * 1024,
        "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c17 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_c_lang_spj_compile = {
    "src_name": "spj-{spj_version}.c",
    "exe_name": "spj-{spj_version}",
    "max_cpu_time": 3000,
    "max_real_time": 10000,
    "max_memory": 1024 * 1024 * 1024,
    "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c17 {src_path} -lm -o {exe_path}"
}

_c_lang_spj_config = {
    "exe_name": "spj-{spj_version}",
    "command": "{exe_path} {in_file_path} {user_out_file_path}",
    "seccomp_rule": "c_cpp"
}

_cpp_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // code
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2) << std::endl;
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++20 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_lang_spj_compile = {
    "src_name": "spj-{spj_version}.cpp",
    "exe_name": "spj-{spj_version}",
    "max_cpu_time": 10000,
    "max_real_time": 20000,
    "max_memory": 1024 * 1024 * 1024,
    "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++20 {src_path} -lm -o {exe_path}"
}

_cpp_lang_spj_config = {
    "exe_name": "spj-{spj_version}",
    "command": "{exe_path} {in_file_path} {user_out_file_path}",
    "seccomp_rule": "c_cpp"
}

_java_lang_config = {
    "template": """//PREPEND BEGIN
class Main {
//PREPEND END

//TEMPLATE BEGIN
  static int add(int a, int b) {
    // code
  }
//TEMPLATE END

//APPEND BEGIN
  public static void main(String [] args) {
    System.out.println(add(1, 2));
  }
}
//APPEND END""",
    "compile": {
        "src_name": "Main.java",
        "exe_name": "Main",
        "max_cpu_time": 5000,
        "max_real_time": 10000,
        "max_memory": -1,
        "compile_command": "/usr/bin/javac {src_path} -d {exe_dir}"
    },
    "run": {
        "command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k Main",
        "seccomp_rule": None,
        "env": default_env,
        "memory_limit_check_only": 1
    }
}

_py3_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
def add(a, b):
  # code

//TEMPLATE END

//APPEND BEGIN
print(add(1, 2))
//APPEND END""",
    "compile": {
        "src_name": "solution.py",
        "exe_name": "solution.py",
        "max_cpu_time": 3000,
        "max_real_time": 10000,
        "max_memory": 128 * 1024 * 1024,
        "compile_command": "/usr/bin/python3 -m py_compile {src_path}",
    },
    "run": {
        "command": "/usr/bin/python3 -BS {exe_path}",
        "seccomp_rule": "general",
        "env": default_env
    }
}

_go_lang_config = {
    "template": """//PREPEND BEGIN
package main

import "fmt"
//PREPEND END

//TEMPLATE BEGIN
func add(a int, b int) int {
	// code
}
//TEMPLATE END

//APPEND BEGIN
func main() {
	fmt.Println(add(1, 2))
}
//APPEND END""",
    "compile": {
        "src_name": "main.go",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/go build -o {exe_path} {src_path}",
        "env": ["GOCACHE=/tmp", "GOPATH=/tmp", "GOMAXPROCS=1"] + default_env
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": "golang",
        "env": ["GOMAXPROCS=1"] + default_env,
        "memory_limit_check_only": 1
    }
}

_node_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
function add(a, b) {
  // code
}
//TEMPLATE END

//APPEND BEGIN
console.log(add(1, 2))
//APPEND END""",
    "compile": {
        "src_name": "main.js",
        "exe_name": "main.js",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/node --check {src_path}",
        "env": default_env
    },
    "run": {
        "command": "/usr/bin/node {exe_path}",
        "seccomp_rule": "node",
        "env": default_env,
        "memory_limit_check_only": 1
    }
}

languages = [
    {"config": _c_lang_config, "name": "C", "description": "GCC 13", "content_type": "text/x-csrc",
      "spj": {"compile": _c_lang_spj_compile, "config": _c_lang_spj_config}},
    {"config": _cpp_lang_config, "name": "C++", "description": "GCC 13", "content_type": "text/x-c++src", 
      "spj": {"compile": _cpp_lang_spj_compile, "config": _cpp_lang_spj_config}},
    {"config": _java_lang_config, "name": "Java", "description": "Temurin 21", "content_type": "text/x-java"},
    {"config": _py3_lang_config, "name": "Python3", "description": "Python 3.12", "content_type": "text/x-python"},
    {"config": _go_lang_config, "name": "Golang", "description": "Golang 1.22", "content_type": "text/x-go"},
    {"config": _node_lang_config, "name": "JavaScript", "description": "Node.js 20", "content_type": "text/javascript"},
]
