from tkinter import filedialog as fd
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

def abspath(*paths:str):
    """
    
    >>> abspath("/bob", "charlie", "marco", "harley")
    >>> abspath("documents/c", "save00")
    >>> abspath("save00")
    """
    res = ""
    for path in paths:
        path = str(path).replace("~", str(HOME))
        res = os.path.abspath(os.path.join(res, path))
    return res

def ensure_dir_exists(dirpath):
    dirpath = os.path.abspath(dirpath)
    if not os.path.isfile(dirpath) and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)


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


def load_config(filename, save_dir=None, source_dir=None, store_dir=None, dry_run=False):
    global CONFIG
    filename = remove_zip_end(filename, '.json') + '.json'
    fp = open(filename, 'r')
    result = json.load(fp)
    fp.close()
    if save_dir is not None:
        result["SaveDir"] = save_dir
    if source_dir is not None:
        result["SourceDir"] = source_dir
    if store_dir is not None:
        result["StoreDir"] = store_dir
    # result["SaveDir"] = os.path.abspath(
    #     str(result["SaveDir"]).replace('~', str(HOME)))

    result["SourceDir"] = os.path.abspath(
        str(result["SourceDir"]).replace('~', str(HOME)))

    result["StoreDir"] = os.path.abspath(
        str(result["StoreDir"]).replace('~', str(HOME)))

    if dry_run:
        return result
    else:
        CONFIG = result


def save_game(save_name):
    global CONFIG
    ensure_dir_exists(CONFIG['StoreDir'])
    save_name = remove_zip_end(basename(save_name)) + '.zip'
    zipname = path.abspath(path.join(CONFIG['StoreDir'], save_name))
    zipdir(dirname=CONFIG['SaveDir'], zipname=zipname,
           source_dir=CONFIG['SourceDir'])


def has_ending(name, end):
    name = str(name)
    end = str(end)
    n = len(end)
    return end==name[-n:]

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
    files = list(filter(lambda x : has_ending(x, '.zip'), files))
    files.sort(reverse=True, key=lambda x: os.path.getmtime(
        os.path.join(CONFIG['StoreDir'], x)))
    for save_name in files:
        save_name = remove_zip_end(basename(save_name))
        yield save_name


def list_saves():
    return list(_list_saves())

### Display ###


# Where the configuration files are stored for this tool
CONFIG_DIR = path.abspath(path.join(HOME, '.game_backup_config')) if os.getenv(
    'CONFIG_DIR') is None else os.getenv('CONFIG_DIR')

ensure_dir_exists(CONFIG_DIR)


def create_page1(log):
    page1 = tk.Frame()
    button_frame = tk.Frame(page1)
    button_frame.style = ttk.Style()
    button_frame.style.theme_use("default")
    button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    savelist_frame = tk.Frame(page1)
    savelist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    saves_title = tk.Label(savelist_frame, text="--Game Save Files--")
    saves_title.pack(side=tk.TOP, padx=0, pady=0)
    saves_list = Listbox(savelist_frame, width=40)
    saves_list.pack(side=tk.TOP, padx=0, pady=0)

    config_title = tk.Label(button_frame, text="--Select Game Config--")
    config_title.pack(side=tk.TOP, padx=0, pady=1)
    config_options = []
    config_selector = ttk.Combobox(
        button_frame, values=config_options, width=20)
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

    inner_data = {
        'current_save': None
    }

    def update_config_options(*args, **kwargs):
        files = list(filter(lambda x: has_ending(x, '.json'), os.listdir(CONFIG_DIR)))
        files = list(map(lambda x : remove_zip_end(x, '.json'), files))
        config_selector['values'] = (files)

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
        selects = list(saves_list.curselection())
        if len(selects) >= 1:
            
            select_to_delete = saves_list.get(selects[0])
            log("Deleting:", select_to_delete)
            try:
                delete_game(select_to_delete)
            except Exception as e:
                log("Error:", e)
            update_saves_list()

    config_selector.bind("<<ComboboxSelected>>", update_saves_list)
    config_selector.bind("<Button>", update_config_options)
    saves_list.bind("<<ListboxSelect>>", update_chosen_save)
    save_button.bind("<Button>", call_save)
    load_button.bind("<Button>", call_load)
    delete_button.bind("<Button>", call_delete)
    return page1


def askdirectory(initialdir=HOME, title="Select A Directory", **kwargs):
    return fd.askdirectory(initialdir=initialdir, title=title, **kwargs)


def create_page2(log):
    page2 = tk.Frame()
    left_panel = tk.Frame(page2)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH)
    right_panel = tk.Frame(page2)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

    config_title = tk.Label(left_panel, text='--Available Config Files--')
    config_list = tk.Listbox(left_panel, width=25)
    config_title.pack(side=tk.TOP, fill='x', pady=0)
    config_list.pack(side=tk.TOP, fill='y')

    name_label = tk.Label(right_panel, text="--Name of Config File--")
    name_entryvar = tk.StringVar()
    name_entry = tk.Entry(right_panel, textvariable=name_entryvar)
    name_buttons = tk.Frame(right_panel)
    refresh_button = tk.Button(left_panel, text="Refresh", bg="#c0c0c0")
    refresh_button.pack(side=tk.TOP)
    save_button = tk.Button(name_buttons, text="Save", bg='#9cff9c')
    rename_button = tk.Button(name_buttons, text="Rename", bg='#9c9cff')
    del_button = tk.Button(name_buttons, text="Delete", bg='#ff9c9c')

    name_label.pack(side=tk.TOP, fill='x')
    name_entry.pack(side=tk.TOP, fill='x')
    name_buttons.pack(anchor=tk.CENTER)
    # name_buttons.pack(side=tk.TOP, fill='x', anchor=tk.CENTER)
    # save_button.pack(side=tk.LEFT, fill='x')
    # rename_button.pack(side=tk.LEFT, fill='x')
    # del_button.pack(side=tk.LEFT, fill='x')
    # refresh_button.grid(row=0, column=0)
    save_button.grid(row=0, column=1)
    rename_button.grid(row=0, column=2)
    del_button.grid(row=0, column=3)

    save_label = tk.Label(right_panel, text="--Choose the folder to backup--")
    save_entryvar = tk.StringVar()
    save_entry = tk.Entry(right_panel, textvariable=save_entryvar)
    save_filepicker = tk.Button(
        right_panel, text="Choose Folder", bg='#9c9c9c')

    store_label = tk.Label(
        right_panel, text="--Choose the folder to store backups in--")
    store_entryvar = tk.StringVar()
    store_entry = tk.Entry(right_panel, textvariable=store_entryvar)
    store_filepicker = tk.Button(
        right_panel, text="Choose Folder", bg='#9c9c9c')

    save_label.pack(side=tk.TOP, fill='x')
    save_entry.pack(side=tk.TOP, fill='x')
    save_filepicker.pack(side=tk.TOP)

    store_label.pack(side=tk.TOP, fill='x')
    store_entry.pack(side=tk.TOP, fill='x')
    store_filepicker.pack(side=tk.TOP)

    def logger_exception(func):
        def inner(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                log("Error:", e)
        return inner
    @logger_exception
    def update_config_list(*args, **kwargs):
        files = list(filter(lambda x: has_ending(x, '.json'), os.listdir(CONFIG_DIR)))
        files = list(map(lambda x : remove_zip_end(x, '.json'), files))
        config_list.delete(0, tk.END)
        for i, conf_name in enumerate(files):
            config_list.insert(i, conf_name)

    @logger_exception
    def update_config_entry(*args, **kwargs):
        selects = list(config_list.curselection())
        if len(selects) >= 1:
            select = config_list.get(selects[0])
            name_entryvar.set(select)
    @logger_exception
    def update_save_entry(*args, **kwargs):
        selects = list(config_list.curselection())
        if len(selects) >= 1:
            select = config_list.get(selects[0])
            conf = load_config(path.abspath(path.join(CONFIG_DIR, select)), dry_run=True)
            save_entryvar.set(os.path.abspath(os.path.join(conf['SourceDir'], conf['SaveDir'])))
    @logger_exception
    def update_store_entry(*args, **kwargs):
        selects = list(config_list.curselection())
        if len(selects) >= 1:
            select = config_list.get(selects[0])
            conf = load_config(path.abspath(path.join(CONFIG_DIR, select)), dry_run=True)
            store_entryvar.set(conf['StoreDir'])
    @logger_exception
    def button_refresh_action(*args, **kwargs):
        update_config_list()
        # update_config_entry()
        # update_save_entry()
        # update_store_entry()
    @logger_exception
    def button_save_action(*args, **kwargs):
        filename = remove_zip_end(name_entryvar.get(), '.json') + '.json'
        filepath = path.abspath(path.join(CONFIG_DIR, filename))
        store_dir = store_entryvar.get()
        save_dir  = save_entryvar.get()


        if store_dir == '':
            raise ValueError("Directory/Folder to store backups is not specified!")
        elif not os.path.isdir(store_dir):
            ensure_dir_exists(store_dir)
        if not os.path.isdir(save_dir):
            raise FileNotFoundError("Directory/Folder to be backed up does not exist!")

        store_dir = os.path.abspath(store_dir)
        save_dir  = os.path.abspath(save_dir)
        data = {
            "StoreDir" : store_dir,
            "SaveDir"  : basename(save_dir),
            "SourceDir": os.path.dirname(save_dir)
        }

        with open(filepath, 'w') as f:
            json.dump(data, f)

        update_config_list()
    @logger_exception
    def button_rename_action(*args, **kwargs):
        dstname = remove_zip_end(name_entryvar.get(), '.json') + '.json'
        dstpath = path.abspath(path.join(CONFIG_DIR, dstname))
        selects = list(config_list.curselection())
        if len(selects) >= 1:
            select = config_list.get(selects[0])
            srcname = remove_zip_end(select, '.json') + '.json'
            srcpath = path.abspath(path.join(CONFIG_DIR, srcname))
            os.rename(srcpath, dstpath)
        update_config_list()
    
    @logger_exception
    def button_delete_action(*args, **kwargs):
        selects = list(config_list.curselection())
        if len(selects) >= 1:
            select = config_list.get(selects[0])
            srcname = remove_zip_end(select, '.json') + '.json'
            srcpath = path.abspath(path.join(CONFIG_DIR, srcname))
            os.remove(srcpath)
        update_config_list()

        update_config_list()

    @logger_exception
    def filepick_save(*args, **kwargs):
        filename = save_entryvar.get()
        if not os.path.exists(filename):
            filename = HOME
        filename = askdirectory(filename)
        if os.path.exists(filename):
            save_entryvar.set(os.path.abspath(filename))

    @logger_exception
    def filepick_store(*args, **kwargs):
        filename = store_entryvar.get()
        if not os.path.exists(filename):
            filename = HOME
        filename = askdirectory(filename)
        if os.path.exists(filename):
            store_entryvar.set(os.path.abspath(filename))
    @logger_exception
    def config_list_action(*args, **kwargs):
        update_config_entry()
        update_save_entry()
        update_store_entry()

    config_list.bind("<<ListboxSelect>>", config_list_action)
    refresh_button.bind("<Button>", button_refresh_action)
    save_button.bind("<Button>", button_save_action)
    rename_button.bind("<Button>", button_rename_action)
    del_button.bind("<Button>", button_delete_action)
    save_filepicker.bind("<Button>", filepick_save)
    store_filepicker.bind("<Button>", filepick_store)
    page2.bind("<Button>", update_config_list)

    update_config_list()
    
    return page2


def main():
    # Open Window
    WINDOW = tk.Tk()

    log_textvar = tk.StringVar(value="(Status)")
    log_label = tk.Label(textvariable=log_textvar)

    def log(*args, sep=" ", prefix="(Status) "):
        log_textvar.set(prefix + sep.join(map(str, args)))
        print(prefix, *args)

    # Add/Create Widgets
    notebook = ttk.Notebook()
    page1 = create_page1(log)
    notebook.add(page1, text="Saves")
    page2 = create_page2(log)
    notebook.add(page2, text="Settings")
    notebook.pack()

    WINDOW.title("Game Backup Manager")

    ### Last thing to do is pack the Status Label ###
    log_label.pack(side=tk.BOTTOM, fill='x')

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
