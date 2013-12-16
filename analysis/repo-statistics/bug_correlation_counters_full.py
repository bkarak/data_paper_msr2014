import json

from helpers.data_helper import ArrayCount, save_to_file, load_projects_json
from helpers.mongo_helper import MongoProjectIterator


def main():
    projects = load_projects_json()
    results = {}
    security_bugs = ['HRS_REQUEST_PARAMETER_TO_COOKIE',
                     'HRS_REQUEST_PARAMETER_TO_HTTP_HEADER',
                     'PT_ABSOLUTE_PATH_TRAVERSAL',
                     'SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE',
                     'SQL_PREPARED_STATEMENT_GENERATED_FROM_NONCONSTANT_STRING',
                     'XSS_REQUEST_PARAMETER_TO_JSP_WRITER',
                     'XSS_REQUEST_PARAMETER_TO_SEND_ERROR',
                     'XSS_REQUEST_PARAMETER_TO_SERVLET_WRITER']
    total_projects = len(projects)
    count = 0

    print 'Found %d Projects' % (total_projects,)

    for p in projects:
        piter = MongoProjectIterator(p.group_id(), p.artifact_id(), fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version', 'JarMetadata.version_order', 'BugCollection.BugInstance.category', 'BugCollection.BugInstance.type', 'BugCollection.BugInstance.Class.classname','BugCollection.BugInstance.Method.name', 'BugCollection.BugInstance.Field.name'])
        doc_list = piter.documents_list()
        proj_array_count = ArrayCount()
        bug_list = []
        count += 1

        print '[%d:%d] %s||%s: %d versions' % (count, total_projects, p.group_id(), p.artifact_id(), len(doc_list))

        for d in doc_list:
            for bi in d.get('BugCollection', {}).get('BugInstance', []):
                if not isinstance(bi, dict):
                    #print 'Invalid BugInstance (%s)' % (bi,)
                    continue

                bug_c = bi.get('category', '')
                if bug_c == 'SECURITY':
                    bug_type = bi.get('type', None)
                    
                    if bug_type is None:
                        print 'Invalid Type!'
                        continue
                        
                    if bug_type in security_bugs:
                        bug_category = 'SECURITY_HIGH'
                    else:
                        bug_category = 'SECURITY_LOW'
                else:
                    bug_category = bug_c
                
                # create signature
                signatures_ids = []
                classnames = bi['Class']

                if isinstance(classnames, list):
                    for c in classnames:
                        signatures_ids.append(c.get('classname', 'NotSet'))
                elif isinstance(classnames, dict):
                    signatures_ids.append(classnames.get('classname', 'NotSet'))

                # methods
                methodnames = bi.get('Method', {})

                if isinstance(methodnames, list):
                    for m in methodnames:
                        signatures_ids.append(m.get('name', 'NotSet'))
                elif isinstance(methodnames, dict):
                    signatures_ids.append(methodnames.get('name', 'NotSet'))

                # fields
                fieldnames = bi.get('Field', {})
                if isinstance(fieldnames, list):
                    for f in fieldnames:
                        signatures_ids.append(f.get('name', 'NotSet'))
                elif isinstance(fieldnames, dict):
                    signatures_ids.append(fieldnames.get('name', 'NotSet'))

                type = bi['type']
                signature = '%s||%s||%s' % (bug_category, type, '||'.join(signatures_ids))

                # method
                if signature not in bug_list:
                    bug_list.append(signature)
                    proj_array_count.incr(bug_category)
                
                proj_array_count.incr('TOTAL_' + bug_category)

        print proj_array_count.get_series()
        results['%s||%s' % (p.group_id(), p.artifact_id())] = proj_array_count.get_series()

    save_to_file('bug_correlation_counters_full.json', json.dumps(results))


if __name__ == "__main__":
    main()
