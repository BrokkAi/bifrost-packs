<?php

function request_param(string $name): string
{
    return '';
}

function import(): mixed
{
    request_param('feed');
    return simplexml_load_file('/srv/app/feeds/default.xml');
}
