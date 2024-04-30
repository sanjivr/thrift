#/bin/bash

wdir=$(dirname $(realpath $0))

source ${wdir}/develop/bin/activate
#python ${wdir}/budget-report.py
jupyter-notebook --notebook-dir=~/git/sanjivr/thrift/
