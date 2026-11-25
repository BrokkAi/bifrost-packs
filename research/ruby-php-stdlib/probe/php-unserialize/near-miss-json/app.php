<?php

function receive(string $peer): mixed
{
    $conn = stream_socket_client($peer);
    $bytes = fread($conn, 65536);
    return json_decode($bytes, true);
}
