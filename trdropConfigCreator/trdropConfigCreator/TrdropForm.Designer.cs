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

        //this.videoOptionsTabPage1 = new VideoOptionsTabPage("Video 1");
        private void InitializeComponent()
        {
            this.videoTabControl = new MetroFramework.Controls.MetroTabControl();
            this.addVideoTab = new MetroFramework.Controls.MetroTabPage();
            this.plotSettingsTabControl = new MetroFramework.Controls.MetroTabControl();
            this.plotSettingsTabTage = new MetroFramework.Controls.MetroTabPage();
            this.plotBGAlphaTextBox = new MetroFramework.Controls.MetroTextBox();
            this.plotBGAlphaMaxLabel = new MetroFramework.Controls.MetroLabel();
            this.plotBGAlphaMinLabel = new MetroFramework.Controls.MetroLabel();
            this.plotBGAlphaTrackBar = new MetroFramework.Controls.MetroTrackBar();
            this.plotBGAlphaLabel = new MetroFramework.Controls.MetroLabel();
            this.linesColorHexLabel = new MetroFramework.Controls.MetroLabel();
            this.plotLinesColorPanel = new System.Windows.Forms.Panel();
            this.plotLinesColorHexBox = new MetroFramework.Controls.MetroTextBox();
            this.linesColorLabel = new MetroFramework.Controls.MetroLabel();
            this.plotAxesColorHexLabel = new MetroFramework.Controls.MetroLabel();
            this.plotAxesColorPanel = new System.Windows.Forms.Panel();
            this.plotAxesColorHexBox = new MetroFramework.Controls.MetroTextBox();
            this.plotAxesColorLabel = new MetroFramework.Controls.MetroLabel();
            this.plotBGColorHexLabel = new MetroFramework.Controls.MetroLabel();
            this.plotBGColorPanel = new System.Windows.Forms.Panel();
            this.plotBGColorHexBox = new MetroFramework.Controls.MetroTextBox();
            this.plotBGColorLabel = new MetroFramework.Controls.MetroLabel();
            this.renderButton = new MetroFramework.Controls.MetroButton();
            this.progressBar = new MetroFramework.Controls.MetroProgressBar();
            this.videoTabControl.SuspendLayout();
            this.plotSettingsTabControl.SuspendLayout();
            this.plotSettingsTabTage.SuspendLayout();
            this.SuspendLayout();
            // 
            // videoOptionsTabPage1
            // 
            this.videoOptionsTabPage1.BackColor = System.Drawing.Color.Transparent;
            this.videoOptionsTabPage1.HorizontalScrollbarBarColor = true;
            this.videoOptionsTabPage1.HorizontalScrollbarHighlightOnWheel = false;
            this.videoOptionsTabPage1.HorizontalScrollbarSize = 10;
            this.videoOptionsTabPage1.Location = new System.Drawing.Point(4, 46);
            this.videoOptionsTabPage1.Name = "videoOptionsTabPage1";
            this.videoOptionsTabPage1.Padding = new System.Windows.Forms.Padding(3);
            this.videoOptionsTabPage1.Size = new System.Drawing.Size(810, 430);
            this.videoOptionsTabPage1.TabIndex = 0;
            this.videoOptionsTabPage1.Text = "Video 1";
            this.videoOptionsTabPage1.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.videoOptionsTabPage1.VerticalScrollbarBarColor = true;
            this.videoOptionsTabPage1.VerticalScrollbarHighlightOnWheel = false;
            this.videoOptionsTabPage1.VerticalScrollbarSize = 10;
            this.videoOptionsTabPage1.Visible = false;
            this.videoOptionsTabPage1.Click += new System.EventHandler(this.videoOptionsTabPage1_Click);
            // 
            // videoTabControl
            // 
            this.videoTabControl.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.videoTabControl.Controls.Add(this.videoOptionsTabPage1);
            this.videoTabControl.Controls.Add(this.addVideoTab);
            this.videoTabControl.FontWeight = MetroFramework.MetroTabControlWeight.Regular;
            this.videoTabControl.ItemSize = new System.Drawing.Size(80, 42);
            this.videoTabControl.Location = new System.Drawing.Point(12, 63);
            this.videoTabControl.Multiline = true;
            this.videoTabControl.Name = "videoTabControl";
            this.videoTabControl.SelectedIndex = 0;
            this.videoTabControl.Size = new System.Drawing.Size(818, 480);
            this.videoTabControl.SizeMode = System.Windows.Forms.TabSizeMode.Fixed;
            this.videoTabControl.Style = MetroFramework.MetroColorStyle.Purple;
            this.videoTabControl.TabIndex = 0;
            this.videoTabControl.TabStop = false;
            this.videoTabControl.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.videoTabControl.UseSelectable = true;
            this.videoTabControl.SelectedIndexChanged += new System.EventHandler(this.videoTabControl_SelectedIndexChanged);
            this.videoTabControl.Deselected += new System.Windows.Forms.TabControlEventHandler(this.videoTabControl_Deselected);
            this.videoTabControl.MouseDown += new System.Windows.Forms.MouseEventHandler(this.VideoTabControl_MouseDown);
            this.videoTabControl.MouseUp += new System.Windows.Forms.MouseEventHandler(this.videoTabControl_MouseUp);
            // 
            // addVideoTab
            // 
            this.addVideoTab.BackColor = System.Drawing.Color.DimGray;
            this.addVideoTab.HorizontalScrollbarBarColor = true;
            this.addVideoTab.HorizontalScrollbarHighlightOnWheel = false;
            this.addVideoTab.HorizontalScrollbarSize = 10;
            this.addVideoTab.Location = new System.Drawing.Point(4, 46);
            this.addVideoTab.Name = "addVideoTab";
            this.addVideoTab.Padding = new System.Windows.Forms.Padding(3);
            this.addVideoTab.Size = new System.Drawing.Size(810, 430);
            this.addVideoTab.Style = MetroFramework.MetroColorStyle.Purple;
            this.addVideoTab.TabIndex = 1;
            this.addVideoTab.Text = "+";
            this.addVideoTab.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.addVideoTab.VerticalScrollbarBarColor = true;
            this.addVideoTab.VerticalScrollbarHighlightOnWheel = false;
            this.addVideoTab.VerticalScrollbarSize = 10;
            // 
            // plotSettingsTabControl
            // 
            this.plotSettingsTabControl.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.plotSettingsTabControl.Controls.Add(this.plotSettingsTabTage);
            this.plotSettingsTabControl.Location = new System.Drawing.Point(12, 546);
            this.plotSettingsTabControl.Name = "plotSettingsTabControl";
            this.plotSettingsTabControl.SelectedIndex = 0;
            this.plotSettingsTabControl.Size = new System.Drawing.Size(814, 264);
            this.plotSettingsTabControl.Style = MetroFramework.MetroColorStyle.Purple;
            this.plotSettingsTabControl.TabIndex = 1;
            this.plotSettingsTabControl.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.plotSettingsTabControl.UseSelectable = true;
            // 
            // plotSettingsTabTage
            // 
            this.plotSettingsTabTage.Controls.Add(this.plotBGAlphaTextBox);
            this.plotSettingsTabTage.Controls.Add(this.plotBGAlphaMaxLabel);
            this.plotSettingsTabTage.Controls.Add(this.plotBGAlphaMinLabel);
            this.plotSettingsTabTage.Controls.Add(this.plotBGAlphaTrackBar);
            this.plotSettingsTabTage.Controls.Add(this.plotBGAlphaLabel);
            this.plotSettingsTabTage.Controls.Add(this.linesColorHexLabel);
            this.plotSettingsTabTage.Controls.Add(this.plotLinesColorPanel);
            this.plotSettingsTabTage.Controls.Add(this.plotLinesColorHexBox);
            this.plotSettingsTabTage.Controls.Add(this.linesColorLabel);
            this.plotSettingsTabTage.Controls.Add(this.plotAxesColorHexLabel);
            this.plotSettingsTabTage.Controls.Add(this.plotAxesColorPanel);
            this.plotSettingsTabTage.Controls.Add(this.plotAxesColorHexBox);
            this.plotSettingsTabTage.Controls.Add(this.plotAxesColorLabel);
            this.plotSettingsTabTage.Controls.Add(this.plotBGColorHexLabel);
            this.plotSettingsTabTage.Controls.Add(this.plotBGColorPanel);
            this.plotSettingsTabTage.Controls.Add(this.plotBGColorHexBox);
            this.plotSettingsTabTage.Controls.Add(this.plotBGColorLabel);
            this.plotSettingsTabTage.HorizontalScrollbarBarColor = true;
            this.plotSettingsTabTage.HorizontalScrollbarHighlightOnWheel = false;
            this.plotSettingsTabTage.HorizontalScrollbarSize = 10;
            this.plotSettingsTabTage.Location = new System.Drawing.Point(4, 38);
            this.plotSettingsTabTage.Name = "plotSettingsTabTage";
            this.plotSettingsTabTage.Size = new System.Drawing.Size(806, 222);
            this.plotSettingsTabTage.Style = MetroFramework.MetroColorStyle.Purple;
            this.plotSettingsTabTage.TabIndex = 0;
            this.plotSettingsTabTage.Text = "Plot Settings";
            this.plotSettingsTabTage.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.plotSettingsTabTage.VerticalScrollbarBarColor = true;
            this.plotSettingsTabTage.VerticalScrollbarHighlightOnWheel = false;
            this.plotSettingsTabTage.VerticalScrollbarSize = 10;
            // 
            // plotBGAlphaTextBox
            // 
            // 
            // 
            // 
            this.plotBGAlphaTextBox.CustomButton.Image = null;
            this.plotBGAlphaTextBox.CustomButton.Location = new System.Drawing.Point(24, 1);
            this.plotBGAlphaTextBox.CustomButton.Name = "";
            this.plotBGAlphaTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.plotBGAlphaTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.plotBGAlphaTextBox.CustomButton.TabIndex = 1;
            this.plotBGAlphaTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.plotBGAlphaTextBox.CustomButton.UseSelectable = true;
            this.plotBGAlphaTextBox.CustomButton.Visible = false;
            this.plotBGAlphaTextBox.Lines = new string[0];
            this.plotBGAlphaTextBox.Location = new System.Drawing.Point(747, 29);
            this.plotBGAlphaTextBox.MaxLength = 32767;
            this.plotBGAlphaTextBox.Name = "plotBGAlphaTextBox";
            this.plotBGAlphaTextBox.PasswordChar = '\0';
            this.plotBGAlphaTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.plotBGAlphaTextBox.SelectedText = "";
            this.plotBGAlphaTextBox.SelectionLength = 0;
            this.plotBGAlphaTextBox.SelectionStart = 0;
            this.plotBGAlphaTextBox.ShortcutsEnabled = true;
            this.plotBGAlphaTextBox.Size = new System.Drawing.Size(46, 23);
            this.plotBGAlphaTextBox.TabIndex = 35;
            this.plotBGAlphaTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.plotBGAlphaTextBox.UseSelectable = true;
            this.plotBGAlphaTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.plotBGAlphaTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // plotBGAlphaMaxLabel
            // 
            this.plotBGAlphaMaxLabel.AutoSize = true;
            this.plotBGAlphaMaxLabel.Location = new System.Drawing.Point(720, 50);
            this.plotBGAlphaMaxLabel.Name = "plotBGAlphaMaxLabel";
            this.plotBGAlphaMaxLabel.Size = new System.Drawing.Size(28, 19);
            this.plotBGAlphaMaxLabel.TabIndex = 34;
            this.plotBGAlphaMaxLabel.Text = "100";
            this.plotBGAlphaMaxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // plotBGAlphaMinLabel
            // 
            this.plotBGAlphaMinLabel.AutoSize = true;
            this.plotBGAlphaMinLabel.Location = new System.Drawing.Point(497, 50);
            this.plotBGAlphaMinLabel.Name = "plotBGAlphaMinLabel";
            this.plotBGAlphaMinLabel.Size = new System.Drawing.Size(16, 19);
            this.plotBGAlphaMinLabel.TabIndex = 33;
            this.plotBGAlphaMinLabel.Text = "0";
            this.plotBGAlphaMinLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // plotBGAlphaTrackBar
            // 
            this.plotBGAlphaTrackBar.BackColor = System.Drawing.Color.Transparent;
            this.plotBGAlphaTrackBar.LargeChange = 1;
            this.plotBGAlphaTrackBar.Location = new System.Drawing.Point(501, 29);
            this.plotBGAlphaTrackBar.MouseWheelBarPartitions = 5;
            this.plotBGAlphaTrackBar.Name = "plotBGAlphaTrackBar";
            this.plotBGAlphaTrackBar.Size = new System.Drawing.Size(236, 23);
            this.plotBGAlphaTrackBar.TabIndex = 32;
            this.plotBGAlphaTrackBar.Text = "metroTrackBar4";
            this.plotBGAlphaTrackBar.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.plotBGAlphaTrackBar.Value = 100;
            // 
            // plotBGAlphaLabel
            // 
            this.plotBGAlphaLabel.AutoSize = true;
            this.plotBGAlphaLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.plotBGAlphaLabel.Location = new System.Drawing.Point(441, 29);
            this.plotBGAlphaLabel.Name = "plotBGAlphaLabel";
            this.plotBGAlphaLabel.Size = new System.Drawing.Size(60, 25);
            this.plotBGAlphaLabel.TabIndex = 31;
            this.plotBGAlphaLabel.Text = "Alpha:";
            this.plotBGAlphaLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // linesColorHexLabel
            // 
            this.linesColorHexLabel.AutoSize = true;
            this.linesColorHexLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.linesColorHexLabel.Location = new System.Drawing.Point(276, 176);
            this.linesColorHexLabel.Name = "linesColorHexLabel";
            this.linesColorHexLabel.Size = new System.Drawing.Size(45, 25);
            this.linesColorHexLabel.TabIndex = 30;
            this.linesColorHexLabel.Text = "Hex:";
            this.linesColorHexLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // plotLinesColorPanel
            // 
            this.plotLinesColorPanel.BackColor = System.Drawing.Color.Crimson;
            this.plotLinesColorPanel.Location = new System.Drawing.Point(197, 171);
            this.plotLinesColorPanel.Name = "plotLinesColorPanel";
            this.plotLinesColorPanel.Size = new System.Drawing.Size(64, 39);
            this.plotLinesColorPanel.TabIndex = 29;
            // 
            // plotLinesColorHexBox
            // 
            // 
            // 
            // 
            this.plotLinesColorHexBox.CustomButton.Image = null;
            this.plotLinesColorHexBox.CustomButton.Location = new System.Drawing.Point(62, 1);
            this.plotLinesColorHexBox.CustomButton.Name = "";
            this.plotLinesColorHexBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.plotLinesColorHexBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.plotLinesColorHexBox.CustomButton.TabIndex = 1;
            this.plotLinesColorHexBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.plotLinesColorHexBox.CustomButton.UseSelectable = true;
            this.plotLinesColorHexBox.CustomButton.Visible = false;
            this.plotLinesColorHexBox.Lines = new string[0];
            this.plotLinesColorHexBox.Location = new System.Drawing.Point(327, 178);
            this.plotLinesColorHexBox.MaxLength = 32767;
            this.plotLinesColorHexBox.Name = "plotLinesColorHexBox";
            this.plotLinesColorHexBox.PasswordChar = '\0';
            this.plotLinesColorHexBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.plotLinesColorHexBox.SelectedText = "";
            this.plotLinesColorHexBox.SelectionLength = 0;
            this.plotLinesColorHexBox.SelectionStart = 0;
            this.plotLinesColorHexBox.ShortcutsEnabled = true;
            this.plotLinesColorHexBox.Size = new System.Drawing.Size(84, 23);
            this.plotLinesColorHexBox.TabIndex = 28;
            this.plotLinesColorHexBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.plotLinesColorHexBox.UseSelectable = true;
            this.plotLinesColorHexBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.plotLinesColorHexBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // linesColorLabel
            // 
            this.linesColorLabel.AutoSize = true;
            this.linesColorLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.linesColorLabel.Location = new System.Drawing.Point(30, 176);
            this.linesColorLabel.Name = "linesColorLabel";
            this.linesColorLabel.Size = new System.Drawing.Size(101, 25);
            this.linesColorLabel.TabIndex = 27;
            this.linesColorLabel.Text = "Lines Color:";
            this.linesColorLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // plotAxesColorHexLabel
            // 
            this.plotAxesColorHexLabel.AutoSize = true;
            this.plotAxesColorHexLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.plotAxesColorHexLabel.Location = new System.Drawing.Point(276, 102);
            this.plotAxesColorHexLabel.Name = "plotAxesColorHexLabel";
            this.plotAxesColorHexLabel.Size = new System.Drawing.Size(45, 25);
            this.plotAxesColorHexLabel.TabIndex = 26;
            this.plotAxesColorHexLabel.Text = "Hex:";
            this.plotAxesColorHexLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // plotAxesColorPanel
            // 
            this.plotAxesColorPanel.BackColor = System.Drawing.Color.Crimson;
            this.plotAxesColorPanel.Location = new System.Drawing.Point(197, 97);
            this.plotAxesColorPanel.Name = "plotAxesColorPanel";
            this.plotAxesColorPanel.Size = new System.Drawing.Size(64, 39);
            this.plotAxesColorPanel.TabIndex = 25;
            // 
            // plotAxesColorHexBox
            // 
            // 
            // 
            // 
            this.plotAxesColorHexBox.CustomButton.Image = null;
            this.plotAxesColorHexBox.CustomButton.Location = new System.Drawing.Point(62, 1);
            this.plotAxesColorHexBox.CustomButton.Name = "";
            this.plotAxesColorHexBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.plotAxesColorHexBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.plotAxesColorHexBox.CustomButton.TabIndex = 1;
            this.plotAxesColorHexBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.plotAxesColorHexBox.CustomButton.UseSelectable = true;
            this.plotAxesColorHexBox.CustomButton.Visible = false;
            this.plotAxesColorHexBox.Lines = new string[0];
            this.plotAxesColorHexBox.Location = new System.Drawing.Point(327, 104);
            this.plotAxesColorHexBox.MaxLength = 32767;
            this.plotAxesColorHexBox.Name = "plotAxesColorHexBox";
            this.plotAxesColorHexBox.PasswordChar = '\0';
            this.plotAxesColorHexBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.plotAxesColorHexBox.SelectedText = "";
            this.plotAxesColorHexBox.SelectionLength = 0;
            this.plotAxesColorHexBox.SelectionStart = 0;
            this.plotAxesColorHexBox.ShortcutsEnabled = true;
            this.plotAxesColorHexBox.Size = new System.Drawing.Size(84, 23);
            this.plotAxesColorHexBox.TabIndex = 24;
            this.plotAxesColorHexBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.plotAxesColorHexBox.UseSelectable = true;
            this.plotAxesColorHexBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.plotAxesColorHexBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // plotAxesColorLabel
            // 
            this.plotAxesColorLabel.AutoSize = true;
            this.plotAxesColorLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.plotAxesColorLabel.Location = new System.Drawing.Point(30, 102);
            this.plotAxesColorLabel.Name = "plotAxesColorLabel";
            this.plotAxesColorLabel.Size = new System.Drawing.Size(98, 25);
            this.plotAxesColorLabel.TabIndex = 23;
            this.plotAxesColorLabel.Text = "Axes Color:";
            this.plotAxesColorLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // plotBGColorHexLabel
            // 
            this.plotBGColorHexLabel.AutoSize = true;
            this.plotBGColorHexLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.plotBGColorHexLabel.Location = new System.Drawing.Point(274, 29);
            this.plotBGColorHexLabel.Name = "plotBGColorHexLabel";
            this.plotBGColorHexLabel.Size = new System.Drawing.Size(45, 25);
            this.plotBGColorHexLabel.TabIndex = 22;
            this.plotBGColorHexLabel.Text = "Hex:";
            this.plotBGColorHexLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // plotBGColorPanel
            // 
            this.plotBGColorPanel.BackColor = System.Drawing.Color.Chartreuse;
            this.plotBGColorPanel.Location = new System.Drawing.Point(195, 24);
            this.plotBGColorPanel.Name = "plotBGColorPanel";
            this.plotBGColorPanel.Size = new System.Drawing.Size(64, 39);
            this.plotBGColorPanel.TabIndex = 21;
            // 
            // plotBGColorHexBox
            // 
            // 
            // 
            // 
            this.plotBGColorHexBox.CustomButton.Image = null;
            this.plotBGColorHexBox.CustomButton.Location = new System.Drawing.Point(62, 1);
            this.plotBGColorHexBox.CustomButton.Name = "";
            this.plotBGColorHexBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.plotBGColorHexBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.plotBGColorHexBox.CustomButton.TabIndex = 1;
            this.plotBGColorHexBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.plotBGColorHexBox.CustomButton.UseSelectable = true;
            this.plotBGColorHexBox.CustomButton.Visible = false;
            this.plotBGColorHexBox.Lines = new string[0];
            this.plotBGColorHexBox.Location = new System.Drawing.Point(325, 31);
            this.plotBGColorHexBox.MaxLength = 32767;
            this.plotBGColorHexBox.Name = "plotBGColorHexBox";
            this.plotBGColorHexBox.PasswordChar = '\0';
            this.plotBGColorHexBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.plotBGColorHexBox.SelectedText = "";
            this.plotBGColorHexBox.SelectionLength = 0;
            this.plotBGColorHexBox.SelectionStart = 0;
            this.plotBGColorHexBox.ShortcutsEnabled = true;
            this.plotBGColorHexBox.Size = new System.Drawing.Size(84, 23);
            this.plotBGColorHexBox.TabIndex = 20;
            this.plotBGColorHexBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.plotBGColorHexBox.UseSelectable = true;
            this.plotBGColorHexBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.plotBGColorHexBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // plotBGColorLabel
            // 
            this.plotBGColorLabel.AutoSize = true;
            this.plotBGColorLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.plotBGColorLabel.Location = new System.Drawing.Point(30, 29);
            this.plotBGColorLabel.Name = "plotBGColorLabel";
            this.plotBGColorLabel.Size = new System.Drawing.Size(154, 25);
            this.plotBGColorLabel.TabIndex = 19;
            this.plotBGColorLabel.Text = "Background Color:";
            this.plotBGColorLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // renderButton
            // 
            this.renderButton.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.renderButton.FontSize = MetroFramework.MetroButtonSize.Tall;
            this.renderButton.Location = new System.Drawing.Point(652, 827);
            this.renderButton.Name = "renderButton";
            this.renderButton.Size = new System.Drawing.Size(164, 40);
            this.renderButton.TabIndex = 2;
            this.renderButton.Text = "Render";
            this.renderButton.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.renderButton.UseSelectable = true;
            // 
            // progressBar
            // 
            this.progressBar.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.progressBar.Location = new System.Drawing.Point(23, 837);
            this.progressBar.Name = "progressBar";
            this.progressBar.Size = new System.Drawing.Size(609, 23);
            this.progressBar.Style = MetroFramework.MetroColorStyle.Purple;
            this.progressBar.TabIndex = 3;
            this.progressBar.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.progressBar.Value = 75;
            // 
            // TrdropForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(842, 886);
            this.Controls.Add(this.progressBar);
            this.Controls.Add(this.renderButton);
            this.Controls.Add(this.plotSettingsTabControl);
            this.Controls.Add(this.videoTabControl);
            this.MinimumSize = new System.Drawing.Size(842, 886);
            this.Name = "TrdropForm";
            this.Style = MetroFramework.MetroColorStyle.Purple;
            this.Text = "trdrop";
            this.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.videoTabControl.ResumeLayout(false);
            this.plotSettingsTabControl.ResumeLayout(false);
            this.plotSettingsTabTage.ResumeLayout(false);
            this.plotSettingsTabTage.PerformLayout();
            this.ResumeLayout(false);

        }

        private MetroFramework.Controls.MetroTabControl videoTabControl;
        private MetroFramework.Controls.MetroTabPage addVideoTab;
        private MetroFramework.Controls.MetroTabControl plotSettingsTabControl;
        private MetroFramework.Controls.MetroTabPage plotSettingsTabTage;
        private MetroFramework.Controls.MetroLabel linesColorHexLabel;
        private System.Windows.Forms.Panel plotLinesColorPanel;
        private MetroFramework.Controls.MetroTextBox plotLinesColorHexBox;
        private MetroFramework.Controls.MetroLabel linesColorLabel;
        private MetroFramework.Controls.MetroLabel plotAxesColorHexLabel;
        private System.Windows.Forms.Panel plotAxesColorPanel;
        private MetroFramework.Controls.MetroTextBox plotAxesColorHexBox;
        private MetroFramework.Controls.MetroLabel plotAxesColorLabel;
        private MetroFramework.Controls.MetroLabel plotBGColorHexLabel;
        private System.Windows.Forms.Panel plotBGColorPanel;
        private MetroFramework.Controls.MetroTextBox plotBGColorHexBox;
        private MetroFramework.Controls.MetroLabel plotBGColorLabel;
        private MetroFramework.Controls.MetroTextBox plotBGAlphaTextBox;
        private MetroFramework.Controls.MetroLabel plotBGAlphaMaxLabel;
        private MetroFramework.Controls.MetroLabel plotBGAlphaMinLabel;
        private MetroFramework.Controls.MetroTrackBar plotBGAlphaTrackBar;
        private MetroFramework.Controls.MetroLabel plotBGAlphaLabel;
        private MetroFramework.Controls.MetroButton renderButton;
        private MetroFramework.Controls.MetroProgressBar progressBar;
        private VideoOptionsTabPage videoOptionsTabPage1 = new VideoOptionsTabPage("Video 1");
    }
}

