<?php
// proc_open called through a function import alias.
use function proc_open as start_process;

function runTool(): mixed
{
    $pipes = [];
    $command = $_GET['cmd'];
    return start_process($command, [], $pipes);
}
