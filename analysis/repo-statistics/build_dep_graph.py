import json

from helpers.mongo_helper import MongoDocumentIterator
from helpers.data_helper import save_to_file

#
# This script generates the "data/project_versions.json", which is a json dict (object)
# with the following structure {<group_id>||<artifact_id> : version_count}
#

__author__ = "Vassilios Karakoidas (vassilios.karakoidas@gmail.com)"

def main():
    results = {}
    miter = MongoDocumentIterator(fields=['JarMetadata'])

    print 'Found %d Documents' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        try:
            if d is not None:
                print 'Working %d of %d' % (miter.count(), miter.total(),)
                node_key = '%s||%s||%s' % (d['JarMetadata']['group_id'], d['JarMetadata']['artifact_id'], d['JarMetadata']['version'])
                deps = []

                for dep in d.get('JarMetadata', {}).get('dependencies', {}):
                    if isinstance(dep, dict):
                        dep_group_id = dep.get('groupId', None)
                        dep_artifact_id = dep.get('artifactId', None)
                        dep_version = dep.get('version', None)

                        if dep_group_id is None or dep_artifact_id is None:
                            continue

                        if dep_version is None:
                            deps.append('%s||%s' % (dep_group_id, dep_artifact_id))
                        else:
                            deps.append('%s||%s||%s' % (dep_group_id, dep_artifact_id, dep_version))

                results[node_key] = {'dependencies ' : deps, 'timestamp' : d['JarMetadata'].get('jar_last_modification_date', 0), 'version_order' : d['JarMetadata']['version_order']}
        except Exception, e:
            print d

    save_to_file('project_graph.json', json.dumps(results))


if __name__ == "__main__":
    main()
