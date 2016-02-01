# coding=utf-8


languages = {
    1: {
        "name": "c",
        "src_name": "main.c",
        "code": 1,
        "syscalls": "!execve:k,flock:k,ptrace:k,sync:k,fdatasync:k,fsync:k,msync,sync_file_range:k,syncfs:k,unshare:k,setns:k,clone:k,query_module:k,sysinfo:k,syslog:k,sysfs:k",
        "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -std=c99 {src_path} -lm -o {exe_path}/main",
        "execute_command": "{exe_path}/main"
    },
    2: {
        "name": "cpp",
        "src_name": "main.cpp",
        "code": 2,
        "syscalls": "!execve:k,flock:k,ptrace:k,sync:k,fdatasync:k,fsync:k,msync,sync_file_range:k,syncfs:k,unshare:k,setns:k,clone:k,query_module:k,sysinfo:k,syslog:k,sysfs:k",
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -std=c++11 {src_path} -lm -o {exe_path}/main",
        "execute_command": "{exe_path}/main"
    },
    3: {
        "name": "java",
        "src_name": "Main.java",
        "code": 3,
        "syscalls": "!execve:k,flock:k,ptrace:k,sync:k,fdatasync:k,fsync:k,msync,sync_file_range:k,syncfs:k,unshare:k,setns:k,clone[a&268435456==268435456]:k,query_module:k,sysinfo:k,syslog:k,sysfs:k",
        "compile_command": "/usr/bin/javac {src_path} -d {exe_path}",
        "execute_command": "java -cp {exe_path} -Djava.security.manager -Djava.security.policy==policy Main"
    }
}


