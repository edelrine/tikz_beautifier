<!DOCTYPE html>
<html>
    <?php include("header.php"); ?>
    <body>
        <form method="post" action="converter.php">
        <h1>
            Tikz beautifier online :
        </h1>

        <?php 
            function get_input($variableName, $choice, $default) {
                return (isset($_POST[$variableName]) and in_array($_POST[$variableName], $choice)) ? $_POST[$variableName] : $default; 
            }

            $tf = array("true", "false");
            $color =  get_input("color", $tf, "true");
            $ident =  get_input("ident", array("\t",""," ","  ","   ","    "), "    ");
            $round =  get_input("round", array("-1","0","1","2","3","4"), "2");
            $sort = get_input("sort", $tf, "true");
            $order = get_input("order", array("abscissa","ordinate"), "abscissa");
            $absci_order = get_input("absci_order", array("ascending" ,"descending"), "ascending"); 
            $ordi_order = get_input("ordi_order", array("ascending" ,"descending"), "ascending"); 
            $by_type = get_input("by_type", $tf, "false"); 
            $latex = get_input("latex", $tf, "true"); 
            $clip = get_input("clip", $tf, "true"); 
            $clip_fix = (isset($_POST["clip_fix"]) and is_float($_POST["clip_fix"]) ? $_POST["clip_fix"] : "1");  
            $clip_dyn = (isset($_POST["clip_dyn"]) and is_float($_POST["clip_dyn"]) ? $_POST["clip_dyn"] : "0.10");  
            $tikz = (isset($_POST["tikz"]) ? htmlspecialchars($_POST["tikz"]) : "");

            $clip_fix = max(0,min($clip_fix, 42));
            $clip_dyn = max(-25,min($clip_fix, 25));
        ?>

        <textarea name="tikz" placeholder="Your Tikz code here" autofocus required><?php echo $tikz ?></textarea>
        <div id="contener_submit">
            <input type="submit" value="Submit" class="button"/>
            <input type="reset" value="Reset" class="button"/>
        </div>


        <?php 
            if (isset($_POST["tikz"])) {
                if(strlen($tikz) > 4000){
                    echo '<h2 class="error"><br />Sorry your code is more than 4000 characters long, use the off-line version of our <a href="nortegithub">github</a>!</h2>';
                }else{
                    $start_time = microtime(true); 
                    $tikz_file = fopen("./tikz_to_convert", "w+");
                    fwrite($tikz_file, $tikz);
                    fclose($tikz_file);
                    $command = 'python3 python/main.py ./tikz_to_convert -hide -tab "'.($ident).'" -round "'.($round).'" ' ;
                    $command = $command.($color=="true" ?'':'-no-color ').($sort=="true" ?'': '-no-sort ').($order=="abscissa" ?'': '-ordinate-last ');
                    $command = $command.($absci_order=="ascending" ?'': '-decreasing-abscissa ').($ordi_order=="ascending" ?'': '-decreasing-ordinate ').($by_type=="true" ?'': '-by-type ');
                    $command = $command.($tikz =="true" ?'': '-tikz-only ');    
                    $command = $command.($clip=="true" ?'': '-no-clip ').'-clip-fix "'.($clip_fix).'" -clip-dyn "'.($clip_dyn).'"';
                    $command = escapeshellcmd($command);
                    $output = shell_exec($command);

                    $pathferror = "python/tikz_beautifier.log";
                    $ferror = fopen($pathferror, "r+");    //log on python directory
                    if (filesize($pathferror) > 0) {
                        $error = htmlspecialchars(fread($ferror,filesize($pathferror)));
                        echo '<h2 class="error"><br />Sorry, an error occurred, read the log and contact the <a href="mailto:louis-max.harter@protonmail.com">admin</a> if necessary.</h2>';
                        echo '<label for="log">Log :</label><br />';
                        echo '<textarea name="log" placeholder="log">'.($error).'</textarea>';
                    }
                    fclose($ferror);

                    $pathfresult = "./tikz_to_convert_clear.tikz";
                    $fresult = fopen($pathfresult, "r+");   //result on php directory
                    if (filesize($pathfresult) > 0) {
                        echo '<p>Scirpt run in '.round(microtime(true) - $start_time, 3).'s</p>';
                        $result = htmlspecialchars(fread($fresult,filesize($pathfresult)));
                        echo '<label for="result">Result :</label><br />';
                        echo '<textarea name="result" placeholder="result">'.($result).'</textarea>';
                    }
                    fclose($fresult);

                    file_put_contents("python/tikz_beautifier.log", "");
                    file_put_contents("tikz_to_convert_clear.tikz", "");
                }
            }
        ?>

        <fieldset>
            <legend>Options :</legend>
            <div id="contener">
                <div class="ident">
                    <label for="ident">Identation :</label><br />
                    <select name="ident" id="ident">
                        <option value="\t"  <?php echo $ident=="\t"?'selected':'' ?>>tab</option>
                        <option value=""    <?php echo $ident==""?'selected':'' ?>>disable</option>
                        <option value=" "   <?php echo $ident==" "?'selected':'' ?>>1 space</option>
                        <option value="  "  <?php echo $ident=="  "?'selected':'' ?>>2 space</option>
                        <option value="   " <?php echo $ident=="   "?'selected':'' ?>>3 space</option>
                        <option value="    "<?php echo $ident=="    "?'selected':'' ?>>4 space</option>
                    </select>
                </div>
                <div class="color">
                    <label for="color">Set colors names :</label><br />
                    <input type="radio" name="color" value="true" id="color_yes" <?php echo $color=="true" ? 'checked':'' ?>/> 
                    <label for="color_yes">Yes</label><br />
                    <input type="radio" name="color" value="false" id="color_no" <?php echo $color=="true" ? '':'checked' ?>/> 
                    <label for="color_no">No</label><br />
                </div>
                <div class="round">
                    <label for="round">Round values :</label><br />
                    <select name="round" id="round">
                        <option value="-1" <?php echo $round=="-1" ? '':'selected' ?>>disable</option>
                        <option value="0" <?php echo $round=="0" ? 'selected':'' ?>>0 digit</option>
                        <option value="1" <?php echo $round=="1" ? 'selected':'' ?>>1 digit</option>
                        <option value="2" <?php echo $round=="2" ? 'selected':'' ?>>2 digit</option>
                        <option value="3" <?php echo $round=="3" ? 'selected':'' ?>>3 digit</option>
                        <option value="4" <?php echo $round=="4" ? 'selected':'' ?>>4 digit</option>
                    </select>
                </div>
                <div class="sort">
                    <label for="sort">Drawn sort :</label><br />
                    <input type="radio" name="sort" value="true" id="sort_yes" <?php echo $sort=="true" ? 'checked':'' ?>/> 
                    <label for="sort_yes">Yes</label><br />
                    <input type="radio" name="sort" value="false" id="sort_no" <?php echo $sort=="true" ? '':'checked' ?>/> 
                    <label for="color_no">No</label><br />
                </div>
            </div>
        </fieldset>
        <fieldset>
            <legend>Margin and Latex default packtage :</legend>
            <div id="contener">
                <div class="clip">
                    <label for="clip">Set margin (clip):</label><br />
                    <input type="radio" name="clip" value="true" id="clip_yes" <?php echo $clip=="true" ? 'checked':'' ?>/> 
                    <label for="clip_yes">Yes</label><br />
                    <input type="radio" name="clip" value="false" id="clip_no" <?php echo $clip=="true" ? '':'checked' ?>/> 
                    <label for="color_no">No</label><br />
                </div>
                <div class="clip_fix">
                    <label for="clip_fix">Set const margin :</label><br />
                    <input type="number" min="0" max="42" step="0.5" id="clip_fix" name="clip_fix" class="number_input" <?php echo ($clip_fix == "0" ? 'placeholder="0"' : 'value='.$clip_fix)?>/>
                </div>
                <div class="clip_dyn">
                    <label for="clip_dyn">Set dynamic margin :</label><br />
                    <input type="number" min="-25" max="25" step="0.05" id="clip_dyn" name="clip_dyn" class="number_input" <?php echo ($clip_dyn == "0" ? 'placeholder="0"' : 'value='.$clip_dyn)?>/>
                </div>
                <div class="latex">
                    <label for="latex">Keep Latex :</label><br />
                    <input type="radio" name="latex" value="true" id="latex_yes" <?php echo $latex=="true" ? 'checked':'' ?>/> 
                    <label for="latex_yes">Keep latex</label><br />
                    <input type="radio" name="latex" value="false" id="latex_no" <?php echo $latex=="true" ? '':'checked' ?>/> 
                    <label for="latex_no">Only Tikz</label><br />
                    </select>
                </div>
            </div>
        </fieldset>
        <fieldset>
            <legend>Advance sorting options :</legend>
            <div id="contener">
                <div class="order">
                    <label for="order">Priority order :</label><br />
                    <input type="radio" name="order" value="abscissa" id="abscissa" <?php echo $order=="abscissa" ? 'checked':'' ?>/> 
                    <label for="abscissa">Abscissa first</label><br />
                    <input type="radio" name="order" value="ordonnate" id="ordonnate" <?php echo $order=="abscissa" ? '':'checked' ?>/> 
                    <label for="ordonnate">Ordonnate first</label><br />
                </div>
                <div class="absci_order">
                    <label for="absci_order">Abscissa order :</label><br />
                    <input type="radio" name="absci_order" value="ascending" id="ascending" <?php echo $absci_order=="ascending" ? 'checked':'' ?>/> 
                    <label for="ascending">ascending</label><br />
                    <input type="radio" name="absci_order" value="descending" id="descending" <?php echo $absci_order=="ascending" ? '':'checked' ?>/> 
                    <label for="absci_order">descending</label><br />
                </div>
                <div class="ordi_order">
                    <label for="ordo_order">Ordinate order :</label><br />
                    <input type="radio" name="ordi_order" value="ascending" id="ascending" <?php echo $ordi_order=="ascending" ? 'checked':'' ?>/> 
                    <label for="ascending">ascending</label><br />
                    <input type="radio" name="ordi_order" value="descending" id="descending" <?php echo $ordi_order=="ascending" ? '':'checked' ?>/> 
                    <label for="descending">descending</label><br />
                </div>
                <div class="by_type">
                    <label for="by_type">By type :</label><br />
                    <input type="radio" name="by_type" value="true" id="by_type_true" <?php echo $by_type=="true" ? 'checked':'' ?>/> 
                    <label for="by_type_true">ascending</label><br />
                    <input type="radio" name="by_type" value="false" id="by_type_false" <?php echo $by_type=="true" ? '':'checked' ?>/> 
                    <label for="by_type_false">descending</label><br />
                </div>
            </div>
        </fieldset>
    </body>

    <?php include("footer.php"); ?>

</html>