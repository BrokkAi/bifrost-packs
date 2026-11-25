<?php

function request_param(string $name): string
{
    return '';
}

function fetch(): string|false
{
    $url = trim(request_param('url'));
    return file_get_contents($url);
}
