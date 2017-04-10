[![Tweet this](http://img.shields.io/badge/%20-Tweet-00aced.svg)](https://twitter.com/intent/tweet?text=Easy%20install%20of%20@Debian%20and%20@Ubuntu%20on%20servers%20using%20%23ansible&tw_p=tweetbutton&via=renard_0)
[![Follow me on twitter](http://img.shields.io/badge/Twitter-Follow-00aced.svg)](https://twitter.com/intent/follow?region=follow_link&screen_name=renard_0&tw_p=followbutton)


# System installation


This Ansible playbook will install a Debian / Ubuntu system on current
server.

## Prerequisite

You will need to boot your server using a live CD or use a PXE boot that let
your hard drive unused.

You can find live images on following sites:

- https://www.debian.org/CD/live/
- http://www.ubuntu.com/download/desktop

If you are using Private Server hosting you should reboot the server in
rescue mode. This might also work with some Virtual Private Server
provider. Please check your provider support.


### Ansible setup

With Ubuntu, you need to add Universe section in `/etc/apt/sources.list`:

	sudo apt-add-repository "deb http://archive.ubuntu.com/ubuntu/ yakkety universe"
	sudo apt-add-repository "deb http://archive.ubuntu.com/ubuntu/ yakkety-security universe"
	sudo apt-add-repository "deb http://archive.ubuntu.com/ubuntu/ yakkety-updates universe"

Once the server is booted you first need to install ansible's dependencies:

	sudo apt-get install --no-install-recommends \
		rsync git python-jinja2 python-yaml python-paramiko	

Then you can checkout ansible in `~/Developer/ansible`:

	mkdir -p ~/Developer/ansible
	git clone --recurse-submodules https://github.com/ansible/ansible.git ~/Developer/ansible -b stable-2.2

Then you can setup the ansible environment:

	. ~/Developer/ansible/hacking/env-setup


## Usage


You can install your host using command:

	ansible-playbook chroot.yml -i inventory \
		-e mirror=http://ftp2.fr.debian.org/debian \
		-e distrib=jessie

Be careful because all data on your hard drive will be erased. You have been
warned.

If your hard drive has a preexisting swap partition, your live CD might actually be using it, so turn it off:

	swapoff -a

If your hard drive has no partition label you may get an error such as:

    Created data directory /tmp/fai
    Starting setup-storage 1.5
    Command had non-zero exit code

Simply create a partition layout using `parted` (change `/dev/sda` with your
hard drive configuration):

	parted /dev/sda -s mklabel gpt


## Role Description

The install process runs in 2 parts:

- install `debootstrap` and fix its scripts for recent distributions such as
  `trusty` or `jessie`.
- run `system_install` module.
- Fix `ssh` configuration to allow `root` login (`PermitRootLogin` is set to `yes`).
- Update `grub` configuration to be more verbose.



### Configuration

To see all options for `system_install`, run:

	ansible-doc -M library system_install


### System install

The process runs from thoses scripts

#### action_plugins/system_install.py

This script is responsible to deploy all requirements on target host (in
term of Ansible's definition) such as:

- The `system_install` module
- `setup-storage` used to partition hard drive (if needed).
- specific partition layouts, relative to `files` directory (if needed).

#### library/system_install

This is the module file run on target host. It runs:

- disk partition (if needed)
- debootstrap in directory defined in `path` module parameter.
- Install extra packages as defined in `extra_packages` parameter.
- Install kernel if `kernel` parameter is defined.
- setup root password as of `root_password` parameter.
- make sure required files are presents such as:
  - `/etc/fstab`
  - `/etc/network/interfaces` (setup for DHCP configuration)


## Extra

If you want to create an image of you newly installed system for future
usage, you can run the following command as root:


	tar --anchored --preserve-permissions --numeric-owner \
		--xattrs --xattrs-include '*' --selinux --acls \
		--one-file-system --exclude '/tmp/*' \
		-czvf /tmp/`lsb_release -si`-`lsb_release -sc`-`uname -p`.tgz /

The archive is not minimalistic but is a good start. If you want to create
more optimized images for PXE usage have a look at
[cw.ramdisk](https://github.com/cw-ansible/cw.ramdisk)

## Copyright

Author: Sébastien Gross `<seb•ɑƬ•chezwam•ɖɵʈ•org>` [@renard_0](https://twitter.com/renard_0)

License: WTFPL, grab your copy here: http://www.wtfpl.net
