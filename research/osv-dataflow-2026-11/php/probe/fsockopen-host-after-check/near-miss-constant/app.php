<?php

function request_param(string $name): string
{
    return '';
}

function probe(): mixed
{
    request_param('url');
    return fsockopen('status.example.test', 80);
}
