# coding=utf8
 
"""
    A simple thread pool
 
    Usage:
 
        pool = ThreadPool(size=10)  # size: how many threads in pool [default: 1]
        pool.start()  # start all threads to work!
        pool.append_job(myjob, *args, **kwargs)
        pool.join()   # wait all jobs done
        pool.stop()   # kill all threads in pool
"""
 
 
import threading
from Queue import Queue, Empty
 
# macros: thread's states
RUNNING = 1
STOPPED = 0
 
 
class ThreadWorker(threading.Thread):
 
    def __init__(self, pool):
        super(ThreadWorker, self).__init__()
        self.pool = pool
        # subthreads terminates once the main thread end
        self.setDaemon(True)
        self.state = STOPPED
 
    def start(self):
        self.state = RUNNING
        super(ThreadWorker, self).start()
 
    def stop(self):
        self.state = STOPPED
 
    def run(self):
 
        while self.state is RUNNING:
            # don't use `Queue.empty` to check but use Exception `Empty`,
            # because another thread may put a job right after your checking
            try:
                job, args, kwargs = self.pool.jobs.get(block=False)
            except Empty:
                continue
            else:
                # do job
                try:
                    result = job(*args, **kwargs)
                    self.pool.results.put(result)  # collect the result
                except Exception, e:
                    self.stop()
                    raise e
                finally:
                    self.pool.jobs.task_done()
 
 
class ThreadPool(object):
 
    def __init__(self, size, result_queue):
        self.size = size
        self.jobs = Queue()
        self.results = result_queue
        self.threads = []
 
    def start(self):
        """start all threads"""
        for i in range(self.size):
            self.threads.append(ThreadWorker(self))
 
        for thread in self.threads:
            thread.start()
 
    def append_job(self, job, *args, **kwargs):
        self.jobs.put((job, args, kwargs))
 
    def join(self):
        """waiting all jobs done"""
        self.jobs.join()
 
    def stop(self):
        """kill all threads"""
        for thread in self.threads:  # stop all threads
            thread.stop()
 
        for thread in self.threads:  # waiting completing
            if thread.isAlive():
                thread.join()
 
        del self.threads[:]
 
 
if __name__ == '__main__':
    '''Time this test should get about 1s'''
 
    from time import sleep
 
    thread_pool = ThreadPool(size=10, result_queue=Queue())
 
    def job(i):
        print "Hello! %d" % i
        sleep(i)

        return 1
 
    thread_pool.start()
 
    for x in range(10):
        thread_pool.append_job(job, x)
 
    thread_pool.join()
    thread_pool.stop()