<?php

function request_param(string $name): string
{
    return '';
}

function context(): mixed
{
    $header = request_param('h');
    return stream_context_create(['http' => ['header' => $header]]);
}
