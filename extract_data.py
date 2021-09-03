import os
from typing import List
import pandas as pd
import click
import logging
from classification import setup_logging
import itertools

TRANSCRIPT_PATH = os.environ.get("TRANSCRIPT_PATH")
logger = logging.getLogger(__name__)


def thom_reut_convert(ticker:str) -> List[str]:
    path = os.path.join(TRANSCRIPT_PATH, ticker)
    txt_list = [x for x in os.listdir(path) if x[-4:] == '.txt']
    locations = []
    for f in txt_list:
        out = ''
        with open(os.path.join(path, f)) as txt_file:
            txt = txt_file.read()
            # parse date, quarter, year of call 
            qt_txt = [x for x in txt.split('\n') if 'Earnings' in x][0]
            quarter = qt_txt.split()[0]   # not using right now
            year = qt_txt.split()[1]
            corp_idx = txt.find('Corporate Participants')+len('Corporate Participants')
            corp_idx_end = txt.find('Conference Call Participants')
            conf_idx = txt.find('Conference Call Participants') + len('Conference Call Participants')
            conf_idx_end = txt.find('Presentation')
            
            corp_txt = txt[corp_idx:corp_idx_end].split('\n') 
            corp_name = [x.strip() for x in corp_txt if x.strip() != '']
            corp_people = []
            for i, corp in enumerate(corp_name):
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

            if 'Definitions' in txt:
                txt = txt[0:txt.find('Definitions')]
            elif 'Diclaimer' in txt:
                txt = txt[0:txt.find('Disclaimer')]
                
            if 'PRESENTATION SUMMARY' in txt:
                logger.info('need to include presentation sentences')
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

                location = os.path.join(TRANSCRIPT_PATH, ticker + '_' + quarter + '_' +year + '.csv')     
                df.to_csv(location, index=False)
                logger.info('converted: ' + location)
                locations += [location]
    return locations


def extract_sentences(locations:List[str]) -> str:
    sentences = []
    for file in locations:
        logger.info(f'extracting sentences from{file}')
        df = pd.read_csv(os.path.join(TRANSCRIPT_PATH, file))
        new_sentence = df['transcript'].apply(lambda x: x.split('.')).to_list()
        sentences += list(itertools.chain.from_iterable(new_sentence))
    sentences = [sentence for sentence in sentences if sentence]
    return sentences


@click.command()
@click.option('--ticker','-t',required=True,type=str,help='ticker for the companies earnings call')
@click.option('--new-transcripts/--reuse', '-nt/-r',type=bool,required=True,help='adding new transcripts or using existing ones')
def main(ticker:str, new_transcripts:bool):
    setup_logging()
    locations = []
    if new_transcripts:
        locations = thom_reut_convert(ticker)
    else:
        path = TRANSCRIPT_PATH
        csv_list = [x for x in os.listdir(path) if x[-4:] == '.csv']
        locations = [x for x in csv_list if 'speakers' not in x or 'sentence' not in x]
    sentences = extract_sentences(locations)
    df = pd.DataFrame()
    df['sentence'] = sentences
    df['guidance/useless'] = [None]*len(sentences)
    df.to_csv(TRANSCRIPT_PATH +'/sentences.csv')


if __name__ == "__main__":
    main()
