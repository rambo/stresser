# Selenium stuff

Random selenium related scripts for testing misc things

## Install Selenium & friends

All of this supposes Ubuntu LTS (Trusty).

First Oracle Java, 6 should be ok.

    sudo add-apt-repository ppa:webupd8team/java
    sudo apt-get update
    sudo apt-get install oracle-java6-installer

Then [Google Chrome][chromeppa] (Chromium chromedriver simply does not work)

    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 
    sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    sudo apt-get update
    sudo apt-get install google-chrome-stable

[chromeppa]: http://www.ubuntuupdates.org/ppa/google_chrome
    
Then FF, Xvfb and some python utilities

    sudo apt-get install firefox Xvfb unzip wget python pip
    pip install selenium

Then [chromedriver][chromedriverurl]

    mkdir -p /opt/chromedriver/
    cd /opt/chromedriver/
    wget http://chromedriver.storage.googleapis.com/2.10/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip

[chromedriverurl]: http://chromedriver.storage.googleapis.com/index.html 

And finally Selenium itself

    mkdir -p /opt/selenium/server/
    cd /opt/selenium/server/
    wget http://selenium-release.storage.googleapis.com/2.42/selenium-server-standalone-2.42.2.jar
    ln -s selenium-server-standalone-2.42.2.jar selenium-server-standalone-current.jar


## Start Selenium

Use the start_headless.sh script from the bin/ directory.
