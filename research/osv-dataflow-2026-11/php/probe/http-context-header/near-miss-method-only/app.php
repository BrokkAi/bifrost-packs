<?php

function request_param(string $name): string
{
    return '';
}

function context(): mixed
{
    $method = request_param('m') === 'post' ? 'POST' : 'GET';
    return stream_context_create(['http' => ['method' => 'GET']]);
}
