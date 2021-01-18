from utils import *
from collections import deque

def space_before(token1, token2):
    """return True if the two token need to be separete with espace"""
    if token1 == None or \
            token1 in "{([" or \
            token2 in "})],." or \
            token1 == "\\begin" or \
            token1[0] == "\\" or \
            token1[-1] == "=" or \
            token2[0] == "=":
        return False

    return token1 == "--" or \
           token2 == "--" or \
           token1[-1].isalpha() or \
           token2[0].isalpha() or \
           token1[-1].isdigit() or \
           token2[0].isdigit()


class MultiDimensionalArray(list):
    def __init__(self, data):
        """Set a MultiDimensionalArray

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda
        [1, [2, 3, [4], [5]]]
        >>> mda[1]
        [2, 3, [4], [5]]
        """
        list.__init__(self, data)

    def to_string(self, tabulation="    ", expend=False, raw=False):
        """return indented string of the MultiDimensionalArray

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.to_string()
        '1 2 3 4 5'
        >>> mda = MultiDimensionalArray([1,'\\n',[2,3,'\\n',[4],'\\n',[5]]])
        >>> print(mda.to_string())
        1 
             2 3 
                 4
                 5
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> print(mda.to_string(expend=True))
        1
             2
             3
                 4
                 5
        """

        back_to_line = True

        def branch(branch_data, deep=0, last_token=None):
            nonlocal back_to_line, expend
            text = ""
            for token in branch_data:
                if isinstance(token, list):
                    text += branch(token, deep=deep + 1, last_token=last_token)
                    continue

                token = repr(token) if raw else str(token)

                if back_to_line:
                    text += tabulation * deep
                    back_to_line = False

                if space_before(last_token, token):
                    text += " "

                text += token

                if token == "\n":
                    back_to_line = True
                if expend:
                    back_to_line = True
                    text += "\n"

                last_token = token

            return text

        return branch(self).rstrip()

    def get_element(self, index):
        """return the element poited by the index

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.get_element([])
        [1, [2, 3, [4], [5]]]
        >>> mda.get_element([1,2])
        [4]
        >>> node = mda.get_element([1,3])
        >>> node.append(6)
        >>> mda
        [1, [2, 3, [4], [5, 6]]]
        """
        assert isinstance(index, list) or isinstance(index, Pointer) or isinstance(index,
                                                                                   tuple), "index must be a list, tuple or Pointer"
        elements = self
        for i in index:
            assert isinstance(elements, list) or 0 <= i < len(elements), "index point out of MultiDimensionalArray"
            elements = elements[i]
        return elements

    def set_element(self, index, element):
        """set a new element at the index position
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.set_element([1,2], 42)
        >>> mda
        [1, [2, 3, 42, [5]]]
        """
        node = self.get_element(index[:-1])
        node[index[-1]: index[-1] + 1] = [element]

    def DFS(self, on_node=True, on_leaf=True, max_deep=-1):
        """make a deep first search on the mda

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> [index for token, index in mda.iter_data(DFS=True)]
        [[0], [1], [1, 0], [1, 1], [1, 2], [1, 2, 0], [1, 3], [1, 3, 0]]
        >>> [token for token, index in mda.iter_data(DFS=True)]
        [1, [2, 3, [4], [5]], 2, 3, [4], 4, [5], 5]
        """
        stack_index = [[position] for position in range(len(self))][::-1]
        stack_token = [node for node in self][::-1]

        while stack_token:
            index = stack_index.pop()
            token = stack_token.pop()

            if not isinstance(token, list):
                if on_leaf:
                    yield [token, Pointer(token, index=index)]

            else:
                if on_node:
                    yield [token, Pointer(token, index=index)]

                if len(index) == max_deep:
                    continue

                for position, token in reversed(list(enumerate(token))):
                    stack_token.append(token)
                    stack_index.append(index + [position])

    def BFS(self, on_node=True, on_leaf=True, max_deep=-1):
        """make a breadth first search on the mda

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> [token for token, index in mda.iter_data()]
        [1, [2, 3, [4], [5]], 2, 3, [4], [5], 4, 5]
        >>> [index for token, index in mda.iter_data()]
        [[0], [1], [1, 0], [1, 1], [1, 2], [1, 3], [1, 2, 0], [1, 3, 0]]
        >>> [token for token, index in mda.iter_data(on_node=False)]
        [1, 2, 3, 4, 5]
        """
        fifo_index = deque([[position] for position in range(len(self))])
        fifo_token = deque([node for node in self])

        while fifo_index:
            index = fifo_index.popleft()
            token = fifo_token.popleft()

            if not isinstance(token, list):
                if on_leaf:
                    yield [token, Pointer(self, index=index)]

            else:
                if on_node:
                    yield [token, Pointer(self, index=index)]

                if len(index) == max_deep:
                    continue

                for position, new_token in enumerate(token):
                    fifo_token.append(new_token)
                    fifo_index.append(index + [position])

    def iter_data(self, on_node=True, on_leaf=True, index_start=[0], max_deep=-1, DFS=False):
        """make a BFS on the MultiDimensionalArray and return [element, index] at each node

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> [token for token, index in mda.iter_data()]
        [1, [2, 3, [4], [5]], 2, 3, [4], [5], 4, 5]
        >>> [index for token, index in mda.iter_data()]
        [[0], [1], [1, 0], [1, 1], [1, 2], [1, 3], [1, 2, 0], [1, 3, 0]]
        >>> [token for token, index in mda.iter_data(on_node=False)]
        [1, 2, 3, 4, 5]
        >>> [index for token, index in mda.iter_data(DFS=True)]
        [[0], [1], [1, 0], [1, 1], [1, 2], [1, 2, 0], [1, 3], [1, 3, 0]]
        >>> [token for token, index in mda.iter_data(DFS=True)]
        [1, [2, 3, [4], [5]], 2, 3, [4], 4, [5], 5]

        """
        assert isinstance(on_node, bool), "on_node must be a bool"
        assert isinstance(on_leaf, bool), "on_leaf must be a bool"
        assert isinstance(index_start, list), "index_start must be a list"
        assert isinstance(max_deep, int), "max_deep must be a int"

        mda = []  # rebuild mda from index_start
        branch = self.get_element(index_start[:-1])
        for position in range(index_start[-1], len(branch)):
            mda.append(branch[position])
        mda = MultiDimensionalArray(mda)

        if DFS:
            for token, index in mda.DFS(on_node=on_node, on_leaf=on_leaf, max_deep=max_deep):
                index[0] += index_start[-1]
                yield [token, Pointer(self, index=index_start[:-1] + index)]

        else:
            for token, index in mda.BFS(on_node=on_node, on_leaf=on_leaf, max_deep=max_deep):
                index[0] += index_start[-1]
                yield [token, Pointer(self, index=index_start[:-1] + index)]

    def filter(self, fct_check, max_element=-1, **args_iter):
        """selection a total of max_element when fct_check return true, fct_check is call with in parameter the
        element and his index

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> fct_check = lambda element, index: (isinstance(element, int) and element%2 == 0)
        >>> [mda.get_element(index) for index in mda.filter(fct_check)]
        [2, 4]
        """
        assert isinstance(max_element, int), "max_element must be a int"
        assert callable(fct_check), "fct_check need to be callable"
        selection = []
        for element, index in self.iter_data(**args_iter):
            if fct_check(element, index):
                selection.append(Pointer(self, index=index))
                if len(selection) == max_element:
                    break;
        return selection

    def search(self, value, **args):
        """return all index who match with the value

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.search(2)
        [[1, 0]]
        >>> mda.get_element([1, 0])
        2
        """
        return self.filter(lambda element, index: element == value, **args)

    def search_regex(self, pattern, **args):
        """return all index who match with the value
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> odd_number = r"^\d*[13579]$"
        >>> [mda.get_element(index) for index in mda.search_regex(odd_number)]
        [1, 3, 5]
        """
        assert isinstance(pattern, str), "pattern need to ba a string"
        return self.filter(lambda element, index: re.search(pattern, str(element)), on_node=False, **args)

    def append(self, index, element, extend=False):
        """append a new element at the index node index
    
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.append([1,3],6)
        >>> mda
        [1, [2, 3, [4], [5, 6]]]

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.append([1,3,0],6)        
        >>> mda
        [1, [2, 3, [4], [5, 6]]]
        """
        if not isinstance(self.get_element(index), list):
            index.pop()
        node = self.get_element(index)
        if not extend:
            element = [element]
        node[::] = node[::] + element

    def remove(self, index):
        """append a new element at the index node index
    
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.remove([1,3])
        >>> mda
        [1, [2, 3, [4]]]

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.remove([1])        
        >>> mda
        [1]
        """
        node = self.get_element(index[:-1])
        del node[index[-1]]

    def insert(self, index, element, extend=False):
        """insert element at the left of index

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> mda.insert([0],0)
        >>> mda
        [0, 1, [2, 3, [4], [5]]]
        """
        node = self.get_element(index[:-1])
        position = index[-1]
        if not extend:
            element = [element]
        node[position:position] = element


class Pointer(list):
    def __init__(self, mda, index=[0]):
        """Set a pointer on a MultiDimensionalArray class
       
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p
        [0]
        """
        # super(Pointer, self).__init__(index) ?
        self.mda = mda
        if mda == []:
            index = []
        list.__init__(self, index)

    def get_index(self):
        """return the index of the pointer
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p
        [0]
        >>> p.get_index()
        [0]
        """
        return self

    def set_index(self, index):
        """set a new index
       
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p
        [0]
        >>> p.set_index([0,2,0])
        >>> p
        [0, 2, 0]
        """
        self[::] = index

    def get_element(self):
        """returns the pointed item
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p.get_element()
        1
        >>> p.go_to(1)
        >>> p.get_element()
        [2, 3, [4], [5]]
        """
        return self.mda.get_element(self)

    def set_element(self, element):
        """set a element at the index position
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1,2])
        >>> p.set_element(42)
        >>> p.get_parent()
        [2, 3, 42, [5]]
        >>> mda
        [1, [2, 3, 42, [5]]]

        """
        self.mda.set_element(self, element)

    def go_to(self, position):
        """go on a certain position
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p
        [0]
        >>> p.go_to(1)
        >>> p
        [1]
        """
        assert isinstance(position, int), "position must be a int"
        assert position >= 0, "index must be positive"
        # self[-1] = self.merge_index(position)
        self[-1] = position

    def get_position(self):
        """return the last index
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[0,3])
        >>> p.get_position()
        3
        """
        return self[-1] if self != [] else 0

    def get_parent(self):
        """return the parent element of the pointed item
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p.get_element()
        1
        >>> p.get_parent()
        [1, [2, 3, [4], [5]]]

        >>> p = Pointer(mda, index=[1,3])
        >>> p.get_element()
        [5]
        >>> p.get_parent()
        [2, 3, [4], [5]]
        """
        return self.mda.get_element(self[:-1])

    def merge_index(self, i, loop=True):
        """return the nearest correct index
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p.merge_index(99)
        1
        >>> p.set_index([1,3])
        >>> p.merge_index(-1)
        4
        >>> p.merge_index(-99)
        0
        """
        if i < 0:
            if i < - len(self.get_parent()) or loop == False:
                return 0
            else:
                return len(self.get_parent()) + i + 1
        elif i >= len(self.get_parent()):
            return len(self.get_parent()) - 1
        return i

    def move(self, step):
        """move the cursor of step position
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1,0])
        >>> p.move(2)
        >>> p
        [1, 2]

        >>> p.move(-9)
        >>> p
        [1, 0]
        """
        assert isinstance(step, int), "step must be a int"
        self[-1:] = [self.merge_index(self.get_position() + step, loop=False)]  # wip

    def go_next(self):
        self.move(1)

    def go_back(self):
        self.move(-1)

    def go_down(self):
        """go down a node
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1])
        >>> p.go_down()
        >>> p
        [1, 0]
        """
        assert isinstance(self.get_element(), list), "element need to be node to go deeper"
        self += [0]

    def go_up(self):
        """go up a node
        
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1,0])
        >>> p.go_up()
        >>> p
        [1]
        """
        assert self != [], "can go up at root"
        self.pop()

    def move_until(self, function, step=1):
        """move the pointer until the function return True"""
        last_position = self.get_position()
        self.move(step)
        while last_position != self.get_position() and function(self.get_element(), self) == False:
            last_position = self.get_position()
            self.move(step)

    def next_node(self):
        """go next node

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1,0])
        >>> p.next_node()
        >>> p
        [1, 2]
        >>> p.get_element()
        [4]
        """
        return self.move_until(lambda token, index: isinstance(token, list))

    def previous_node(self):
        """go to the previous node"""
        return self.move_until(lambda token, index: isinstance(token, list), step=-1)

    def find_next(self, element):
        """move pointer to the next occurence
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1,0])
        >>> p.find_next([4])
        >>> p
        [1, 2]
        """
        self.move_until(lambda token, index: token == element)

    def append(self, element, extend=False):
        """append a new element at the index node index
    
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1,3])
        >>> p.append(6)
        >>> mda
        [1, [2, 3, [4], [5], 6]]
        >>> p.get_parent()
        [2, 3, [4], [5], 6]

        """
        remember_position = self.get_position()
        self.go_up()
        self.mda.append(self, element, extend=extend)
        self.go_down()
        self.go_to(remember_position)

    def remove(self):
        """append a new element at the index node index
    
        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda, index=[1,3])
        >>> p.remove()
        >>> mda
        [1, [2, 3, [4]]]
        """
        self.mda.remove(self)

    def insert(self, element, extend=False):
        """insert element at the left of index

        >>> mda = MultiDimensionalArray([1,[2,3,[4],[5]]])
        >>> p = Pointer(mda)
        >>> p.insert(0)
        >>> mda
        [0, 1, [2, 3, [4], [5]]]
        """
        self.mda.insert(self, element, extend=extend)

    def is_coordinate(self):
        """check is pointed element is a couple (x, ",", y)

        >>> mda = MultiDimensionalArray([1,[2,3,[4, 5]]])
        >>> p = Pointer(mda, index=[1,2])
        >>> p.is_coordinate()
        True
        """
        node = self.get_element()
        if not isinstance(node, list):
            return False

        if not 2 <= len(node) <= 3:
            return False

        if not is_float(node[0]) or not is_float(node[-1]):
            return False
        return True

    def next_coordinate(self):
        self.move_until(lambda token, index: index.is_coordinate())

    def previous_coordinate(self):
        self.move_until(lambda token, index: index.is_coordinate(), step=-1)


if __name__ == '__main__':
    import doctest

    # doctest.testmod()
    doctest.run_docstring_examples(MultiDimensionalArray.iter_data, globals())
