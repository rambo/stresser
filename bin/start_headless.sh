#!/bin/bash -x
/usr/bin/Xvfb :99 -ac -screen 0 1280x1024x8 &
XVFB_PID=$!
export DISPLAY=:99
#java -jar /opt/selenium/server/selenium-server-standalone-current.jar -log ~/selenium.log 
# hub
java -jar /opt/selenium/server/selenium-server-standalone-current.jar -role hub -port 4444 -log ~/seleniumhub.log &
HUB_PID=$!
sleep 5
# node
#java -jar /opt/selenium/server/selenium-server-standalone-current.jar -role node -port 4445 -log ~/seleniumnode.log -hub http://localhost:4444/grid/register -Dwebdriver.chrome.driver=/usr/lib/chromium-browser/chromedriver
# install real chrome via http://www.ubuntuupdates.org/ppa/google_chrome
# Then install chromedriver (prebuilt) from http://chromedriver.storage.googleapis.com/index.html 
java -jar /opt/selenium/server/selenium-server-standalone-current.jar -role node -port 4445 -log ~/seleniumnode.log -hub http://localhost:4444/grid/register -Dwebdriver.chrome.driver=/opt/chromedriver/chromedriver
kill $HUB_PID
wait $HUB_PID
kill $XVFB_PID
wait $XVFB_PID
