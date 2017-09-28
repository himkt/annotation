#! env python

import argparse
import json
import natto
import os.path
import subprocess
import sys

PWD = os.path.dirname(os.path.realpath(__file__))  # NOQA
sys.path.append(os.path.join(PWD, '../src/'))  # NOQA
from generator import SimpleTextGenerator


def decorate(surface, cursor_position, current_position):
    if cursor_position == current_position:
        return f'{start_color}{surface}{finish_color}'
    return surface


if __name__ == '__main__':
    start_color, finish_color = '\033[1;31;40m', '\033[0m'

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=argparse.FileType(),
                        help='path to configuration file')
    parser.add_argument('--lang', '-l', type=str, default='ja',
                        help='language [ja/en]')
    parser.add_argument('--mecab-dict', '-d', type=str, default='ipadic',
                        help='mecab dictionary [ipadic/neologd]')
    parser.add_argument('--annotation-file', type=argparse.FileType('a'),
                        help='path to the file where annotations are stored',
                        default=os.path.join(PWD, '../work/annotation.tsv'))
    parser.add_argument('--input-file', '-i', type=argparse.FileType(),
                        help='path to the input file')
    args = parser.parse_args()

    config = json.load(args.config)
    labels = config['labels']

    mecab_option = ''
    if args.mecab_dict == 'neologd':
        dict_path = subprocess.check_output(['mecab-config', '--dicdir'])
        dict_path = dict_path.decode('utf-8').rstrip()
        path_to_neologd = os.path.join(dict_path, 'mecab-ipadic-neologd')
        mecab_option = f'-d {path_to_neologd}'

    nm = natto.MeCab(mecab_option)
    gen = SimpleTextGenerator(args.input_file)

    while True:
        input_sentence = gen.__next__()
        print(input_sentence)
        morphs = nm.parse(input_sentence, as_nodes=True)
        surfaces, features = [], []

        for morph in morphs:
            surfaces.append(morph.surface)
            features.append(morph.feature)

        while True:
            len_sequence = len(surfaces)
            ground_truthes = [None for _ in range(len_sequence)]

            cursor_position = 0
            while cursor_position < len_sequence:
                surfaces_ = [None for _ in range(len_sequence)]
                for current_position, surface in enumerate(surfaces):
                    surface_ = decorate(surface, cursor_position, current_position)  # NOQA
                    surfaces_[current_position] = surface_

                if len_sequence - 1 == cursor_position:
                    ground_truthes.append('EOS')
                    break

                print('\t'.join(surfaces_))
                ground_truth = input('label ("bt" if you wanna go back): ')

                if ground_truth == 'bt':
                    cursor_position -= 1
                    if cursor_position < 0:
                        cursor_position = 0
                    continue

                if ground_truth not in labels:
                    print(f'label {ground_truth} is not in defined labels')

                ground_truthes[cursor_position] = ground_truth
                cursor_position += 1

            for s, m, l in zip(surfaces, features, ground_truthes):
                print(f'{s}\t{m}\t{l}')

            if input('ok? [y/n]: ') == 'y':
                for s, m, l in zip(surfaces, features, ground_truthes):
                    print(f'{s}\t{m}\t{l}', file=args.annotation_file)

                print('', file=args.annotation_file)
                break
