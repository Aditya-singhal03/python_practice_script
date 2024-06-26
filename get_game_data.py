import os
import json
import shutil
from subprocess import PIPE , run
import sys

GAME_DIR_PATTERN = 'game'
GAME_CODE_EXTENSION = '.go'
GAME_COMPILE_COMMAND = ['go' , 'build']

def compile_game_code(path):
    code_file_name = None
    for _, _, files in  os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break
        break

    if code_file_name==None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command , path)

def run_command(command,path):
    cwd = os.getcwd()
    os.chdir(path)

    result = run(command , stdout= PIPE , stdin= PIPE , universal_newlines=True)
    print("compiled result" , result)

    os.chdir(cwd)


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def find_all_game_path(source):
    game_paths = []

    for root, dirs, _ in os.walk(source):
        for dir in dirs:
            if GAME_DIR_PATTERN in dir.lower():
                game_paths.append(os.path.join(root,dir))
    
    return game_paths

def get_name_from_path(paths,to_strip):
    new_names = []
    for path in paths:
        _ , tail = os.path.split(path)
        tail = tail.replace(to_strip,'')
        new_names.append(tail)
    return new_names

def copy_and_overwrite(source,dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source,dest)

def make_json_metadata_file(path,game_dirs):
    data = {
        'gameNames':game_dirs,
        'numberOfGames':len(game_dirs)
    }

    with open(path,'w') as f:
        json.dump(data,f)

def main(source,target):
    cwd = os.getcwd()
    source_path = os.path.join(cwd,source)
    target_path = os.path.join(cwd,target)
    game_paths = find_all_game_path(source_path)

    create_dir(target_path)

    new_game_names = get_name_from_path(game_paths,"_game")
    for src , dest_name in zip(game_paths , new_game_names):
        dest_path = os.path.join(target_path,dest_name)
        copy_and_overwrite(src,dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path,"metadata.json")
    
    make_json_metadata_file(json_path,new_game_names)
    
   


if __name__=='__main__':
    args = sys.argv
    if len(args)!=3:
        print("you must pass a source and target directory - only.")
    source , target = args[1:]
    main(source,target)
