using System;
using System.Data;

namespace Verify.DataSetReadXml.Incomplete
{
    public sealed class FieldReceiver
    {
        private readonly DataSet orders = new DataSet();

        public void Run()
        {
            orders.ReadXml(Console.ReadLine());
        }
    }
}
