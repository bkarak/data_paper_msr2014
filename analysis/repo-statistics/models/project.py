

class Project(object):
    def __init__(self, group_id, artifact_id):
        super(Project, self).__init__()
        self.__group_id = group_id
        self.__artifact_id = artifact_id
        self.__version_count = 0

    def group_id(self):
        return self.__group_id

    def artifact_id(self):
        return self.__artifact_id

    def key(self):
        return '%s||%s' % (self.group_id, self.artifact_id())

    def set_version_count(self, c):
        self.__version_count = c

    def version_count(self):
        return self.__version_count

    @staticmethod
    def parse_project(project_key, version_count):
        pk_arr = project_key.split('||')
        prj_obj = Project(pk_arr[0].strip(), pk_arr[1].strip())
        prj_obj.set_version_count(version_count)

        return prj_obj



