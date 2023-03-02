""" Tool to measure the time each function takes. 
Use it by adding the @profile decorator to a function:

@profile
def myFun(args):
    ...

"""

import cProfile, pstats, io


def profile(fnc):
    """ A decorator that uses cProfile to profile a function 
        Sort by:
            calls (call count)
            cumulative (cumulative time)
            cumtime (cumulative time)
            file (file name)
            filename (file name)
            module (file name)
            ncalls (call count)
            pcalls (primitive call count)
            line (line number)
            name (function name)
            nfl (name/file/line)
            stdname (standard name)
            time (internal time)
            tottime (internal time)
    """

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        # ps.dump_stats(filename='profiling_results.prof')
        print(s.getvalue())
        return retval

    return inner
