#Introduction
This application creates a database used for Swiss Style tournament pairings. It records player registrations, matches, and wins. It also pairs players as they move through the tournament.

##Instructions
1. Clone the repository from Github to your local.
2. Download and install [Virtual Box](https://www.virtualbox.org/wiki/Downloads). Only the platform package is needed, Extension Packs and SDK are not needed. This application was developed against the 5.1.14 version.
3. Download and install [Vagrant](https://www.vagrantup.com/downloads.html). This application was developed against the 1.9.2 version.
4. Once both Virtual Box and Vagrant are installed, open the virtual box application.
5. Open up the terminal and enter in the command Vagrant up.
6. Navigate to the vagrant folder using the command 'cd /vagrant'.
7. Enter in the command psql tournament, which will navigate you to the psql command line. 
8. Enter in the command \i tournament.sql', which will create the database, tables, and views.
9. Return to the vagrant folder on your virtual box using the command '\q'.
10. Run the test file for the application using the command, 'python tournament.sql'.