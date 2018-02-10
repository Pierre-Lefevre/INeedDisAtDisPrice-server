#!/bin/bash

cd ~/INeedDisAtDisPrice-server/scrapies
/usr/local/bin/scrapy crawl cron

cd ~/INeedDisAtDisPrice-server/server/utils
node checkAlerts.js
