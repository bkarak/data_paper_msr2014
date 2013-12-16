import json

from helpers.data_helper import ArrayCount, save_to_file, load_projects_json
from helpers.mongo_helper import MongoProjectIterator


def main():
    projects = load_projects_json()
    total_projects = len(projects)
    count = 0
    bugless_count = 0

    print 'Found %d Projects' % (total_projects,)

    for p in projects:
        piter = MongoProjectIterator(p.group_id(), p.artifact_id(), fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version', 'JarMetadata.version_order', 'BugCollection.BugInstance.category', 'BugCollection.BugInstance.type'])
        doc_list = piter.documents_list()
        proj_array_count = ArrayCount()
        bug_list = []
        count += 1

        for d in doc_list:
        	bug_instances = d.get('BugCollection', {}).get('BugInstance', [])
        	if len(bug_instances) == 0:
        		bugless_count += 1
        		break

        print '[%d:%d:%d] %s||%s: %d versions' % (count, total_projects, bugless_count, p.group_id(), p.artifact_id(), len(doc_list))

    print "bugless: %d, total: %d" % (bugless_count, total)

if __name__ == "__main__":
    main()
