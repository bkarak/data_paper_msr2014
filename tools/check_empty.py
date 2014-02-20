import urllib, xmldict


def main():
    base_url = 'http://mirrors.ibiblio.org/maven2/'

    fp = open('data/bugless_projects.json', 'r')
    c = 0

    for l in fp:
        arr = l.strip().split('||')
        group_id = arr[0]
        artifact_id = arr[1]
        c += 1

        maven_base_url = '%s%s/%s/' % (base_url, group_id.replace('.', '/'), artifact_id)
        maven_metadata_name = '%smaven-metadata.xml' % (maven_base_url,)
        local_maven_metadata_name = 'work/maven-metadata.xml.%d' % (c,)
        urllib.urlretrieve(maven_metadata_name, local_maven_metadata_name)
        json_xml = xmldict.parse(open(local_maven_metadata_name, 'r').read())
        versions = json_xml.get('metadata', {}).get('versioning', {}).get('versions', {}).get('version')
        version_list = []

        if isinstance(versions, list):
            version_list.extend(versions)
        else:
            version_list.append(versions)

        for v in version_list:
            vfile = '%s-%s.jar' % (artifact_id, v)
            vfile_url = '%s%s/%s' % (maven_base_url, v, vfile)
            urllib.urlretrieve(vfile_url, 'work/%s' % (vfile,))
            print vfile_url

    fp.close()


if __name__ == "__main__":
    main()
