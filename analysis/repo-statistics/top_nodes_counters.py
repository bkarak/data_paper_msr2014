import csv
import json

def main():
    with open("data/project_counters.json") as data_file:
        data = json.load(data_file)

    with open('data/graph-results.csv', 'rb') as f:
        reader = csv.reader(f)
        counter = 0
        for row in reader:
            counter = counter + 1
            try:
                (group_id,artifact,version) = row[0].split("||")
                #print "%s %s %s" % (group_id,artifact,version)
                #print row[1]
                #print row[2]
                #print row[3]
        
                my_key = ''.join([group_id,"||",artifact]) 
                if my_key in data:
                    #print data.get(my_key)
                    #json_object = json.load(data.get(my_key))
                    obj = data.get(my_key)
                    for my_version in obj[u'versions']:
                        if my_version[u'JarMetadata'][u'version'] == version:
                            print "%s %s %s" % (group_id,artifact,version)
                            print row[1]
                            print row[2]
                            print row[3]
                            print my_version[u'Counters']
            except:
                pass
            if counter == 50:
                break
            
if __name__== "__main__":
 main()
