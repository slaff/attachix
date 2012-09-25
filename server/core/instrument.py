# Instrument your source code
import logging
import gc


def dump():
    """
    Dumps the information about the variables and functions
    """
    logging.getLogger().debug("Garbage: %s" % gc.garbage)
    try:
        from guppy import hpy
        hp = hpy()
        h = hp.heap()
        logging.getLogger().debug("Heap: %s" % h.byrcs)
    except Exception as ex:
        logging.getLogger().warn("Failed dumping the heap data: %s" % ex)

def dumpOnSignal(signum, frame):
    dump()

def enableProfiler(signum, config):
    """
    Enables the profiler on specified signal
    """
    try:
        # If the profiler is available on the system then enable it
        import gevent_profiler
        
        if config.has_key('summaryOutput'):
            gevent_profiler.set_summary_output(config['summaryOutput'])

        if config.has_key('statsOutput'):
            gevent_profiler.set_stats_output(config['statsOutput'])

        if config.has_key('traceOutput'):
            gevent_profiler.set_trace_output(config['traceOutput'])

        if config.has_key('printPercentage'):
            gevent_profiler.print_percentages(config['printPercentage'])

        if config.has_key('countTimeBlocking'):
            gevent_profiler.time_blocking(config['countTimeBlocking'])

        gevent_profiler.attach_on_signal(signum=signum, duration=config['duration'])
        logging.getLogger().info("The profiler is enabled and waiting on signal %s." % signum)

    except Exception as ex:
        logging.getLogger().warn("Failed enabling the profiler: %s" % ex)


