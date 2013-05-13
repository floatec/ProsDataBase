Install
====================
Install Git
--------------------
	sudo apt-get install git

Clone the Project
--------------------
    cd path/of/your/choice
	git clone https://github.com/floatec/MEPSS2013.git

Install Django and other necessary packages
--------------------
	cd /path/to/your/Project
	sudo apt-get install python-pip
	sudo pip install -r deploy/requirements.txt

Initalize the Project
--------------------
navigate into your projects folder:
    cd path/to/your/Project/MEPSS2013/ProsDataBase
	./manange.py syncdb
please say yes if you are asked to create an admin user
	./manage.py migrate

if you like to use another database than the default sqlite(only recomended for develping) you can change it in ProsDataBase/ProsDataBase/settings.py


	
