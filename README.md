##Cosmetics shop web-site

###Installation
1. Install dependencies
```
pip install -r requirements.txt
```
2. Models migrate
```
python manage.py migrate
```

###Permissions
3. Translation permissions
```
python manage.py translation_perms
```
4. Create permissions groups 
```
python manage.py create_groups
```
5. Add custom superuser permissions
```
python manage.py add_superuser_perm
```

###Run project
6. Run web server
```
python manage.py runserver
```
