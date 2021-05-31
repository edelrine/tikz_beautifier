import re
import os
import csv
from utils import *
from class_multidimensionalarray import MultiDimensionalArray, Pointer


class Latex(MultiDimensionalArray):
    def __init__(self, string):
        """
        Init a Latex class based on MultiDimensionalArray.

        Latex class, is tolerant to alone close bracket and will avoid them,
        Alone open bracket will create new node.

        >>> latex = Latex("\\documentclass[10.3pt]{article}\\n\\\\begin{document}\\n\\section{A section}\\n\\end{document}")
        >>> latex
        ['\\\\documentclass', '[', ['10.3pt'], ']', '{', ['article'], '}', '\\n', '\\\\begin', ['{', ['document'], '}', '\\n', '\\\\section', '{', ['A section'], '}', '\\n'], '\\\\end', '{', ['document'], '}']
        """
        REGEX_FLAOT = r'[-+]\b[-+]?\d*\.*\d+'
        REGEX_SPLIT_DATA = r'(\[|\]|\(|\)|\{|\}|,|\n|=|--|' + REGEX_FLAOT + ')'
        BRACKET_OPEN = ('(', '[', '{', '\\begin')
        BRACKET_CLOSE = (')', ']', '}', '\\end')
        BRACKET_INVERSE = {
            **{o: c for o, c in zip(BRACKET_OPEN, BRACKET_CLOSE)},
            **{c: o for o, c in zip(BRACKET_OPEN, BRACKET_CLOSE)}
        }

        # parse latex
        stack_bracket = []
        latex = MultiDimensionalArray([''])
        pointer = Pointer(latex)

        for token in re.split(REGEX_SPLIT_DATA, string):
            # empty token
            if not token:
                continue

            # go up in the tree structure
            if token in BRACKET_CLOSE and BRACKET_INVERSE[token] in stack_bracket:
                while stack_bracket.pop() != BRACKET_INVERSE[token]:
                    pointer.go_up()
                pointer.go_up()

            # add token
            pointer.append(token)

            # strat child
            if token in BRACKET_OPEN:
                pointer.append([])
                pointer.next_node()
                pointer.go_down()
                stack_bracket.append(token)

        pointer.set_index([0])
        pointer.remove()  # remove ''

        super(Latex, self).__init__(latex)

    def rename_colors(self, data_colors):
        """
        rename all colors contains in the document with more explicite name

        >>> latex = Latex("\\definecolor{ududff}{rgb}{0.3,0.3,1} and I use ududff color !")
        >>> rgb_to_name = {}
        >>> with open(os.path.join(os.getcwd(),'colors','rgb_to_name.csv'), 'r') as csv_file:
        ...     csv_reader = csv.reader(csv_file, delimiter=',')
        ...     for row in csv_reader:
        ...         rgb_to_name[row[0]] = [int(row[1]),int(row[2]),int(row[3])]
        >>> latex.rename_colors(rgb_to_name)
        >>> latex
        ['\\\\definecolor', '{', ['Neon_Blue'], '}', '{', ['rgb'], '}', '{', ['0.3', ',', '0.3', ',', '1'], '}', 'and I use Neon_Blue color !']
        """
        for pointer in self.search('\\definecolor'):
            pointer.next_node()  # old
            old_name = pointer.get_element()[0]

            pointer.next_node()  # rgb
            if len(pointer.get_element()) == 0:
                continue  # empty  categorie
            if stripped(pointer.get_element()[0]) != 'rgb':
                continue  # unknow categorie

            pointer.next_node()  # hue {'0.3', ',', '0.3', ',', '1'}
            r, _, g, _, b = pointer.get_element()
            if not is_float(r) or not is_float(g) or not is_float(b):
                continue

            r, g, b = map(float, [r, g, b])
            new_name = get_color_name(data_colors, r * 256, g * 256, b * 256)
            for index_old_name in self.search_regex(str(old_name)):
                old_element = index_old_name.get_element()
                index_old_name.set_element(
                    old_element.replace(old_name, new_name))

    def round_digit(self, index_start=None, nb_digit=2):
        """
        Round float in the latex file

        >>> latex = Latex("\\definecolor{ududff}{rgb}{0.30196078431372547,1,1.000}")
        >>> latex.round_digit()
        >>> latex
        ['\\\\definecolor', '{', ['ududff'], '}', '{', ['rgb'], '}', '{', [0.3, ',', 1, ',', 1], '}']
        """
        if index_start is None:
            index_start = [0]
        for pointer in self.filter(
            lambda element, index:
            is_float(element),
            index_start=index_start
        ):
            token = float(pointer.get_element())
            pointer.set_element(
                int(token)
                if is_int(token)
                else round(float(token), nb_digit)
            )

    def get_tikz(self):
        """
        return a pointer for all tikz contain in latex

        >>> with open(os.path.join(os.getcwd(),'example_tikz','tikz_medium')) as latex:
        ...     txt = ''.join(latex.readlines())
        >>> latex = Latex(txt)
        >>> [pointer for pointer in latex.get_tikz()]
        [[20]]
        >>> [pointer.get_element() for pointer in latex.get_tikz()]
        [['{', ['tikzpicture'], '}', '[', [], ']', '\\n', '\\\\begin', ['{', ['scriptsize'], '}', '\\n', '\\\\draw', '[', ['color', '=', 'ududff'], ']', '(', ['-4.1', ',', '3.94'], ')', ' node ', '{', ['$c$'], '}', ';', '\\n'], '\\\\end', '{', ['scriptsize'], '}', '\\n']]
        """
        for pointer in self.search('\\begin'):
            pointer.next_node()  # go to \begin content
            pointer.go_down()  # enter the content
            pointer.next_node()  # go \begin categorie

            if isinstance(pointer.get_element(), list):
                if len(pointer.get_element()) == 0:
                    continue

                if stripped(pointer.get_element()[0]) == 'tikzpicture':
                    pointer.go_up()
                    yield pointer

    def tikz_set_clip(self, index_start=None, fixed_margin=1, dynam_margin=1.1):
        """
        set clip on tikz
        >>> txt = "\\draw[color=black] (-4, 4) node {$A$};\\n\\draw[color=Neon_Blue] (-3, 3.) node {$B$};\\n\\draw[fill=Neon_Blue] (9, 9) circle (2pt);"
        >>> latex = Latex(txt)
        >>> latex.tikz_set_clip()
        >>> latex.round_digit()
        >>> latex
        ['\\\\draw', '[', ['color', '=', 'black'], ']', ' ', '(', [-4, ',', 4], ')', ' node ', '{', ['$A$'], '}', ';', '\\n', '\\\\draw', '[', ['color', '=', 'Neon_Blue'], ']', ' ', '(', [-3, ',', 3], ')', ' node ', '{', ['$B$'], '}', ';', '\\n', '\\\\draw', '[', ['fill', '=', 'Neon_Blue'], ']', ' ', '(', [9, ',', 9], ')', ' circle ', '(', ['2pt'], ')', '\\n', '\\\\clip', '(', [-5.65, ',', 1.7], ')', 'rectangle', '(', [10.65, ',', 10.3], ')', ';']
        """
        if index_start is None:
            if [tikz for tikz in self.get_tikz()]:
                for tikz in self.get_tikz():
                    self.tikz_set_clip(
                        index_start=tikz, fixed_margin=fixed_margin, dynam_margin=dynam_margin)
            else:
                self.tikz_set_clip(
                    index_start=[0], fixed_margin=fixed_margin, dynam_margin=dynam_margin)
            return

        x_max, y_max = -float('inf'), -float('inf')
        x_min, y_min = float('inf'), float('inf')

        for pointer in self.search_regex('node|--|circle', index_start=index_start):
            # \draw[color=Neon_Blue] (-6.86, 2.24) node {$A$};
            pointer.previous_coordinate()
            if not pointer.is_coordinate():
                continue

            x, _, y = pointer.get_element()
            x, y = float(x), float(y)
            x_min = min(x_min, x)
            x_max = max(x_max, x)
            y_min = min(y_min, y)
            y_max = max(y_max, x)

        if x_max == -float('inf'):
            return  # no coordinate find

        x_center = (x_max + x_min) / 2
        y_center = (y_max + y_min) / 2
        x_range = (x_max - x_min) / 2
        y_range = (y_max - y_min) / 2

        x_range = x_range * dynam_margin + fixed_margin
        y_range = y_range * dynam_margin + fixed_margin

        if not [clip for clip in self.search('\\clip', index_start=index_start)]:
            # set new clip, for exemple : \clip (None, None) rectangle (None, None);
            pointer.find_next('\n')
            pointer.insert(['\n', '\\clip', '(', [None, ',', None], ')', 'rectangle', '(', [None, None], ')'],
                           extend=True)

        for pointer in self.search('\\clip', index_start=index_start):
            # edit clip
            pointer.next_node()
            pointer.set_element(
                [str(x_center - x_range), ',', str(y_center - y_range)])
            pointer.next_node()
            pointer.set_element(
                [str(x_center + x_range), ',', str(y_center + y_range)])

    def tikz_sort_line(self, index_start=[-1], ordinate_first=False, decreasing_abscissa=False,
                       decreasing_ordinate=False):
        """
        sorting by coordinates

        We start with point placed like this :
        A B
        C D

        >>> latex = Latex("\\drawn(0,1) node {A}\\n\\drawn(1,1) node {B}\\n\\drawn(0,0) node {C}\\n\\drawn(0,1) node {D}'Some things else'")
        >>> latex.tikz_sort_line()
        >>> [pointer.get_element() for pointer in latex.search_regex("A|B|C|D", DFS=True)]
        ['C', 'A', 'D', 'B']
        >>> latex.tikz_sort_line(decreasing_ordinate=True)
        >>> [pointer.get_element() for pointer in latex.search_regex("A|B|C|D", DFS=True)]
        ['A', 'D', 'B', 'C']
        >>> latex.tikz_sort_line(decreasing_abscissa=True)
        >>> [pointer.get_element() for pointer in latex.search_regex("A|B|C|D", DFS=True)]
        ['C', 'A', 'D', 'B']
        >>> latex.tikz_sort_line(ordinate_first=True)
        >>> [pointer.get_element() for pointer in latex.search_regex("A|B|C|D", DFS=True)]
        ['C', 'A', 'D', 'B']
        """
        if index_start == [-1]:
            if [tikz for tikz in self.get_tikz()]:
                for tikz in self.get_tikz():
                    self.tikz_sort_line(index_start=tikz, ordinate_first=ordinate_first,
                                        decreasing_abscissa=decreasing_abscissa,
                                        decreasing_ordinate=decreasing_ordinate)
            else:
                self.tikz_sort_line(index_start=[0], ordinate_first=ordinate_first,
                                    decreasing_abscissa=decreasing_abscissa, decreasing_ordinate=decreasing_ordinate)
            return

        lines = []
        line = []

        branch, position = self.get_element(index_start[:-1]), index_start[-1]
        for token in branch[position::]:
            line.append(token)
            if token == '\n':
                lines.append(line)
                line = []
        if line:
            lines.append(line)

        def get_line_order(line):
            nonlocal ordinate_first, decreasing_abscissa, decreasing_ordinate
            mda = MultiDimensionalArray(line)
            p = Pointer(mda)
            p.next_coordinate()
            if not p.is_coordinate():
                return (float('inf'), float('inf'))

            x, _, y = p.get_element().copy()
            x, y = float(x), float(y)

            if decreasing_abscissa:
                x *= -1

            if decreasing_ordinate:
                y *= -1

            if ordinate_first:
                return (y, x)
            return (x, y)

        lines.sort(key=lambda line: get_line_order(line))
        flatten_lines = []
        for line in lines:
            flatten_lines.extend(line)

        # set back the sorted line
        branch, position = self.get_element(index_start[:-1]), index_start[-1]
        branch[position::] = flatten_lines

    def tikz_only(self, n=0):
        tikzs = [tikz for tikz in self.get_tikz()]
        self = tikzs[n].get_element()


latex = Latex(
    "\\documentclass[10.3pt]{article}\\n\\\\begin{document}\\n\\section{A section}\\n\\end{document}")

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    # doctest.run_docstring_examples(Latex.get_tikz, globals())
