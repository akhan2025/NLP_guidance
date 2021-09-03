import os
import pandas as pd

TRANSCRIPT_PATH = os.environ.get("TRANSCRIPT_PATH")

def thom_reut_convert(ticker):
    path = os.path.join(TRANSCRIPT_PATH, ticker)
    txt_list = [x for x in os.listdir(path) if x[-4:] == '.txt']
    for f in txt_list:
        out = ''
        with open(os.path.join(path, f)) as txt_file:
            txt = txt_file.read()
            # parse date, quarter, year of call 
            qt_txt = [x for x in txt.split('\n') if 'Earnings' in x][0]
            quarter = qt_txt.split()[0]   # not using right now
            year = qt_txt.split()[1]     # not using right now
#             date_idx = txt.find('EVENT DATE/TIME: ') + len('EVENT DATE/TIME: ')
#             date_idx_end = date_idx + 50  # static charater count for length of date
#             date = parse(txt[date_idx:date_idx_end].split('\n')[0]).strftime('%m-%d-%y')
            comp_name = qt_txt.split(' Earnings Call')[0][qt_txt.split(' Earnings Call')[0].find(year)+ len(year) + 1:]
    
   # parse names of call participants, separated into corporate participants and conference participants
            corp_idx = txt.find('Corporate Participants')+len('Corporate Participants')
            corp_idx_end = txt.find('Conference Call Participiants')
            conf_idx = txt.find('Conference Call Participiants') + len('Conference Call Participiants')
            conf_idx_end = txt.find('Presentation')
            corp_txt = txt[corp_idx:corp_idx_end].split('\n')
            corp_name = [x.strip() for x in corp_txt if x.strip() != '']
            corp_people = []
            for i, corp, in enumerate(corp_name):
                if '*' in corp:
                    corp_people.append(tuple([corp, corp_name[i+1]]))
            corp_name = [(x[0].replace('*','').strip(), x[1]) for x in corp_people]
            conf_txt = txt[conf_idx:conf_idx_end].split('\n')
            conf_name = [x.strip() for x in conf_txt if x.strip() != '']
            conf_people = []
            for i, conf, in enumerate(conf_name):
                if '*' in conf:
                    conf_people.append(tuple([conf, conf_name[i+1]]))
            conf_name = [(x[0].replace('*','').strip(), x[1]) for x in conf_people]
            speaker_list = corp_name + conf_name

            columns = ['participiant', 'occupation']
            df_speaker = pd.DataFrame(speaker_list, columns=columns)
            df_speaker.to_csv(os.path.join(path, ticker + '_' + quarter +'_' + year + '_speakers.csv'), index=False)

            # remove footer
            if 'Definitions' in txt:
                txt = txt[0:txt.find('Definitions')]
            elif 'Diclaimer' in txt:
                txt = txt[0:txt.find('Disclaimer')]
                
            if 'PRESENTATION SUMMARY' in txt:
                continue
            
            
            elif 'Presentation' in txt:
                txt = txt[txt.find('Presentation')+len('Presentation'):]
                present_txt = txt.split('\n')
                present_txt = [line.strip() for line in present_txt if '----' not in line and '==' not in line and line != '']
                speakers = [person for person in present_txt if '[' in person]

                last_index = 0
                present_txt.remove(speakers[0])
                filtered_txt = []
                for speaker in speakers[1:]:
                    for i, line in enumerate(present_txt):
                        if line == speaker:
                            filtered_txt.append(''.join(present_txt[last_index:i]))
                            last_index = i
                            break
                    present_txt.remove(speaker)

                filtered_txt.append("".join(present_txt[last_index:]))
                df = pd.DataFrame(columns=['speaker', 'transcript'])
                df['speaker'] = speakers
                df['transcript'] = filtered_txt
                
             
        df.to_csv(os.path.join(path, ticker + '_' + quarter + '_' +year + '.csv'), index=False)
        print('converted: ' + os.path.join(path, ticker + '_' + quarter + "_" + year + '.csv'))
