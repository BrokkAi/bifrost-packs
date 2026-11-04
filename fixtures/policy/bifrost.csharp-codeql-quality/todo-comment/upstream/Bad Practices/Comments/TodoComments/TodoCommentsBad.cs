// Source: github/codeql/csharp/ql/test/query-tests/Bad Practices/Comments/TodoComments/TodoCommentsBad.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;

class Bad
{
    public static double SolveQuadratic(double a, double b, double c)
    {
        // TODO: handle case where a == 0
        return (-b + Math.Sqrt(b * b - 4 * a * c)) / (2 * a);
    }
}
