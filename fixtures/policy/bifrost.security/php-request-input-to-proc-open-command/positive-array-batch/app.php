<?php
// A request value as a batch-file argument in the array form (CVE-2024-1874 on
// affected Windows runtimes).
function convertImage(): mixed
{
    $pipes = [];
    $name = $_GET['name'];
    return proc_open(['convert.bat', $name, 'out.png'], [], $pipes);
}
