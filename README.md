# Tikz_beautifier
This project is a beautifier for [Tikz](https://en.wikipedia.org/wiki/PGF/TikZ)code.
Tikz code is a derivate of [Latex](https://en.wikipedia.org/wiki/LaTeX), it's used for geometry.
You can generate Tikz on [Geogebra](https://www.geogebra.org/classic) if you go to the export options. 

# Features :
- Auto name colors
- Round float
- Sort drawn command line
    - by category 
    - by position 
- Clip function
- Remove auto latex import

Lightweight, only html, css and php !

# How to use this beautifier : 
### Online version :
The online version has all the features of off-line beautifer, it's only limited to 4000 characters.

### Web version offline :
If you want to install this site locally on your computer you can do :

On windows :
- Install Linux (Ubuntu) : Half a day and you have peace of mind for life
- Run it thanks python : 20 minutes you can automize the converter
- Run it on the Linux terminal of Windows : 2h, not tested
- Run it on Windows terminal : not tested

On Linux :
```sh
sudo apt install php git -y
git clone https://github.com/edelrine/tikz_beautifier.git
cd tikz_beautifier
php -S localhost:8000
```

Now, in your web browser, you can go on http://localhost:8000/converter.php

### Command line version :
You can use the command-line version if you want to automize this program:

On linux :
```sh
sudo apt install git -y
git clone https://github.com/edelrine/tikz_beautifier.git
cd tikz_beautifier
cd python
python3 main.py example_tikz/tikz_hug 
```

Of course, you can replace example_tikz/tikz_hug by your file to convert.

##### Command-line options :

-no-save : Don't save file after conversion
-tab TAB : Change ident by TAB (ex -tab "   ")
-round INT : Change the number of digit, (ex -round 2)(set to -1 if you don't want to round numbers
-no-color : Don't set colors names
-hide : Dont show result in terminal
-no-sort : Dont sort \drawn command in Tikz
-ordinate-first : sort the blocks by ordinate then by abscissa (also -of)
-decreasing-abscissa : sorted abscissa in decreasing order (also -da)
-decreasing-ordinate : sorted ordinate in decreasing order (also -do)
-by-type : Sort \drawn command in Tikz by category (circle, line, rectangle, etc...)
-no-clip : Dont define a limit for the picture
-clip-fix : Static margin for the clip
-clip-dyn : Dynamical clip margin based on percentage of element size (margin = clip-fix + max(width, lenght) * clip-dyn)
-tikz-only : Remove default import for Latex 


### To do :
- An more friendly interface
- Images to explain the parameters
- Host the online version
- Include the readme directly on the web page

License
----
 GPL-3.0 License 
