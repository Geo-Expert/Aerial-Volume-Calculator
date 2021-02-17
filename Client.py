import subprocess
from tkinter import filedialog
from tkinter import *


root = Tk()
filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
root.destroy()
print(filename)

proc = subprocess.Popen('curl ' + 'localhost:8080 ' + '-d ' + filename, stdout=subprocess.PIPE, shell=True)

(out,err) = proc.communicate()
print('\n', out)
print('\n press q to quit')
key="something"
while key != "q":
    key=str(input())
