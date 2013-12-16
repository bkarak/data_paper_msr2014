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

""" Read URLs from an AMQP queue, download referenced JAR, process it with
Findbugs, store the results to a MongoDB collection.

"""
import json, pika, sys, os, logging, pymongo, time, urllib

from subprocess import Popen, PIPE, STDOUT
from threading import Thread

__author__ = 'Georgios Gousios <gousiosg@gmail.com>, Vassilios Karakoidas (vassilios.karakoidas@gmail.com), Dimitrios Mitropoulos (dimitro@aueb.gr)'


RETRY_ATTEMPTS = 3

#format=('%(asctime)s %(levelname)s %(name)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format=format)
log = logging.getLogger("process")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)
fh = logging.FileHandler('run.log', mode='a')
log.addHandler(fh)

class RunFindbugs:
    options = None
    clienttags = []
    chan = None
    conn = None
    closing = False
    amqp_node = None
    retries = 0
    db = None
    msgs = 0
    msgs_acked = 0
    msgs_rejected = 0

    def __init__(self, opts):
        self.options = opts
        self.amqp_nodes = self.options.queue_hosts.split(",")
        self.amqp_node = self.amqp_nodes.pop(0)
        self.connect()

    def connect(self):
        """
        Connects to an AMQP host. The same argument defines whether the host
        to connect to will be the same as the one used before or whether
        a new host from the host list will be tried.
        """
        self._connect_to()

    def _connect_to(self):
        """
        Connects to an AMQP host.
        """
        self.retries += 1
        if self.retries > 10:
            log.error("Failed 10 attempts to connect to RabbitMQ")
            return

        log.info("Trying to connect to %s", self.amqp_node)
        credentials = pika.PlainCredentials(self.options.queue_uname,
                                            self.options.queue_passwd)
        params = pika.ConnectionParameters(host=self.amqp_node,
                                           credentials=credentials,
                                           virtual_host="/")
        try:
            conn = pika.SelectConnection(parameters=params,
                                         on_open_callback=self.on_connected)
            self.retries = 0
            conn.ioloop.start()
        except StatsException:
            self.stats()
            return self._connect_to()
        except SystemExit:
            log.info("System exit caught, exiting")
            self.closing = True
            conn.close()
        except Exception:
            log.exception("Could not connect to AMQP node %s" % self.amqp_node)
            if not conn is None and conn.is_open:
                conn.close()
            self._connect_to()

    def on_connected(self, connection):
        """
        Called when a connection has been succesfully opened. Attempts to
        open a channel.
        """
        self.conn = connection
        self.conn.channel(self.on_channel_open)
        self.conn.add_on_close_callback(self.on_closed)
        log.info("Connection open, opening channel")

    def on_closed(self, frame):
        """
        Called when a connection has been closed, either because the program
        has been shut down or because of an error. In the second case, it
        will retry to connect to the same host for a configurable number of
        times and will then fallback to the remaining AMQP nodes.
        """
        if self.closing:
            log.info("Connection to AMQP closed")
            self.conn.ioloop.stop()
            return

        log.warn("Connection closed unexpectedly, attempting reconnect")
        self.conn = None
        attempts = 0
        while self.conn == None:
            if attemts == RETRY_ATTEMPTS:
                log.warn("Failed all %d attempts to connect to %s, trying with remaining nodes" % (RETRY_ATTEMPTS, self.current_amqp_node))
                self.connect(False)
                attempts = 0
                continue

            try:
                attempts += 1
                self.connect(True)
            except Exception, e:
                retry = attempts * RETRY_ATTEMPTS
                log.warn("Cannot connect to %s after %d attempts, retrying after %d sec" % (self.current_amqp_node, attempts, retry))
                time.sleep(retry)

    def on_channel_open(self, channel_):
        """
        Called when a channel has been opened.
        """

        self.chan = channel_

        log.info("Setting message prefetch count to 1")
        self.chan.basic_qos(prefetch_count=1)

        log.info("Channel opened, declaring exchanges and queues")
        self.chan.exchange_declare(exchange=self.options.queue_exchange, exchange_type="topic", durable=True, auto_delete=False)
        # Declare a queue
        self.chan.queue_declare(queue="urls", durable=True, exclusive=False, auto_delete=False, callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        log.info("Queue declared")
        self.chan.queue_bind(callback=self.on_queue_bound, queue='urls', exchange=self.options.queue_exchange, routing_key="url.#")

    def on_queue_bound(self, frame):
        log.info("Binding %s(%s) to queue %s with handler %s", self.options.queue_exchange, "urls" , "urls", "run_findbugs")
        self.chan.basic_consume(self.run_findbugs, queue='urls')

    def run_findbugs(self, channel, method, header, body):
        import zipfile

        def has_classes(filename):
            try:
                if zipfile.is_zipfile(filename):
                    z = zipfile.ZipFile(filename)

                    for f in z.namelist():
                        if f.endswith('.class'):
                            log.info('%s (jar) contains .class files!' % (filename,))
                            return True
                else:
                    log.warn('%s is not a JAR file!' % (filename,))

                return False
            except Exception, e:
                log.error('Invalid JAR File: %s (%s)' % (filename, e))
                return False
    
        def get_jar_size(filename):
            size = 0
            if zipfile.is_zipfile(filename):
                try:
                    z = zipfile.ZipFile(filename)
                    for info in z.infolist():
                        if info.filename.endswith('.class'):
                            size += info.file_size

                    return size
                except Exception, e:
                    log.error('get_jar_size(): %s' % (e,))
                    return 0
            else:
                log.warn('%s is not a JAR file!' % (filename,))
                return 0

        def get_metadata_from_url(url):
            url_arr = url.split('/')
            # -1: jar, -2: version, -3: artifact_id, remaining up to /maven2 -> groupId

            metadata = {'jar_filename':url_arr[-1],
                        'version':url_arr[-2],
                        'artifact_id':url_arr[-3],
                        'group_id':reduce(lambda acc, x: acc + "." + x, url_arr[4:-3], "")[1:]}

            return metadata

        try:
            body = body.strip()
            metadata = get_metadata_from_url(body)
            jar_file = metadata['jar_filename']
            findbugs_output = "%s.xml" % (jar_file,)

            # See if result already in DB
            if self.record_exists(metadata):
                channel.basic_ack(method.delivery_tag)
                return

            # Download jar
            if not os.path.exists(jar_file):
                log.info("Downloading URL %s to file %s", body, jar_file)
                urllib.urlretrieve(body, jar_file)

            if has_classes(jar_file):
                # Exec findbugs
                cmd = '%s -textui -xml -output %s %s' % (os.path.join(os.path.curdir, "findbugs", "bin", "findbugs"), findbugs_output, jar_file)
                log.info("Cmd line: %s" % (cmd,))
                ret = os.system(cmd)

                # Read output
                findbugs_xml = open(findbugs_output, "r").read()

                # Convert to JSON
                ## XXX: convert xml to json and store it to mongo
                def __convert_findbugs_xml(url, findbugs_xml):
                    import xmldict, json

                    result_json = json.loads(json.dumps(xmldict.parse(findbugs_xml)).replace('"@','"'))
                    url_arr = get_metadata_from_url(url)

                    # -1: jar, -2: version, -3: artifact_id, -4: group_id
                    _jar_filename = metadata['jar_filename']
                    _version = metadata['version']
                    _artifact_id = metadata['artifact_id']
                    _group_id = metadata['group_id']

                    # get pom information
                    _pom_url = url.replace('.jar', '.pom')
                    _pom_filename = _jar_filename.replace('.jar', '.pom')

                    log.info('Downloading POM: %s -> %s' % (_pom_url, _pom_filename))                    
                    urllib.urlretrieve(_pom_url, _pom_filename)
                    _dependencies = []

                    if os.path.exists(_pom_filename):
                        try:
                            _pom_json = json.loads(json.dumps(xmldict.parse(open(_pom_filename, 'r').read())))
                            _dependencies = _pom_json.get('project', {}).get('dependencies', {}).get('dependency', [])
                        except Exception, e:
                            log.warn('Could not download/parse data from %s' % (_pom_filename,))

                        os.remove(_pom_filename)

                    # get xml information                    
                    _metadata_url = url.replace('%s/%s' % (_version, _jar_filename), 'maven-metadata.xml')
                    _metadata_filename = '%s-metadata.xml' % (_jar_filename,)
                    
                    log.info('Downloading %s -> %s' % (_metadata_url, _metadata_filename))
                    urllib.urlretrieve(_metadata_url, _metadata_filename)
                    _version_order = 0

                    if os.path.exists(_metadata_filename):
                        try:
                            _metadata_json = json.loads(json.dumps(xmldict.parse(open(_metadata_filename, 'r').read())))
                            _versions = _metadata_json.get('metadata', {}).get('versioning', {}).get('versions', {}).get('version', [])

                            if not isinstance(_versions, list):
                                _versions = [_versions]

                            _versions = [x.strip() for x in _versions]                            
                            try:
                                _version_order = _versions.index(_version.strip()) + 1
                            except ValueError, ve:
                                log.warn('Could not find version (%s in %s): %s' % (_version, _versions, ve))
                        except Exception, e:
                            log.warn('Could not parse data from %s: %s' % (_metadata_filename, e))

                        os.remove(_metadata_filename)

                    _jar_date = os.stat(jar_file).st_mtime
                    _jar_size = get_jar_size(jar_file)
                    result_json['JarMetadata'] = {'jar_filename':_jar_filename,
                                                  'jar_last_modification_date':_jar_date,
                                                  'jar_size':_jar_size,
                                                  'version':_version,
                                                  'version_list':_versions,
                                                  'artifact_id':_artifact_id,
                                                  'group_id':_group_id,
                                                  'version_order' :_version_order,
                                                  'dependencies':_dependencies}

                    return result_json

                # Save it
                if not self.record_exists(metadata):
                    self.store_to_mongo(__convert_findbugs_xml(body, findbugs_xml))
                    channel.basic_ack(method.delivery_tag)                    
            else:
                log.warn('%s contains no .class files' % (jar_file,))
                channel.basic_reject(method.delivery_tag)

            self.msgs_acked += 1
        except Exception as e:
            log.exception("Unexpected error: %s,  msg: %s" % (e, body))
            channel.basic_reject(method.delivery_tag)
            self.msgs_rejected += 1
        finally:
            # The following is supposed to be the "Pythonic" way of doing file deletions!
            # http://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
            try:
                if os.path.exists(jar_file):
                    os.remove(jar_file)
                if os.path.exists(findbugs_output):
                    os.remove(findbugs_output)
            except OSError, ose:
                log.error('Could not delete: %s' % (ose,))

    def get_collection(self):
        if self.db is None:
            self.get_mongo_db()
            if self.db is None:
                log.error("Cannot connect to MongoDB")

        coll = self.db[self.options.mongo_collection]

        return coll

    def store_to_mongo(self, json):
        try:
            id = self.get_collection().insert(json)
            log.debug("Stored with ID: " + str(id))
        except pymongo.errors.AutoReconnect, ae:
            log.warning('Mongo Connection is Down. Reconnecting! (store_to_mongo, %s)' % (ae,))
            self.store_to_mongo(json)

    def record_exists(self, metadata):
        try:
            q = {'JarMetadata.group_id' : metadata['group_id'],
                 'JarMetadata.artifact_id' : metadata['artifact_id'],
                 'JarMetadata.version' : metadata['version']}
            
            if self.get_collection().find(q, timeout=False).count() <= 0:              
                log.info('Record does not exist ... continuing! (%s-%s-%s)' % (metadata['group_id'], metadata['artifact_id'], metadata['version']))
                return False
            else:
                log.warn('Record exists ... skipping! (%s-%s-%s)' % (metadata['group_id'], metadata['artifact_id'], metadata['version']))
                return True
        except pymongo.errors.AutoReconnect, ae:
            log.warning('Mongo Connection is Down. Reconnecting! (record_exists, %s)' % (ae,))
            return self.record_exists(metadata)

    def get_mongo_db(self):
        """
        Gets a connection to MongoDB
        """
        conn = pymongo.Connection(host=self.options.mongo_host, max_pool_size=10, network_timeout=1)
        mongo_db = conn[self.options.mongo_db]
        mongo_db.authenticate(self.options.mongo_uname, self.options.mongo_passwd)
        self.db = mongo_db

    def stats(self):
        """
        Prints msg consumption statistics
        """
        log.info("Msgs acked: %d" % self.msgs_acked)
        log.info("Msgs rejected: %d" % self.msgs_rejected)


class StatsException():
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def parse_arguments(args):
    from argparse import ArgumentParser

    default_pid_file = os.path.join("var", "run", "process", "process.pid")

    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", default=False, dest="debug", help="Enable debug mode")
    parser.add_argument("-P", "--workers", default=1, dest="workers", help="Workers to spawn", type=int)

    # Queue connection info
    parser.add_argument("-a", "--queue-username", required=True, default="", dest="queue_uname", help="Username to connect to the queue")
    parser.add_argument("-b", "--queue-password", required=True, default="", dest="queue_passwd", help="Password to connect to the queue")
    parser.add_argument("-c", "--queue-hosts", required=True, default="127.0.0.1", dest="queue_hosts", help="Comma separated list of hosts running AMQP")
    parser.add_argument("-e", "--queue-exchange", required=True, default="", dest="queue_exchange", help="Exchange name to bind to")

    # MongoDB connection info
    parser.add_argument("-u", "--mongo-username", required=True, default="", dest="mongo_uname", help="Username to connect to MongoDB")
    parser.add_argument("-w", "--mongo-passwd", required=True, default="", dest="mongo_passwd", help="Password to connect to MongoDB")
    parser.add_argument("-x", "--mongo-host", required=True, default="127.0.0.1", dest="mongo_host", help="Host running MongoDB")
    parser.add_argument("-y", "--mongo-database", required=True, default="", dest="mongo_db", help="Database to use for storing messages")
    parser.add_argument("-z", "--mongo-collection", required=True, default="", dest="mongo_collection", help="Collection to use for storing messages")

    return parser.parse_args(args)


def debug(opts):
    RunFindbugs(opts)

def spawn_workers(opts):
    log.info("Spawning %s workers" % opts.workers)
    i = 0

    while i < opts.workers:
        Thread(target=RunFindbugs, args=[opts])
        RunFindbugs(opts)
        i += 1

def main():
    opts = parse_arguments(sys.argv[1:])

    # Debug mode, process messages without going to the background
    if opts.debug:
        debug(opts)        

    # Catch every exception, make sure it gets logged properly
    try:
        spawn_workers(opts)
        return 1
    except Exception:
        log.exception("Unknown error")
        return 0

if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
