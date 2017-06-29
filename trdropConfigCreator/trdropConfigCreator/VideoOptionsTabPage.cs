using System;
using System.Drawing;
using System.Windows.Forms;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace trdropConfigCreator
{
    partial class VideoOptionsTabPage : MetroFramework.Controls.MetroTabPage
    {
        public VideoOptionsTabPage(string text) : base()
        {
            InitializeComponent();
            this.Text = text;
        }

        private void inputBrowseButton_Click(object sender, EventArgs e)
        {
            OpenFileDialog browseDialog = new OpenFileDialog();
            browseDialog.Filter = "Video Files (*.avi)|*.avi";
            if (browseDialog.ShowDialog() == DialogResult.OK)
            {
                inputFileTextBox.Text = browseDialog.FileName;
            }
        }

        private void pxToleranceTrackBar_ValueChanged(object sender, EventArgs e)
        {
            pxToleranceTextBox.Text = pxToleranceTrackBar.Value.ToString();
        }

        private void lnToleranceTrackBar_ValueChanged(object sender, EventArgs e)
        {
            lnToleranceTextBox.Text = lnToleranceTrackBar.Value.ToString();
        }

        private void pxToleranceTextBox_LostFocus(object sender, EventArgs e)
        {
            int.TryParse(pxToleranceTextBox.Text, out int num);
            pxToleranceTrackBar.Value = num;
        }

        private void pxToleranceTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                //int.TryParse(pxToleranceTextBox.Text, out int num);
                //pxToleranceTrackBar.Value = num;
                this.Focus();
            }
        }

        private void pxToleranceTextBox_KeyPress(object sender, KeyPressEventArgs e)
        {
            if(e.KeyChar == 13) e.Handled = true;
        }

        private void colorPanel_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            Panel panel = (Panel)sender;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                panel.BackColor = cd.Color;
                videoColorHexBox.Text = ColorTranslator.ToHtml(Color.FromArgb(cd.Color.ToArgb()));
            }

        }


    }
}
