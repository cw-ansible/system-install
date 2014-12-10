# System installation

This ansible playbook will install a Debian / Ubuntu system on current
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

Once the server is booted you first need to install ansible's dependencies.

	sudo apt-get install --no-install-recommends \
		rsync git python-jinja2 python-yaml
	

Then you can checkout ansible in `~/Developer/ansible`:

	mkdir -p ~/Developer
	git clone https://github.com/ansible/ansible.git ~/Developer
	cd ~/Developer/ansible
	git submodule init
	git submodule update
	
Then you can setup the ansible environment:

	. ~/Developer/ansible/hacking/env-setup


## Usage


You can install your host using command:

	ansible-playbook chroot.yml -i inventory \
		-e partition=partition-encrypted-tmpfs \
		-e mirror=http://mirrors.online.net/ubuntu


Be careful because all data on your hard drive will be erased. You have been
warned.



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

## Copyright

Author: Sébastien Gross <seb•ɑƬ•chezwam•ɖɵʈ•org>
License: WTFPL, grab your copy here: http://www.wtfpl.net
