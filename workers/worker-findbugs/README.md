evol_security_publication_2012 -- Worker
========================================

Instructions
------------

On OSX Mountain Lion
```bash
git clone git@github.com:bkarak/evol_security_publication_2012.git
sudo easy_install pip
sudo pip install pika python-daemon pymongo
cd evol_security_publication_2012
./process.py -a findbugs -b findbags -e findbugs -c 83.212.106.194 -u findbugs -w findbags -x 83.212.106.194 -y findbugs -z findbugs -d
```

On Debian Squeeze (more python pkgs required):
```bash
# As root
apt-get install python-pip git screen openjdk-6-jdk
pip install pika python-daemon pymongo argparse

# As normal user
git clone git@github.com:bkarak/evol_security_publication_2012.git
cd evol_security_publication_2012
./process.py -a findbugs -b findbags -e findbugs -c 83.212.106.194 -u findbugs -w findbags -x 83.212.106.194 -y findbugs -z findbugs -d
```

Connection details
------------------

RabbitMQ connection details
```
host = 83.212.106.194
user = findbugs
passwd = findbags
```

MongoDB connection details
```
host = 83.212.106.194
user = findbugs
passwd = findbags
db = findbugs
```

