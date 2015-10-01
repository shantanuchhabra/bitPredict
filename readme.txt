################################################################################

bitPredict: 15-112 Term Project by Shantanu Chhabra (schhabra), Fall 2014

################################################################################

Welcome! This app analyzes bitcoin history and predicts the behavior of 
bitcoins to help you make better decisions about buying, selling or waiting.
In special cases, the algorithm tells you to wait so that you can sell at a 
higher price or buy at a lower price based on your intention. If you press
"FREEZE" in that special case, you will be prompted to buy/sell whenever it's 
best suited, provided the app remains open and you stay at the Predict page. 
There are several other features in this app like, "View Charts", "Personalize".
To read more about the algorithm, see algoInfo.txt or just use the app! :)
To get the correct prediction, please refresh the data as soon as you open
the app. This will take at most 40 seconds. You will not need to refresh the 
data again unless you close the app. The data automatically gets updated.
The "View Charts" button lets you view the variation of the bitcoin over the 
past one year or six months or three months.
Under the "Personalize" section, you can enter your Purchase History and see the
app plot your purchase history on a graph, along with the Resistance and Support
Lines.

This app was built in Python 2.7 using no external modules. The only modules 
used to build this app were Tkinter, datetime, time, urllib, contextlib, math,
copy, os, tkMessageBox, tkSimpleDialog and webbrowser. The file, 
eventBasedAnimationClass.py must be saved in the same directory as the project
.py file. The tempDir folder must also be in the same directory as the project
.py file.
All you need to do to run the app is run the file, bitPredict.py. Have fun!:)

################################################################################