# Extracts the bug counters data from the JSON representation
# and outputs them in CSV format so that it can be read by R.

import ijson
import json
import sys
import csv

bug_types = [
    'SECURITY_HIGH',
    'SECURITY_LOW',
    'STYLE',
    'CORRECTNESS',
    'BAD_PRACTICE',
    'MT_CORRECTNESS',
    'I18N',
    'PERFORMANCE',
    'EXPERIMENTAL',
]

with open("data/project_counters_jarsize.csv", "w") as csv_output:
    csvwriter = csv.writer(csv_output)        
    project_counts = {}
    project_key = ""
    row = ['project', 'version', 'jarsize']
    for bug_type in bug_types:
        row.append(bug_type)
    csvwriter.writerow(row)
    with open("data/project_counters.json", "r") as json_file:
        json_input = json.load(json_file)
        for project, data in json_input.iteritems():
            for version in data['versions']:
                meta_data = version['JarMetadata']                    
                row = [project, meta_data['version_order'],
                       meta_data['jar_size']]
                counters = version['Counters']
                counters = version['Counters']
                if 'MALICIOUS_CODE' in counters:
                    malicious_code = counters.pop('MALICIOUS_CODE')
                    if 'SECURITY_LOW' in counters:
                        counters['SECURITY_LOW'] += malicious_code
                    else:
                        counters['SECURITY_LOW'] = malicious_code
                security_low = 0
                for bug_type in bug_types:
                    if bug_type in counters:
                        row.append(counters[bug_type])
                    else:
                        row.append('NA')
                csvwriter.writerow(row)
            
