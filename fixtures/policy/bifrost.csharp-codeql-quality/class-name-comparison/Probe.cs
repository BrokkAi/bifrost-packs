using System;

public class ClassNameProbe
{
    public bool Bad(object account)
    {
        bool full = account.GetType().FullName == "Trusted.Bank.Account";
        bool reversed = "Trusted.Bank.Account" == account.GetType().FullName;
        bool literal = typeof(ClassNameProbe).FullName == "ClassNameProbe";
        bool self = GetType().FullName == "ClassNameProbe";
        bool equals = account.GetType().FullName.Equals("Trusted.Bank.Account");
        bool equalsReversed = "Trusted.Bank.Account".Equals(account.GetType().FullName);
        bool staticEquals = object.Equals(account.GetType().FullName, "Trusted.Bank.Account");
        bool reference = Object.ReferenceEquals("Trusted.Bank.Account", account.GetType().FullName);
        return full || reversed || literal || self || equals || equalsReversed || staticEquals || reference;
    }

    public bool NearMiss(object account, Local.Named named, string expected)
    {
        bool different = account.GetType().FullName != "Trusted.Bank.Account";
        bool shortName = account.GetType().Name == "Account";
        bool qualified = account.GetType().AssemblyQualifiedName == "Trusted.Bank.Account";
        bool notLiteral = account.GetType().FullName == expected;
        bool typeCheck = account.GetType() == typeof(ClassNameProbe);
        bool isCheck = account is ClassNameProbe;
        bool otherFullName = named.FullName == "Trusted.Bank.Account";
        bool otherGetType = named.GetType(1).FullName == "Trusted.Bank.Account";
        bool stringEquals = string.Equals(account.GetType().FullName, "Trusted.Bank.Account");
        bool prefix = account.GetType().FullName.StartsWith("Trusted.");
        return different || shortName || qualified || notLiteral || typeCheck || isCheck
            || otherFullName || otherGetType || stringEquals || prefix;
    }
}
