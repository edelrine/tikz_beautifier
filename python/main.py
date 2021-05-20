import time
import logging 
import argparse
import traceback
from class_latex import *
from class_multidimensionalarray import *
dirpath, filename = os.path.split(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def run(fct, condition, *args, **kargs):
    try:
        if condition :
            logging.debug("Starting "+fct.__name__)
            return fct(*args, **kargs)
        else :
            logging.debug("Passing "+fct.__name__)
            return None
    except:
        logging.exception("["+fct.__name__+"]")
        return None

def tikz_beautifier(file, multidimensional=False ,**options):
    """run beautifier from python
    return the latex string or the multidimensional object of set to true
    set multidimensional=True if you want to get the multidensional array and not the formatted string"""
    LOCALTIME = time.localtime()
    dirpath, filename = os.path.split(os.path.abspath(__file__))
    logging.debug("Start from function at"+str(time.asctime(LOCALTIME)))
    logging.debug("Dirpath : "+str(dirpath)+" filename "+str(filename))

    logging.info("Generating Latex file")
    latex = Latex(file)


    def set_colors(latex):
        rgb_to_name = {}
        with open(os.path.join(dirpath, "colors", "rgb_to_name.csv"), "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rgb_to_name[row[0]] = [int(row[1]), int(row[2]), int(row[3])]
        latex.rename_colors(rgb_to_name)
    run(set_colors, not options["no_color"], latex)


    def show_source(file):
        logging.info("source :\n"+str(file)+"\n")
    run(show_source, not options["hide_source"], file)


    def set_clip(latex, options):
        latex.tikz_set_clip(fixed_margin=options["clip_fix"], dynam_margin=options["clip_dyn"])
    run(set_clip, options["no_clip"], latex, options)

    
    def round_digit(latex, options):
        latex.round_digit(nb_digit=int(options["round"]))
    run(round_digit, int(options["round"]) != 0, latex, options)

    
    def sort_lines(latex, options):
        latex.tikz_sort_line(ordinate_first=options["ordinate_first"],
                             decreasing_abscissa=options["decreasing_abscissa"],
                             decreasing_ordinate=options["decreasing_ordinate"])
    run(sort_lines, not options["no_sort"], latex, options)


    def tikz_only(latex, options):
        latex.tikz_only()
    run(tikz_only, options["tikz_only"], latex, options)


    if multidimensional:
        return latex

    def get_result(latex, options):
        strip = options['no_strip'] == False
        return latex.to_string(tabulation=options["tab"], strip=strip)
    return run(get_result, True, latex, options)



def tikz_beautifier_command_line(path_file, **options):
    """run beautifier from terminal"""
    LOCALTIME = time.localtime()
    dirpath, filename = os.path.split(os.path.abspath(__file__))
    logging.debug("Start from command line at"+str(time.asctime(LOCALTIME)))
    logging.debug("Dirpath : "+str(dirpath)+" filename "+str(filename))

    
    def open_file(path_file):
        with open(path_file, "r") as file:
            return "".join(file.read())
    latex = run(open_file, True, path_file)

    if latex == []:
        logging.warning("[Open file] :\nParsed file is empty.\n")
        return None

    latex_result = run(tikz_beautifier,True, latex, **options)
    if latex_result == None:
        logging.warning("latex_result is empty")
        return None

    def show_result(latex_result):
        logging.info(str(latex_result) + "\n")
    run(show_result, not options["hide_output"], latex_result)

    
    def save(path_file):
        name = path_file.split("/")[-1].split(".")[0]
        file_to_save = "".join([p + "/" for p in path_file.split("/")[:-1]]) + name + "_clear.tikz"
        with open(file_to_save, 'w+') as d:
            d.write(latex_result)
        logging.info("file save as" + str(file_to_save))
    run(save, options["no_save"], path_file)

    logging.debug("End at "+str(time.asctime(LOCALTIME))+"s")

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
