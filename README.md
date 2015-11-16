# Selenium stuff

Scripts/helpers to run massively parallel Selenium tests (mostly having the workers doing the same thing instead of separate things, like simulating 
masses of actual real users with real browsers running with full Javascript support)

Pro tip for thos wishing to work on the code <http://guide.python-distribute.org/pip.html#installing-from-a-vcs>


## Install Selenium & friends

All of this supposes Ubuntu LTS (Trusty).

First Oracle Java, 7 should be ok.

    sudo add-apt-repository ppa:webupd8team/java
    sudo apt-get update
    sudo apt-get install oracle-java7-installer oracle-java7-set-default

Then [Google Chrome][chromeppa] (Chromium chromedriver simply does not work)

    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 
    sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    sudo apt-get update
    sudo apt-get install google-chrome-stable

[chromeppa]: http://www.ubuntuupdates.org/ppa/google_chrome
    
Then FF, Xvfb and some python utilities

    sudo apt-get install firefox firefox-locale-en Xvfb unzip wget python python-pip dbus-x11
    pip install selenium

Then [chromedriver][chromedriverurl]

    mkdir -p /opt/chromedriver/
    cd /opt/chromedriver/
    wget http://chromedriver.storage.googleapis.com/2.20/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    chmod a+x -R /opt/chromedriver/

[chromedriverurl]: http://chromedriver.storage.googleapis.com/index.html 

And finally [Selenium][seleniumurl] itself

    mkdir -p /opt/selenium/server/
    cd /opt/selenium/server/
    wget http://selenium-release.storage.googleapis.com/2.48/selenium-server-standalone-2.48.2.jar
    ln -s selenium-server-standalone-2.48.2.jar selenium-server-standalone-current.jar

[seleniumurl]: http://selenium-release.storage.googleapis.com/index.html

## Start Selenium

Use the start_headless.sh script from the bin/ directory as normal user (not root!)

    su selenium -c bin/start_headless.sh selenium

If you get "Unable to connect to host 127.0.0.1 on port 7055 after 45000 ms." Firefox has changed something yet again, downgrade it with

    apt-get install firefox=42.0+build2-0ubuntu0.14.04.1
    apt-mark hold firefox # apt-mark unhold firefox

# ZMQ stuff

Use ZMQ from packages

    sudo apt-get install python-zmq
    toggleglobalsitepackages # If using virtualenv-wrappers

