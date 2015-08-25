/usr/bin/docker run -t -i --privileged -v /var/test_case/:/var/judger/test_case/ -v /var/code/:/var/judger/code/ judger /bin/bash

python judge/judger/run.py -solution_id 1 -max_cpu_time 1 -max_memory 1 -test_case_id 1
