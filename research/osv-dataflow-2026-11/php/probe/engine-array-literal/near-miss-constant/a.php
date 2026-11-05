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
    src(); sink(["k" => "v"]);
}
