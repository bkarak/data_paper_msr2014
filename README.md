The Bug Catalog of the Maven Ecosystem (v2012)
==============================================

Maven is a build automation tool used primarily for Java projects and it is
hosted by the [Apache Software Foundation](http://maven.apache.org)
It uses XML to describe the software project being built, its dependencies
on other external modules, the build order, and required plug-ins.
To build a software component, it dynamically downloads Java libraries
and Maven plug-ins from the Maven central repository,
and stores them in a local cache. The repository can be updated with
new projects and also with new versions of existing projects
that can depend on other versions.

To statically analyze the Maven repository
we used [FindBugs](http://findbugs.sourceforge.net/)
a static analysis tool that examines bytecode to detect software bugs.
Specifically, we ran FindBugs on all the project versions of all
the projects that exist in the repository
to identify all bugs contained in it.

Download
--------

* *Tools*: 

Publications
------------

* Dimitris Mitropoulos, Vassilios Karakoidas, Panos Louridas, Georgios Gousios, and Diomidis Spinellis. Dismal code: Studying the evolution of security bugs. *In Proceedings of the LASER Workshop 2013, Learning from Authoritative Security Experiment Results*, pages 37-48. Usenix Association, October 2013.
* Dimitris Mitropoulos, Vassilios Karakoidas, Panos Louridas, Georgios Gousios, and Diomidis Spinellis. The Bug Catalog of the Maven Ecosystem, MSR 2014.


Contributors
------------

* Dimitrios Mitropoulos
* Vassilios Karakoidas
* Panos Louridas
* Georgios Gousios
* Diomidis Spinellis