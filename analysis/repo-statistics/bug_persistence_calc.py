# Calculates the bug persistence statistics

import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import collections

bug_types_closed = collections.OrderedDict()
bug_types_closed['SECURITY_HIGH'] = []
bug_types_closed['SECURITY_LOW'] = []
bug_types_closed['STYLE'] =  []
bug_types_closed['CORRECTNESS'] = []
bug_types_closed['BAD_PRACTICE'] = []
bug_types_closed['MT_CORRECTNESS'] = []
bug_types_closed['I18N'] =  []
bug_types_closed['PERFORMANCE'] = []
bug_types_closed['EXPERIMENTAL'] = []

bug_labels = [
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

projects_closed = set()

with open("data/bug_persistence.json", "r") as json_file:
    json_input = json.load(json_file, object_pairs_hook=collections.OrderedDict)
    bugs_opened = {}
    prev_project = ''
    for project_version, data in json_input.iteritems():
        project = project_version.rpartition('||')[0]
        if project != prev_project:
            bugs_opened = {}
            projects_closed.add(prev_project)
            if project in projects_closed:
                print project, "met again!"
            prev_project = project
        version_order = data.get('version_order', 0)
        #print project_version, version_order
        if version_order == 0:
            continue
        bugs = data['Bugs']
        for bug in bugs_opened.keys():
            if bug not in bugs:
                bug_type = bug.partition('||')[0]
                if bug_type == 'MALICIOUS_CODE':
                    bug_type = 'SECURITY_LOW'
                diff = version_order - bugs_opened[bug]
                bug_types_closed[bug_type].append(diff)
                if diff < 1:
                    print (project, bug_type, diff, version_order,
                           bugs_opened[bug])
                del bugs_opened[bug]
        for bug in bugs:
            if bug == 'MALICIOUS_CODE':
                bug = 'SECURITY_LOW'
            if bug not in bugs_opened:
                bugs_opened[bug] = version_order

bug_type_arrays = []
bug_type_desc = []

for bug_type, bugs_closed in bug_types_closed.iteritems():
    bug_type_arrays.append(np.array(bugs_closed))
    bug_type_desc.append(st.describe(bugs_closed))

results_matrix = collections.defaultdict(dict)

n = len(bug_types_closed)

results_matrix = [[[] for j in range(n)] for i in range(n)]

for i in range(n):
    for j in range(i+1, n):
        z_stat, p_val = st.ranksums(bug_type_arrays[i],
                                    bug_type_arrays[j])
        print (bug_labels[i], bug_labels[j], z_stat, p_val,
               bug_type_desc[i], bug_type_desc[j])
        results_matrix[i][j] = (z_stat,
                                p_val,
                                bug_type_desc[i][2], # mean
                                bug_type_desc[j][2], # mean
                                bug_type_desc[i][0], # size
                                bug_type_desc[j][0]) # size

with open("bug_persistence.tex", "w") as bug_persistence_tex:
    start = r"""
\begin{tabular}{|l|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2.5cm}|}
\hline 
"""
    bug_persistence_tex.write(start)
    for i in range(n-1):
        row = [bug_labels[i]]
        for j in range(n):
            if j <= i:
                if j < i:
                    row.append('')
            else:
                results = results_matrix[i][j]
                z_stat_str = '${:.2f}$'.format(results[0])
                significant = True
                if results[1] < 0.001:
                    p_val_str = '$p \ll 0.05$'
                elif results[1] < 0.01:
                    p_val_str = '$p < 0.01$'
                elif results[1] < 0.05:
                    p_val_str = '$p < 0.05$'
                else:
                    p_val_str = '$p = {:.2f}$'.format(results[1])
                    significant = False
                mean_i_str = '{:.2f}'.format(results[2])
                mean_j_str = '{:.2f}'.format(results[3])
                size_i_str = str(results[4])
                size_j_str = str(results[5])
                cell_fmt = r'{}, {}\newline {}, {}\newline {}, {}'
                cell = cell_fmt.format(z_stat_str,
                                       p_val_str,
                                       mean_i_str,
                                       mean_j_str,
                                       size_i_str,
                                       size_j_str)
                if not significant:
                    cell = '{{\it ({})}}'.format(cell)
                row.append(cell)
        bug_persistence_tex.write(' & '.join(row) + r'\\' + '\n')

    bug_persistence_tex.write(r"\hline" + '\n')
    for i in range(n):
        label = '' if i == 0 else bug_labels[i]
        empties = ' & ' * (n - i - 1)
        line = r'\multicolumn{{{0}}}{{l|}}{{{1}}} {2} \\'.format(i+1, label,
                                                                 empties)
        line += '\n'
        bug_persistence_tex.write(line)
        line = r'\cline{{1-{0}}}'.format(i+1) + '\n'
        bug_persistence_tex.write(line)
        
    bug_persistence_tex.write(r'\hline' + '\n')
    bug_persistence_tex.write(r'\end{tabular}' + '\n')
