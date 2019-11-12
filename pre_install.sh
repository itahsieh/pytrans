#!/bin/sh


sudo apt-get update
sudo apt-get install python python-pip
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
# pip install --upgrade setuptools
# python -m pip install --upgrade pip
# sudo vim /usr/bin/pip
#
# # change the original snippet
#
# from pip import main
# if __name__ == '__main__':
#     sys.exit(main())
#
# # to ====>
# 
# from pip import __main__
# if __name__ == '__main__':
#     sys.exit(__main__._main())
# 
pip install cffi --user
pip install pysftp --user
pip install pyserial
pip install numpy
pip install psycopg2-binary
