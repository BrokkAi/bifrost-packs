<?php

function request_param(string $name): string
{
    return '';
}

function fetch(): string|false
{
    $url = filter_var(request_param('url'), FILTER_VALIDATE_URL);
    return file_get_contents($url);
}
