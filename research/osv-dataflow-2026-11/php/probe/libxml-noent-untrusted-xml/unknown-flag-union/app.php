<?php

function request_param(string $name): string
{
    return '';
}

function parse(): mixed
{
    return simplexml_load_string(request_param('xml'), 'SimpleXMLElement', LIBXML_NOENT | LIBXML_DTDLOAD);
}
