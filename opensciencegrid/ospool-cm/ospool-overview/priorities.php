<?php
  $title = "Priorities";
  include("header.php");
?>
          
<h2>Priorities</h2>
<pre><?php readfile("data/userprio.txt"); ?></pre>

<?php
  include("footer.php");
?>
