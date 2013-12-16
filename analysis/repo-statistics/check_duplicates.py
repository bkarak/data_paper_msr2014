import json
from helpers.data_helper import ArrayCount, save_to_file
from helpers.mongo_helper import MongoDocumentIterator

__author__ = "Vassilios Karakoidas (vassilios.karakoidas@gmail.com)"


def main():
    versions = []
    dup_versions = ArrayCount()
    miter = MongoDocumentIterator(fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version'])

    print 'Found %d Documents' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        if d is not None:
            group_id = d['JarMetadata']['group_id']
            artifact_id = d['JarMetadata']['artifact_id']
            version = d['JarMetadata']['version']
            ga = '%s||%s||%s' % (group_id, artifact_id, version)

            if ga not in versions:
                versions.append(ga)
            else:
                dup_versions.incr(ga)

            print '[%d:%d:%d]: Processed %s' % (dup_versions.item_count(), len(versions), miter.count(), ga)

    print 'Total documents: %d, dups: %d, versions: %d' % (miter.total(), dup_versions.item_count(), len(versions))
    save_to_file('duplicates.json', json.dumps(dup_versions.get_series()))

if __name__ == "__main__":
    main()

