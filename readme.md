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

Deployment
========================

Install Mysql
------------------------
you can also use PostgreSQL
	sudo apt-get install mysql-server mysql-client
create an super user
Install git
-----------------------
	sudo apt-get install git

clone project
----------------------
	git clone https://github.com/floatec/MEPSS2013.git

install django and dependencies
----------------------
	cd to/your/project/folder
	sudo apt-get install python-pip
	sudo pip install -r deploy/requirements.txt

initial project
----------------------
	mysql --user=root --password=root localhost
	mysql>CREATE DATABASE prosdatabase;
	mysql>GRANT ALL PRIVILEGES ON prosdatabase.* TO 'prosdatabase'@'localhost' IDENTIFIED BY 'some_pass' WITH GRANT OPTION;
	mysql>exit
change your mysql configuration ProsDataBase/ProsData/Base/settings.py
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'prosdatabase',
            'USER': 'prosdatabase',
            'PASSWORD': 'pass',
        }
    }

navigate into your projects folder:
    cd path/to/your/Project/MEPSS2013/ProsDataBase
	./manange.py syncdb
please say yes if you are asked to create an admin user
	./manage.py migrate
you can noew test it by running
	./manage.py runserver
and open http://localhost:8000 in your browser or try it with wget/curl

setup NginX
----------------------
install nginx
    sudo apt-get install nginx python-flup
run django in fsatcgi mode
    python ./manage.py runfcgi host=127.0.0.1 port=8080
don't forget to add it to your init.d script!
    sudo touch /etc/nginx/sites-available/sample_project.conf
    sudo ln -s /etc/nginx/sites-available/sample_project.conf /etc/nginx/sites-enabled/sample_project.conf
add your config
    server {
        listen 80;
        server_name myhostname.com;
        access_log /var/log/nginx/sample_project.access.log;
        error_log /var/log/nginx/sample_project.error.log;

        # https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-production
        location /static/ { # STATIC_URL
            alias /your/path/to/the/static/folder/; # STATIC_ROOT
            expires 30d;
        }



        location / {
            include fastcgi_params;
            fastcgi_pass 127.0.0.1:8000;
             fastcgi_split_path_info ^()(.*)$;
        }
    }
