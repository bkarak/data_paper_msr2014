import json

from helpers.data_helper import save_to_file
from helpers.mongo_helper import MongoDocumentIterator


def main():
    project_list = []

    miter = MongoDocumentIterator(query={'BugCollection.BugInstance.category':'SECURITY'},fields=['JarMetadata.group_id', 'JarMetadata.artifact_id'])

    print 'Found %d documents with SECURITY bugs' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        if d is not None:
            print '%d of %d (security)' % (miter.count(), miter.total())
            group_id = d.get('JarMetadata', {}).get('group_id', 'NotSet')
            artifact_id = d.get('JarMetadata', {}).get('artifact_id', 'NotSet')
            project_key = '%s||%s' % (group_id, artifact_id)

            if project_key not in project_list:
                project_list.append(project_key)

    miter = MongoDocumentIterator(query={'BugCollection.BugInstance.category':'MALICIOUS_CODE'},fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version','BugCollection.BugInstance.category', 'BugCollection.BugInstance.type'])

    print 'Found %d documents with MALICIOUS_CODE bugs' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        if d is not None:
            print '%d of %d (malicious_code)' % (miter.count(), miter.total())
            group_id = d.get('JarMetadata', {}).get('group_id', 'NotSet')
            artifact_id = d.get('JarMetadata', {}).get('artifact_id', 'NotSet')
            project_key = '%s||%s' % (group_id, artifact_id)
            if project_key not in project_list:
                project_list.append(project_key)

    print "Total: %d Projects" % (len(project_list),)

    save_to_file('vuln_projects.json', json.dumps(project_list))


if __name__ == "__main__":
    main()
