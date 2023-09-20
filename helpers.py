import os
from hashlib import sha256
from random import randint
import operator

from constants import ALLOWED_EXTENSIONS


def generate_hash(st):
    return sha256(st.encode('utf-8')).hexdigest()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def quick_sort(ls, attribute=None):
    if len(ls) < 2:
        return ls
    pivot = randint(1, len(ls) - 1)
    left = []
    centre = []
    right = []
    for element in ls:
        if attribute:
            if operator.attrgetter(attribute)(element) < operator.attrgetter(attribute)(ls[pivot]):
                left.append(element)
            elif operator.attrgetter(attribute)(element) > operator.attrgetter(attribute)(ls[pivot]):
                right.append(element)
            else:
                centre.append(element)
        else:
            if element < ls[pivot]:
                left.append(element)
            elif element > ls[pivot]:
                right.append(element)
            else:
                centre.append(element)
    return quick_sort(left, attribute) + centre + quick_sort(right, attribute)


def save_file(file, course_name, topic_subtopic, sec_filename, root_path):
    file_name_from_request = file.filename
    if allowed_file(file_name_from_request):
        filename_for_save = f'{course_name}_{topic_subtopic}_{sec_filename}'
        folder_path = os.path.join(root_path, course_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, filename_for_save)
        file.save(file_path)
        return file_path
    return





if __name__ == '__main__':
    print(generate_hash('123456'))
    ls = [4, 6, 8, 2, 1, 8, 9, 6, 4]
    print(quick_sort(ls))
