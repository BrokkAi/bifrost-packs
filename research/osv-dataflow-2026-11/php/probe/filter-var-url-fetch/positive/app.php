<?php

function request_param(string $name): string
{
    return '';
}

function fetch(): string|false
{
    $url = request_param('url');
    if (filter_var($url, FILTER_VALIDATE_URL) === false) {
        return false;
    }
    return file_get_contents($url);
}
