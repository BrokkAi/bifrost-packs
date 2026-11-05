<?php

function request_param(string $name): string
{
    return '';
}

function probe(): mixed
{
    $url = request_param('url');
    $host = parse_url($url, PHP_URL_HOST);
    if ($host !== 'status.example.test') {
        return false;
    }
    return fsockopen($host, 80);
}
