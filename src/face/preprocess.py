import os
from pathlib import Path

path_prefix='face_data/'

def options_get():
    return [path_prefix+'color_faces/', path_prefix+'gray_faces/']

# def options_set_default():
#     with open('options/key_bindings.txt', 'w') as f:
#         f.write("save_path_color = 'data/color_faces/'" + '\n')
#         f.write("save_path_gray = 'data/gray_faces/'" + '\n')


def check_dirs_data():
    for d in options_get():
        if not Path(d).is_dir():
            os.mkdir(d)

    if not os.path.isfile(path_prefix+'users.txt'):
        with open(path_prefix+'users.txt', 'w'): pass


def preprocessing():
    check_dirs_data()
    return [*options_get()]