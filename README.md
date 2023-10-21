# Dank Meme Application

This application allows users to share dank memes with each other. It has many vulnerabilities. Your job is to fix it.

Additional READMEs have been included in subdirectories of this project.

As it is best not to run untrusted or vulnerable code on your host machine, we strongly recommend running this app via
Docker.

Instructions to install Docker can be found on [Docker's website](https://docs.docker.com/get-docker/).

Scripts for running and testing the app via Docker have been provided.

Linux/Mac (recommended):
- ./run-app-docker.sh
- ./test-app.docker.sh

Windows:
- Open a terminal
- Run `docker build . -t appsecchallenge` if you haven't built the container yet.
- Use `.\run-app-docker.bat` to run the application
- Use `.\test-app-docker.bat` to test the application

No efforts have been made to ensure compatibility with operating systems outside the docker container, as again, it's
not recommended to run this outside of the docker container.

## Toubleshooting

### Deleting the DB and uploaded images

In order to delete the DB and uploaded images delete the "instance" subfolder from the project.
If you have failing test cases due to data bleed try deleting this folder.

#### Windows

Windows is not officially supported.

Here are a few things that have helped for those who have tried.

##### syntax error: unexpected end of file #####
If you run into "syntax error: unexpected end of file" when running run-app-docker.bat or test-app-docker.bat the line endings in the file need to ne changed from Windows (CRLF) to Linux (LF).  This is easy to do with Visual Studio Code.

This can occur if you have Git configured to Checkout Windows/Commit Linux


##### Use a Unix based shell rather than cmd or powershell

Using Git Bash rather than cmd has helped, especially since the support scripts are .sh and not .bat.
The Git for Windows installer also installs [Git Bash](https://gitforwindows.org/), so you may already have it on your
computer

##### Run your shell as an administrator

Search for your command (cmd, Git Bash, etc), right click and "Run as administrator"

##### Automated tests

Some test cases give different results in Windows than they do in Linux. Scoring will be done in Linux.

