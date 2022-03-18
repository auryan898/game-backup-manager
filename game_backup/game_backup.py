from tkinter.constants import HORIZONTAL
import tkinter as tk
from tkinter import Listbox, Scale, ttk, StringVar, TclError, Button as TkButton
from os.path import basename
from zipfile import ZipFile
import os
from os import path
import pathlib
import json

from numpy import source

HOME = pathlib.Path.home()

CONFIG = {
    "StoreDir": path.abspath(path.join(HOME, 'Documents/GameSaves')),
    "SourceDir": None,
    "SaveDir": None
}


def zipdir(dirname, zipname="sample.zip", source_dir='./'):
    cwd = os.getcwd()
    os.chdir(os.path.abspath(source_dir))
    # dirname = path.abspath(path.join(path.abspath(source_dir), dirname))
    with ZipFile(zipname, 'w') as zipobj:
        # Iterate over all the files in directory
        for foldername, subfolders, filenames in os.walk(dirname):
            for filename in filenames:
                # Create complete filepath of file in directory
                filepath = os.path.join(foldername, filename)
                # Add file to zip
                zipobj.write(filepath, (filepath))
    os.chdir(cwd)


def unzipdir(zipname="sample.zip", source_dir='./'):
    with ZipFile(zipname, 'r') as zipobj:
        zipobj.extractall(source_dir)


def load_config(filename, save_dir=None, source_dir=None, store_dir=None):
    global CONFIG
    fp = open(filename, 'r')
    CONFIG = json.load(fp)
    fp.close()
    if save_dir is not None:
        CONFIG["SaveDir"] = save_dir
    if source_dir is not None:
        CONFIG["SourceDir"] = source_dir
    if store_dir is not None:
        CONFIG["StoreDir"] = store_dir
    CONFIG["SaveDir"] = str(CONFIG["SaveDir"]).replace('~', str(HOME))

    CONFIG["SourceDir"] = str(CONFIG["SourceDir"]).replace('~', str(HOME))

    CONFIG["StoreDir"] = str(CONFIG["StoreDir"]).replace('~', str(HOME))


def save_game(save_name):
    global CONFIG
    save_name = remove_zip_end(basename(save_name)) + '.zip'
    zipname = path.abspath(path.join(CONFIG['StoreDir'], save_name))
    zipdir(dirname=CONFIG['SaveDir'], zipname=zipname,
           source_dir=CONFIG['SourceDir'])


def remove_zip_end(name, end='.zip'):
    name = str(name)
    n = len(end)
    if end == name[-n:]:
        return name[:-n]
    return name


def load_game(save_name):
    global CONFIG
    save_name = remove_zip_end(basename(save_name)) + '.zip'
    zipname = path.abspath(path.join(CONFIG['StoreDir'], save_name))
    unzipdir(zipname=zipname, source_dir=CONFIG['SourceDir'])

def delete_game(save_name):
    save_name = remove_zip_end(basename(save_name)) + '.zip'
    zipname = path.abspath(path.join(CONFIG['StoreDir'], save_name))
    os.remove(zipname)

def _list_saves():
    global CONFIG
    files = os.listdir(CONFIG['StoreDir'])
    files.sort(reverse=True, key=lambda x: os.path.getmtime(os.path.join(CONFIG['StoreDir'],x)))
    for save_name in files:
        save_name = remove_zip_end(basename(save_name))
        yield save_name


def list_saves():
    return list(_list_saves())

### Display ###


# Where the configuration files are stored for this tool
CONFIG_DIR = path.abspath(path.join(HOME, '.game_backup_config')) if os.getenv(
    'CONFIG_DIR') is None else os.getenv('CONFIG_DIR')

def create_page1():
    page1 = tk.Frame()
    button_frame = tk.Frame(page1)
    button_frame.style = ttk.Style()
    button_frame.style.theme_use("default")
    button_frame.pack(side=tk.RIGHT, expand=True)

    savelist_frame = tk.Frame(page1)
    savelist_frame.pack(side=tk.LEFT, expand=True)


    saves_title = tk.Label(savelist_frame, text="--Game Save Files--")
    saves_title.pack(side=tk.TOP, padx=0, pady=0)
    saves_list = Listbox(savelist_frame, width=40)
    saves_list.pack(side=tk.TOP, padx=0, pady=0)

    config_title = tk.Label(button_frame, text="--Select Game Config--")
    config_title.pack(side=tk.TOP, padx=0, pady=1)
    config_options = list(map(lambda x: remove_zip_end(
        basename(x), end='.json'), os.listdir(CONFIG_DIR)))
    config_selector = ttk.Combobox(button_frame, values=config_options, width=20)
    config_selector.pack(side=tk.TOP, padx=0, pady=0)

    load_button = tk.Button(button_frame, text='Load', bg='#9c9cff')
    load_button.pack(side=tk.TOP, fill='x', pady=10)

    entry_label = tk.Label(button_frame, text='--Current Save Name--')
    entry_label.pack(side=tk.TOP, fill='x')
    save_textvar = tk.StringVar()
    save_text = tk.Entry(button_frame, textvariable=save_textvar)
    save_text.pack(side=tk.TOP, fill='x', pady=0)
    save_button = tk.Button(button_frame, text='Save', bg='#9cff9c')
    save_button.pack(side=tk.TOP, fill='x', pady=0)
    delete_button = tk.Button(button_frame, text='Delete', bg='#ff7777')
    delete_button.pack(side=tk.TOP, fill='x', pady=10)
    
    log_textvar = tk.StringVar(value="(Status)")
    log_label = tk.Label(textvariable=log_textvar)
    log_label.pack(side=tk.BOTTOM, fill='x')
    
    inner_data = {
        'current_save': None
    }

    def log(*args, sep=" ", prefix="(Status) "):
        log_textvar.set(prefix + sep.join(map(str, args)))
        print(prefix, *args)

    def update_saves_list(*args, **kwargs):
        filename = config_selector.get() + '.json'
        load_config(path.abspath(path.join(CONFIG_DIR, filename)))
        
        saves_list.delete(0, tk.END)
        for i, save_name in enumerate(_list_saves()):
            saves_list.insert(i, save_name)

    def update_chosen_save(*args, **kwargs):
        selects = list(saves_list.curselection())
        if len(selects) >= 1:
            select = saves_list.get(selects[0])
            inner_data['current_save'] = select
            save_textvar.set(select)
        else:
            return

    def call_save(*args, **kwargs):
        name = save_textvar.get()
        log("Saving:", name)
        try:
            save_game(name)
            log("Done Saving Game:", name)
        except Exception as e:
            log("Error: Could not save", name, "\n|", e, "|")

        update_saves_list()
    
    def call_load(*args, **kwargs):
        name = save_textvar.get()
        log("Loading:", name)
        try:
            load_game(name)
            log("Done Loading Game:", name)
        except Exception as e:
            log("Error: Could not load", name, "\n|", e, "|")

    def call_delete(*args, **kwargs):
        log("Deleting:", save_textvar.get())
        delete_game(save_textvar.get())
        update_saves_list()

    config_selector.bind("<<ComboboxSelected>>", update_saves_list)
    saves_list.bind("<<ListboxSelect>>", update_chosen_save)
    save_button.bind("<Button>", call_save)
    load_button.bind("<Button>", call_load)
    delete_button.bind("<Button>", call_delete)
    return page1

def main():
    # Open Window
    WINDOW = tk.Tk()

    # Add/Create Widgets
    notebook = ttk.Notebook()
    page1 = create_page1()
    notebook.add(page1, text="Saves")
    page2 = tk.Frame()
    notebook.add(page2, text="Settings")
    notebook.pack()

    WINDOW.title("Game Backup Manager")

    
    # Pack in the elements

    # Start Main Loop
    WINDOW.mainloop()


if __name__ == '__main__':
    # zipdir('save00')
    # unzipdir()
    # load_config('config.json')
    # save_game('new_save')
    # load_game('new_save')
    # print(list(list_saves()))
    main()
