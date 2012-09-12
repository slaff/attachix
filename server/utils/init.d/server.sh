#!/bin/sh -e
### BEGIN INIT INFO
# Provides:  WorkDispatcher
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# X-Interactive:     true
# Short-Description: Start/stop the work dispatcher

. ./etc.conf

PYTHON="python"
BIN="vserver.py"
LOG="$LOG_DIR/server.log"

stop() {
    echo -n "Stopping $BIN"
    pids=`ps -ef|grep $BIN|grep $PYTHON|awk '{print $2}'`
    if [ -z "$pids" ]; then
        echo "\t[fail]"
        return 1
    fi

    kill -TERM $pids
    echo "\t[ok]"
}

start() {
    echo -n "Starting $BIN"
    (cd $DIR; nohup $PYTHON $DIR/$BIN >> $LOG &)
    RETVAL=$?
    echo "\t[ok($RETVAL)]"
}


case $1 in
        start)
            start
            break;
        ;;
        stop)
            stop
            break
        ;;
        status)
            pids=`ps -ef|grep $BIN|grep $PYTHON|awk '{print $2}'`
            if [ -z "$pids" ]; then
                echo "Not Running!"
                exit 1;
            fi

            echo "Running on pids: $pids"
            break;
        ;;
        restart)
            stop
            start
            break
        ;;
        *)
                echo "Usage:\n\t$0 {start|stop|restart|status}"
                exit 1
        ;;
esac

exit 0;