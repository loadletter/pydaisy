pydaisy
=======

Port of the daisy chatbot to python

IIRC it works like this:

##sqlite version

Import the original daisy memory file (ie: replace filename with ../MEM.DSY):
~~~
python ImportText.py botname filename
~~~

Run the bot with:
~~~
python Memory.py botname filename
~~~

Learning should work with the other script:
~~~
python Tests.py chatbot
~~~
(BOTNAME and LEARN should be changed in the file)
