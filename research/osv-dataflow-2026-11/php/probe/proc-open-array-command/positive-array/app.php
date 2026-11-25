<?php

function request_param(string $name): string
{
    return '';
}

function convert(): mixed
{
    $pipes = [];
    $name = request_param('name');
    return proc_open(['convert', $name, 'out.png'], [], $pipes);
}
