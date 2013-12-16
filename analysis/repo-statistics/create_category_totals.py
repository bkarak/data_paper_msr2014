import json
from helpers.data_helper import ArrayCount


def main():
    fp = open('data/bug_correlation_counters_full.json', 'r')
    json_corr = json.load(fp)
    fp.close()

    totals = ArrayCount()

    for (k, v) in json_corr.iteritems():
        if len(v) > 0:
            for (key, value) in v.iteritems():
                totals.incr(key, delta=value)

    total = 0

    for (k, v) in totals.get_series().iteritems():
        if k.startswith('TOTAL_'):
            total += v

    print 'Total: %d' % (total,)

    for (k, v) in totals.get_series().iteritems():
        if k.startswith('TOTAL_'):
            print '%s %.2f' % (k.replace('TOTAL_', '').title(), (float(v) / float(total))*100)


if __name__ == "__main__":
    main()
