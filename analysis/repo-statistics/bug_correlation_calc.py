# Calculates pairwise correlations from the data in
# data/bug_correlation_counters.json

import json
import pandas as pd
import numpy as np
import scipy.stats as st
from itertools import izip
import sys
import itertools
from corrplot import corrplot

bug_types = [
    'SECURITY_HIGH',
    'SECURITY_LOW',
    'MALICIOUS_CODE',
    'STYLE',
    'BAD_PRACTICE',
    'CORRECTNESS',
    'MT_CORRECTNESS',
    'PERFORMANCE',
    'I18N',
    'EXPERIMENTAL'
    ]

labels = []
for bug_type in bug_types:
    if bug_type == 'I18N':
        labels.append(bug_type.lower())
    elif bug_type == 'MT_CORRECTNESS':
        labels.append('MT Correctness')
    elif bug_type == 'MALICIOUS_CODE':
        pass
    else:
        labels.append(bug_type.title().replace('_', ' '))

with open("data/bug_correlation_counters.json") as infile:
    json_input = json.load(infile)

data = pd.DataFrame(json_input).T

for bug_type in bug_types:
    print bug_type, data[bug_type].count()

print "MALICIUS_CODE & SECURITY_LOW ", len(data[data['MALICIOUS_CODE']
                                                * data['SECURITY_LOW'] > 0])
    
data['SECURITY_LOW'] = (data['MALICIOUS_CODE'].fillna(0)
                        + data['SECURITY_LOW'].fillna(0)).replace(0, np.nan)
data['TOTAL_SECURITY_LOW'] = (data['TOTAL_MALICIOUS_CODE'].fillna(0)
                              + data['TOTAL_SECURITY_LOW'].fillna(0)
                              ).replace(0, np.nan)
data = data.drop(['MALICIOUS_CODE', 'TOTAL_MALICIOUS_CODE'], axis=1)
bug_types.remove('MALICIOUS_CODE')

num_bug_types = len(bug_types)
corrmatrix = np.identity(num_bug_types)
pvalues = np.zeros([num_bug_types, num_bug_types])

for i in xrange(num_bug_types):
    for j in xrange(i + 1, num_bug_types):
        icolumn = bug_types[i]
        jcolumn = bug_types[j]
        data_pair = data[[icolumn, jcolumn]].dropna()
        (corr, pvalue) = st.spearmanr(data_pair[icolumn], data_pair[jcolumn])
        print "{} ({}) {} ({}) {} {}".format(icolumn, data[icolumn].count(),
                                             jcolumn, data[jcolumn].count(),
                                             corr, pvalue)
        corrmatrix[i, j] = corrmatrix[j, i] = corr
        pvalues[i, j] = pvalues[j, i] = pvalue


with open("corrmatrix.tex", "w") as corrmatrix_tex:
    start = r"""
\begin{tabular}{lccccccccc}
\hline
"""
    corrmatrix_tex.write(start)
    for i, row in enumerate(corrmatrix):
        table_row = labels[i] + ' & '
        table_row += ' & '.join(map('{:.2f}'.format, row)) +  r'\\' + '\n'
        corrmatrix_tex.write(table_row)
    end = r"""\hline
\end{tabular}
"""
    corrmatrix_tex.write(end)

plot = corrplot(corrmatrix, pvalues, labels)

plot.tight_layout()
plot.savefig('corrplot.pdf', format='pdf')
plot.show()
