from class_latex import *
from class_multidimensionalarray import *


def tikz_beautifier(path_file, **DEFAULT_OPTION):
    TIME_START = time.time()
    error = ""

    try:
        with open(path_file, "r") as file:
            latex = Latex("".join(file.read()))
    except Exception as e:
        error += "[Open file] :\n" + str(e) + "\n"

    if latex == []:
        error += "[Open file] :\nParsed file is empty.\n"
        return;

    if not options["no_color"]:
        try:
            rgb_to_name = {}
            with open(os.path.join(os.getcwd(), "colors", "rgb_to_name.csv"), "r") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    rgb_to_name[row[0]] = [int(row[1]), int(row[2]), int(row[3])]
            latex.rename_colors(rgb_to_name)
        except Exception as e:
            error += "[Set colors name] :\n" + str(e) + "\n"

    if int(options["round"]) >= 0:
        try:
            latex.round_digit(nb_digit=int(options["round"]))
        except Exception as e:
            error += "[Round float] :\n" + str(e) + "\n"

    if not options["no_sort"]:
        try:
            latex.tikz_sort_line(ordinate_first=options["ordinate_first"],
                            decreasing_abscissa=options["decreasing_abscissa"],
                            decreasing_ordinate=options["decreasing_ordinate"])
        except Exception as e:
            error += "[Sort drawn] :\n" + str(e) + "\n"

    if not options["no_clip"]:
        try:
            latex.tikz_set_clip(fixed_margin=options["clip_fix"], dynam_margin=options["clip_dyn"])
        except Exception as e:
            error += "[Set clip] :\n" + str(e) + "\n"

    if options["tikz_only"]:
        try:
            latex.tikz_only()
        except Exception as e:
            error += "[Tikz only] :\n" + str(e) + "\n"

    if not options["hide"]:
        try:
            print(latex.to_string(tabulation=options["tab"]))
            print()
        except Exception as e:
            error += "[show result] :\n" + str(e) + "\n"

    if not options["no_save"] or True:
        try:
            name = path_file.split("/")[-1].split(".")[0]
            file_to_save = "".join([p + "/" for p in path_file.split("/")[:-1]]) + name + "_clear.tikz"
            with open(file_to_save, 'w+') as d:
                d.write(latex.to_string(tabulation=options["tab"]))
            print("file save as", file_to_save)
        except Exception as e:
            error += "[save file] :\n" + str(e) + "\n"

    try:
        with open(os.path.join(os.getcwd(), "tikz_beautifier.log"), 'w+') as d:
            d.write(error)
    except Exception as e:
        error += "[save error file] :\n" + str(e) + "\n"

    if error != "":
        print()
        print("Error :")
        print(error)
        print()

    print("End in", round(time.time() - TIME_START, 4), "s")


if __name__ == '__main__':
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

    args = parser.parse_args()
    # print(vars(args))
    options = {}
    for keys, value in vars(args).items():
        options[keys] = value
    tikz_beautifier(options["path"], **options)
