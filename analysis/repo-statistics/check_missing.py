import xmldict
import httplib

from urllib2 import urlopen

from helpers.mongo_helper import get_version, get_mongo_connection, MONGO_COL

def url_exists(base_url, path):
    conn = httplib.HTTPConnection(base_url)
    conn.request('HEAD', path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200


def main():
    base_url = 'http://mirrors.ibiblio.org/maven2'
    col_obj = get_mongo_connection()[MONGO_COL]
    fp = open('data/missing_versions.txt', 'r')

    total_jars = 0
    missing = 0
    really_missing = 0

    for line in fp:
        (group_id, artifact_id) = line.strip().split('||')
        maven_base_url = '%s/%s/%s/' % (base_url, group_id.replace('.', '/'), artifact_id)
        maven_metadata_name = '%smaven-metadata.xml' % (maven_base_url,)

        try:
            fp = urlopen(maven_metadata_name)
            json_xml = xmldict.parse(fp.read())
            versions = json_xml.get('metadata', {}).get('versioning', {}).get('versions', {}).get('version')
            version_list = []

            if isinstance(versions, list):
                version_list.extend(versions)
            else:
                version_list.append(versions)

            for v in version_list:
                docs = get_version(col_obj, group_id, artifact_id, v)
                total_jars += 1

                if len(docs) == 0:
                    missing += 1
                    print '[%d]: Missing %s||%s||%s' % (total_jars, group_id, artifact_id, v)
                    url_jar_path = '/maven2/%s/%s/%s/%s-%s.jar' % (group_id.replace('.', '/'), artifact_id, v, artifact_id, v)

                    if not url_exists('mirrors.ibiblio.org', url_jar_path):
                        really_missing += 1
                        print '%s%s' % ('mirrors.ibiblio.org', url_jar_path)
        except Exception, e:
            print '[%d] ERROR: %s (%s)' % (total_jars, maven_metadata_name, e)
            continue

    fp.close()

    print 'Total: %d, Missing: %d (%d)' % (total_jars, missing - really_missing, missing)


if __name__ == "__main__":
    main()
