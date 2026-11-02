// Source: github/codeql/csharp/ql/src/Bad Practices/ErroneousClassCompareFix.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
class ErroneousClassCompareFix
{
    public static void ApproveTransaction(object account, Transaction transaction)
    {
        if (account.GetType() == typeof(Trusted.Bank.Account))
        {
            transaction.Process();
        }
    }
}
