#!/bin/sh
export PYTHONBREAKPOINT=celery.contrib.rdb.set_trace
export DJANGO_SETTINGS_MODULE=config.settings.devel
watchmedo auto-restart -d apps/ -d config/ -p '*.py' -R -- celery -A config worker -c 2 -Q celery,validation -l DEBUG
