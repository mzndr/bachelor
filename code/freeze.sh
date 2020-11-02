#!/bin/sh
pip freeze | grep -v "pkg-resources" > requirements.txt
