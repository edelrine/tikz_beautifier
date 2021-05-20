import time
import argparse
import traceback
from class_latex import *
from class_multidimensionalarray import *

def tikz_beautifier(file, multidimensional=False ,**options):
    """run beautifier from python
    return (latex result, logs)
    set multidimensional=True if you want to get the multidensional array and not the formatted string"""
    error_log=""
    latex = Latex(file)
    dirpath, filename = os.path.split(os.path.abspath(__file__))
    def run(fct, **args):
        nonlocal error_log
        try:
            return fct(**args)
        except:
            error_log += "["+fct.__name__+"]" +"\n" + traceback.format_exc() + "\n"

    @run
    def set_colors():
        rgb_to_name = {}
        with open(os.path.join(dirpath, "colors", "rgb_to_name.csv"), "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rgb_to_name[row[0]] = [int(row[1]), int(row[2]), int(row[3])]
        latex.rename_colors(rgb_to_name)
    if not options["no_color"]:
        set_colors


    @run
    def show_source():
            print("source :")
            print(file)
            print()
    if not options["hide_source"]:
        show_source


    @run
    def set_clip():
        latex.tikz_set_clip(fixed_margin=options["clip_fix"], dynam_margin=options["clip_dyn"])
    if options["no_clip"]:
        set_clip



    @run
    def round_digit():
        latex.round_digit(nb_digit=int(options["round"]))
    if int(options["round"]) != 0:
        round_digit


    @run
    def sort_lines():
        latex.tikz_sort_line(ordinate_first=options["ordinate_first"],
                             decreasing_abscissa=options["decreasing_abscissa"],
                             decreasing_ordinate=options["decreasing_ordinate"])
    if not options["no_sort"]:
        sort_lines


    @run
    def tikz_only():
        latex.tikz_only()
    if options["tikz_only"]:
        tikz_only


    if multidimensional:
        return latex, error_log

    latex_result = "No result"
    @run
    def get_result():
        nonlocal latex_result
        strip = options['no_strip'] == False
        latex_result = latex.to_string(tabulation=options["tab"], strip=strip)
    get_result
    return latex_result, error_log



def tikz_beautifier_command_line(path_file, **options):
    """run beautifier from terminal"""
    TIME_START = time.time()
    error_log = ""
    dirpath, filename = os.path.split(os.path.abspath(__file__))

    def run(fct, **args):
        nonlocal error_log
        try:
            return fct(**args)
        except:
            error_log += "["+fct.__name__+"]" +"\n" + traceback.format_exc() + "\n"
            return None

    @run
    def open_file():
        with open(path_file, "r") as file:
            return "".join(file.read())
    latex = open_file


    if latex == []:
        error += "[Open file] :\nParsed file is empty.\n"
        return;

    latex_result, logs = tikz_beautifier(latex, **options)
    error_log += logs

    @run
    def show_result():
        print(latex_result, "\n")
    if not options["hide_output"]:
        show_result

    @run
    def save():
        name = path_file.split("/")[-1].split(".")[0]
        file_to_save = "".join([p + "/" for p in path_file.split("/")[:-1]]) + name + "_clear.tikz"
        with open(file_to_save, 'w+') as d:
            d.write(latex_result)
        print("file save as", file_to_save)
    if options["no_save"]:
        save


    if error_log != "":
        t = time.localtime()
        error_log += "Log make at : " + str( time.strftime("%H:%M:%S", t)) + "\n"
        print("\n Error :",error_log,"\n\n")

    @run
    def save_error_log():
        with open(os.path.join(dirpath, "tikz_beautifier.log"), 'w+') as d:
            d.write(error_log)
    save_error_log

    print("End in", round(time.time() - TIME_START, 4), "s")



if __name__ == '__main__':
    #extract command line parameters, see tikz_beautifier_command_line or tikz_beautifier for main code
    parser = argparse.ArgumentParser(
        prog="Tikz Beautifier",
        description="Formats a Tikz code",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Enjoy !"
    )

    #required 
    parser.add_argument('path', 
        type=str, 
        help="the path of the file to convert")


    formatting = parser.add_argument_group(title="Formatting")
    formatting.add_argument('-tab', 
        type=str, 
        help="the tabulation you want", default="\t")
    formatting.add_argument("-tikz-only", "-to",
        help="remove Latex default importation",
        action='store_true')
    formatting.add_argument("-no-strip", "-ns",
        help="keep extra spaces",
        action='store_true')


    clean_up = parser.add_argument_group(title="Clean up")
    clean_up.add_argument('-round',
        type=int,
        help="round to ndigits precision after the decimal point, set -1 if you didn't want to round number",
        default=3)
    clean_up.add_argument('-no-color',
        help="dont gives a name to colors",
        action='store_true')

    CLI = parser.add_argument_group(title="Commande line settings")
    CLI.add_argument('-v',
        help="level of debugging, -v to -vvv",
        action='count',
        default="0")
    CLI.add_argument('-no-save',
        help="dont saves in the same location as the source",
        action='store_true')
    CLI.add_argument("-hide-source", "-hs",
        help="show source from input",
        action='store_true')
    CLI.add_argument("-hide-output", "-ho",
        help="dont show the result in the terminal",
        action='store_true')

    sorting = parser.add_argument_group(title="Sorting")
    sorting.add_argument("-no-sort",
        help="dont sort \\drawn",
        action='store_true')
    sorting.add_argument("-bytype",
        help="separates blocks by category (circle, line, rectangle, etc...)",
        action='store_true')
    sorting.add_argument("-ordinate-first", "-of",
        help="sort the blocks by ordinate then by abscissa",
        action='store_true')
    sorting.add_argument("-decreasing-abscissa", "-da",
        help="sorted abscissa in decreasing order",
        action='store_true')
    sorting.add_argument("-decreasing-ordinate", "-do",
        help="sorted ordinate in decreasing order",
        action='store_true')

    clipping = parser.add_argument_group(title="Clipping")
    clipping.add_argument("-no-clip",
        help="dont set automatic clip",
        action='store_true')
    clipping.add_argument("-clip-fix",
        type=float,
        help="specifies a fixed margin",
        default="1")
    clipping.add_argument("-clip-dyn",
        type=float,
        help="specifies a dynamic margin, in percent",
        default="0.1")

    args = parser.parse_args()
    options = {keys : value for keys, value in vars(args).items()}
    tikz_beautifier_command_line(options["path"], **options)
