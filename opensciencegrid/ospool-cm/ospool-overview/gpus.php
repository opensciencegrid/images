<?php
  $title = "GPUs";
  include("header.php");
?>
          
<h2>GPUs</h2>

<div class="box">
<pre><?php readfile("data/gpus.txt"); ?></pre>
</div>

<?php
  include("footer.php");
?>
