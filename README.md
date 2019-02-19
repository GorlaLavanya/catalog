Item Catalog Web App

##By Gorla Lavanya This web app is a project for the Udacity FSND Course.

About

This project is a RESTful web application utilizing the Flask framework which accesses a SQL database that populates Institutes and Courses. OAuth2 provides authentication for further CRUD functionality on the application. Currently OAuth2 is implemented for Google Accounts.

In This Project

This project has one main Python module final.py which runs the Flask application. A SQL database is created using the fdatabase_setup.py module and you can populate the database with test data using final.py. The Flask application uses stored HTML templates in the templates folder to build the front-end of the application.


Skills Required

Python

HTML

CSS

OAuth

Flask Framework

sqlalchemy


Installation

There are some dependancies and a few instructions on how to run the application. Seperate instructions are provided to get GConnect working also.


Dependencies

Vagrant

Udacity Vagrantfile

VirtualBox


How to Install

Install Vagrant & VirtualBox

Clone the Udacity Vagrantfile

Go to Vagrant directory and either clone this repo or download and place zip here

Launch the Vagrant VM (vagrant up)

Log into Vagrant VM (vagrant ssh)

Navigate to cd /vagrant as instructed in terminal

The app imports requests which is not on this vm. Run pip install requests
Or you can simply Install the dependency libraries (Flask, sqlalchemy, requests,psycopg2 and oauth2client) by running pip install -r requirements.txt

Setup application database python/finalproject/fdatabase_setup.py

*Insert sample data python/finalproject/dbcontent.py

Run application using python /finalproject/final.py

Access the application locally using http://localhost:8080

*Optional step(s)

Using Google Login

To get the Google login working there are a few additional steps:

Go to Google Dev Console

Sign up or Login if prompted

Go to Credentials

Select Create Crendentials > OAuth Client ID

Select Web application

Enter name 'Institute details'

Authorized JavaScript origins = 'http://localhost:8080'

Authorized redirect URIs = 'http://localhost:8080/login' && 'http://localhost:8080/gconnect'

Select Create

Copy the Client ID and paste it into the data-clientid in login.html

On the Dev Console Select Download JSON

Rename JSON file to client_secrets.json

Place JSON file in finalproject directory that you cloned from here

Run application using python/institute/final.py

JSON Endpoints

The following are open to the public:

InstitutesJSON: /institute/JSON - Displays the all instiutes catalog. Institutes and all courses.

courseJSON: /institute/<int:institute_id>/menu/JSON- Displays menus of specific Institute. 

courenamesJSON:/institute/<int:institute_id>/menu/<int:course_id>/JSON- Displays the menu of specific institute in institutes.


Miscellaneous

This project is inspiration from gmawji.
