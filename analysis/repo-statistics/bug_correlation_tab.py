# Extracts the bug correlation data from the JSON representation
# and outputs them in CSV format so that it can be read by R.

import ijson
import sys
import csv

bug_types = set()

def get_bug_type(prefix):
    return prefix[prefix.rfind(".") + 1:]

with open("data/bug_correlation_counters.json", "r") as json_input:
    parser = ijson.parse(json_input)
    for prefix, event, value in parser:
        if (event == 'number'):
            bug_types.add(get_bug_type(prefix))

with open("data/bug_correlation_counters.json", "r") as json_input, \
        open("data/bug_correlation_counters.csv", "w") as csv_output:
    csvwriter = csv.writer(csv_output)
    parser = ijson.parse(json_input)
    project_counts = {}
    project_key = ""
    row = ['project']
    for bug_type in bug_types:
        row.append(bug_type)
    csvwriter.writerow(row)
    for prefix, event, value in parser:
        if (event == 'start_map'):
            if prefix == '':
                continue
            project_key = prefix
        if (event == 'number'):
            project_counts[get_bug_type(prefix)] = value
        if (event == 'end_map'):
            row = [project_key]
            for bug_type in bug_types:
                bug_count = project_counts[bug_type] if bug_type in project_counts else 'NA'
                row.append(bug_count)
            csvwriter.writerow(row)
            project_counts = {}
            project_key = ""
            
