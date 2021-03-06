#!/usr/bin/env python
from __future__ import print_function

import sys
import build
import logging
import optparse
import platform

def main():
    # configure parser
    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose', action="count", dest='verbosity', default=1, help='print more information to stdout')
    parser.add_option('-q', '--quiet', action='store_const', const=0, dest='verbosity', help='print less information to stdout')
    (options, args) = parser.parse_args()

    # configure logging
    log = logging.getLogger()
    if options.verbosity >= 2:
        log.setLevel(logging.DEBUG)
    elif options.verbosity == 1:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)

    pld = platform.linux_distribution()[0]
    if pld in ['debian', 'Ubuntu']:
        log.info('Detected: {0}'.format(pld))
        cmd = ['sudo', 'apt-get', 'update', '-y']
        build.run_cmd(cmd, check_rc='getting updates failed')
        # get prerequisites
        cmd = ['sudo','apt-get','install','-y','make','autoconf2.13','texinfo',
               'help2man','g++','git','libtool','python-dev','libbz2-dev','zlib1g-dev',
               'libcurl4-gnutls-dev','libxml2-dev','pkg-config','uuid-dev','libssl-dev','lsb-release']
        if pld in ['Ubuntu'] and platform.linux_distribution()[1] < '14':
            cmd.extend(['ruby1.9.1','ruby1.9.1-dev',])
        else:
            cmd.extend(['ruby','ruby-dev',])
        build.run_cmd(cmd, check_rc='installing prerequisites failed')
        # if old, bootstrap g++
        if pld in ['Ubuntu'] and platform.linux_distribution()[1] < '14':
            # ubuntu12 ships with g++ 4.6 - needs 4.8+ to build clang
            log.info('Detected: Old Ubuntu - need to get g++ 4.8 to build clang')
            cmd = ['sudo','apt-get','install','-y','python-software-properties']
            build.run_cmd(cmd, check_rc='installing add-apt-repository prereq failed')
            cmd = ['sudo', 'add-apt-repository', '-y', 'ppa:ubuntu-toolchain-r/test']
            build.run_cmd(cmd, check_rc='installing ppa failed')
            cmd = ['sudo', 'apt-get', 'update', '-y']
            build.run_cmd(cmd, check_rc='getting updates failed')
            cmd = ['sudo', 'apt-get', 'install', '-y', 'g++-4.8']
            build.run_cmd(cmd, check_rc='installing g++-4.8 failed')
            cmd = ['sudo', 'update-alternatives', '--install', '/usr/bin/g++', 'g++', '/usr/bin/g++-4.8', '50']
            build.run_cmd(cmd, check_rc='swapping g++-4.8 failed')
            cmd = ['sudo', 'update-alternatives', '--install', '/usr/bin/gcc', 'gcc', '/usr/bin/gcc-4.8', '50']
            build.run_cmd(cmd, check_rc='swapping gcc-4.8 failed')
        # if new, get autoconf
        if pld in ['Ubuntu'] and platform.linux_distribution()[1] > '16':
            log.info('Detected: Ubuntu 16+ - need to get autoconf')
            cmd = ['sudo','apt-get','install','-y','autoconf']
            build.run_cmd(cmd, check_rc='installing autoconf failed')
        # get necessary ruby gems
        cmd = ['sudo','gem','install','-v','1.8.1','ffi']
        build.run_cmd(cmd, check_rc='installing ffi failed')
        cmd = ['sudo','gem','install','-v','1.8.5','json']
        build.run_cmd(cmd, check_rc='installing json failed')
        cmd = ['sudo','gem','install','-v','1.4.0','fpm']
        build.run_cmd(cmd, check_rc='installing fpm failed')

    elif pld in ['CentOS', 'CentOS Linux', 'Red Hat Enterprise Linux Server', 'Scientific Linux']:
        log.info('Detected: {0}'.format(pld))
        # prep
        cmd = ['sudo','yum','clean','all']
        build.run_cmd(cmd, check_rc='yum clean failed')
        cmd = ['sudo','yum','update','-y','glibc*','yum*','rpm*','python*']
        build.run_cmd(cmd, check_rc='yum update failed')
        # get prerequisites
        cmd = ['sudo','yum','install','-y','epel-release','wget','openssl','ca-certificates']
        build.run_cmd(cmd, check_rc='installing epel failed')
        cmd = ['sudo','yum','install','-y','gcc-c++','git','autoconf','automake','texinfo',
               'help2man','rpm-build','rubygems','ruby-devel','python-devel','zlib-devel',
               'bzip2-devel','libcurl-devel','libxml2-devel','libtool','libuuid-devel','openssl-devel']
        build.run_cmd(cmd, check_rc='installing prerequisites failed')
        # get necessary ruby gems
        cmd = ['sudo','gem','install','-v','1.8.1','ffi']
        build.run_cmd(cmd, check_rc='installing ffi failed')
        cmd = ['sudo','gem','install','-v','1.8.5','json']
        build.run_cmd(cmd, check_rc='installing json failed')
        cmd = ['sudo','gem','install','-v','1.4.0','fpm']
        build.run_cmd(cmd, check_rc='installing fpm failed')
        # if old, bootstrap g++
        if platform.linux_distribution()[1] < '7':
            # centos6 ships with g++ 4.4 - needs 4.8+ to build clang
            log.info('Detected: Old {0} - need to get g++ 4.8 to build clang'.format(pld))
            cmd = ['sudo','yum','install','-y','centos-release-scl']
            build.run_cmd(cmd, check_rc='install centos-release-scl failed')
            cmd = ['sudo','yum','install','-y','devtoolset-6']
            build.run_cmd(cmd, check_rc='install devtoolset-6 failed')
            print('========= set environment to use the new g++ ========= ')
            print('export CC=/opt/rh/devtoolset-6/root/usr/bin/gcc')
            print('export CXX=/opt/rh/devtoolset-6/root/usr/bin/g++')
    elif pld in ['openSUSE ', 'SUSE Linux Enterprise Server']:
        log.info('Detected: {0}'.format(pld))
        # get prerequisites
        cmd = ['sudo','zypper','install','-y','ruby-devel','makeinfo','rubygems','libopenssl-devel',
               'help2man','python-devel','libbz2-devel','libcurl-devel','libxml2-devel','uuid-devel']
        build.run_cmd(cmd, check_rc='installing prerequisites failed')
        # get necessary ruby gems
        cmd = ['sudo','gem','install','-v','1.8.1','ffi']
        build.run_cmd(cmd, check_rc='installing ffi failed')
        cmd = ['sudo','gem','install','-v','1.8.5','json']
        build.run_cmd(cmd, check_rc='installing json failed')
        cmd = ['sudo','gem','install','-v','1.4.0','fpm']
        build.run_cmd(cmd, check_rc='installing fpm failed')
    else:
        if platform.mac_ver()[0] != '':
            log.info('Detected: {0}'.format(platform.mac_ver()[0]))
            # get prerequisites
            cmd = ['brew','install','git','help2man','texinfo','libtool']
            build.run_cmd(cmd, check_rc='installing prerequisites failed')
            cmd = ['brew','link','texinfo','--force']
            build.run_cmd(cmd, check_rc='linking texinfo failed')
        else:
            log.error('Cannot determine prerequisites for platform [{0}]'.format(pld))
            return 1

if __name__ == '__main__':
    sys.exit(main())
