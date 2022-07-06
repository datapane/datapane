import os

dname = os.getcwd()
os.chdir(dname)


with open('readme.txt', 'w') as f:
    f.write(dname)


