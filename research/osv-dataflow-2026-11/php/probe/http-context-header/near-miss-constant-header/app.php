<?php

function request_param(string $name): string
{
    return '';
}

function context(): mixed
{
    request_param('h');
    return stream_context_create(['http' => ['header' => 'Accept: text/plain']]);
}
