#!/usr/bin/env python

"""
logger is a supervisord event listener program.

It aggregates the output of multiple programs running in supervisor and
reprints their output with the addition of a honcho-like prefix. This prefix
helps to distinguish the output of different programs.

Here's an example supervisor configuration file that uses logger:

    [supervisord]
    nodaemon=true
    environment=PYTHONUNBUFFERED="1"
    logfile=/dev/null
    logfile_maxbytes=0

    [program:web]
    command=gunicorn myproject:app
    stdout_logfile=NONE
    stderr_logfile=NONE
    stdout_events_enabled=true
    stderr_events_enabled=true

    [program:worker]
    command=celery -A myproject worker -l info
    stdout_logfile=NONE
    stderr_logfile=NONE
    stdout_events_enabled=true
    stderr_events_enabled=true

    [eventlistener:logger]
    command=bin/logger.py
    buffer_size=100
    events=PROCESS_LOG
    stderr_logfile=/dev/fd/1
    stderr_logfile_maxbytes=0

And here's an example of the output you might see from supervisord:

    2017-01-24 17:25:02,903 INFO supervisord started with pid 15433
    2017-01-24 17:25:03,907 INFO spawned: 'logger' with pid 15439
    2017-01-24 17:25:03,910 INFO spawned: 'web' with pid 15440
    2017-01-24 17:25:03,913 INFO spawned: 'worker' with pid 15441
    2017-01-24 17:25:05,216 INFO success: logger entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
    2017-01-24 17:25:05,217 INFO success: web entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
    2017-01-24 17:25:05,217 INFO success: worker entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
    web (stderr)         | 2017-01-24 17:25:04,203 [15440] [gunicorn.error:INFO] Starting gunicorn 19.6.0
    web (stderr)         | 2017-01-24 17:25:04,205 [15440] [gunicorn.error:INFO] Listening at: http://127.0.0.1:5000 (15440)
    web (stderr)         | 2017-01-24 17:25:04,206 [15440] [gunicorn.error:INFO] Using worker: sync
    web (stderr)         | 2017-01-24 17:25:04,211 [15449] [gunicorn.error:INFO] Booting worker with pid: 15449
    worker               |
    worker               |  -------------- celery@mahler.local v3.1.25 (Cipater)
    worker               | ---- **** -----
    worker               | --- * ***  * -- Darwin-16.3.0-x86_64-i386-64bit
    ...

Note that in the configuration above we disable the logfiles for the
individual programs and for the supervisor daemon itself. This isn't required
but may be useful in containerised environments.

By setting "stderr_logfile=/dev/fd/1" in the [eventlistener:logger] section,
we redirect the aggregated output back to STDOUT (FD 1). You can also log the
aggregated output to a single file.
"""

import sys

WIDTH = 20


def main():
    while True:
        _write("READY\n")
        header = _parse_header(sys.stdin.readline())
        payload = sys.stdin.read(int(header["len"]))

        # Only handle PROCESS_LOG_* events and just ACK anything else.
        if header["eventname"] == "PROCESS_LOG_STDOUT":
            _log_payload(payload)
        elif header["eventname"] == "PROCESS_LOG_STDERR":
            _log_payload(payload, err=True)

        _write("RESULT 2\nOK")


def _write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def _parse_header(data):
    return dict([x.split(":") for x in data.split()])


def _log_payload(payload, err=False):
    headerdata, data = payload.split("\n", 1)
    header = _parse_header(headerdata)
    name = header["processname"]
    if err:
        name += " (stderr)"
    prefix = "{name:{width}} | ".format(name=name, width=WIDTH)
    for line in data.splitlines():
        sys.stderr.write(prefix + line + "\n")
    sys.stderr.flush()


if __name__ == "__main__":
    main()
