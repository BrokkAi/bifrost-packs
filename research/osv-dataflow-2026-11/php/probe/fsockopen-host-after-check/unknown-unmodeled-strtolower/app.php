<?php

function request_param(string $name): string
{
    return '';
}

function probe(): mixed
{
    $host = strtolower(parse_url(request_param('url'), PHP_URL_HOST));
    return fsockopen($host, 80);
}
