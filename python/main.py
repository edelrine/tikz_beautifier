import time
import logging
import argparse
import traceback
from class_latex import *
from class_multidimensionalarray import *

dirpath, filename = os.path.split(os.path.abspath(__file__))
logging.basicConfig(
    format="[%(levelname)-7s][%(funcName)-14s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("beautifier")
logger.setLevel(logging.CRITICAL+1) #desactivate log

def run(fct, condition=True, *args, **kargs):
    try:
        time_start = time.time()
        if condition :
            logger.debug("Starting "+fct.__name__)
            return fct(*args, **kargs)
        else :
            logger.debug("Skipping "+fct.__name__)
            return None
    except:
        logger.exception("["+fct.__name__+"]")
        return None

    finally:
        logger.debug("Ending   {:<20} in {:<6}s.".format(fct.__name__, str(round(time.time() - time_start, 3))))            


def beautifier(file, multidimensional=False ,**options):
    """run beautifier from python
    return the latex string or the multidimensional object of set to true
    set multidimensional=True if you want to get the multidensional array and not the formatted string"""
    LOCALTIME = time.localtime()
    dirpath, filename = os.path.split(os.path.abspath(__file__))
    logger = logging.getLogger("beautifier")
    logger.setLevel(
        [logging.WARNING, logging.INFO, logging.DEBUG]
        [min(options.get("v",2), 2)]
    )
    logger.debug("Start from function, "+str(time.asctime(LOCALTIME)))
    logger.debug("Dirpath : "+str(dirpath)+" filename "+str(filename))


    latex = run(Latex,True, file)


    def set_colors(latex):
        rgb_to_name = {}
        with open(os.path.join(dirpath, "colors", "rgb_to_name.csv"), "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rgb_to_name[row[0]] = [int(row[1]), int(row[2]), int(row[3])]
        latex.rename_colors(rgb_to_name)
    run(set_colors, 
        not options.get("no_color", False), 
        latex
    )


    def show_source(file):
        logger.info("source :\n\n"+str(file)+"\n")
    run(show_source, 
        not options.get("hide_source", False), 
        file
    )

    def set_clip(latex, options):
        latex.tikz_set_clip(
            fixed_margin=options.get("clip_fix",1), 
            dynam_margin=options.get("clip_dyn",0.1))
    run(set_clip,
        options.get("no_clip", False),
        latex, options
    )

    
    def round_digit(latex, options):
        latex.round_digit(nb_digit=int(options.get("round", 3)))
    run(round_digit, 
        int(options.get("round",3)) != 0, 
        latex, options
    )
    
    def sort_lines(latex, options):
        latex.tikz_sort_line(
            ordinate_first=options.get("ordinate_first",False),
            decreasing_abscissa=options.get("decreasing_abscissa",False),
            decreasing_ordinate=options.get("decreasing_ordinate",False))
    run(sort_lines, 
        not options.get("no_sort",False)
        , latex, options
    )


    def tikz_only(latex, options):
        latex.tikz_only()
    run(tikz_only, 
        options.get("tikz_only",False), 
        latex, options
    )


    if multidimensional:
        return latex

    def get_result(latex, options):
        strip = options.get('no_strip',False) == False
        return latex.to_string(tabulation=options.get("tab","\t"), strip=strip)
    return run(get_result, True, latex, options)


def beautifier_CLI(path_file, **options):
    """run beautifier from terminal"""

    LOCALTIME = time.localtime()
    dirpath, filename = os.path.split(os.path.abspath(__file__))
    logger = logging.getLogger("beautifier")
    logger.setLevel(
        [logging.WARNING, logging.INFO, logging.DEBUG]
        [min(options.get("v",2), 2)]
    )
    logger.debug("Start from command line, "+str(time.asctime(LOCALTIME)))
    logger.debug("Dirpath : "+str(dirpath)+" filename "+str(filename))

    
    def open_file(path_file):
        with open(path_file, "r") as file:
            return "".join(file.read())
    latex = run(open_file, True, path_file)

    if latex == []:
        logger.warning("[Open file] :\nParsed file is empty.\n")
        return None

    latex_result = run(beautifier,True, latex, **options)
    if latex_result == None:
        logger.warning("latex_result is empty")
        return None

    def show_result(latex_result):
        logger.info("Result :\n\n"+str(latex_result) + "\n")
    run(show_result, 
        not options.get("hide_output",False),
        latex_result
    )

    
    def save(path_file):
        name = path_file.split("/")[-1].split(".")[0]
        file_to_save = "".join([p + "/" for p in path_file.split("/")[:-1]]) + name + "_clear.tikz"
        with open(file_to_save, 'w+') as d:
            d.write(latex_result)
        logger.info("file save as" + str(file_to_save))
    run(save,
        options.get("no_save",False),
        path_file
    )

    logger.debug("End at "+str(time.asctime(LOCALTIME))+"s")

if __name__ == '__main__':
    #extract command line parameters, see beautifier_CLI or beautifier for main code
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
        help="level of debugging, -v to -vv (no output, infos, debug)",
        action='count',
        default=0)
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

    clipping = parser.add_argument_group(title="Clipping (experimental)")
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
    beautifier_CLI(options["path"], **options)
