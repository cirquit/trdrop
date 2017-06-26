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
        private void InitializeComponent()
        {
            this.videoTabControl = new System.Windows.Forms.TabControl();
            this.videoSubTabControl = new System.Windows.Forms.TabControl();
            this.tabPage3 = new System.Windows.Forms.TabPage();
            this.tabPage4 = new System.Windows.Forms.TabPage();
            this.addVideoTab = new System.Windows.Forms.TabPage();
            this.videoTabControl.SuspendLayout();
            this.firstVideoTab.SuspendLayout();
            this.videoSubTabControl.SuspendLayout();
            this.SuspendLayout();
            // 
            // videoTabControl
            // 
            this.videoTabControl.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.videoTabControl.Controls.Add(this.firstVideoTab);
            this.videoTabControl.Controls.Add(this.addVideoTab);
            this.videoTabControl.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.videoTabControl.ItemSize = new System.Drawing.Size(100, 42);
            this.videoTabControl.Location = new System.Drawing.Point(12, 12);
            this.videoTabControl.Multiline = true;
            this.videoTabControl.Name = "videoTabControl";
            this.videoTabControl.Padding = new System.Drawing.Point(20, 3);
            this.videoTabControl.SelectedIndex = 0;
            this.videoTabControl.Size = new System.Drawing.Size(821, 345);
            this.videoTabControl.TabIndex = 0;
            this.videoTabControl.HandleCreated += new System.EventHandler(this.VideoTabControl_HandleCreated);
            this.videoTabControl.MouseDown += new System.Windows.Forms.MouseEventHandler(this.VideoTabControl_MouseDown);
            // 
            // firstVideoTab
            // 
            this.firstVideoTab.Controls.Add(this.videoSubTabControl);
            this.firstVideoTab.Location = new System.Drawing.Point(4, 46);
            this.firstVideoTab.Name = "firstVideoTab";
            this.firstVideoTab.Padding = new System.Windows.Forms.Padding(3);
            this.firstVideoTab.Size = new System.Drawing.Size(813, 295);
            this.firstVideoTab.TabIndex = 0;
            this.firstVideoTab.Text = "Video 1";
            this.firstVideoTab.UseVisualStyleBackColor = true;
            // 
            // videoSubTabControl
            // 
            this.videoSubTabControl.Alignment = System.Windows.Forms.TabAlignment.Left;
            this.videoSubTabControl.Controls.Add(this.tabPage3);
            this.videoSubTabControl.Controls.Add(this.tabPage4);
            this.videoSubTabControl.DrawMode = System.Windows.Forms.TabDrawMode.OwnerDrawFixed;
            this.videoSubTabControl.ItemSize = new System.Drawing.Size(25, 100);
            this.videoSubTabControl.Location = new System.Drawing.Point(7, 7);
            this.videoSubTabControl.Multiline = true;
            this.videoSubTabControl.Name = "videoSubTabControl";
            this.videoSubTabControl.SelectedIndex = 0;
            this.videoSubTabControl.Size = new System.Drawing.Size(800, 282);
            this.videoSubTabControl.SizeMode = System.Windows.Forms.TabSizeMode.Fixed;
            this.videoSubTabControl.TabIndex = 0;
            this.videoSubTabControl.DrawItem += new System.Windows.Forms.DrawItemEventHandler(this.VideoSubTabControl_DrawItem);
            // 
            // tabPage3
            // 
            this.tabPage3.Location = new System.Drawing.Point(104, 4);
            this.tabPage3.Name = "tabPage3";
            this.tabPage3.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage3.Size = new System.Drawing.Size(692, 274);
            this.tabPage3.TabIndex = 0;
            this.tabPage3.Text = "tabPage3";
            this.tabPage3.UseVisualStyleBackColor = true;
            // 
            // tabPage4
            // 
            this.tabPage4.Location = new System.Drawing.Point(104, 4);
            this.tabPage4.Name = "tabPage4";
            this.tabPage4.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage4.Size = new System.Drawing.Size(692, 274);
            this.tabPage4.TabIndex = 1;
            this.tabPage4.Text = "tabPage4";
            this.tabPage4.UseVisualStyleBackColor = true;
            // 
            // addVideoTab
            // 
            this.addVideoTab.Location = new System.Drawing.Point(4, 46);
            this.addVideoTab.Name = "addVideoTab";
            this.addVideoTab.Padding = new System.Windows.Forms.Padding(3);
            this.addVideoTab.Size = new System.Drawing.Size(813, 295);
            this.addVideoTab.TabIndex = 1;
            this.addVideoTab.Text = "+";
            this.addVideoTab.UseVisualStyleBackColor = true;
            // 
            // TrdropForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(845, 587);
            this.Controls.Add(this.videoTabControl);
            this.Name = "TrdropForm";
            this.Text = "trdrop";
            this.videoTabControl.ResumeLayout(false);
            this.firstVideoTab.ResumeLayout(false);
            this.videoSubTabControl.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        private System.Windows.Forms.TabControl videoTabControl;
        private System.Windows.Forms.TabControl videoSubTabControl;
        private VideoOptionsTabPage firstVideoTab = new VideoOptionsTabPage("Video 1");
        private System.Windows.Forms.TabPage addVideoTab = new System.Windows.Forms.TabPage();
        private System.Windows.Forms.TabPage tabPage3;
        private System.Windows.Forms.TabPage tabPage4;
    }
}

