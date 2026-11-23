<?php
// The request value is read, but every element of the command array is a
// constant.
function convertImage(): mixed
{
    $pipes = [];
    $name = $_GET['name'];
    return proc_open(['convert', 'in.png', 'out.png'], [], $pipes);
}
