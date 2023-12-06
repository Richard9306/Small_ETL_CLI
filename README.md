# Small_ETL_CLI
recruitment task


## Table of Contents
* [Author](#author)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [To Do](#todo)


## Author
### Ryszard Najewski

## Technologies Used
- Python 3.10.7
- Project requirements/dependencies are listed in the [requirements.txt](requirements.txt) file.

## Features
- Parsing data from multiple files(json, csv, xml)
- Validating and inserting data in sqlite database
- User-friendly interface from command line
- Available few commands for base user and admin


## Setup
To run this app you need to:
1. prepare virtual enviroment
2. run command: git clone https://github.com/Richard9306/Small_ETL_CLI 
Now you're ready to use my app. How to use it? Very simple. First you need to specified in bottom of the script.py paths your files in this 3 formats: .json, .csv and .xml. And now you're ready to go!
Here are available commands:
- The most important command, stands for creating and loading data to database with one click ! Important: all the rest of commands require user's login and password !
  + python script.py create_database
- Commands available for all users:
  + python scripty.py print-children --login "your_login" --password "your_password"
  + python scripty.py find-similar-children-by-age --login "your_login" --password "your_password"
- Admin's commands:
  + python scripty.py print-all-accounts --login "your_login" --password "your_password"
  + python scripty.py print-oldest-account --login "your_login" --password "your_password"
  + python scripty.py group-by-age --login "your_login" --password "your_password"

## To Do
- adding tests
- adding password hashing
- rebuilding methods in DatabaseManager to smaller

