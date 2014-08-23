# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "chef/fedora-20"

  config.vm.provision "shell", path: "scripts/yum.sh"
  config.vm.provision "shell", path: "scripts/python.sh", privileged: false
  config.vm.provision "shell",
    inline: "source ~/microauth/bin/activate; python /vagrant/run.py&",
    run: "always", privileged: false
  config.vm.network "forwarded_port", guest: 5000, host: 5000
end
