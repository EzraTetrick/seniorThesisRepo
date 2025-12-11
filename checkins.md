## Week 1 Summary (09/21/25)

### This week I worked on:

Researching which Python web framework to use. I have decided on using FastAPI for the front end component of my project. I also decided on using SQLite for the database but I plan on using SQALchemy to allow me to seemlessy switch to a more performant database if it becomes necessary in the future. FsatAPI has a builtin task scheduler that I wil use for the monitoring checks. If that turns out to not scale well enough then I will swap it out for something like Celery + Redis.

### This week I learned:

I learned about the different web frameworks available in python such as FastAPI, Flask, Django, but I ultimately decided to go with FastAPI because I would like to learn how to use it and it seems to scale well. I also learned about some other db options outside of SQlite which I have used before.

### My successes this week were:

Deciding which python libraries I am going to use.

### The challenges I faced this week were:

Narrowing down my options and trying to keep my requirements simple.

---

## Week 2 Summary (09/28/2025)
### This week I worked on:

- Installing Ubuntu server on a computer
- Updating and installing required programs including git, and python
- Set up SSH keys and configured some security configurations to keep server secure
- Experimented with some python packages for SNMP

### This week I learned:

- How to install ubuntu server on an computer with a different OS
- How to configure SSH keys
- How to set up SSH key for GitHub login

### My successes this week were:

- Got Ubuntu server running on a computer
- Configured SSH keys

### The challenges I faced this week were:
- Ran into a version issue where the cryptography library in Python would not build with a certain version, and it took a while to get to the bottom of it

---

## Week 3 Summary (10/05/2025)
### This week I worked on:

Learning the pysnmp library.

### This week I learned:

More about how to get specific OIDs from devices using different versions of SNMP(v2c and v3).

### My successes this week were:

I was able to successfully get SNMP info from several different devices using the pysnmp library.

### The challenges I faced this week were:

I ran into some issues with using the correct OID format but I was able to figure it out with some more research.

---

## Week 4 Summary (10/12/2025)
### This week I worked on:

Creating a database design

### This week I learned:

How to use the SQLAlchemy Python library to create a database instead of something like sqlite3.

### My successes this week were:

I have a good idea of the information I need to store in my database

### The challenges I faced this week were:

Relearning some SQL, as it has been a while since I worked with databases

---

## Week 5 Summary (10/19/2025)
### This week I worked on:
Experimented with using BitWarden as a way to store and retrieve credentials, along with the benefit of including MFA.

### This week I learned:
How to use the BitWarden API and CLI tool.

### My successes this week were:
Was able to install and log in to the tool.

### The challenges I faced this week were:
For some reason the cli tool was not returning a session key when I log in so I was not able to retrieve the credentials I need from BitWarden. I think I will have to take another approach for now since I can't get this working.

---

## Week 6 Summary (10/26/2026)
### This week I worked on:

Designing and creating the db.

### This week I learned:

How to set up a db using SQLAlchemy. How to make db diagrams in Visio.

### My successes this week were:

Created the db and inserted some test data into it. Created a design document for the different objects I need to store.

### The challenges I faced this week were:

I was trying to decide whether to use some type-checking libraries to help make my code cleaner, but it ended up becoming too confusing right now. I will probably revisit it if I have time near the end of the project. For now, it's not necessary.

---

## Week 7 Summary (11/02/20)
### This week I worked on:

I began implementing the home page of my website.

### This week I learned:

How to create a basic webpage with fastapi.

### My successes this week were:

I was able to successfully create a home page for my app and began implementing some basic functions.

### The challenges I faced this week were:

I was having some issues with the file structure of my project but was able to get it fixed after some troubleshooting

---

## Week 8 Summary (11/09/2026)
### This week I worked on:

Creating the SNMP template function of my app to store SNMP credentials and settings.

### This week I learned:

The different inputs that SNMPv2c and v3 require for authentication.

### My successes this week were:

I was able to create a new webpage for configuring the SNMP templates.

### The challenges I faced this week were:

I had to learn a little bit of Javascript to create the desired effect in some of my menus.

---

## Week 9 Summary (11/16/2025)
### This week I worked on:

Creating the devices and device management page. There is now a page to add, remove and modify devices. The home page also dispalys a list of all devices now.

### This week I learned:

How to configure html forms and fastapi to get input from users and then store it in my db.

### My successes this week were:

Created the device and device management page and udpated the database.

### The challenges I faced this week were:

I am not very knowledable on webdev so I had to learn a few things about html and specifically forms to be able to get user input working right.

---

## Week 10 Summary (11/30/2025)
### This week I worked on:

Refactoring my existing SNMP code to allow for different authentication with different version and settings of SNMP. Also added functionality to select SNMP login template when adding a device and the app will automatically reach out to the device and gather some basic info from it.

### This week I learned:

More about the pysnmp library and the different types of authentication supported.

### My successes this week were:

I was able to get my code working to allow SNMPv2c and SNMPv3 authentication to switches. 

### The challenges I faced this week were:

I had a lot of issues trying to understand the pysnmp library since I am using the async version for my SNMP code. Eventually I was able to find which parts of the library I needed to import and got things working.

---

## Week 11 Summary (12/02/2025)
### This week I worked on:

[Your answer here]

### This week I learned:

[Your answer here]

### My successes this week were:

[Your answer here]

### The challenges I faced this week were:

[Your answer here]

---

## Week 12 Summary (MM/DD/YYYY)
### This week I worked on:

[Your answer here]

### This week I learned:

[Your answer here]

### My successes this week were:

[Your answer here]

### The challenges I faced this week were:

[Your answer here]

---

## Week 13 Summary (MM/DD/YYYY)
### This week I worked on:

[Your answer here]

### This week I learned:

[Your answer here]

### My successes this week were:

[Your answer here]

### The challenges I faced this week were:

[Your answer here]

---
