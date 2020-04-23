import requests as curl, time

rrr = "seven"
print(rrr.encode())
# print(rrr.encode('base64','strict'))

print(rrr.encode(encoding='UTF-8',errors='strict'))

print(time.time())


import getopt, sys

opts, args = getopt.getopt(sys.argv[1:], "ho:", ["help", "output="]) # "ho:"也可以写成'-h-o:'
print(opts)
print(args)

