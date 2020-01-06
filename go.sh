#!/bin/sh

killall supervisord

echo "Configuring projects..."
echo
#PYTHONPATH=src python go.py

echo
echo "Starting supervisor..."
echo
supervisord -c conf/supervisord.conf

sleep 1
supervisorctl status

echo
echo "Web interface at: http://localhost:9001"
