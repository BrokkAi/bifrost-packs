<?php

function request_param(string $name): string
{
    return '';
}

function fetch(): string|false
{
    $ctx = stream_context_create(['http' => ['timeout' => 5]]);
    return file_get_contents(request_param('url'), false, $ctx);
}
