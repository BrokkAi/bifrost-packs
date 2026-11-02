using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace UnmanagedProbe;

public class NativeMethods
{
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int MessageBox(IntPtr hWnd, string text, string caption, uint type);

    [DllImport("kernel32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static extern bool Beep(uint frequency, uint duration);

    [MethodImpl(MethodImplOptions.InternalCall)]
    public extern void InternalCall();

    public static int ManagedBox(IntPtr hWnd, string text, string caption, uint type)
    {
        return 0;
    }

    public void ExternInBody()
    {
        string note = "static extern int Fake();";
        _ = note.Length;
    }
}

public struct NativeStruct
{
    [DllImport("kernel32.dll")]
    public static extern uint GetTickCount();
}

public class Caller
{
    public void Local()
    {
        LocalBeep();

        [DllImport("kernel32.dll")]
        static extern bool LocalBeep();
    }

    public void Bad(NativeMethods native)
    {
        NativeMethods.MessageBox(IntPtr.Zero, "Hello", "Title", 0);
        NativeMethods.Beep(440, 100);
        native.InternalCall();
    }

    public void NearMiss(NativeMethods native)
    {
        NativeMethods.ManagedBox(IntPtr.Zero, "extern", "Title", 0);
        native.ExternInBody();
        NativeStruct.GetTickCount();
    }
}
