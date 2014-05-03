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
* *Dataset*: The raw dump of our [MongoDB](http://www.mongodb.org/) database can be downloaded from [here](http://istlab.dmst.aueb.gr/~bkarak/findbugs.tar.bz2). To restore it, you can use the *mongorestore* utility, which is shipped with a typical MongoDB installation package.
* *Tools*: There is a number of tools and libraries, which were developed to process the data collected and produce the published results. Inside the [analysis](https://github.com/bkarak/data_paper_msr2014/tree/master/analysis) directory there are numerous python, R and ruby scripts with examples how to process the data.


Publications
------------

* Dimitris Mitropoulos, Vassilios Karakoidas, Panos Louridas, Georgios Gousios, and Diomidis Spinellis. The bug catalog of the Maven ecosystem. *In MSR '14: Proceedings of the 2014 International Working Conference on Mining Software Repositories*. ACM, 2014
* Dimitris Mitropoulos, Vassilios Karakoidas, Panos Louridas, Georgios Gousios, and Diomidis Spinellis. Dismal code: Studying the evolution of security bugs. *In Proceedings of the LASER Workshop 2013, Learning from Authoritative Security Experiment Results*, pages 37-48. Usenix Association, October 2013. (See also the corresponding [Github repository](https://github.com/bkarak/evol_security_publication_2012))


Contributors
------------

[Dimitrios Mitropoulos](http://istlab.dmst.aueb.gr/content/members/m_dimitro.html), [Vassilios Karakoidas](http://bkarak.wizhut.com/),
[Panos Louridas](http://istlab.dmst.aueb.gr/content/members/m_louridas.html),[Georgios Gousios](http://www.gousios.gr/), [Diomidis Spinellis](http://www.dmst.aueb.gr/dds)
