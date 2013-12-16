#!/usr/bin/env python
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
#
# initial script to test findbugs time.
# change the path of the repository accordingly.
#
# Authors:
#    Vassilios Karakoidas (vassilios.karakoidas@gmail.com)
#    Dimitrios Mitropoulos (dimitro@aueb.gr)
#

# configuration variables
MAVEN_REPOSITORY=/Users/dimitro/Software/uk.maven.org/maven2
MAVEN_FULL_JARS=maven-full-jars.text
MAVEN_BINARIES=maven-binaries-jars.text

WORK_DIR=Software

# main script

find $MAVEN_REPOSITORY -type f -name *.jar > $MAVEN_FULL_JARS
cat $MAVEN_FULL_JARS | grep -v sources | grep -v javadoc > $MAVEN_BINARIES

for jfile in `cat $MAVEN_BINARIES`
do
	cd $WORK_DIR
	echo 'Extracting '.$jfile
	jar xvf $jfile	
	cd ..
	echo 'Calculating FindBugs'
	findbugs/bin/findbugs -textui -xml -output `basename $jfile`-findbugs.xml -include security_only_search.xml $jfile
	rm -rf work/*
done
