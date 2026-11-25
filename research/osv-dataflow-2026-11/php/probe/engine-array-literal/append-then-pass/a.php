<?php

function src(): string
{
    return "";
}

function sink(mixed $s): void
{
}

function handler(): void
{
    $u = src(); $a = []; $a[] = $u; sink($a);
}
