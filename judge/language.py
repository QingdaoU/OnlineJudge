# coding=utf-8


languages = {
    1: {
        "name": "c",
        "src_name": "main.c",
        "code": 1,
        "compile_max_cpu_time": 3000,
        "compile_max_memory": 128 * 1024 * 1024,
        "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c99 {src_path} -lm -o {exe_path}/main",
        "spj_compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -Werror -fmax-errors=3 -std=c99 {src_path} -lm -o {exe_path}",
        "execute_command": "{exe_path}/main",
        "use_sandbox": True
    },
    2: {
        "name": "cpp",
        "src_name": "main.cpp",
        "code": 2,
        "compile_max_cpu_time": 3000,
        "compile_max_memory": 256 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}/main",
        "spj_compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -Werror -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}",
        "execute_command": "{exe_path}/main",
        "use_sandbox": True
    },
    3: {
        "name": "java",
        "src_name": "Main.java",
        "code": 3,
        "compile_max_cpu_time": 3000,
        "compile_max_memory": -1,
        "compile_command": "/usr/bin/javac {src_path} -d {exe_path} -encoding UTF8",
        "execute_command": "/usr/bin/java -cp {exe_path} -Xss1M -XX:MaxPermSize=16M "
                           "-XX:PermSize=8M -Xms16M -Xmx{max_memory} -Djava.security.manager "
                           "-Djava.security.policy==policy -Djava.awt.headless=true Main",
        "use_sandbox": False
    }
}


