#!/bin/sh

python manage.py flush --noinput && python manage.py loaddata fixtures/carleton.yaml
