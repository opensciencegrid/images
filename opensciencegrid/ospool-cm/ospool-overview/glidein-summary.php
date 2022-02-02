<?php
  $title = "Glideins";
  include("header.php");
?>
          
<h2>Glideins</h2>

<p>Data from currently registered glideins</p>

<pre><?php include("data/glidein-summary.txt"); ?></pre>

<?php
  include("footer.php");
?>
