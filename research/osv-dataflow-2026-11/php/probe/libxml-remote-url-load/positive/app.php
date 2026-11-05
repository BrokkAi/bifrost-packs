<?php

function request_param(string $name): string
{
    return '';
}

function import(): mixed
{
    return simplexml_load_file(request_param('feed'));
}
