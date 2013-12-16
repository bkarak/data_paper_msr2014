import json

from helpers.mongo_helper import MongoDocumentIterator
from helpers.data_helper import ArrayCount, save_to_file

#
# This script generates the "data/project_versions.json", which is a json dict (object)
# with the following structure {<group_id>||<artifact_id> : version_count}
#

__author__ = "Vassilios Karakoidas (vassilios.karakoidas@gmail.com)"

def main():
    results = ArrayCount()
    miter = MongoDocumentIterator(fields=['JarMetadata.group_id', 'JarMetadata.artifact_id'])

    print 'Found %d Documents' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        if d is not None:
            group_id = d['JarMetadata']['group_id']
            artifact_id = d['JarMetadata']['artifact_id']
            ga = '%s||%s' % (group_id, artifact_id)
            results.incr(ga)
            print 'Working %d of %d' % (miter.count(), miter.total(),)

    save_to_file('project_versions.json', json.dumps(results.get_series()))


if __name__ == "__main__":
    main()
