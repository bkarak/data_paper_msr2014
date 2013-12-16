# Calculate various statistics on the diffs between bug type counts

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math
from collections import defaultdict, OrderedDict
import itertools

bug_types = (
    'SECURITY_HIGH',
    'SECURITY_LOW',
    'STYLE',
    'CORRECTNESS',
    'BAD_PRACTICE',
    'MT_CORRECTNESS',
    'I18N',
    'PERFORMANCE',
    'EXPERIMENTAL',
)

# the bug_types_diffs dict contains, for each bug type, a list of the
# diffs for that bug type, for all projects
bug_types_diffs = OrderedDict()
for bug_type in bug_types:
    bug_types_diffs[bug_type] = []

bug_labels = {
    'SECURITY_HIGH': 'Security High',
    'SECURITY_LOW': 'Security Low',
    'STYLE': 'Style',
    'CORRECTNESS': 'Correctness',
    'BAD_PRACTICE': 'Bad Practice',
    'MT_CORRECTNESS': 'MT Correctness',
    'I18N': 'i18n',
    'PERFORMANCE': 'Performance',
    'EXPERIMENTAL': 'Experimental'
}

# diffs is a dict with the projects as keys. The value for each key
# is itself a dict with the various bug types as keys and a list of
# their diffs as values.
diffs = {}

counts = {}

counts_corrs = {}

# get defect counts
with open("data/project_counters.json", "r") as json_file:
    json_input = json.load(json_file)
    for project, data in json_input.iteritems():
        counts[project] = []
        bad_project = False
        for version in data['versions']:
            if bad_project == True:
                break
            version_order = version['JarMetadata']['version_order']
            if version_order == 0:
                bad_project = True
                continue
            counts[project].append({})
            counters = version['Counters']
            if 'MALICIOUS_CODE' in counters:
                malicious_code = counters.pop('MALICIOUS_CODE')
                if 'SECURITY_LOW' in counters:
                    counters['SECURITY_LOW'] += malicious_code
                else:
                    counters['SECURITY_LOW'] = malicious_code
            for counter, value in counters.iteritems():
                if version_order != len(counts[project]):
                    bad_project = True
                    break
                else:
                    counts[project][version_order - 1][counter] = value

# calculate diffs per project and bug type
for project, project_counts in counts.iteritems():
    diffs[project] = defaultdict(list)
    num_versions = len(project_counts)
    for (i, j) in itertools.izip(range(num_versions), range(1, num_versions)):
        counters_to_check = set()
        prev_counters = project_counts[i].viewkeys()
        cur_counters = project_counts[j].viewkeys()
        counters_to_check = prev_counters | cur_counters
        for counter_to_check in counters_to_check:
            prev_counts = project_counts[i]
            prev_value = prev_counts.get(counter_to_check, 0)
            cur_counts = project_counts[j]
            cur_value = cur_counts.get(counter_to_check, 0)
            diff = cur_value - prev_value
            if not (diff == 0 and cur_value == 0):
                if abs(diff) > 1000:
                    print project, i, j, counter_to_check, diff
                diffs[project][counter_to_check].append(diff)

# For each project and each kind of bug calculate the correlation between
# the number of bugs and the version ordinals
np.seterr(all='ignore')                
# we ignore this because lots of spearmans return no correlation at all
for project, project_counts in counts.iteritems():
    counter_evol = defaultdict(list)
    for version_counts in project_counts:
        for counter, counter_count in version_counts.iteritems():
            counter_evol[counter].append(counter_count)
    for counter, counter_counts in counter_evol.iteritems():
        cc_arr = np.array(counter_counts)        
        if len(cc_arr) > 1:
            versions_arr = np.arange(1, len(cc_arr)+1)
            (rho, p_value) = st.spearmanr(cc_arr, versions_arr)
            if p_value < 0.05:
                counts_corrs.setdefault(counter, []).append(rho)
                if counter == 'SECURITY_HIGH':
                    print project, counter, len(cc_arr), cc_arr, rho, p_value
            else:
                counts_corrs.setdefault(counter, []).append(0)

np.seterr(all=None) 
# Populate the bug_types_diffs dictionary (pull together all per-project
# diffs in one dictionary)
for project, project_diffs in diffs.iteritems():
    for counter, counter_diffs in project_diffs.iteritems():
        bug_types_diffs[counter].extend(counter_diffs)

# Output descriptive statistics for each bug type diffs across projects
for bug_type, bug_type_diffs in bug_types_diffs.iteritems():
    cd_arr = np.array(bug_type_diffs)
    hist = np.histogram(cd_arr)
    percentiles = [st.scoreatpercentile(cd_arr, p) for p in [1, 25, 50, 75, 99]]
    # print bug_type, st.describe(cd_arr), percentiles, hist

fig1 = plt.figure(1, figsize=(16, 10))

num_plots = len(bug_types_diffs.keys())
num_cols = 3
num_rows = num_plots / num_cols
if num_rows % num_cols != 0:
    num_rows += 1
num_plot = 1
for bug_type, bug_type_diffs in bug_types_diffs.iteritems():
    cd_arr = np.array(bug_type_diffs)
    ax = plt.subplot(num_rows, num_cols, num_plot)
    ax.tick_params(axis='x', labelsize='small')
    plt.hist(cd_arr, 30, log=True)
    plt.title(bug_labels[bug_type])
    num_plot += 1

fig2 = plt.figure(2, figsize=(16, 10))

num_plot = 1
for bug_type, bug_type_corrs in counts_corrs.iteritems():
    cc_arr = np.array(bug_type_corrs)
    ax = plt.subplot(num_rows, num_cols, num_plot)
    plt.hist(cc_arr, 30, log=True)
    total = len(bug_type_corrs)
    zeros = total - len(np.nonzero(bug_type_corrs)[0])
    title = "{} ({}, no correlation: {})".format(bug_labels[bug_type],
                                                 total,
                                                 zeros)
    plt.title(title)
    num_plot += 1

plt.tight_layout()
fig1.savefig('bugdiffs.pdf', format='pdf')
fig2.savefig('bugsversionscorr.pdf', format='pdf')
plt.show()
