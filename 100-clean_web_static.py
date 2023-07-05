#!/usr/bin/python3
""" Fabric script that creates and distributes an archive to your web servers """

from fabric.api import *
import os
from datetime import datetime


env.hosts = ['35.231.33.237', '34.74.155.163']
env.user = 'ubuntu'


def do_pack():
    """ Creates a compressed archive of the web_static folder """
    try:
        if not os.path.exists("versions"):
            local("mkdir versions")
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_path = "versions/web_static_{}.tgz".format(now)
        local("tar -czvf {} web_static".format(archive_path))
        return archive_path
    except:
        return None


def do_deploy(archive_path):
    """ Distributes an archive to your web servers """
    if not os.path.exists(archive_path):
        return False

    try:
        archive_name = os.path.basename(archive_path)
        archive_no_ext = os.path.splitext(archive_name)[0]

        put(archive_path, "/tmp/{}".format(archive_name))
        run("mkdir -p /data/web_static/releases/{}/".format(archive_no_ext))
        run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/"
            .format(archive_name, archive_no_ext))
        run("rm /tmp/{}".format(archive_name))
        run("mv /data/web_static/releases/{}/web_static/* \
            /data/web_static/releases/{}/".format(archive_no_ext, archive_no_ext))
        run("rm -rf /data/web_static/releases/{}/web_static".format(archive_no_ext))
        run("rm -rf /data/web_static/current")
        run("ln -s /data/web_static/releases/{}/ /data/web_static/current"
            .format(archive_no_ext))
        return True
    except:
        return False


def deploy():
    """ Creates and distributes an archive to your web servers """
    archive_path = do_pack()
    if archive_path is None:
        return False
    success = do_deploy(archive_path)
    if success:
        do_clean(2)
    return success


def do_clean(number=0):
    """ Deletes out-of-date archives """
    number = int(number)
    if number < 1:
        number = 1
    with cd("/data/web_static/releases"):
        releases = run("ls -tr").split()
        for release in releases[:-number]:
            if release != "test":
                run("rm -rf {}".format(release))
    with cd("/versions"):
        archives = local("ls -tr").split()
        for archive in archives[:-number]:
            local("rm -f {}".format(archive))