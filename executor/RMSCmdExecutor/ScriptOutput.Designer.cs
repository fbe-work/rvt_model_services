namespace RMSCmdExecutor
{
    partial class ScriptOutput
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.renderer = new System.Windows.Forms.TextBox();
            this.SuspendLayout();
            // 
            // renderer
            // 
            this.renderer.Dock = System.Windows.Forms.DockStyle.Fill;
            this.renderer.Font = new System.Drawing.Font("Courier New", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.renderer.Location = new System.Drawing.Point(0, 0);
            this.renderer.Multiline = true;
            this.renderer.Name = "renderer";
            this.renderer.ReadOnly = true;
            this.renderer.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.renderer.Size = new System.Drawing.Size(984, 462);
            this.renderer.TabIndex = 6;
            // 
            // ScriptOutput
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(984, 462);
            this.Controls.Add(this.renderer);
            this.MinimizeBox = false;
            this.Name = "ScriptOutput";
            this.ShowIcon = false;
            this.ShowInTaskbar = false;
            this.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Show;
            this.Text = "ScriptOutput";
            this.TopMost = true;
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        public System.Windows.Forms.TextBox renderer;

        public void AppendText(string OutputText)
        {
            renderer.AppendText(OutputText);
            renderer.SelectionStart = renderer.Text.Length;
            renderer.ScrollToCaret();
        }

        public string GetContents()
        {
            return renderer.Text;
        }

    }
}