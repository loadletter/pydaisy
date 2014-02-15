pydaisy
=======

Port of the daisy chatbot to python

IIRC it works like this:

##sqlite version

Import the original daisy memory file (ie: replace filename with ../MEM.DSY):
~~~
python ImportText.py botname filename
~~~


Script with learning support (BOTNAME and LEARN need be set in the file):
~~~
python Tests.py chatbot
~~~


Other possible usage (No learning support):
~~~
python Memory.py botname filename
~~~
