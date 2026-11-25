<?php

function request_param(string $name): string
{
    return '';
}

function convert(): mixed
{
    $pipes = [];
    request_param('name');
    return proc_open(['convert', 'in.png', 'out.png'], [], $pipes);
}
