from problem.models import ProblemIOMode


default_env = ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]

_c_lang_config = {
    "template": """//PREPEND BEGIN
#include <stdio.h>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  printf("%d", add(1, 2));
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.c",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 10000,
        "max_memory": 256 * 1024 * 1024,
        "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -w -fmax-errors=3 -std=c11 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_c_o2_lang_config = {
    "template": """//PREPEND BEGIN
#include <stdio.h>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  printf("%d", add(1, 2));
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.c",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 10000,
        "max_memory": 256 * 1024 * 1024,
        "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c11 {src_path} -lm -o {exe_path}",
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
    "max_cpu_time": 8000,
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
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -w -fmax-errors=3 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_o2_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_11_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -w -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_11_o2_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_14_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -w -fmax-errors=3 -std=c++14 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_14_o2_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++14 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_17_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -w -fmax-errors=3 -std=c++17 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": {ProblemIOMode.standard: "c_cpp", ProblemIOMode.file: "c_cpp_file_io"},
        "env": default_env
    }
}

_cpp_17_o2_lang_config = {
    "template": """//PREPEND BEGIN
#include <iostream>
//PREPEND END

//TEMPLATE BEGIN
int add(int a, int b) {
  // Please fill this blank
  return ___________;
}
//TEMPLATE END

//APPEND BEGIN
int main() {
  std::cout << add(1, 2);
  return 0;
}
//APPEND END""",
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 10000,
        "max_real_time": 20000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++17 {src_path} -lm -o {exe_path}",
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
    "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++17 {src_path} -lm -o {exe_path}"
}

_cpp_lang_spj_config = {
    "exe_name": "spj-{spj_version}",
    "command": "{exe_path} {in_file_path} {user_out_file_path}",
    "seccomp_rule": "c_cpp"
}

_java_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
//TEMPLATE END

//APPEND BEGIN
//APPEND END""",
    "compile": {
        "src_name": "Main.java",
        "exe_name": "Main",
        "max_cpu_time": 5000,
        "max_real_time": 10000,
        "max_memory": -1,
        "compile_command": "/usr/bin/javac {src_path} -d {exe_dir} -encoding UTF8"
    },
    "run": {
        "command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k -Djava.security.manager -Dfile.encoding=UTF-8 "
                   "-Djava.security.policy==/etc/java_policy -Djava.awt.headless=true Main",
        "seccomp_rule": None,
        "env": default_env,
        "memory_limit_check_only": 1
    }
}


_py2_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
//TEMPLATE END

//APPEND BEGIN
//APPEND END""",
    "compile": {
        "src_name": "solution.py",
        "exe_name": "solution.pyc",
        "max_cpu_time": 3000,
        "max_real_time": 10000,
        "max_memory": 256 * 1024 * 1024,
        "compile_command": "/usr/bin/python -m py_compile {src_path}",
    },
    "run": {
        "command": "/usr/bin/python {exe_path}",
        "seccomp_rule": "general",
        "env": default_env
    }
}
_py3_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
//TEMPLATE END

//APPEND BEGIN
//APPEND END""",
    "compile": {
        "src_name": "solution.py",
        "exe_name": "__pycache__/solution.cpython-36.pyc",
        "max_cpu_time": 3000,
        "max_real_time": 10000,
        "max_memory": 256 * 1024 * 1024,
        "compile_command": "/usr/bin/python3 -m py_compile {src_path}",
    },
    "run": {
        "command": "/usr/bin/python3 {exe_path}",
        "seccomp_rule": "general",
        "env": default_env + ["PYTHONIOENCODING=utf-8"]
    }
}

_pypy2_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
//TEMPLATE END

//APPEND BEGIN
//APPEND END""",
    "run": {
        "exe_name": "solution.py",
        "command": "/usr/bin/pypy {exe_path}",
        "seccomp_rule": "",
        "env": default_env,
        "memory_limit_check_only": 1
    }
}

_pypy3_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
//TEMPLATE END

//APPEND BEGIN
//APPEND END""",
    "run": {
        "exe_name": "solution.py",
        "command": "/usr/bin/pypy3 {exe_path}",
        "seccomp_rule": "",
        "env": default_env + ["PYTHONIOENCODING=utf-8"],
        "memory_limit_check_only": 1
    }
}

_php_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END
//TEMPLATE BEGIN
//TEMPLATE END
//APPEND BEGIN
//APPEND END""",
    "run": {
        "exe_name": "solution.php",
        "command": "/usr/bin/php {exe_path}",
        "seccomp_rule": "",
        "env": default_env,
        "memory_limit_check_only": 1
    }
}

_js_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END
//TEMPLATE BEGIN
//TEMPLATE END
//APPEND BEGIN
//APPEND END""",
    "run": {
        "exe_name": "solution.js",
        "command": "/usr/bin/node {exe_path}",
        "seccomp_rule": "",
        "env": ["NO_COLOR=true"] + default_env,
        "memory_limit_check_only": 1
    }
}

_go_lang_config = {
    "template": """//PREPEND BEGIN
//PREPEND END

//TEMPLATE BEGIN
//TEMPLATE END

//APPEND BEGIN
//APPEND END""",
    "compile": {
        "src_name": "main.go",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/go build -o {exe_path} {src_path}",
        "env": ["GOCACHE=/tmp", "GOPATH=/tmp/go"]
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": "",
        # 降低内存占用
        "env": ["GODEBUG=madvdontneed=1"] + default_env,
        "memory_limit_check_only": 1
    }
}

languages = [
    {"config": _c_lang_config, "spj": {"compile": _c_lang_spj_compile, "config": _c_lang_spj_config},
     "name": "C", "description": "GCC 9.3.0", "content_type": "text/x-csrc"},
    {"config": _c_o2_lang_config, "name": "C With O2", "description": "GCC 9.3.0", "content_type": "text/x-csrc"},
    {"config": _cpp_lang_config, "spj": {"compile": _cpp_lang_spj_compile, "config": _cpp_lang_spj_config},
     "name": "C++", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _cpp_o2_lang_config, "name": "C++ With O2", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _cpp_11_lang_config, "name": "C++ 11", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _cpp_11_o2_lang_config, "name": "C++ 11 With O2", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _cpp_14_lang_config, "name": "C++ 14", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _cpp_14_o2_lang_config, "name": "C++ 14 With O2", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _cpp_17_lang_config, "name": "C++ 17", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _cpp_17_o2_lang_config, "name": "C++ 17 With O2", "description": "G++ 9.3.0", "content_type": "text/x-c++src"},
    {"config": _java_lang_config, "name": "Java", "description": "OpenJDK 1.8", "content_type": "text/x-java"},
    {"config": _js_lang_config, "name": "JavaScript", "description": "JavaScript (Node.Js 14.17.2)", "content_type": "text/typescript"},
    {"config": _php_lang_config, "name": "PHP", "description": "PHP 8.0.8", "content_type": "text/x-php"},
    {"config": _py2_lang_config, "name": "Python2", "description": "Python 2.7.17", "content_type": "text/x-python"},
    {"config": _py3_lang_config, "name": "Python3", "description": "Python 3.6.9", "content_type": "text/x-python"},
    {"config": _pypy2_lang_config, "name": "Pypy2", "description": "Python 2.7.18 with PyPy 7.3.5", "content_type": "text/x-python"},
    {"config": _pypy3_lang_config, "name": "Pypy3", "description": "Python 3.7.10 with PyPy 7.3.5", "content_type": "text/x-python"},
    {"config": _go_lang_config, "name": "Golang", "description": "Golang 1.14", "content_type": "text/x-go"}
]
