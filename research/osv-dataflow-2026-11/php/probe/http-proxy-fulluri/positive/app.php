<?php

function request_param(string $name): string
{
    return '';
}

function fetch(): string|false
{
    $ctx = stream_context_create(['http' => ['proxy' => 'tcp://proxy.internal.test:3128', 'request_fulluri' => true]]);
    return file_get_contents(request_param('url'), false, $ctx);
}
