
CutDB
============= 
cutDB is a database application built for analysing cuticular cllagens from C. elgans

Installation
-----------------
You need the following python package to make thins installation work:

+ django 
+ django-tinymce 
+ django-mathfilters 
+ django-colorful 
+ biopython 
+ mysqlclient
+ numpy
+ cython


You can get it by simply enter into your (preferable virtual_env) commandline

   pip install django django-tinymce django-mathfilters django-colorful biopython mysqlclient cythong 

You should copy the template_settings.py to local_settings.py file and make proper adjustments in the file.

You will also nee a working binary of ClustalO, which you can get from here http://www.clustal.org/omega/
Set the full binary (path+executable) in your local_settings.py


The development server can be started with:

    python .\manage.py runserver --settings cutDB.settings.local_settings

The first page you usually find under http://127.0.0.1:8000/database/