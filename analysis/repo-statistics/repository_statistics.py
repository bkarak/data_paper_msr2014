from helpers.data_helper import load_projects_json

from maths import statistics

__author__ = 'Vassilios Karakoidas (vassilios.karakoidas@gmail.com)'


def main():
    project_list = load_projects_json()

    project_count = len(project_list)
    version_list = [x.version_count() for x in project_list]
    version_count = sum(version_list)

    version_list = sorted(version_list)

    print "Projects: %d" % (project_count,)
    print "Versions (total): %d" % (version_count,)
    print "Max. Version Count: %d" % (statistics.stat_max(version_list),)
    print "Min. Version Count: %d" % (statistics.stat_min(version_list),)
    print "Mean: %.2f" % (statistics.mean(version_list))
    print "Median: %d" % (version_list[statistics.median(version_list)])
    print "Range: %d" % (statistics.stat_range(version_list))
    print "1st Qrt: %d" % (version_list[statistics.first_quartile(version_list)])
    print "3rd Qrt: %d" % (version_list[statistics.third_quartile(version_list)])

if __name__ == "__main__":
    main()
