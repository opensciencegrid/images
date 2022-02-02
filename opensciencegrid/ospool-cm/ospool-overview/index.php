<?php
  $title = "Overview";
  include("header.php");
?>

<div class="box">
<pre><?php readfile("data/submitters.txt"); ?></pre>
</div>
          
<div class="box">
<img src='data/display.png'>
</div>

<div class="box">
<img src='data/idle.png'>
</div>


<?php
  include("footer.php");
?>
