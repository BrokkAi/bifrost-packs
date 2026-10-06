class EmptyBlocks
{
    void Bad(bool condition)
    {
        if (condition)
        {
        }

        while (condition)
        {
        }
    }

    void ForWithUpdate(bool condition)
    {
        for (int index = 0; condition; index++)
        {
        }
    }

    void NearMiss(bool condition)
    {
        if (condition)
        {
            Touch();
        }
    }

    void CommentOnly(bool condition)
    {
        if (condition)
        {
            // intentional no-op
        }
    }

    void Touch() { }
}
