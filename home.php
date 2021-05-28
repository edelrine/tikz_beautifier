<!DOCTYPE html>
<html>

    <?php include("header.php"); ?>

    <body>
		<h1>Tikz_beautifier</h1>
		<p>This project is a beautifier for <a href="https://en.wikipedia.org/wiki/PGF/TikZ">Tikz</a> code.
		Tikz code is a derivate of <a href="https://en.wikipedia.org/wiki/LaTeX">Latex</a>, it's used for geometry.<br />
		You can generate Tikz on <a href="https://www.geogebra.org/classic">Geogebra</a> if you go to the export options. 
	</p>
		<h1>Features :</h1>
		<ul>
			<li>Auto name colors</li>
			<li>Round float</li>
			<li>Sort drawn command line
			<ul>
				<li>by category </li>
				<li>by position </li>
			</ul>
		</ul>

		<p>Lightweight, only html, css and php !</p>

		<h1>How to use this beautifier :</h1>
		<h3>Online version :</h3>

		<p>The online version has all the feature of off-line beautifer, it's only limited to 4000 characters.</p>
		<h3>Web version offline :</h3>
		<p>If you want to install this site locally on your computer you can do :</p>
		<p>On windows :</p>
		<ul>
			<li>Install Linux (Ubuntu) : Half a day and you have peace of mind for life</li>
			<li>Run it thanks python : 20 minutes you can automize the converter</li>
			<li>Run it on the Linux terminal of Windows : 2h, not tested, only Windows 10</li>
			<li>Run it on Windows terminal : not tested</li>
		</ul>
		<br />
		<p>On Linux :</p>
		<pre>
			<code class="language-sh">
sudo apt install php git -y
git clone https://github.com/edelrine/tikz_beautifier.git
cd tikz_beautifier
php -S localhost:8000
			</code>
		</pre>
		<p>Now, in your web browser, you can go on <a href="http://localhost:8000/converter.php">http://localhost:8000/converter.php</a></p>

		<h3>Command line version :</h3>
		<p>You can use the command-line version if you want to automize this program:</p>
		<p>On linux :</p>
		<pre>
			<code class="language-sh">
sudo apt install git -y
git clone https://github.com/edelrine/tikz_beautifier.git
cd tikz_beautifier
cd python
python3 main.py example_tikz/tikz_hug
			</code>
		</pre>

		<p>Of course, you can replace example_tikz/tikz_hug by your file to convert.</p>
		<h5>Command-line options :</h5>
		<p>-no-save : Don't save file after conversion<br />
			-tab TAB : Change ident by TAB (ex -tab &quot;   &quot;)<br />
			-round INT : Change the number of digit, (ex -round 2)(set to -1 if you don't want to round numbers<br />
			-no-color : Don't set colors names<br />
			-hide : Dont show result in terminal<br />
			-no-sort : Dont sort \drawn command in Tikz<br />
			-ordinate-first : sort the blocks by ordinate then by abscissa (also -of)<br />
			-decreasing-abscissa : sorted abscissa in decreasing order (also -da)<br />
			-decreasing-ordinate : sorted ordinate in decreasing order (also -do)<br />
			-by-type : Sort \drawn command in Tikz by category (circle, line, rectangle, etc...)<br />
			-no-clip : Dont define a limit for the picture<br />
			-clip-fix : Static margin for the clip<br />
			-clip-dyn : Dynamical clip margin based on percentage of element size (margin = clip-fix + max(width, lenght) * clip-dyn)<br />
			-tikz-only : Remove default import for Latex
		</p>

		<h3>To do :</h3>
		<ul>
			<li>An more friendly interface</li>
			<li>Images to explain the parameters</li>
			<li>Host the online version</li>
			<li>Include the readme directly on the web page</li>
		</ul>
		<h2>License</h2>
		<p>GPL-3.0 License </p>


    </body>

    <?php include("footer.php"); ?>
</html>


