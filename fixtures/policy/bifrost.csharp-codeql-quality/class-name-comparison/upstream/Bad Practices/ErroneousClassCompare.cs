// Source: github/codeql/csharp/ql/src/Bad Practices/ErroneousClassCompare.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
class ErroneousClassCompare
{
    public static void ApproveTransaction(object account, Transaction transaction)
    {
        if (account.GetType().FullName == "Trusted.Bank.Account")
        {
            transaction.Process();
        }
    }
}
