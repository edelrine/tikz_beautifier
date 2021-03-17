import time
import argparse
import traceback
from class_latex import *
from class_multidimensionalarray import * 

def tikz_beautifier(file, multidimensional=False ,**DEFAULT_OPTION):
    """run beautifier from python return (latex result, logs)
    set multidimensional=True if you want to get only multidensional array"""
    error_log=""
    latex = Latex(file)
    dirpath, filename = os.path.split(os.path.abspath(__file__))

    options = {arg:True for arg in args}
    for arg, value in kargs:
        options[arg] = value

    
    def run(fct, error_message, **args):
        nonlocal error_log
        try:
            return fct(**args)
        except:
            error_log += "["+error_message+"]" +"\n" + traceback.format_exc() + "\n"


    def set_colors():
        if "no_color" in options.keys():
            return
        rgb_to_name = {}
        with open(os.path.join(dirpath, "colors", "rgb_to_name.csv"), "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rgb_to_name[row[0]] = [int(row[1]), int(row[2]), int(row[3])]
        latex.rename_colors(rgb_to_name)
    run(set_colors, "set colors")


    def set_clip():
        if "no_clip" in options.keys():
            return
        latex.tikz_set_clip(fixed_margin=options["clip_fix"], dynam_margin=options["clip_dyn"])
    run(set_clip, "set clip")


    def round_digit():
        if not "round" in options.keys() or int(options["round"]) == 0:
            return
        latex.round_digit(nb_digit=int(options["round"]))
    run(round_digit, "round digit")

    latex.tikz_sort_line(ordinate_first=options["ordinate_first"],
                             decreasing_abscissa=options["decreasing_abscissa"],
                             decreasing_ordinate=options["decreasing_ordinate"])


    def sort_lines():
        if "no_sort" in options.keys():
            return
        latex.tikz_sort_line(ordinate_first=options["ordinate_first"],
                             decreasing_abscissa=options["decreasing_abscissa"],
                             decreasing_ordinate=options["decreasing_ordinate"])
    run(sort_lines, "sort lines")


    def tikz_only():
        if "tikz_only" in options.keys():
            return
        latex.tikz_only()
    run(tikz_only, "tikz only")

    if multidimensional:
        return latex, error_log

    latex_result = "No result"
    def get_result():
        nonlocal latex_result
        strip = not 'no_strip' in options.keys() or options['no_strip'] == False
        latex_result = latex.to_string(tabulation=options["tab"], strip=strip)
    run(get_result, "get result")
    return latex_result, error_log




def tikz_beautifier_command_line(path_file, *args, **kargs):
    """run beautifier from terminal"""
    TIME_START = time.time()
    error_log = ""
    dirpath, filename = os.path.split(os.path.abspath(__file__))

    options = {arg:True for arg in args}
    for arg, value in kargs:
        options[arg] = value

    def run(fct, error_message, **args):
        nonlocal error_log
        try:
            return fct(**args)
        except:
            error_log += "["+error_message+"]" +"\n" + traceback.format_exc() + "\n"


    def open_file():
        with open(path_file, "r") as file:
            return "".join(file.read())
    latex = run(open_file, "Open file") 

    if latex == []:
        error += "[Open file] :\nParsed file is empty.\n"
        return;


    latex_result, logs = tikz_beautifier(latex, *args, **kargs)
    error_log += logs


    def show_latex():
        if "hide" in options.keys():
            return
        print(latex_result, "\n")
    run(show_latex, "show result")


    def save():
        if "no_save" in options.keys():
            return
        name = path_file.split("/")[-1].split(".")[0]
        file_to_save = "".join([p + "/" for p in path_file.split("/")[:-1]]) + name + "_clear.tikz"
        with open(file_to_save, 'w+') as d:
            d.write(latex_result)
        print("file save as", file_to_save)
    run(save, "save file")


    if error_log != "":
        t = time.localtime()
        error_log += "Log make at : " + str( time.strftime("%H:%M:%S", t)) + "\n"
        print("\n Error :",error_log,"\n\n")


    def save_error_log():
        with open(os.path.join(dirpath, "tikz_beautifier.log"), 'w+') as d:
            d.write(error_log)
    run(save_error_log, "save error log")

    print("End in", round(time.time() - TIME_START, 4), "s")




if __name__ == '__main__':
    #extract command line parameters, see tikz_beautifier_command_line or tikz_beautifier for main code
    parser = argparse.ArgumentParser(description="Formats a Tikz code",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('path', type=str, help="the path of the file to convert")
    parser.add_argument('-tab', type=str, help="the tabulation you want", default="\t")
    parser.add_argument('-round', type=int,
                        help="round to ndigits precision after the decimal point, set -1 if you didn't want to round number",
                        default=3)
    parser.add_argument('-no-color', help="dont gives a name to colors", action='store_true')
    parser.add_argument('-no-save', help="dont saves in the same location as the source", action='store_true')
    parser.add_argument("-hide", help="dont show the result in the terminal", action='store_true')
    parser.add_argument("-no-sort", help="dont sort \\drawn", action='store_true')
    parser.add_argument("-ordinate-first", "-of", help="sort the blocks by ordinate then by abscissa",
                        action='store_true')
    parser.add_argument("-decreasing-abscissa", "-da", help="sorted abscissa in decreasing order", action='store_true')
    parser.add_argument("-decreasing-ordinate", "-do", help="sorted ordinate in decreasing order", action='store_true')
    parser.add_argument("-by-type", help="separates blocks by category (circle, line, rectangle, etc...)",
                        action='store_true')
    parser.add_argument("-no-clip", help="dont set automatic clip", action='store_true')
    parser.add_argument("-clip-fix", type=float, help="specifies a fixed margin", default="1")
    parser.add_argument("-clip-dyn", type=float, help="specifies a dynamic margin (%)", default="0.1")
    parser.add_argument("-tikz-only", "-to", help="remove Latex default importation", action='store_true')

    parser.add_argument("-no-strip", "-ns", help="keep extra spaces", action='store_true')

    args = parser.parse_args()
    options = {}
    for keys, value in vars(args).items():
        options[keys] = value
    tikz_beautifier_command_line(options["path"], **options)
