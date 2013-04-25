Install
====================
Install Git
--------------------
	sudo apt-get install git

Install Django
--------------------
	cd /path/to/your/Project
	pip install -r deploy/requirements.txt

Clone the Project
--------------------
	git clone https://github.com/floatec/MEPSS2013.git

Initalize the Project
--------------------
if you like to use an other database the te defoult sqlite(only recomended for develping) you can change it in ProsDataBase/ProsDataBase/settings.py

	./manange.py syncdb
	./manage.py migrate
	
please say yes if you get asked to create an admin user

	
