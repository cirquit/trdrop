using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace trdropConfigCreator
{
    class HexBox : MetroFramework.Controls.MetroTextBox
    {
        System.Windows.Forms.Panel colorPanel;

        public HexBox(System.Windows.Forms.Panel colorPanel) : base()
        {
            this.colorPanel = colorPanel;
            this.CustomButton.Image = null;
            this.CustomButton.Location = new System.Drawing.Point(62, 1);
            this.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.CustomButton.TabIndex = 1;
            this.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.CustomButton.UseSelectable = true;
            this.CustomButton.Visible = false;
            this.Lines = new string[0];
            this.Location = new System.Drawing.Point(261, 99);
            this.MaxLength = 32767;
            this.PasswordChar = '\0';
            this.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.SelectedText = "";
            this.SelectionLength = 0;
            this.SelectionStart = 0;
            this.ShortcutsEnabled = true;
            this.Size = new System.Drawing.Size(84, 23);
            this.TabIndex = 16;
            this.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.UseSelectable = true;
            this.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            this.TextChanged += new System.EventHandler(checkIfHex);
        }

        public void checkIfHex(object sender, EventArgs e)
        {
            MetroFramework.Controls.MetroTextBox hexBox = (MetroFramework.Controls.MetroTextBox)sender;
            if (hexBox.Text.Length == 7 && hexBox.Text[0] == '#')
            {
                bool charsCorrect = false;
                foreach (var c in hexBox.Text.Substring(1))
                {
                    charsCorrect = ((c >= '0' && c <= '9') ||
                                    (c >= 'a' && c <= 'f') ||
                                    (c >= 'A' && c <= 'F'));

                    if (!charsCorrect) break;
                }
                if(charsCorrect)
                {
                    System.Drawing.Color c = System.Drawing.ColorTranslator.FromHtml(hexBox.Text);
                    this.colorPanel.BackColor = c;
                }
            }
        }
    }
}
