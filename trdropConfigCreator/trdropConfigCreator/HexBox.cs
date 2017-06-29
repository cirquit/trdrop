using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace trdropConfigCreator
{
    class HexBox : MetroFramework.Controls.MetroTextBox
    {
        System.Windows.Forms.Panel colorPanel;
        bool valid = false;

        public HexBox(System.Windows.Forms.Panel colorPanel) : base()
        {
            this.colorPanel = colorPanel;
           
            this.TextChanged += new EventHandler(validate);
            this.LostFocus += new EventHandler(check);
        }

        private void check(object sender, EventArgs e)
        {
            MetroFramework.Controls.MetroTextBox hexBox = (MetroFramework.Controls.MetroTextBox)sender;
            if(hexBox.Text.Length != 7)
            {
                //TODO
                valid = false;

            }
        }

        private void validate(object sender, EventArgs e)
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
