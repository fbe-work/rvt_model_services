using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using IronPython.Runtime.Exceptions;
using Microsoft.Scripting.Hosting;

namespace RMSCmdExecutor
{
    /// A stream to write output to...
    /// This can be passed into the python interpreter to render all output to.
    /// Only a minimal subset is actually implemented - this is all we really expect to use.
    public class ScriptOutputStream: Stream
    {
        private readonly ScriptOutput _gui;
        private string _outputBuffer;

        public ScriptOutputStream(ScriptOutput gui)
        {
            _outputBuffer = String.Empty;
            _gui = gui;
        }

        public void write(string s)
        {
            Write(Encoding.ASCII.GetBytes(s), 0, s.Length);
        }

        public void WriteError(string error_msg)
        {
            Write(Encoding.ASCII.GetBytes(error_msg), 0, error_msg.Length);
        }

        public override void Write(byte[] buffer, int offset, int count)
        {
            lock (this)
            {
                if (_gui.IsDisposed)
                {
                    return;
                }

                if (!_gui.Visible)
                {
                    _gui.Show();
                    _gui.Focus();
                }

                var actualBuffer = new byte[count];
                Array.Copy(buffer, offset, actualBuffer, 0, count);
                var text = Encoding.UTF8.GetString(actualBuffer);

                // append output to the buffer
                _outputBuffer += text;

                if (count % 1024 != 0) {
                    // write to output window
                    _gui.AppendText(_outputBuffer);

                    // reset buffer and flush state for next time
                    _outputBuffer = String.Empty;
                }
            }
        }

        public override void Flush()
        {
        }

        public override long Seek(long offset, SeekOrigin origin)
        {
            throw new NotImplementedException();
        }

        public override void SetLength(long value)
        {
            throw new NotImplementedException();
        }

        public override int Read(byte[] buffer, int offset, int count)
        {
            throw new NotImplementedException();
        }

        public override bool CanRead
        {
            get { return false; }
        }

        public override bool CanSeek
        {
            get { return false; }
        }

        public override bool CanWrite
        {
            get { return true; }
        }

        public override long Length
        {
            get { return 0; }
        }

        public override long Position
        {
            get { return 0; }
            set { }
        }
    }
}