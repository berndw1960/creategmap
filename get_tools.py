#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import tarfile
import configparser
import urllib.request
import shutil


WORK_DIR = os.environ['HOME'] + "/map_build/"


def info(msg):
    print("II: " + msg)


config = configparser.ConfigParser()


# config writer
def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


def list_test_version():
    config.read('pygmap3.cfg')
    print()
    for i in ['splitter', 'mkgmap']:
        try:
            target = http.client.HTTPConnection("www.mkgmap.org.uk")
            target.request("GET", "/download/" + i + ".html")
            htmlcontent = target.getresponse()
            data = htmlcontent.read()
            data = data.decode('utf8')
            target.close()
        except http.client.NotConnected:
            print()
            print(" can't connect to " + target)
            print()
            break
        data = re.findall(i + r"\S*.zip", data)
        list_new = []
        for x in data:
            x = os.path.splitext(os.path.basename(x))[0]
            x = x.replace("-src", "")
            x = x.replace(i + "-", "")
            x = re.sub(r"\d+", "", x)
            if x.endswith("-r"):
                x = x[:-2]
            elif x.endswith("r"):
                x = x[:-1]
            if x != '':
                if x not in list_new:
                    list_new.append(x)

        info("Testversions of " + i)
        print()
        if list_new:
            for x in list_new:
                print("    " + x)
        else:
            print("    No test versions found for " + i + "!")
        print()


# get splitter and mkgmap
def get_tools():
    config.read('pygmap3.cfg')

    for i in ['splitter', 'mkgmap']:
        try:
            target = http.client.HTTPConnection("www.mkgmap.org.uk")
            target.request("GET", "/download/" + i + ".html")
            htmlcontent = target.getresponse()
            data = htmlcontent.read()
            data = data.decode('utf8')

            if i == "splitter":
                file = r"-r\d{3}.zip"
            elif i == "mkgmap":
                file = r"-r\d{4}.zip"

            if config.has_option(i, 'test'):
                test = config[i]['test']
                pattern = re.compile(i + "-" + test + file)
            else:
                pattern = re.compile(i + file)

            i_rev_pre = sorted(pattern.findall(data), reverse=True)[0]
            i_rev = os.path.splitext(os.path.basename(i_rev_pre))[0]

            target.close()

        except http.client.NotConnected:
            print()
            print(" can't connect to " + target)
            print()
            break

        if not os.path.exists(i_rev):
            if os.path.isfile(i_rev + ".tar.gz"):
                tar = tarfile.open((i_rev) + ".tar.gz")
                tar.extractall()
                tar.close()
            else:
                url = "http://www.mkgmap.org.uk/download/" + i_rev + ".tar.gz"
                file = i_rev + ".tar.gz"
                print()
                info("download " + url)

                # Download the file from `url` and save it under `file_name`:
                try:
                    uo = urllib.request.urlopen
                    with uo(url) as response, open(file, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)
                except urllib.error.URLError:
                    print()
                    print(" can't download " + file)
                    print()
                    break

                tar = tarfile.open((i_rev) + ".tar.gz")
                tar.extractall()
                tar.close()

        if config.has_option(i, 'test'):
            print()
            info("using " + i_rev)

        config.set(i, 'rev', i_rev)
        write_config()
