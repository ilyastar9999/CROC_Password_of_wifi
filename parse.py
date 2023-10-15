import pandas as pd
def parse_csv():
    pipls = pd.read_csv('Контакты учеников.tsv', delimiter='\t', encoding='utf-8')
    teachers = pd.read_csv('Контакты учителей.tsv', delimiter='\t', encoding='utf-8')
    
    for i in range(len(pipls)):
        try:
            pipls[i] = str(pipls[i]).lower()
            if (str(pipls[i]).find('@') == -1):
                del pipls[i]
        except:
            break
    print(pipls)
    for i in range(len(teachers)):
        try:
            pipls[i] = str(teachers[i]).lower()
            if (str(teachers[i]).find('@') == -1):
                del teachers[i]
        except:
            break
    print(teachers)
    return pipls, teachers
