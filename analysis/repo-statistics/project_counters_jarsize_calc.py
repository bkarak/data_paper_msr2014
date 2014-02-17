# Extracts the bug counters data from the JSON representation
# and calculates correlations between bug types and jarsizes

import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st

bug_types = [
    'SECURITY',
    'MALICIOUS_CODE',
    'STYLE',
    'CORRECTNESS',
    'BAD_PRACTICE',
    'MT_CORRECTNESS',
    'I18N',
    'PERFORMANCE',
    'EXPERIMENTAL',
]

bug_type_labels = [
    'Security',
    'Malicious Code',
    'Style',
    'Correctness',
    'Bad Practice',
    'MT Correctness',
    'i18n',
    'Performance',
    'Experimental',
]

rows = []

with open("data/project_counters.json", "r") as json_file:
    json_input = json.load(json_file)
    for project, data in json_input.iteritems():
        for version in data['versions']:
            meta_data = version['JarMetadata']
            row = [meta_data['jar_size']]
            jar_size = meta_data['jar_size']
            counters = version['Counters']
            if 'SECURITY_LOW' in counters:
                security_low = counters.pop('SECURITY_LOW')
            else:
                security_low = 0
            if 'SECURITY_HIGH' in counters:
                security_high = counters.pop('SECURITY_HIGH')
            else:
                security_high = 0
            if security_low or security_high:
                counters['SECURITY'] = security_low + security_high
            for bug_type in bug_types:
                if bug_type in counters:
                    row.append(counters[bug_type])
                else:
                    row.append(np.nan)
            rows.append(row)
                                     
num_plots = len(bug_types)
num_cols = 4
num_rows = num_plots / num_cols
if num_rows % num_cols != 0:
    num_rows += 1
num_plot = 1

fig1 = plt.figure(1, figsize=(16, 10))
fig1.subplots_adjust(hspace=0.4)

kilobyte = 1024.0

counts_arr = np.array(rows)

jarsizematrix = []
column_indx = 1
for i, bug_type in enumerate(bug_types):
    data_pairs = np.array([counts_arr[:,0], counts_arr[:,column_indx]]).T
    data_pairs = data_pairs[~np.isnan(data_pairs).any(1)]
    # counts_arr[1] = counts_arr[1] / kilobyte
    plt.subplot(num_rows, num_cols, num_plot)
    jarsizes = data_pairs[:,0]
    bug_counts = data_pairs[:,1]
    (rho, p_value) = st.spearmanr(jarsizes, bug_counts)
    print bug_type, rho, p_value
    jarsizematrix.append([bug_type_labels[i], rho, p_value])
    plt.scatter(jarsizes, bug_counts)
    plt.title(bug_type)
    num_plot += 1
    column_indx += 1

with open("jarsizecorr.tex", "w") as jarsizecorr_tex:
    start = r"""
\begin{tabular}{lcc}
\hline \\
Category & Spearman Correlation & $p$-value \\ \hline 
"""
    jarsizecorr_tex.write(start)
    for row in jarsizematrix:
        if row[2] < 0.001:
            p_val_str = '$\ll 0.05$'
        elif row[2] < 0.01:
            p_val_str = '$< 0.01$'
        elif row[2] < 0.05:
            p_val_str = '$< 0.05$'
        else:
            p_val_str = '{:.2f}'.format(row[2])
        table_row = (row[0] + ' & '
                     + '{:.2f}'.format(row[1]) + ' & '
                     + p_val_str +  r'\\' + '\n')
        jarsizecorr_tex.write(table_row)
    end = r"""\hline \\
\end{tabular}
"""
    jarsizecorr_tex.write(end)
    
plt.show()
