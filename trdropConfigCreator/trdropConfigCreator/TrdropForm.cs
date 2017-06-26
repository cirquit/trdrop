using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using YamlDotNet;

namespace trdropConfigCreator
{
    public partial class TrdropForm : MetroFramework.Forms.MetroForm
    {

        public TrdropForm()
        {
            InitializeComponent();
        }

        //Slightly modified version of this code: https://stackoverflow.com/questions/6738126/winforms-tabcontrol-add-new-tab-button/36959196#36959196

        [System.Runtime.InteropServices.DllImport("user32.dll")]
        private static extern IntPtr SendMessage(IntPtr hWnd, int msg, IntPtr wp, IntPtr lp);
        private const int TCM_SETMINTABWIDTH = 0x1300 + 49;

        private void VideoTabControl_HandleCreated(object sender, EventArgs e)
        {
            SendMessage(this.videoTabControl.Handle, TCM_SETMINTABWIDTH, IntPtr.Zero, (IntPtr)16);
        }

        private void VideoTabControl_MouseDown(object sender, MouseEventArgs e)
        {
            int lastIndex = this.videoTabControl.TabCount - 1;
            if (this.videoTabControl.GetTabRect(lastIndex).Contains(e.Location))
            {
                if(lastIndex < 3)
                {
                    VideoOptionsTabPage videoTab = new VideoOptionsTabPage("Video " + (lastIndex + 1));
                    this.videoTabControl.TabPages.Insert(lastIndex,videoTab);
                    this.videoTabControl.SelectedIndex = lastIndex;
                }
                else
                {
                    this.videoTabControl.SelectedIndex = lastIndex - 1;
                    MessageBox.Show("trdrop currently only supports up to 3 videos. Sorry.");
                }
            } 
        }

        private void VideoTabControl_Selecting(object sender, TabControlCancelEventArgs e)
        {
            if (e.TabPageIndex == this.videoTabControl.TabCount - 1)
                e.Cancel = true;
        }

        private void metroPanel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void metroTabPage3_Click(object sender, EventArgs e)
        {

        }

        private void metroLabel17_Click(object sender, EventArgs e)
        {

        }

        private void metroTabPage4_Click(object sender, EventArgs e)
        {

        }

        private void metroTabPage6_Click(object sender, EventArgs e)
        {

        }
        /*
//From https://docs.microsoft.com/en-us/dotnet/framework/winforms/controls/how-to-display-side-aligned-tabs-with-tabcontrol
private void VideoSubTabControl_DrawItem(Object sender, System.Windows.Forms.DrawItemEventArgs e)
{
Graphics g = e.Graphics;
Brush _textBrush;

// Get the item from the collection.
TabPage _tabPage = this.videoSubTabControl.TabPages[e.Index];

// Get the real bounds for the tab rectangle.
Rectangle _tabBounds = videoSubTabControl.GetTabRect(e.Index);

if (e.State == DrawItemState.Selected)
{
// Draw a different background color, and don't paint a focus rectangle.
_textBrush = new SolidBrush(Color.White);
g.FillRectangle(Brushes.SlateGray, e.Bounds);
}
else
{
_textBrush = new System.Drawing.SolidBrush(e.ForeColor);
//g.FillRectangle(Brushes.SlateGray, e.Bounds);
e.DrawBackground();
}

// Use our own font.
Font _tabFont = new Font("Microsoft Sans Serif", (float)10.0, FontStyle.Bold, GraphicsUnit.Point);

// Draw string. Center the text.
StringFormat _stringFlags = new StringFormat();
_stringFlags.Alignment = StringAlignment.Center;
_stringFlags.LineAlignment = StringAlignment.Center;
//g.DrawString(_tabPage.Text, _tabFont, _textBrush, _tabBounds, new StringFormat(_stringFlags));
}
*/
    }
}
