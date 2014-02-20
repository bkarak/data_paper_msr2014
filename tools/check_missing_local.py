import os
import zipfile
import xmldict
import sys

from helpers.data_helper import load_projects_json

from helpers.mongo_helper import get_version, get_mongo_connection, MONGO_COL


def has_classes(filename):
    try:
        if zipfile.is_zipfile(filename):
            z = zipfile.ZipFile(filename)
            for f in z.namelist():
                if f.endswith('.class'):
                    #print 'Valid JAR file: %s' % (filename,)
                    return True
        else:
            print '%s is not a zipfile (has_classes)' % (filename,)

        return False
    except Exception, e:
        return False


def main():
    base_url = '/Users/bkarak/devel/repositories/maven/maven/'
    col_obj = get_mongo_connection()[MONGO_COL]
    projects = load_projects_json()

    total_jars = 0
    missing = 0
    really_missing = 0

    for proj in projects:
        group_id = proj.group_id().strip()
        artifact_id = proj.artifact_id().strip()
        maven_base_url = '%s%s/%s/' % (base_url, group_id.replace('.', '/'), artifact_id)
        maven_metadata_name = '%smaven-metadata.xml' % (maven_base_url,)

        if not os.path.exists(maven_metadata_name):
            continue

        json_xml = xmldict.parse(open(maven_metadata_name, 'r').read())
        versions = json_xml.get('metadata', {}).get('versioning', {}).get('versions', {}).get('version')
        version_list = []

        if isinstance(versions, list):
            version_list.extend(versions)
        else:
            version_list.append(versions)

        for v in version_list:
            if v is not None:
                v = v.strip()
            docs = get_version(col_obj, group_id, artifact_id, v)
            total_jars += 1

            if len(docs) == 0:
                missing += 1
                sys.stderr.write('[%d]: Missing %s||%s||%s\n' % (total_jars, group_id, artifact_id, v))
                local_jar_path = '%s%s/%s-%s.jar' % (maven_base_url, v, artifact_id, v)

                if not os.path.exists(local_jar_path):
                    sys.stderr.write('[%d]: Invalid Jar: %s||%s||%s\n' % (total_jars, group_id, artifact_id, v))
                    really_missing += 1
                else:
                    if has_classes(local_jar_path):
                        sys.stderr.write('ADDED: Total: %d, Missing: %d (%d)\n' % (total_jars, missing - really_missing, missing))
                        print "findbugs -textui -xml -output `basename %s`-findbugs.xml %s" % (local_jar_path, local_jar_path)
                    else:
                        really_missing += 1
                        sys.stderr.write('HAS_NO_CLASSES: %s\n' % (local_jar_path,))


    sys.stderr.write('Total: %d, Missing: %d (%d)\n' % (total_jars, missing - really_missing, missing))


if __name__ == "__main__":
    main()
