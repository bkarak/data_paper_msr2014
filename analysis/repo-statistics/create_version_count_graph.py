import StringIO
from helpers.data_helper import load_projects_json, ArrayCount, save_to_file


def main():
    statistics = ArrayCount()

    for p in load_projects_json():
        statistics.incr(p.version_count())

    strio = StringIO.StringIO()

    for (k, v) in statistics.get_series().iteritems():
        strio.write(str(k) + "," + str(v) + "\n")

    save_to_file('version_count.dat', strio.getvalue())


if __name__ == "__main__":
    main()

