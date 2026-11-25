<?php
// A request value concatenated into a shell command string.
function convertImage(): mixed
{
    $pipes = [];
    $name = $_GET['name'];
    return proc_open('convert ' . $name . ' out.png', [], $pipes);
}
