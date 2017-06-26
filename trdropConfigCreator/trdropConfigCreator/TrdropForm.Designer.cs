using System;

namespace trdropConfigCreator
{
    partial class TrdropForm
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

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>

        //this.firstVideoTab = new VideoOptionsTabPage("Video 1");
        private void InitializeComponent()
        {
            this.videoTabControl = new MetroFramework.Controls.MetroTabControl();
            this.addVideoTab = new System.Windows.Forms.TabPage();
            this.metroTabControl1 = new MetroFramework.Controls.MetroTabControl();
            this.metroTabPage1 = new MetroFramework.Controls.MetroTabPage();
            this.metroTabPage2 = new MetroFramework.Controls.MetroTabPage();
            this.metroTabPage3 = new MetroFramework.Controls.MetroTabPage();
            this.metroTabPage4 = new MetroFramework.Controls.MetroTabPage();
            this.metroTabPage5 = new MetroFramework.Controls.MetroTabPage();
            this.videoTabControl.SuspendLayout();
            this.firstVideoTab.SuspendLayout();
            this.metroTabControl1.SuspendLayout();
            this.SuspendLayout();
            // 
            // videoTabControl
            // 
            this.videoTabControl.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.videoTabControl.Controls.Add(this.firstVideoTab);
            this.videoTabControl.Controls.Add(this.addVideoTab);
            this.videoTabControl.FontWeight = MetroFramework.MetroTabControlWeight.Regular;
            this.videoTabControl.ItemSize = new System.Drawing.Size(100, 42);
            this.videoTabControl.Location = new System.Drawing.Point(12, 63);
            this.videoTabControl.Multiline = true;
            this.videoTabControl.Name = "videoTabControl";
            this.videoTabControl.SelectedIndex = 0;
            this.videoTabControl.Size = new System.Drawing.Size(821, 480);
            this.videoTabControl.Style = MetroFramework.MetroColorStyle.Purple;
            this.videoTabControl.TabIndex = 0;
            this.videoTabControl.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.videoTabControl.UseSelectable = true;
            this.videoTabControl.HandleCreated += new System.EventHandler(this.VideoTabControl_HandleCreated);
            this.videoTabControl.MouseDown += new System.Windows.Forms.MouseEventHandler(this.VideoTabControl_MouseDown);
            // 
            // firstVideoTab
            // 
            this.firstVideoTab.BackColor = System.Drawing.Color.Transparent;
            this.firstVideoTab.Controls.Add(this.metroTabControl1);
            this.firstVideoTab.HorizontalScrollbarBarColor = true;
            this.firstVideoTab.HorizontalScrollbarHighlightOnWheel = false;
            this.firstVideoTab.HorizontalScrollbarSize = 10;
            this.firstVideoTab.Location = new System.Drawing.Point(4, 46);
            this.firstVideoTab.Name = "firstVideoTab";
            this.firstVideoTab.Padding = new System.Windows.Forms.Padding(3);
            this.firstVideoTab.Size = new System.Drawing.Size(813, 430);
            this.firstVideoTab.TabIndex = 0;
            this.firstVideoTab.Text = "Video 1";
            this.firstVideoTab.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.firstVideoTab.VerticalScrollbarBarColor = true;
            this.firstVideoTab.VerticalScrollbarHighlightOnWheel = false;
            this.firstVideoTab.VerticalScrollbarSize = 10;
            // 
            // addVideoTab
            // 
            this.addVideoTab.Location = new System.Drawing.Point(4, 46);
            this.addVideoTab.Name = "addVideoTab";
            this.addVideoTab.Padding = new System.Windows.Forms.Padding(3);
            this.addVideoTab.Size = new System.Drawing.Size(813, 430);
            this.addVideoTab.TabIndex = 1;
            this.addVideoTab.Text = "+";
            this.addVideoTab.UseVisualStyleBackColor = true;
            // 
            // metroTabControl1
            // 
            this.metroTabControl1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.metroTabControl1.Controls.Add(this.metroTabPage1);
            this.metroTabControl1.Controls.Add(this.metroTabPage2);
            this.metroTabControl1.Controls.Add(this.metroTabPage3);
            this.metroTabControl1.Controls.Add(this.metroTabPage4);
            this.metroTabControl1.Controls.Add(this.metroTabPage5);
            this.metroTabControl1.FontWeight = MetroFramework.MetroTabControlWeight.Regular;
            this.metroTabControl1.ItemSize = new System.Drawing.Size(100, 50);
            this.metroTabControl1.Location = new System.Drawing.Point(8, 7);
            this.metroTabControl1.Multiline = true;
            this.metroTabControl1.Name = "metroTabControl1";
            this.metroTabControl1.SelectedIndex = 0;
            this.metroTabControl1.Size = new System.Drawing.Size(809, 427);
            this.metroTabControl1.SizeMode = System.Windows.Forms.TabSizeMode.Fixed;
            this.metroTabControl1.Style = MetroFramework.MetroColorStyle.Purple;
            this.metroTabControl1.TabIndex = 2;
            this.metroTabControl1.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.metroTabControl1.UseSelectable = true;
            // 
            // metroTabPage1
            // 
            this.metroTabPage1.HorizontalScrollbarBarColor = true;
            this.metroTabPage1.HorizontalScrollbarHighlightOnWheel = false;
            this.metroTabPage1.HorizontalScrollbarSize = 10;
            this.metroTabPage1.Location = new System.Drawing.Point(4, 54);
            this.metroTabPage1.Name = "metroTabPage1";
            this.metroTabPage1.Size = new System.Drawing.Size(801, 369);
            this.metroTabPage1.TabIndex = 0;
            this.metroTabPage1.Text = "Input";
            this.metroTabPage1.VerticalScrollbarBarColor = true;
            this.metroTabPage1.VerticalScrollbarHighlightOnWheel = false;
            this.metroTabPage1.VerticalScrollbarSize = 10;
            // 
            // metroTabPage2
            // 
            this.metroTabPage2.HorizontalScrollbarBarColor = true;
            this.metroTabPage2.HorizontalScrollbarHighlightOnWheel = false;
            this.metroTabPage2.HorizontalScrollbarSize = 10;
            this.metroTabPage2.Location = new System.Drawing.Point(4, 54);
            this.metroTabPage2.Name = "metroTabPage2";
            this.metroTabPage2.Size = new System.Drawing.Size(801, 369);
            this.metroTabPage2.TabIndex = 1;
            this.metroTabPage2.Text = "Processing";
            this.metroTabPage2.VerticalScrollbarBarColor = true;
            this.metroTabPage2.VerticalScrollbarHighlightOnWheel = false;
            this.metroTabPage2.VerticalScrollbarSize = 10;
            // 
            // metroTabPage3
            // 
            this.metroTabPage3.HorizontalScrollbarBarColor = true;
            this.metroTabPage3.HorizontalScrollbarHighlightOnWheel = false;
            this.metroTabPage3.HorizontalScrollbarSize = 10;
            this.metroTabPage3.Location = new System.Drawing.Point(4, 54);
            this.metroTabPage3.Name = "metroTabPage3";
            this.metroTabPage3.Size = new System.Drawing.Size(801, 369);
            this.metroTabPage3.TabIndex = 2;
            this.metroTabPage3.Text = "Appearance";
            this.metroTabPage3.VerticalScrollbarBarColor = true;
            this.metroTabPage3.VerticalScrollbarHighlightOnWheel = false;
            this.metroTabPage3.VerticalScrollbarSize = 10;
            // 
            // metroTabPage4
            // 
            this.metroTabPage4.HorizontalScrollbarBarColor = true;
            this.metroTabPage4.HorizontalScrollbarHighlightOnWheel = false;
            this.metroTabPage4.HorizontalScrollbarSize = 10;
            this.metroTabPage4.Location = new System.Drawing.Point(4, 54);
            this.metroTabPage4.Name = "metroTabPage4";
            this.metroTabPage4.Size = new System.Drawing.Size(801, 369);
            this.metroTabPage4.TabIndex = 3;
            this.metroTabPage4.Text = "FPS Text";
            this.metroTabPage4.VerticalScrollbarBarColor = true;
            this.metroTabPage4.VerticalScrollbarHighlightOnWheel = false;
            this.metroTabPage4.VerticalScrollbarSize = 10;
            // 
            // metroTabPage5
            // 
            this.metroTabPage5.HorizontalScrollbarBarColor = true;
            this.metroTabPage5.HorizontalScrollbarHighlightOnWheel = false;
            this.metroTabPage5.HorizontalScrollbarSize = 10;
            this.metroTabPage5.Location = new System.Drawing.Point(4, 54);
            this.metroTabPage5.Name = "metroTabPage5";
            this.metroTabPage5.Size = new System.Drawing.Size(801, 369);
            this.metroTabPage5.TabIndex = 4;
            this.metroTabPage5.Text = "Output";
            this.metroTabPage5.VerticalScrollbarBarColor = true;
            this.metroTabPage5.VerticalScrollbarHighlightOnWheel = false;
            this.metroTabPage5.VerticalScrollbarSize = 10;
            // 
            // TrdropForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(845, 580);
            this.Controls.Add(this.videoTabControl);
            this.Name = "TrdropForm";
            this.Style = MetroFramework.MetroColorStyle.Purple;
            this.Text = "trdrop";
            this.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.videoTabControl.ResumeLayout(false);
            this.firstVideoTab.ResumeLayout(false);
            this.metroTabControl1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        private MetroFramework.Controls.MetroTabControl videoTabControl;
        private VideoOptionsTabPage firstVideoTab = new VideoOptionsTabPage("Video 1");
        private System.Windows.Forms.TabPage addVideoTab = new System.Windows.Forms.TabPage();
        private MetroFramework.Controls.MetroTabControl metroTabControl1;
        private MetroFramework.Controls.MetroTabPage metroTabPage1;
        private MetroFramework.Controls.MetroTabPage metroTabPage2;
        private MetroFramework.Controls.MetroTabPage metroTabPage3;
        private MetroFramework.Controls.MetroTabPage metroTabPage4;
        private MetroFramework.Controls.MetroTabPage metroTabPage5;
    }
}

