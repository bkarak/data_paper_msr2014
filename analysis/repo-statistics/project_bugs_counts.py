# Extracts the project counters data from the JSON representation
# and calculates correlations between version numbers and number
# of bugs.

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math
import collections

bugs_per_version = collections.OrderedDict()
bugs_per_version['SECURITY_HIGH'] = []
bugs_per_version['SECURITY_LOW'] = []
bugs_per_version['STYLE'] =  []
bugs_per_version['CORRECTNESS'] = []
bugs_per_version['BAD_PRACTICE'] = []
bugs_per_version['MT_CORRECTNESS'] = []
bugs_per_version['I18N'] =  []
bugs_per_version['PERFORMANCE'] = []
bugs_per_version['EXPERIMENTAL'] = []

bugs_per_version_labels = [
    'Security High',
    'Security Low',
    'Style',
    'Correctness',
    'Bad Practice',
    'MT Correctness',
    'i18n',
    'Performance',
    'Experimental'
]

with open("data/project_counters.json", "r") as json_file:
    json_input = json.load(json_file)
    for project, data in json_input.iteritems():
        for version in data['versions']:
            version_order = version['JarMetadata']['version_order']
            if version_order == 0:
                continue
            counters = version['Counters']
            if 'MALICIOUS_CODE' in counters:
                malicious_code = counters.pop('MALICIOUS_CODE')
                if 'SECURITY_LOW' in counters:
                    counters['SECURITY_LOW'] += malicious_code
                else:
                    counters['SECURITY_LOW'] = malicious_code
            for counter in bugs_per_version.keys():
                if counter in counters:
                    value = counters[counter]
                    bugs_per_version[counter].append((version_order, value))

bug_counts_matrix = []
                    
for counter, counter_list in bugs_per_version.iteritems():
    bugs_per_version_arr = np.array(counter_list).transpose()            
    (rho, p_value) = st.spearmanr(bugs_per_version_arr[0],
                                  bugs_per_version_arr[1])
    print counter, rho, p_value
    bug_counts_matrix.append([counter, rho, p_value])

with open("bugsperversion.tex", "w") as bugsperversion_tex:
    start = r"""
\begin{tabular}{lcc}
\hline \\
Category & Spearman Correlation & $p$-value \\ \hline 
"""
    bugsperversion_tex.write(start)
    for i, row in enumerate(bug_counts_matrix):
        print row
        significant = True
        if row[2] < 0.001:
            p_val_str = '$\ll 0.05$'
        elif row[2] < 0.01:
            p_val_str = '$< 0.01$'
        elif row[2] < 0.05:
            p_val_str = '$< 0.05$'
        else:
            p_val_str = '{:.2f}'.format(row[2])
            significant = False
        if significant:
            rho_str = '{:.2f}'.format(row[1])
        else:
            rho_str = '{{\it ({:.2f}) }}'.format(row[1])
        table_row = (bugs_per_version_labels[i] + ' & '
                     + rho_str + ' & '
                     + p_val_str +  r'\\' + '\n')
        bugsperversion_tex.write(table_row)
    end = r"""\hline \\
\end{tabular}
"""
    bugsperversion_tex.write(end)
    
plt.figure(1, figsize=(16, 10))
num_plots = len(bugs_per_version.keys())
num_cols = 4
num_rows = num_plots / num_cols
if num_rows % num_cols != 0:
    num_rows += 1
num_plot = 1
for counter, counter_list in bugs_per_version.iteritems():
    bugs_per_version_arr = np.array(counter_list).transpose()
    plt.subplot(num_rows, num_cols, num_plot)
    plt.xlim((0, 100))
    ymax = math.ceil(1.1 * bugs_per_version_arr[1].max())
    plt.ylim((0, ymax))
    plt.scatter(bugs_per_version_arr[0], bugs_per_version_arr[1])
    plt.title(counter)
    num_plot += 1

plt.show()

    
