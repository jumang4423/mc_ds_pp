import os
import copy
import json
from pydub import AudioSegment
COUNTER = 0
FILE_CNT_DIGIT_LEN = 4
meta_conf = {
    'output_dir': './output',
    'jsonl_file': './output/train.jsonl',
}
user_conf = {
    'raw_dataset_dir': '/Users/jumang4423/Downloads/train',
    'dataset_dir': '/content/drive/MyDrive/samples/train_musicgen_edm_uncond/train/outputs',
    'file_extention': 'mp3',
    'duration': 30,
    'sample_rate': 44100,
    'instrument': "Mix",
}


def abort():
    print('abort')
    exit()


def print_conf():
    print('Configuration:')
    print(f' meta_conf: {str(meta_conf)}')
    print(f' user_conf: {str(user_conf)}')
    print("hint: raw_dataset_dir has directory with artist name, and mp3 files in it")


def ds_analysis():
    # check raw_dataset_dir is exist
    if not os.path.exists(user_conf['raw_dataset_dir']):
        print('! raw_dataset_dir is not exist')
        print(f'! raw_dataset_dir: {user_conf["raw_dataset_dir"]}')
        abort()
    print('o found raw_dataset_dir')
    # count artists
    artists = [dir for dir in os.listdir(user_conf['raw_dataset_dir']) if not dir.startswith('.')]
    if len(artists) == 0:
        print('! now artists in raw_dataset_dir')
        abort()
    print(f'o found {len(artists)} artists')
    # count mp3 files
    mp3_files = []
    for artist in artists:
        artist_dir = os.path.join(user_conf['raw_dataset_dir'], artist)
        for file in os.listdir(artist_dir):
            if file.endswith(user_conf['file_extention']):
                mp3_files.append(file)
    if len(mp3_files) == 0:
        print('! now mp3 files in raw_dataset_dir')
        abort()
    print(f'o found {len(mp3_files)} mp3 files')


def get_all_sound_files(folder, extention) -> list[str]:
    """
    get all sound file path in folder
    """
    files = []
    for file in os.listdir(folder):
        if file.endswith(extention):
            files.append(os.path.join(folder, file))
    return files


def cut_sound_by_duration(sound_file_path, duration) -> list[str]:
    """
    cut sound file by duration, then return list of sound file path
    """
    global COUNTER
    duration = duration * 1000
    sound = AudioSegment.from_file(sound_file_path)
    length_of_sound = len(sound)
    number_of_files = length_of_sound // duration
    list_of_files = []
    for i in range(number_of_files):
        start = i * duration
        end = start + duration
        new_sound = sound[start:end]
        new_sound_path = os.path.join(
            meta_conf['output_dir'],
            f'train_{str(COUNTER).zfill(FILE_CNT_DIGIT_LEN)}.{user_conf["file_extention"]}'
        )
        new_sound.export(new_sound_path, format=user_conf['file_extention'])
        list_of_files.append(new_sound_path)
        COUNTER += 1
        print(f'o cut sound file: {os.path.basename(new_sound_path)}')
    return list_of_files


def parse_sound_file(sound_file_path, json_base):
    """
    parse sound file and return jsonl file path
    """
    # cut sound file
    sound_file_paths = cut_sound_by_duration(
        sound_file_path,
        user_conf['duration']
    )
    print(f'o cut sound file: {len(sound_file_paths)} files')
    # make jsonl
    jsonl = []
    for sound_file_path in sound_file_paths:
        new_json = copy.deepcopy(json_base)
        new_json['path'] = os.path.join(
            user_conf['dataset_dir'],
            os.path.basename(sound_file_path)
        )
        jsonl.append(json.dumps(new_json))
    # write jsonl
    jsonl_file = open(meta_conf['jsonl_file'], 'a')
    for json_str in jsonl:
        jsonl_file.write(json_str + '\n')
    jsonl_file.close()


def gen():
    # make output dir
    if not os.path.exists(meta_conf['output_dir']):
        os.makedirs(meta_conf['output_dir'])
    # make jsonl file
    jsonl_file = open(meta_conf['jsonl_file'], 'w')
    jsonl_file.close()
    # get all artists
    artists = [dir for dir in os.listdir(user_conf['raw_dataset_dir']) if not dir.startswith('.')]
    for artist in artists:
        print(f'processing {artist}')
        json_base = {
            'artist': artist,
            'sample_rate': user_conf['sample_rate'],
            'file_extension': user_conf['file_extention'],
            'duration': user_conf['duration'],
            'instrument': user_conf['instrument'],
        }
        # get artist genre
        genre = input('genre? (default: electronic)')
        if genre == '':
            genre = 'electronic'
        json_base['genre'] = genre
        # get artist keywords
        keywords = input('keywords? (default: none) (separate with comma)')
        if keywords != '':
            keywords_ar = keywords.split(', ')
            assert len(keywords_ar) > 0
            json_base['keywords'] = keywords
        # parse sound files
        sound_files = get_all_sound_files(
            os.path.join(user_conf['raw_dataset_dir'], artist),
            user_conf['file_extention']
        )
        for sound_file_path in sound_files:
            print(f'processing {sound_file_path}')
            parse_sound_file(
                sound_file_path,
                copy.deepcopy(json_base)
            )
        print(f'processed {artist}')








if __name__ == '__main__':
    print_conf()
    b = input('proceed analysis? (y/n)')
    if b != 'y':
        abort()
    ds_analysis()
    b = input('proceed dataset generation? (y/n)')
    if b != 'y':
        abort()

    gen()
    print('done')
