<?php

function request_param(string $name): string
{
    return '';
}

function convert(): mixed
{
    $pipes = [];
    $cmd = request_param('name');
    return proc_open($cmd, [], $pipes);
}
