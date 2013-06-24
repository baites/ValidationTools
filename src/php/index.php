<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <title>Validation Plots</title>
  <link rel="stylesheet" type="text/css" href="screen.css" />
  <style type="text/css">@import url('screen.css');</style>
  <script type="text/javascript">
  </script>
</head>

<body>
<form id="subForm" action="<?=$PHP_SELF?>">
<?
$webpath = '${webpath}';  
$releases = array();
$datasets = array();
$validators = array();
?>

<? 
  printHead();
?>

<?
if ( ($releases = getListOfDir($webpath.'/data')) == array() ) {
  error("Automated validation page is not ready");
  printTail();
  die();
}  
if ( $release != "" and is_dir("$webpath/data/$release") ) {
  $datasets = getListOfDir("$webpath/data/$release");
  if ( $dataset != "" and is_dir("$webpath/data/$release/$dataset") ) {
  	$validators = getListOfDir("$webpath/data/$release/$dataset");
  }
}
?>
<div id="menu">
<p>
  Release:
  <select name="release" onchange="this.form.submit();">
    <option align="middle" value=""> ======= release ======</option> 
<?
foreach ($releases as $item) { 
?>
    <option id="<?=$item?>" value="<?=$item?>"<? if ($release==$item) print ' selected="selected"'?>><?=$item?></option> 
<?
}  
?>
  </select>
<?
if ( $release != "" ) { 
?>
  Dataset : 
  <select name="dataset" onchange="this.form.submit();">
    <option value=""> ======= dataset ======</option> 
<?
  foreach ($datasets as $item) { 
?> 
    <option id="<?=$item?>" value="<?=$item?>"<? if ($dataset==$item) print ' selected="selected"'?>><?=$item?></option> 
<?
  } 
?>
  </select>
<?
}
if ( $release != "" and $dataset != "" ) {
?>
  Validator :
  <select name="validator" onchange="this.form.submit();">
    <option value=""> ======= validator ======</option>
<?
  foreach ($validators as $item) { 
?>
    <option id="<?=$item?>" value="<?=$item?>"<? if ($validator==$item) print ' selected="selected"'?>><?=$item?></option>
<?
  } 
?>
  </select>
<?
}
?> 
  Keyword : <input type="text" name="keywords" value="<?=$keywords?>" class="text"/><br/>
  View:<br/>  
  <input type="radio" name="view" value="thumbnail" <? if ($view == "thumbnail" || $view == "" ) { ?>checked="checked"<? } ?>/>Thumbnail<br/>
  <input type="radio" name="view" value="fulltable" <? if ($view == "fulltable") { ?>checked="checked"<? } ?>/>Two columns<br/>
  <input type="hidden" name="mode" value="<?=$mode?>"/>
  <input type="submit" name="OK" value="OK"/>
 </p>
</div>

<div id="content">

<?
if ( $release != "" and $dataset == "" ) {
?>
 <h2>Summary</h2>
 <h3>Validation for <span style="color:red"><?=$release?></span>, <span style="color:red"><?=$dataset?></span>, <span style="color:red"><?=$validator?></span> </h3>
 <p> Log files :
   [<a href="<?="data/$release/$release.log"?>" >Hadd</a>]
   [<a href="<?="data/$release/MakePlots.log"?>" >MakePlots</a>]
 </p>
<?
}
else if ( $release != "" and $dataset != "" ) {
?>
 <h2>Summary</h2>
 <h3>Validation for <span style="color:red"><?=$release?></span>, <span style="color:red"><?=$dataset?></span>, <span style="color:red"><?=$validator?></span> </h3>
 <p> Log files :
   [<a href="<?="data/$release/$release.log"?>" >Hadd</a>]
   [<a href="<?="data/$release/MakePlots.log"?>" >MakePlots</a>]
   [<a href="<?="data/$release/$dataset/MessageLogger.log"?>" >MessageLogger</a>]
 </p>
<?
}

// Print validation plots if we set CMSSW release correctly
if ( $dataset == "" or $validator == "" ) {
  if ( $release != "" ) {
?>
 <h2>Release <span style="color:red"><?=$release?></span></h2>
<?
    $desc = "$webpath/data/$release/description.txt";
    if ( is_file($desc) ) readfile($desc);
    print "</div>";
    printTail();
    die();
  }
  else {
    print "<p>Please choose menu items</p>";
    print "</div>";
    printTail();
    die();
  }
?>
 <pre class="description">
<?
}
  $workArea = "$webpath/data/$release/$dataset/$validator";
  if ( is_file("$workArea/description.txt") ) readfile("$workArea/description.txt");
?>
 </pre>
<? 
  $images = getListOfImages($workArea);
  $images = filter($images, explode(' ', $keywords));
?>
 <h2>Result (<?=count($images)?> plots)</h2>
<?
  if ( $view == "thumbnail" or $view == "" ) {
    showPlots("thumbnail", 4, $images);
  } else if ( $view == "fulltable" )  {
    showPlots("fullTable", 2, $images);
  } else { 
    showPlots("zoomin", 1, $images);
  }
?>
</div>
<?
printTail(); 
?>

<?//////////////////////////////////Functions///////////////////////?>

<?
function error($msg) {
?>
<div id="error">
 <h2>Error!!!</h2>
 <p><?=$msg?></p>
</div>
<?
} 

function getListOfDir($path) {
  $dirList = array();
  if ( $dh = @opendir($path) ) {
    while ( False !== ($f = @readdir($dh) ) ) {
      if ( $f != '.' and $f != '..' and substr($f, -4) != ".log" ) array_push($dirList, $f);
    }
    @closedir($dh);
  }
  return $dirList;
}

function getListOfImages($path) {
  $pngList = array();
  if ( $dh = @opendir($path) ) {
    while ( False !== ($f = @readdir($dh) ) ) {
      if ( strlen($f) < 5 ) continue;
      if ( substr($f, -4) != ".png") continue;
      array_push($pngList, substr($f, 0, -4));
    }
    @closedir($dh);
  }
  return $pngList;
}

function filter($strings, $keywords) {
  $strList = array();
  if ( count($strings) == 0 or count($keywords) == 0 ) return $strings;
  foreach ($strings as $str) {
    $matchedAll = True;
    foreach ($keywords as $keyword) {
      if ( $keyword == "" ) continue;
      if ( !stristr($str, $keyword) ) $matchedAll = False;
    }
    if ( $matchedAll ) array_push($strList, $str);
  }
  return $strList;
}

function printHead() { ?>
<div id="header">
 <img src="http://cmsdbs.cern.ch/images/CMSLogo.gif" style="width:30px;height:30px;float:right;" alt="CMS logo"/>
 <h1><a href="index.php">Automated Validation Plots</a></h1>
</div>

<div id="main">
<? 
} 

function printTail() { ?>
</div>

<div id="tail">
<?
$last_modified = filemtime("index.php");
print("Last updated: ".date("m/j/y h:i", $last_modified)."<br/>");
?>
  <a href="http://validator.w3.org/check?uri=referer" target="_blank">XHTML Transitional 1.0</a> /
  <a href="http://jigsaw.w3.org/css-validator/check?uri=referer" target="_blank">CSS</a> / 
  Tested at IE 7, Mozilla-Firefox, Camino and Safari<br/>
  Victor E. Bazterra (baites@fnal.gov) based on Junghwan Goh (jhgoh@fnal.gov) php, Kenneth James Smith (kjsmith@fnal.gov) and Fracisco Yumiceva (yumiceva@fnal.gov) MakePlot
</div>

</form>
</body>

</html>
<? 
}

function showPlots($tableType, $ncolumns, $images) {
?>
 <table class="<?=$tableType?>">
<?
    $release = $GLOBALS['release'];
    $dataset = $GLOBALS['dataset'];
    $validator = $GLOBALS['validator']; 
    $nimages = count($images);
    $nraws = ceil($nimages/$ncolumns);

    for ($i=0; $i<$nraws; $i++) {
      $rest = $nimages-$i*$ncolumns;
      if ($rest > $ncolumns) $rest = $ncolumns;
      if($rest == 1)
      {
        $item = $images[$i*$ncolumns];
        $img  = "data/$release/$dataset/$validator/$item.png";
        $link = "index.php?release=$release&amp;dataset=$dataset&amp;validator=$validator&amp;view=zoomin&amp;keywords=$item";
?>
  <tr><th><?=$item?></th></tr>
  <tr><td><div align="center"><img src="<?=$img?>" alt="<?=$item?>"/></div></td></tr>
<?
      } else {

        for ($j=0; $j<$rest; $j++) {      
          $item = $images[$i*$ncolumns+$j];
          if ($j == 0) {
?>
  <tr><th><?=$item?></th>
<?
          } else if ($j == $rest-1) {
?>
  <th><?=$item?></th></tr>
<?
          } else {
?>
  <th><?=$item?></th>
<?
          } 
        }
        for ($j=0; $j<$rest; $j++) {
          $item = $images[$i*$ncolumns+$j];
          $img  = "data/$release/$dataset/$validator/$item.png";
          $link = "index.php?release=$release&amp;dataset=$dataset&amp;validator=$validator&amp;view=zoomin&amp;keywords=$item";
          if ($j == 0) {
?>
  <tr><td><a href="<?=$link?>"><div align="center"><img src="<?=$img?>" alt="<?=$item?>"/></div></a></td>
<?
          } else if ($j == $rest-1) {
?>
  <td><a href="<?=$link?>"><div align="center"><img src="<?=$img?>" alt="<?=$item?>"/></div></a></td></tr>
<?
          } else {
?>
   <td><a href="<?=$link?>"><div align="center"><img src="<?=$img?>" alt="<?=$item?>"/></div></a></td>
<?
          }
        }
      }
    }
?>
 </table>
<?
} 
?>

