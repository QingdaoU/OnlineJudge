# copy from https://github.com/DMOJ/judge/issues/162
try:
    # in large part from http://code.activestate.com/recipes/578899-strsignal/
    import signal
    import ctypes
    import ctypes.util

    libc = ctypes.CDLL(ctypes.util.find_library("c"))
    strsignal_c = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_int)(("strsignal", libc), ((1,),))
    NSIG = signal.NSIG


    def strsignal_ctypes_wrapper(signo):
        # The behavior of the C library strsignal() is unspecified if
        # called with an out-of-range argument.  Range-check on entry
        # _and_ NULL-check on exit.
        if 0 <= signo < NSIG:
            s = strsignal_c(signo)
            if s:
                return s.decode("utf-8")
        return "Unknown signal %d" % signo


    strsignal = strsignal_ctypes_wrapper
except:
    strsignal = lambda x: 'signal %d' % x
