<?php
// escapeshellarg has no reviewed summary, so the run stays inconclusive. The
// quoting is not proof of safety for the array form on Windows either.
function convertImage(): mixed
{
    $pipes = [];
    $name = escapeshellarg($_GET['name']);
    return proc_open('convert ' . $name, [], $pipes);
}
