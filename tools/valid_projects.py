import json
from helpers.data_helper import load_projects_json, save_to_file
from helpers.mongo_helper import MongoProjectIterator


def main():
    projects = load_projects_json()
    valid_projects = []
    total = len(projects)
    valid = 0
    counter = 0

    for p in projects:
        counter += 1
        key = '%s||%s' % (p.group_id(), p.artifact_id())
        piter = MongoProjectIterator(p.group_id(), p.artifact_id(), fields=['JarMetadata.version_order'])\

        piter.evolution_list()
        print '[%d:%d:%d] Checking ... %s' % (counter, valid, total, key),

        if piter.valid():
            valid_projects.append(key)
            print ' ... Valid (%d versions)' % (len(piter.evolution_list()))
            valid += 1
        else:
            print ' ... Invalid (%d versions)' % (len(piter.evolution_list()))

    print 'Total: %d, Valid: %d' % (total, valid)
    save_to_file('valid_projects.json', json.dumps(valid_projects))


if __name__ == "__main__":
    main()
