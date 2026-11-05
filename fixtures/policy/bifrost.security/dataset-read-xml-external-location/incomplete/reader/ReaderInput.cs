using System;
using System.Data;
using System.IO;

namespace Verify.DataSetReadXml.Incomplete
{
    public sealed class ReaderInput
    {
        public void Run(DataSet orders)
        {
            orders.ReadXml(new StringReader(Console.ReadLine()));
        }
    }
}
