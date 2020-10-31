# tikz_convert.py
from collections import deque       #BFS iterator
import argparse                     #command line argument
import csv                          #read color data
import os.path                      #open files to convert
import os                           #find cwd
import re                           #find regex
import sys                          #command line argument
import time                         #record performance

DEFAULT_OPTION =   {
    "tab":"\t",
    "round":3,
    "no_color":False,
    "no_save":True,
    "hide":False,
    "no_sort":False,
    "decreasing_abscissa":False,
    "decreasing_ordinate":False,
    "ordinate-first":False,
    "by_type":False,
    "no_clip":False,
    "clip_fix":1,
    "clip_dyn":0.1,
    "tikz_only":False
}


SEPARATOR_START = ("(","[","{","\\begin")
SEPARATOR_END = (")","]","}","\\end")
REGEX_SPLIT_DATA = "(\[|\]|\(|\)|\{|\}|,|\n|=|\dcm|\dpt)"
SPACE_BEFORE = ("(","{")
SPACE_AFTER = (",",")")
BANNER = "\n*-------*\n"
regex_float = "[-+]?\d*\.\d+|\d+"

################################################################
####################Basique#####################################
################################################################
def dif(a,b) :
    return abs(a-b)

def is_float(string) :
    if string[0] in ("-","+") :
        string = string[1::]
    return string.replace('.', '', 1).isdigit()

def get_element(data, index) :
    """return the element after all index contain in index"""
    for i in index :
        data = data[i]
    return data

################################################################
####################Colors######################################
################################################################
def get_color_name(data,r,g,b) :
    """return a color name, r,g,b need to be float"""
    minn = 99999999
    minn_name = "no name"
    for name, rgb in data.items() :
        score = dif(rgb[0],r)**2 + dif(rgb[1],g)**2 + dif(rgb[2],b)**2
        if score < minn :
            minn = score
            minn_name = name
    return minn_name

def get_colors_name(data,colors) :
    """return a color names for each colors without duplicate"""
    names = []
    for color in colors :
        name = get_color_name(data, *color)
        del data[name]
        names.append(name)
    return names

################################################################
####################Basic operations############################
################################################################
def parse_text(text) :
    """parse a text to text[line] = [command, options, parameters]"""
    parse_text = []
    for w in re.split(REGEX_SPLIT_DATA, text) :
        if w != "\n" :
            w = w.strip()
        if w != "" :
            parse_text.append(w)
    data = []

    def explore(i, data, deep = 0) :
        nonlocal parse_text

        while i < len(parse_text) :
            element = parse_text[i]
            if element in SEPARATOR_START :
                data.append(element)
                data.append([])
                i = explore(i+1, data[-1], deep = deep + 1)
                if i < len(parse_text) :
                    element = parse_text[i]
                    data.append(element)

            elif element in SEPARATOR_END :
                return i

            else :
                data.append(element)

            i += 1
        return i

    explore(0, data)
    return data

def tree_to_string(tree, tabulation) :
    """return a string of the Tikz"""
    back_to_line = True

    def print_branch(branch, deep = 0) :
        nonlocal back_to_line
        text = ""
        for i in branch :
            if not isinstance(i, str) :
                text += print_branch(i, deep = deep + 1)
            else :
                if back_to_line :   #tabulation
                    text += "".join([tabulation for _ in range(deep)])
                    back_to_line = False

                if i in SPACE_BEFORE :
                    text += " "

                if i == "\n" :      #go back to a new line
                    back_to_line = True
                text += i

                if i in SPACE_AFTER :
                    text += " "

        return text

    return print_branch(tree)


def iter_data(original_data, on_directory=True, on_element=True, stack_start = [], max_deep=-1) :
    """return an iterator on data, [element, stack index], based on BFS"""
    fifo_index = deque() 
    fifo_data = deque()

    if stack_start :
        fifo_index.append([stack_start[-1]])
        fifo_data.append(get_element(original_data,stack_start[:-1]))
        # print("stack start :",stack_start,"stack :",stack,"stack_data :",data_stack)
    else :
        fifo_index.append([0])
        fifo_data.append(original_data)

    while fifo_index :
        index = fifo_index.popleft()
        data = fifo_data.popleft()
        for i in range(index[-1],len(data)) :
            element = data[i]
            if (isinstance(element, list) and on_directory) or (isinstance(element, str) and on_element) :
                yield [element, stack_start[:-1] + index[:-1] + [i]]

            if isinstance(element, list) :
                if len(index) == max_deep :
                    continue
                fifo_index.append(index[:-1] + [i] + [0])
                fifo_data.append(element)   #python uses pointers ._.


def search(data, value, max_element = -1, **args_iter) :
    """return all index who match with the value
    value : all you want
    max_element : number of maximum element return
    stack_start : give the beginning of the dfs"""
    match = []
    counter = 0
    for element, index in iter_data(data, **args_iter) :
        if element == value or value == "":
            match.append(index.copy())
            counter += 1
            if counter == max_element :
                return match
    return match

def search_regex(data, regex, max_element = -1, **args_iter) :
    """return all index who match with the regex
    value : all you want
    max_element : number of maximum element return
    stack_start : give the beginning of the dfs"""
    match = []
    counter = 0
    for element, index in iter_data(data, on_directory=False, **args_iter) :
        if re.findall(regex, element) :
            match.append(index.copy())
            counter += 1
            if counter == max_element :
                return match
    return match

def next_index(data, value, max_element=1, **args_iter) :
    """return the index of the next reference"""
    counter = 0
    for element, stack_index in iter_data(data, **args_iter) :
        if element == value or value == "":
            counter += 1
            if counter == max_element :
                return stack_index
    return -1

def data_replace(data, old_value, new_value) :
    for element, index in iter_data(data, on_directory=False) :
        if element == old_value :
            element = get_element(data, index[:-1])
            element[index[-1]] = new_value

#Make a function to get directly the data after a begin ?

################################################################
####################Complex operations #########################
################################################################
def data_set_color_names(data, data_color) :
    """set a more comprehensible name for rgb colors"""
    colors_rgb = []
    colors_name = []
    min_index_color = [99999999]
    for color_index in search(data, '\\definecolor') :
        if color_index < min_index_color :
            min_index_color = color_index

        color = []
        for i in search(data, "", stack_start=color_index, on_element=False, max_element=3) :
            color.append(get_element(data, i))

        if len(color) == 3 and color[1] == ["rgb"] :
            color[2] = [float(value)*256 for value in color[2] if is_float(value)]
            if len(color[2]) == 3 :
                colors_rgb.append(color[2])
                colors_name.append(color[0][0])

    if colors_rgb :
        new_names = get_colors_name(data_color, colors_rgb)

        miss_replace = []
        for old_name, name, rgb in zip(colors_name, new_names, colors_rgb) :
            data_replace(data, old_name, name)
            if search_regex(data, str(old_name), max_element=1) :
                miss_replace.append((old_name, rgb))

        if miss_replace :   #some element aren't replace
            place_insert = get_element(min_index_color[:-1])
            index = min_index_color[-1]
            for old_name, rgb in miss_replace :
                place_insert = place_insert[:index] + ["\\definecolor", "{", [str(old_name)], "}", "{", ["rgb"], "}", "{", [str(rgb[0]), str(rgb[1]), str(rgb[2])], "}"]

            place_insert.insert(index,"%some color cant be replace, the define function are here")

def data_round_float(data, digit=2) :
    """round float at n digit"""
    for flt_index in search_regex(data, regex_float) :
        elements = get_element(data, flt_index[:-1])
        pos = flt_index[-1]
        if is_float(elements[pos]) :
            elements[pos] = str(round(float(elements[pos]), digit))

def sort_drawn_keys(line) :
    """return extracted information of a line ((y,x,type), ... )"""
    keys = [line[0][1], line[0][0], line[0][2]]
    if options["decreasing_ordinate"] : 
        keys[0] *= -1
    if options["decreasing_abscissa"] :
        keys[1] *= -1
    if options["ordinate_first"] :
        keys[0], keys[1] = keys[1], keys[0]
    if options["by_type"] :
        keys.insert(0, keys.pop())
    return keys

def data_drawn_sort(data) :
    """sort all \\drawn in the tikz"""
    def is_drawn(line) :
        if "\\draw" in line :
            coordinates = next_index(line, "(")
            coordinates = next_index(line, "", on_element=False, stack_start=coordinates)
            if coordinates != -1 :
                coor = get_element(line, coordinates)
                if is_float(coor[0]) and is_float(coor[-1]) :
                    categorie = next_index(line, "", max_element=3, max_deep=0, stack_start=coordinates)
                    categorie = get_element(line,categorie)
                    return [float(coor[0]), float(coor[-1]), categorie]
        return -1

    def sort_drawn(index_original) :
        """sort drawn in specific bloc"""
        local_data = get_element(data,index_original)
        # print("localdata :\n",tree_to_string(local_data, "\t"))
        drawn = []
        no_drawn = []
        line = []

        for elem, index in iter_data(local_data, max_deep = 1) :  #extract information
            if isinstance(elem, str) and elem.startswith("\\") :
                infos = is_drawn(line) 
                if infos != -1:
                    drawn.append([infos, line.copy()])
                else :
                    no_drawn.append(line.copy())
                line = []

            line.append(elem)

        if line :   #Clear Memory Cache
            infos = is_drawn(line) 
            if infos != -1:
                drawn.append([infos, line.copy()])
            else :
                no_drawn.append(line.copy())

        drawn.sort(key=sort_drawn_keys, reverse=True)
        local_data = get_element(data,index_original)
        local_data.clear()

        for l in no_drawn :
            local_data.extend(l)
        for l in drawn :
            local_data.extend(l[1])

    for begin in search(data, "\\begin") :
        categorie = next_index(data, "", max_element=1,on_element=False, stack_start=begin)
        if get_element(data, categorie)[1] == ["scriptsize"] or get_element(data, categorie)[1] == ["tikzpicture"]:
            sort_drawn(categorie)


def data_set_clip(data) :
    """Set the delimitation of the tikz picture"""
    clip_y_min = float("inf")
    clip_x_min = float("inf")
    clip_y_max = float("inf") * -1
    clip_x_max = float("inf") * -1

    for directory, path in iter_data(data, on_element=False) :
        if len(directory) == 3 :
            if is_float(directory[0]) and is_float(directory[2]) :
                x = float(directory[0])
                y = float(directory[2])
                clip_x_max = max(x, clip_x_max)
                clip_y_max = max(y, clip_y_max)
                clip_x_min = min(x, clip_x_max)
                clip_y_min = min(y, clip_y_max)

    if clip_y_max > clip_y_min and clip_x_max > clip_x_min :
        #else no (x,y) found
        lenght = max(clip_x_max - clip_x_min, clip_y_max - clip_y_min)
        margin = options["clip_fix"] + lenght * options["clip_dyn"]
        clip_y_min = round(clip_y_min - margin, 2)
        clip_x_min = round(clip_x_min - margin, 2)
        clip_y_max = round(clip_y_max + margin, 2)
        clip_x_max = round(clip_x_max + margin, 2)

    old_clip = search(data, "\\clip", max_element=1)
    if old_clip != -1 :
        old_clip = old_clip[0]
        group = get_element(data, old_clip[:-1])
        end_clip = next_index(group, ";", max_element=1, on_directory=False, stack_start=[old_clip[-1]])
        group[old_clip[-1]:end_clip[-1] + 2] = []


    for begin in search(data, "\\begin") :  #add clip on tikzpicture part
        adress = next_index(data, "", max_element=1,on_element=False, stack_start=begin)
        if adress != -1 and len(get_element(data, adress)) > 1 and get_element(data, adress)[1] == ["tikzpicture"] : 
            adress.append(3)
            if get_element(data, adress) == "[" :
                adress[-1] += 3 #put the \clip after optional parameters of tikzpicture
            d = get_element(data,adress[:-1])
            d[adress[-1]:adress[-1]] = parse_text(f"\n\\clip({clip_x_min},{clip_y_min}) rectangle ({clip_x_max},{clip_y_min});")
            break

def data_extract_document(data) :
    for begin in search(data, "\\begin") :  #add clip on tikzpicture part
        adress = next_index(data, "", max_element=1,on_element=False, stack_start=begin)
        if adress != -1 and len(get_element(data, adress)) > 1 and get_element(data, adress)[1] == ["document"] : 
            selection = get_element(data, adress).copy()[4:]    #remove ["{",["document"],"}","\n"]
            data *= 0
            data.extend(selection)
            return



################################################################
####################Main########################################
################################################################
def tikz_beautifier(path_file, options=DEFAULT_OPTION) :
    TIME_START = time.time()
    error = ""
    parsed_text = []

    try :
        with open(path_file, "r") as d:
            data = d.read()
        parsed_text = parse_text(data)
        if parsed_text == [] :
            error += "[Open file] :\nParsed file is empty.\n"
    except Exception as e :
        error += "[Open file] :\n" + str(e) + "\n"

    if not options["no_color"] :
        try :
            rgb_to_name = {}
            with open(os.path.join(os.getcwd(),"colors","rgb_to_name.csv"), "r") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    try :
                        if row[0] != "":
                            rgb_to_name[row[0]] = [int(row[1]),int(row[2]),int(row[3])]
                    except :
                        break
            data_set_color_names(parsed_text, rgb_to_name)
        except Exception as e :
            error += "[Set colors name] :\n" + str(e) + "\n"

    options["round"] = int(options["round"])
    if options["round"] >= 0:
        try :
            data_round_float(parsed_text)
        except Exception as e :
            error += "[Round float] :\n" + str(e) + "\n"

    if not options["no_sort"] :
        try :
            data_drawn_sort(parsed_text)
        except Exception as e :
            error += "[Sort drawn] :\n" + str(e) + "\n"

    if not options["no_clip"] :
        try :
            data_set_clip(parsed_text)
        except Exception as e :
            error += "[Set clip] :\n" + str(e) + "\n"


    if options["tikz_only"] :
        try :
            data_extract_document(parsed_text)
        except Exception as e :
            error += "[Tikz only] :\n" + str(e) + "\n"


    if not options["hide"] and parsed_text != []:
        try :
            print(tree_to_string(parsed_text, options["tab"]))
            print()
        except Exception as e :
            error += "[show result] :\n" + str(e) + "\n"

    if not options["no_save"] or True:
        try :
            name = path_file.split("/")[-1].split(".")[0]
            file_to_save = "".join([p + "/" for p in path_file.split("/")[:-1]]) + name + "_clear.tikz"
            with open(file_to_save, 'w+') as d:
                d.write(tree_to_string(parsed_text, options["tab"]))
            print("file save as",file_to_save)
        except Exception as e :
            error += "[save file] :\n" + str(e) + "\n"

    try :
        with open(os.path.join(os.getcwd(),"tikz_beautifier.log"), 'w+') as d:
            d.write(error)
    except Exception as e :
        error += "[save error file] :\n" + str(e) + "\n"

    if error != "" :
        print()
        print("Error :")
        print(error)
        print()


    print("End in",round(time.time() - TIME_START,4),"s")


################################################################
####################From command line###########################
################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Formats a Tikz code", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('path', type=str, help="the path of the file to convert")
    parser.add_argument('-tab', type=str, help="the tabulation you want", default="\t")
    parser.add_argument('-round', type=int, help="round to ndigits precision after the decimal point, set -1 if you didn't want to round number",default=3)
    parser.add_argument('-no-color', help="dont gives a name to colors", action='store_true')
    parser.add_argument('-no-save', help="dont saves in the same location as the source", action='store_true')
    parser.add_argument("-hide", help="dont show the result in the terminal", action='store_true')
    parser.add_argument("-no-sort", help="dont sort \\drawn", action='store_true')
    parser.add_argument("-ordinate-first", "-of", help="sort the blocks by ordinate then by abscissa", action='store_true')
    parser.add_argument("-decreasing-abscissa", "-da", help="sorted abscissa in decreasing order", action='store_true')
    parser.add_argument("-decreasing-ordinate", "-do", help="sorted ordinate in decreasing order", action='store_true')
    parser.add_argument("-by-type", help="separates blocks by category (circle, line, rectangle, etc...)", action='store_true')
    parser.add_argument("-no-clip", help="dont set automatic clip", action='store_true')
    parser.add_argument("-clip-fix", type=float, help="specifies a fixed margin", default="1")
    parser.add_argument("-clip-dyn", type=float, help="specifies a dynamic margin (%)", default="0.1")
    parser.add_argument("-tikz-only","-to", help="remove Latex default importation", action='store_true')


    args = parser.parse_args()
    # print(vars(args))
    options = DEFAULT_OPTION
    for keys, value in  vars(args).items() :
        options[keys] = value
    tikz_beautifier(options["path"],options=options)
