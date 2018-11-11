#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil


def info(msg):
    print("II: " + msg)


def warning(msg):
    print("WW: " + msg)


def error(msg):
    print("EE: " + msg)


def checkprg(programmtofind, solutionhint):

    # test if an executable can be found by
    # following $PATH
    # raise message if fails and returns 1
    # on success return 0
    # search follows $PATH

    if os.system("which " + programmtofind) == 0:
        info(programmtofind + " found")
    else:
        error(programmtofind + " not found")
        print(solutionhint)


def is_there(find, solutionhint):

    # test if a file or dir can be found at a predefined place
    # raise message if fails and returns 1
    # on success return 0

    if os.path.exists(find):
        info(find + " found")
    else:
        error(find + " not found")
        print(solutionhint)


WORK_DIR = (os.environ['HOME'] + "/map_build/")

config = configparser.ConfigParser()


# create the contourlines


def create_cont():

    os.chdir(WORK_DIR)

    config.read('pygmap3.cfg')

    buildmap = config['runtime']['buildmap']
    path = WORK_DIR + config['runtime']['mkgmap'] + "/mkgmap.jar "

    cl_dir = "gps_ready/zipped/" + buildmap + "/"
    cltemp_dir = "cl_temp/"

    for dir in [cltemp_dir, cl_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    path = cltemp_dir
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            os.remove(os.path.join(path, file))

    print("searching for " + buildmap + "_contourlines_gmapsupp.img.zip")

    if not os.path.exists(cl_dir + buildmap +
                          "_contourlines_gmapsupp.img.zip"):
        hint = "Install phyghtmap to create contourlines if needed"
        checkprg("phyghtmap", hint)

        if not os.path.exists("styles/contourlines_style/lines"):
            error("No contourlines_style found")
            quit()

        if config.has_option('maxnodes', buildmap):
            maxnodes = config['maxnodes'][buildmap]
        else:
            maxnodes = config['maxnodes']['default']

        if config.has_option('runtime', 'ed_user'):
            ed_user_opts = (" --earthexplorer-user=" +
                            config['runtime']['ed_user'])
        else:
            ed_user_opts = " "

        if config.has_option('runtime', 'ed_user'):
            ed_pwd_opts = (" --earthexplorer-password=" +
                           config['runtime']['ed_pwd'])
        else:
            ed_pwd_opts = " "

        # use phyghtmap to get the raw-data from the internet,
        # downloaded files will be stored for later builds

        command_line = ("phyghtmap --source=view1,view3,srtm1,srtm3 " +
                        ed_user_opts +
                        ed_pwd_opts +
                        " --start-node-id=1 " +
                        " --start-way-id=1 " +
                        " --max-nodes-per-tile=" +
                        maxnodes +
                        " --max-nodes-per-way=250 " +
                        " --jobs=4 " +
                        " --o5m " +
                        " --no-zero-contour " +
                        " -s 50 " +
                        " -c 500,100 " +
                        " --polygon=poly/" + buildmap + ".poly " +
                        " -o " + cltemp_dir + buildmap)

        if config.has_option('runtime', 'verbose'):
            print()
            info(command_line)
            print()

        os.system(command_line)

        # Java HEAP, RAM oder Mode

        if config['java']['agh'] == "1":
            heap = " -XX:+AggressiveHeap "
        else:
            heap = (config['java']['xmx'] + " " + config['java']['xms'])

        # contourlines-build with mkgmap

        os.chdir(cltemp_dir)
        info("entered " + os.getcwd())

        command_line = ("java -ea " +
                        heap +
                        " -jar " + path +
                        " --max-jobs " +
                        " --read-config=" +
                        WORK_DIR + "styles/contourlines_style/options" +
                        " --style-file=" +
                        WORK_DIR + "styles/contourlines_style" +
                        " --mapname=" +
                        config['mapid'][buildmap] + "8001" +
                        " --description=" +
                        buildmap + "_contourlines " +
                        " --family-name=Contourlines" +
                        " --draw-priority=" +
                        config['contourlines']['draw-priority'] +
                        " --gmapsupp " +
                        " *.o5m ")

        if config.has_option('runtime', 'verbose'):
            print()
            info(command_line)
            print()

        os.system(command_line)

        import zipfile

        img = buildmap + "_contourlines_gmapsupp.img"
        shutil.move("gmapsupp.img", img)
        zip_img = img + ".zip"
        my_zip_img = zipfile.ZipFile(zip_img, 'w', allowZip64=True)
        my_zip_img.write(img, compress_type=zipfile.ZIP_DEFLATED)
        my_zip_img.close()

        if os.path.exists(zip_img):
            os.remove(img)

        os.chdir(WORK_DIR)
        file = "_contourlines_gmapsupp.img.zip"
        shutil.move(cltemp_dir + buildmap + file, cl_dir + buildmap + file)
