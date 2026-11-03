<?php

namespace App\Codec;

function unserialize(string $bytes): int
{
    return strlen($bytes);
}

function receive(string $peer): int
{
    $conn = \stream_socket_client($peer);
    $bytes = \fread($conn, 65536);
    return unserialize($bytes);
}
