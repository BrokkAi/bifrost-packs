<?php

function unwrap(string $peer, mixed $key): string
{
    $conn = stream_socket_client($peer);
    $bytes = fread($conn, 512);
    $plain = '';
    openssl_private_decrypt($bytes, $plain, $key, OPENSSL_PKCS1_OAEP_PADDING);
    return $plain;
}
