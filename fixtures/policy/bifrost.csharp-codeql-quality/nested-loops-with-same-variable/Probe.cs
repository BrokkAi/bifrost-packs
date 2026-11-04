namespace CsharpG08;

public class NestedLoopProbe
{
    public void Bad()
    {
        for (int i = 0; i < 10; i++)
        {
            for (int j = 0; j < 10; i++)
            {
            }
        }
    }

    public void GoodDifferentVariable()
    {
        for (int i = 0; i < 10; i++)
        {
            for (int j = 0; j < 10; j++)
            {
            }
        }
    }

    public void SafeSameCondition()
    {
        for (int i = 0; i < 10; i++)
        {
            for (; i < 10; i++)
            {
            }
        }
    }

    public void BadDifferentCondition()
    {
        for (int i = 0; i < 10; i++)
        {
            for (; i < 9; i++)
            {
            }
        }
    }
}
