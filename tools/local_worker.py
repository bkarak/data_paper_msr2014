import os
import zipfile
from helpers import mongo_helper


def has_classes(filename):
    try:
        if zipfile.is_zipfile(filename):
            z = zipfile.ZipFile(filename)
            for f in z.namelist():
                if f.endswith('.class'):
                    print 'Valid JAR file: %s' % (filename,)
                    return True
        else:
            print '%s is not a zipfile (has_classes)' % (filename,)

        return False
    except Exception, e:
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
            return 0
    else:
        print '%s is not a zipfile (get_jar_size)' % (filename,)
        return 0


def convert_findbugs_xml(findbugs_xml):
    import xmldict
    import json

    xml_data = open(findbugs_xml, 'r').read()
    result_json = json.loads(json.dumps(xmldict.parse(xml_data)).replace('"@', '"'))

    # -1: jar, -2: version, -3: artifact_id, -4: group_id
    _full_name = result_json.get('BugCollection', {}).get('Project', {}).get('Jar', None)

    if _full_name is None:
        raise Exception('Jar tag is not found (%s)' % (result_json,))

    print 'Processing ... %s' % (_full_name,)

    _jar_filename = os.path.basename(_full_name)
    _pom_filename = _full_name.replace('.jar', '.pom')
    _metadata_filename = '%s/maven-metadata.xml' % ('/'.join(_full_name.split('/')[:-2]),)
    _dependencies = []
    _versions = []

    _version = None
    _artifact_id = None
    _group_id = None
    _version_order = 0

    if os.path.exists(_pom_filename):
        try:
            _pom_json = json.loads(json.dumps(xmldict.parse(open(_pom_filename, 'r').read())))
            _dependencies = _pom_json.get('project', {}).get('dependencies', {}).get('dependency', [])
        except Exception, e:
            print 'Could not download/parse data from %s (%s)' % (_pom_filename, e)

    if os.path.exists(_metadata_filename):
        try:
            _metadata_json = json.loads(json.dumps(xmldict.parse(open(_metadata_filename, 'r').read())))
            _group_id = _metadata_json['metadata']['groupId']
            _artifact_id = _metadata_json['metadata']['artifactId']
            _version = _jar_filename.replace('.jar', '').replace(_artifact_id + '-', '').strip()
            _versions = _metadata_json.get('metadata', {}).get('versioning', {}).get('versions', {}).get('version', [])

            if not isinstance(_versions, list):
                _versions = [_versions]

            _versions = [x.strip() for x in _versions]

            try:
                if len(_versions) > 0 and _version is not None:
                    _version_order = _versions.index(_version.strip()) + 1
            except Exception, ve:
                print 'Could not find version (%s): %s' % (_version, ve)
                _version_order = 0
        except Exception, e:
            print 'Could not parse data from %s: %s' % (_metadata_filename, e)

    # get xml information
    _jar_size = get_jar_size(_full_name)
    result_json['JarMetadata'] = {'jar_filename':_jar_filename,
                                  'jar_last_modification_date':0,
                                  'jar_size': _jar_size,
                                  'version': _version,
                                  'version_list': _versions,
                                  'artifact_id': _artifact_id,
                                  'group_id': _group_id,
                                  'version_order': _version_order,
                                  'dependencies':_dependencies}

    if _group_id is None or _artifact_id is None or _version is None:
        return False, result_json

    return True, result_json

def main():
    c = 0
    for (root, dirs, files) in os.walk('data/missing3'):
        for f in files:
            if f.endswith('.xml'):
                jar_filename = '%s/%s' % (root, f)
                try:
                    print "Opening ... %s" % (jar_filename,)
                    (result, result_json) = convert_findbugs_xml('%s/%s' % (root, f))
                    if result:
                        mongo_helper.store_to_mongo(result_json)
                except Exception, e:
                    print "Failure: %s (%s)" % (jar_filename, e)
                    continue
    print c


if __name__ == "__main__":
    main()

