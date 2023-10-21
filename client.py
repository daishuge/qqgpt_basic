from file import read_line, last_line, remove_n,second_last_line
import time

lis=[]

while True:

    if read_line(1)=="<reply_start>" and last_line()!="<reply_end>":
        reply=last_line()

        if reply not in lis:
            print(reply)
            lis.append(reply)
            continue

    if read_line(1)=="<reply_start>" and last_line()=="<reply_end>" or read_line(1)=="" and last_line()=="":

        last_second=second_last_line()
        print(last_second)

        ask=input("You: ")

        #########程序从这里开始###########

        with open("result.txt", "w",encoding='utf-8') as f:
            f.write("<ask>\n"+ask)

        first=True

        while first:
            if read_line(1)=="<reply_start>":
                first=False
                break