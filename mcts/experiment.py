import split_part

for i in range(0,100):
    print("次数", i)
    with open('split_part.py', 'r',encoding='gb18030', errors='ignore') as f:
           exec(f.read())

# # for i in range(10000):
# execfile("split_part.py")