import sys
import os
import re
import shutil

USAGE = '''

To sort the files provide absolute or relative path to the 
folder where the files are stored as a argument.

EXAMPLES:
    > python main.py /path/to/folder
    > python main.py ./folder
    > python main.py d:\\folder

'''

if len(sys.argv) != 2:
    print(USAGE)
    sys.exit(0)

try:
    os.chdir(sys.argv[1])
    cwd = os.getcwd()    
except IOError as err:
    print('\nERROR occurred:', os.strerror(err.errno), '\n')
    sys.exit(0)

print(f'Processing folder {cwd}')
print()

categories = {
    'images'    : ('JPEG', 'PNG', 'JPG', 'SVG'),
    'video'     : ('AVI', 'MP4', 'MOV', 'MKV'),
    'documents' : ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
    'audio'     : ('MP3', 'OGG', 'WAV', 'AMR'),
    'archives'  : ('ZIP', 'GZ', 'TAR'),
    'others'    : ()
}

moved_files = {}
known_extensions = set()
unknown_extensions = set()

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
  
TRANSLATION_MAP = {}

for c, t in zip (CYRILLIC_SYMBOLS, TRANSLATION):
    TRANSLATION_MAP[ord(c)] = t
    TRANSLATION_MAP[ord(c.upper())] = t.upper()

def normalize(name):
    name = name.translate(TRANSLATION_MAP)
    if not name.isalnum():
        name = re.sub(r'\W', '_', name)
    return name

def lookup(folder, count=0):
    for item in os.listdir(folder):
        item_path = folder + '\\' + item
        if os.path.isdir(item_path):
            if item not in categories.keys():
                count = lookup(item_path, count)
        else:
            count += 1
            name, ext = re.search(r'(.*)\.(\w+)', item).groups()
            name = normalize(name)
            new_path = ''
            is_known = False
            for category, extensions in categories.items():
                if ext.upper() in extensions:
                    is_known = True
                    known_extensions.add(ext)
                    dst = cwd + '\\' + category
                    if not os.path.isdir(dst):
                        os.mkdir(dst)
                    if category == 'archives':
                        try:
                            shutil.unpack_archive(item_path, dst + '\\' + name)
                        except:
                            print(f'Could not unpack {item}, probably bad archive. Removing...')
                        finally:
                            os.remove(item_path)
                    else:
                        new_path = dst + '\\' + name + '.' + ext
                        os.rename(item_path, new_path)
                    if category in moved_files:
                        moved_files[category].append(name + '.' + ext)
                    else:
                        moved_files[category] = [name + '.' + ext]
                    break
            if not is_known:
                dst = cwd + '\\others'
                if not os.path.isdir(dst):
                    os.mkdir(dst)
                new_path = dst + '\\' + name + '.' + ext
                os.rename(item_path, new_path)
                unknown_extensions.add(ext)

            print(str(count), ':', item_path, '->', new_path)
    return count

print()
print(f'Total number of files in folder {cwd} is {lookup(cwd)}')
print()
print(f'The list of moved files per category: {moved_files}')
print()
print(f'All known extensions: {known_extensions}')
print()
print(f'All unknown extensions: {unknown_extensions}')