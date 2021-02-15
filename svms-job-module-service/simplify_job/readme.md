### Python: 3.6.x (64 bit)
### MySQL: 5.7.x
### Framework: Django 3.x, DjangoRestFramework 3.11

### Clone Repository:
$ git clone https://bitbucket.org/simplifyworkforce/svms-job-module-service.git

### Create & Activate Virtualenv:
$ cd <app_root>
$ python3 -m venv svmsenv
$ source svmsenv/bin/activate

### Install Dependencies:
(svmsenv) $ pip install -r requirements.txt

### Setup Environment Variables:
On git repository, there is settings.yaml.example file. In order to deploy the application, 
we have to copy it to a file named as "settings.yaml" and then update the required values there.
Please note, we should not delete settings.yaml.example file as that will be required to be
referenced time to time for further environment variable updates.

### Run DB migrations:
(svmsenv) $ python manage.py makemigrations
(svmsenv) $ python manage.py migrate

### Create Initial Superadmin Credentials:
(svmsenv) $ python manage.py createsuperuser
-- then provide superuser credentials as prompted.

### Run the server:
(svmsenv) $ python manage.py runserver

### Load Fixtures
(svmsenv) $ python manage.py loaddata fixtures/*.json
