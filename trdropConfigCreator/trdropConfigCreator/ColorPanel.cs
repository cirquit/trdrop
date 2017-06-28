using System;
using System.Drawing;
using System.Windows.Forms;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace trdropConfigCreator
{
    class ColorPanel : Panel
    {
        private HexBox hexBox;

        public ColorPanel() : base()
        {
            this.BackColor = Color.Chartreuse;
            this.Location = new Point(131, 19);
            this.Name = "videoColorPanel";
            this.Size = new Size(64, 39);
            this.TabIndex = 13;
            this.Click += new EventHandler(this.setPanelColor);
        }

        public void setPanelColor(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();

            if(cd.ShowDialog() == DialogResult.OK)
            {
                this.hexBox.Text = ColorTranslator.ToHtml(Color.FromArgb(cd.Color.ToArgb()));
            }
        }

        public void SetHexBox(HexBox hexBox)
        {
            this.hexBox = hexBox;
        }
    }
}
