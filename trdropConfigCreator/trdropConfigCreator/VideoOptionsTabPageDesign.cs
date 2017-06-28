using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace trdropConfigCreator
{
    partial class VideoOptionsTabPage
    {
        private MetroFramework.Controls.MetroTabControl videoSubTabControl;
        private MetroFramework.Controls.MetroTabPage inputTabPage;
        private MetroFramework.Controls.MetroTabPage processingTabPage;
        private MetroFramework.Controls.MetroTabPage appearanceTabPage;
        private MetroFramework.Controls.MetroTabPage fpsTabPage;
        private MetroFramework.Controls.MetroTabPage outputTabPage;
        private MetroFramework.Controls.MetroButton inputBrowseButton;
        private MetroFramework.Controls.MetroTextBox inputFileTextBox;
        private MetroFramework.Controls.MetroLabel inputFileLabel;
        private MetroFramework.Controls.MetroTextBox lnToleranceTextBox;
        private MetroFramework.Controls.MetroLabel lnToleranceMaxLabel;
        private MetroFramework.Controls.MetroLabel lnToleranceMinLabel;
        private MetroFramework.Controls.MetroTrackBar lnToleranceTrackBar;
        private MetroFramework.Controls.MetroLabel lnToleranceLabel;
        private MetroFramework.Controls.MetroTextBox pxToleranceTextBox;
        private MetroFramework.Controls.MetroLabel pxToleranceMaxLabel;
        private MetroFramework.Controls.MetroLabel pxToleranceMinLabel;
        private MetroFramework.Controls.MetroTrackBar pxToleranceTrackBar;
        private MetroFramework.Controls.MetroLabel pxToleranceLabel;
        private ColorPanel videoColorPanel;
        private HexBox videoColorHexBox;
        private MetroFramework.Controls.MetroLabel videoColorLabel;
        private MetroFramework.Controls.MetroLabel tearColorHexLabel;
        private ColorPanel tearColorPanel;
        private HexBox tearColorHexBox;
        private MetroFramework.Controls.MetroLabel tearColorLabel;
        private MetroFramework.Controls.MetroLabel videoColorHexLabel;
        private MetroFramework.Controls.MetroTextBox fpsTextBox;
        private MetroFramework.Controls.MetroLabel fpsTextLabel;
        private MetroFramework.Controls.MetroCheckBox shadowCheckBox;
        private MetroFramework.Controls.MetroLabel shadowColorHexLabel;
        private ColorPanel shadowColorPanel;
        private HexBox shadowColorHexBox;
        private MetroFramework.Controls.MetroLabel shadowColorLabel;
        private MetroFramework.Controls.MetroComboBox fpsPrecisionDropDown;
        private MetroFramework.Controls.MetroLabel refreshRateLabel;
        private MetroFramework.Controls.MetroLabel fpsPrecisionLabel;
        private MetroFramework.Controls.MetroLabel fpsTextPositionYPxLabel;
        private MetroFramework.Controls.MetroLabel fpsTextPositionXPxLabel;
        private MetroFramework.Controls.MetroTextBox textYPositionTextBox;
        private MetroFramework.Controls.MetroTextBox textXPositionTextBox;
        private MetroFramework.Controls.MetroLabel fpsTextPositionYLabel;
        private MetroFramework.Controls.MetroLabel fpsTextPositionXLabel;
        private MetroFramework.Controls.MetroLabel fpsTextPositionLabel;
        private MetroFramework.Controls.MetroTextBox refreshRateTextBox;
        private MetroFramework.Controls.MetroLabel refreshRateMaxLabel;
        private MetroFramework.Controls.MetroLabel refreshRateMinLabel;
        private MetroFramework.Controls.MetroTrackBar refreshRateTrackBar;
        private MetroFramework.Controls.MetroTextBox outputFileTextBox;
        private MetroFramework.Controls.MetroLabel outputFileLabel;
        private MetroFramework.Controls.MetroLabel logfileExtensionLabel;
        private MetroFramework.Controls.MetroTextBox logfileTextBox;
        private MetroFramework.Controls.MetroLabel logfileLabel;
        private MetroFramework.Controls.MetroTextBox codecTextBox;
        private MetroFramework.Controls.MetroLabel codecLabel;
        private MetroFramework.Controls.MetroCheckBox bmpsCheckBox;
        private MetroFramework.Controls.MetroComboBox outputExtensionDropDown;
        private MetroFramework.Controls.MetroLabel writerLabel;
        private MetroFramework.Controls.MetroLabel writerHeightPxLabel;
        private MetroFramework.Controls.MetroLabel writerWidthPxLabel;
        private MetroFramework.Controls.MetroTextBox writerHeightTextBox;
        private MetroFramework.Controls.MetroTextBox writerWidthTextBox;
        private MetroFramework.Controls.MetroLabel viewerLabel;
        private MetroFramework.Controls.MetroLabel viewerHeightPxLabel;
        private MetroFramework.Controls.MetroLabel viewerWidthPxLabel;
        private MetroFramework.Controls.MetroTextBox viewerHeightTextBox;
        private MetroFramework.Controls.MetroTextBox viewerWidthTextBox;
        private MetroFramework.Controls.MetroLabel viewerHeightLabel;
        private MetroFramework.Controls.MetroLabel viewerWidthLabel;
        private MetroFramework.Controls.MetroLabel outputSizesLabel;
        private MetroFramework.Controls.MetroLabel writerHeightLabel;
        private MetroFramework.Controls.MetroLabel writerWidthLabel;
        private MetroFramework.Controls.MetroLabel lnTolerancePercentageLabel;

        public void InitializeComponent()
        {
            this.videoSubTabControl = new MetroFramework.Controls.MetroTabControl();
            this.inputTabPage = new MetroFramework.Controls.MetroTabPage();
            this.inputBrowseButton = new MetroFramework.Controls.MetroButton();
            this.inputFileTextBox = new MetroFramework.Controls.MetroTextBox();
            this.inputFileLabel = new MetroFramework.Controls.MetroLabel();
            this.processingTabPage = new MetroFramework.Controls.MetroTabPage();
            this.lnToleranceTextBox = new MetroFramework.Controls.MetroTextBox();
            this.lnToleranceMaxLabel = new MetroFramework.Controls.MetroLabel();
            this.lnToleranceMinLabel = new MetroFramework.Controls.MetroLabel();
            this.lnToleranceTrackBar = new MetroFramework.Controls.MetroTrackBar();
            this.lnToleranceLabel = new MetroFramework.Controls.MetroLabel();
            this.pxToleranceTextBox = new MetroFramework.Controls.MetroTextBox();
            this.pxToleranceMaxLabel = new MetroFramework.Controls.MetroLabel();
            this.pxToleranceMinLabel = new MetroFramework.Controls.MetroLabel();
            this.pxToleranceTrackBar = new MetroFramework.Controls.MetroTrackBar();
            this.pxToleranceLabel = new MetroFramework.Controls.MetroLabel();
            this.appearanceTabPage = new MetroFramework.Controls.MetroTabPage();
            this.tearColorHexLabel = new MetroFramework.Controls.MetroLabel();
            this.tearColorPanel = new ColorPanel();
            this.tearColorHexBox = new HexBox(tearColorPanel);
            this.tearColorLabel = new MetroFramework.Controls.MetroLabel();
            this.videoColorHexLabel = new MetroFramework.Controls.MetroLabel();
            this.videoColorPanel = new ColorPanel();
            this.videoColorHexBox = new HexBox(videoColorPanel);
            this.videoColorLabel = new MetroFramework.Controls.MetroLabel();
            this.fpsTabPage = new MetroFramework.Controls.MetroTabPage();
            this.refreshRateTextBox = new MetroFramework.Controls.MetroTextBox();
            this.refreshRateMaxLabel = new MetroFramework.Controls.MetroLabel();
            this.refreshRateMinLabel = new MetroFramework.Controls.MetroLabel();
            this.refreshRateTrackBar = new MetroFramework.Controls.MetroTrackBar();
            this.fpsPrecisionDropDown = new MetroFramework.Controls.MetroComboBox();
            this.refreshRateLabel = new MetroFramework.Controls.MetroLabel();
            this.fpsPrecisionLabel = new MetroFramework.Controls.MetroLabel();
            this.fpsTextPositionYPxLabel = new MetroFramework.Controls.MetroLabel();
            this.fpsTextPositionXPxLabel = new MetroFramework.Controls.MetroLabel();
            this.textYPositionTextBox = new MetroFramework.Controls.MetroTextBox();
            this.textXPositionTextBox = new MetroFramework.Controls.MetroTextBox();
            this.fpsTextPositionYLabel = new MetroFramework.Controls.MetroLabel();
            this.fpsTextPositionXLabel = new MetroFramework.Controls.MetroLabel();
            this.fpsTextPositionLabel = new MetroFramework.Controls.MetroLabel();
            this.fpsTextBox = new MetroFramework.Controls.MetroTextBox();
            this.fpsTextLabel = new MetroFramework.Controls.MetroLabel();
            this.shadowCheckBox = new MetroFramework.Controls.MetroCheckBox();
            this.shadowColorHexLabel = new MetroFramework.Controls.MetroLabel();
            this.shadowColorPanel = new ColorPanel();
            this.shadowColorHexBox = new HexBox(shadowColorPanel);
            this.shadowColorLabel = new MetroFramework.Controls.MetroLabel();
            this.outputTabPage = new MetroFramework.Controls.MetroTabPage();
            this.writerHeightLabel = new MetroFramework.Controls.MetroLabel();
            this.writerWidthLabel = new MetroFramework.Controls.MetroLabel();
            this.writerLabel = new MetroFramework.Controls.MetroLabel();
            this.writerHeightPxLabel = new MetroFramework.Controls.MetroLabel();
            this.writerWidthPxLabel = new MetroFramework.Controls.MetroLabel();
            this.writerHeightTextBox = new MetroFramework.Controls.MetroTextBox();
            this.writerWidthTextBox = new MetroFramework.Controls.MetroTextBox();
            this.viewerLabel = new MetroFramework.Controls.MetroLabel();
            this.viewerHeightPxLabel = new MetroFramework.Controls.MetroLabel();
            this.viewerWidthPxLabel = new MetroFramework.Controls.MetroLabel();
            this.viewerHeightTextBox = new MetroFramework.Controls.MetroTextBox();
            this.viewerWidthTextBox = new MetroFramework.Controls.MetroTextBox();
            this.viewerHeightLabel = new MetroFramework.Controls.MetroLabel();
            this.viewerWidthLabel = new MetroFramework.Controls.MetroLabel();
            this.outputSizesLabel = new MetroFramework.Controls.MetroLabel();
            this.logfileExtensionLabel = new MetroFramework.Controls.MetroLabel();
            this.logfileTextBox = new MetroFramework.Controls.MetroTextBox();
            this.logfileLabel = new MetroFramework.Controls.MetroLabel();
            this.codecTextBox = new MetroFramework.Controls.MetroTextBox();
            this.codecLabel = new MetroFramework.Controls.MetroLabel();
            this.bmpsCheckBox = new MetroFramework.Controls.MetroCheckBox();
            this.outputExtensionDropDown = new MetroFramework.Controls.MetroComboBox();
            this.outputFileTextBox = new MetroFramework.Controls.MetroTextBox();
            this.outputFileLabel = new MetroFramework.Controls.MetroLabel();
            this.lnTolerancePercentageLabel = new MetroFramework.Controls.MetroLabel();

            this.videoSubTabControl.SuspendLayout();
            this.inputTabPage.SuspendLayout();
            this.processingTabPage.SuspendLayout();
            this.appearanceTabPage.SuspendLayout();
            this.fpsTabPage.SuspendLayout();
            this.outputTabPage.SuspendLayout();
            this.SuspendLayout();
            // 
            // this Page
            // 
            this.BackColor = System.Drawing.Color.Transparent;
            this.HorizontalScrollbarBarColor = true;
            this.HorizontalScrollbarHighlightOnWheel = false;
            this.HorizontalScrollbarSize = 10;
            this.Location = new System.Drawing.Point(4, 46);
            this.Name = "videoTab_1";
            this.Padding = new System.Windows.Forms.Padding(3);
            this.Size = new System.Drawing.Size(810, 430);
            this.TabIndex = 0;
            this.Text = "Video 1";
            this.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.VerticalScrollbarBarColor = true;
            this.VerticalScrollbarHighlightOnWheel = false;
            this.VerticalScrollbarSize = 10;
            // 
            // videoSubTabControl
            // 
            this.Controls.Add(this.videoSubTabControl);
            this.videoSubTabControl.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left)
            | System.Windows.Forms.AnchorStyles.Right)));
            this.videoSubTabControl.Controls.Add(this.inputTabPage);
            this.videoSubTabControl.Controls.Add(this.processingTabPage);
            this.videoSubTabControl.Controls.Add(this.appearanceTabPage);
            this.videoSubTabControl.Controls.Add(this.fpsTabPage);
            this.videoSubTabControl.Controls.Add(this.outputTabPage);
            this.videoSubTabControl.SelectedIndex = 0;
            this.videoSubTabControl.FontWeight = MetroFramework.MetroTabControlWeight.Regular;
            this.videoSubTabControl.ItemSize = new System.Drawing.Size(100, 50);
            this.videoSubTabControl.Location = new System.Drawing.Point(23, 7);
            this.videoSubTabControl.Multiline = true;
            this.videoSubTabControl.Name = "videoSubTabControl";
            this.videoSubTabControl.Size = new System.Drawing.Size(791, 427);
            this.videoSubTabControl.SizeMode = System.Windows.Forms.TabSizeMode.Fixed;
            this.videoSubTabControl.Style = MetroFramework.MetroColorStyle.Purple;
            this.videoSubTabControl.TabIndex = 2;
            this.videoSubTabControl.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.videoSubTabControl.UseSelectable = true;
            // 
            // inputTabPage
            // 
            this.inputTabPage.Controls.Add(this.inputBrowseButton);
            this.inputTabPage.Controls.Add(this.inputFileTextBox);
            this.inputTabPage.Controls.Add(this.inputFileLabel);
            this.inputTabPage.HorizontalScrollbarBarColor = true;
            this.inputTabPage.HorizontalScrollbarHighlightOnWheel = false;
            this.inputTabPage.HorizontalScrollbarSize = 10;
            this.inputTabPage.Location = new System.Drawing.Point(4, 54);
            this.inputTabPage.Name = "inputTabPage";
            this.inputTabPage.Size = new System.Drawing.Size(783, 369);
            this.inputTabPage.TabIndex = 0;
            this.inputTabPage.Text = "Input";
            this.inputTabPage.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.inputTabPage.VerticalScrollbarBarColor = true;
            this.inputTabPage.VerticalScrollbarHighlightOnWheel = false;
            this.inputTabPage.VerticalScrollbarSize = 10;
            // 
            // inputBrowseButton
            // 
            this.inputBrowseButton.Location = new System.Drawing.Point(454, 26);
            this.inputBrowseButton.Name = "inputBrowseButton";
            this.inputBrowseButton.Size = new System.Drawing.Size(75, 23);
            this.inputBrowseButton.TabIndex = 4;
            this.inputBrowseButton.Text = "Browse...";
            this.inputBrowseButton.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.inputBrowseButton.UseSelectable = true;
            this.inputBrowseButton.Click += new EventHandler(this.inputBrowseButton_Click);
            // 
            // inputFileTextBox
            // 
            // 
            // 
            // 
            this.inputFileTextBox.CustomButton.Image = null;
            this.inputFileTextBox.CustomButton.Location = new System.Drawing.Point(322, 1);
            this.inputFileTextBox.CustomButton.Name = "";
            this.inputFileTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.inputFileTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.inputFileTextBox.CustomButton.TabIndex = 1;
            this.inputFileTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.inputFileTextBox.CustomButton.UseSelectable = true;
            this.inputFileTextBox.CustomButton.Visible = false;
            this.inputFileTextBox.Lines = new string[0];
            this.inputFileTextBox.Location = new System.Drawing.Point(104, 26);
            this.inputFileTextBox.MaxLength = 32767;
            this.inputFileTextBox.Name = "inputFileTextBox";
            this.inputFileTextBox.PasswordChar = '\0';
            this.inputFileTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.inputFileTextBox.SelectedText = "";
            this.inputFileTextBox.SelectionLength = 0;
            this.inputFileTextBox.SelectionStart = 0;
            this.inputFileTextBox.ShortcutsEnabled = true;
            this.inputFileTextBox.Size = new System.Drawing.Size(344, 23);
            this.inputFileTextBox.TabIndex = 3;
            this.inputFileTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.inputFileTextBox.UseSelectable = true;
            this.inputFileTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.inputFileTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // inputFileLabel
            // 
            this.inputFileLabel.AutoSize = true;
            this.inputFileLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.inputFileLabel.Location = new System.Drawing.Point(3, 24);
            this.inputFileLabel.Name = "inputFileLabel";
            this.inputFileLabel.Size = new System.Drawing.Size(85, 25);
            this.inputFileLabel.TabIndex = 2;
            this.inputFileLabel.Text = "Input File:";
            this.inputFileLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // processingTabPage
            // 
            this.processingTabPage.Controls.Add(this.lnTolerancePercentageLabel);
            this.processingTabPage.Controls.Add(this.lnToleranceTextBox);
            this.processingTabPage.Controls.Add(this.lnToleranceMaxLabel);
            this.processingTabPage.Controls.Add(this.lnToleranceMinLabel);
            this.processingTabPage.Controls.Add(this.lnToleranceTrackBar);
            this.processingTabPage.Controls.Add(this.lnToleranceLabel);
            this.processingTabPage.Controls.Add(this.pxToleranceTextBox);
            this.processingTabPage.Controls.Add(this.pxToleranceMaxLabel);
            this.processingTabPage.Controls.Add(this.pxToleranceMinLabel);
            this.processingTabPage.Controls.Add(this.pxToleranceTrackBar);
            this.processingTabPage.Controls.Add(this.pxToleranceLabel);
            this.processingTabPage.HorizontalScrollbarBarColor = true;
            this.processingTabPage.HorizontalScrollbarHighlightOnWheel = false;
            this.processingTabPage.HorizontalScrollbarSize = 10;
            this.processingTabPage.Location = new System.Drawing.Point(4, 54);
            this.processingTabPage.Name = "processingTabPage";
            this.processingTabPage.Size = new System.Drawing.Size(783, 369);
            this.processingTabPage.TabIndex = 1;
            this.processingTabPage.Text = "Processing";
            this.processingTabPage.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.processingTabPage.VerticalScrollbarBarColor = true;
            this.processingTabPage.VerticalScrollbarHighlightOnWheel = false;
            this.processingTabPage.VerticalScrollbarSize = 10;
            // 
            // lnToleranceTextBox
            // 
            // 
            // 
            // 
            this.lnToleranceTextBox.CustomButton.Image = null;
            this.lnToleranceTextBox.CustomButton.Location = new System.Drawing.Point(37, 1);
            this.lnToleranceTextBox.CustomButton.Name = "";
            this.lnToleranceTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.lnToleranceTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.lnToleranceTextBox.CustomButton.TabIndex = 1;
            this.lnToleranceTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.lnToleranceTextBox.CustomButton.UseSelectable = true;
            this.lnToleranceTextBox.CustomButton.Visible = false;
            this.lnToleranceTextBox.Lines = new string[0];
            this.lnToleranceTextBox.Location = new System.Drawing.Point(669, 101);
            this.lnToleranceTextBox.MaxLength = 32767;
            this.lnToleranceTextBox.Name = "lnToleranceTextBox";
            this.lnToleranceTextBox.PasswordChar = '\0';
            this.lnToleranceTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.lnToleranceTextBox.SelectedText = "";
            this.lnToleranceTextBox.SelectionLength = 0;
            this.lnToleranceTextBox.SelectionStart = 0;
            this.lnToleranceTextBox.ShortcutsEnabled = true;
            this.lnToleranceTextBox.Size = new System.Drawing.Size(59, 23);
            this.lnToleranceTextBox.TabIndex = 12;
            this.lnToleranceTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.lnToleranceTextBox.UseSelectable = true;
            this.lnToleranceTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.lnToleranceTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // lnToleranceMaxLabel
            // 
            this.lnToleranceMaxLabel.AutoSize = true;
            this.lnToleranceMaxLabel.Location = new System.Drawing.Point(632, 122);
            this.lnToleranceMaxLabel.Name = "lnToleranceMaxLabel";
            this.lnToleranceMaxLabel.Size = new System.Drawing.Size(28, 19);
            this.lnToleranceMaxLabel.TabIndex = 11;
            this.lnToleranceMaxLabel.Text = "100";
            this.lnToleranceMaxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // lnToleranceMinLabel
            // 
            this.lnToleranceMinLabel.AutoSize = true;
            this.lnToleranceMinLabel.Location = new System.Drawing.Point(131, 122);
            this.lnToleranceMinLabel.Name = "lnToleranceMinLabel";
            this.lnToleranceMinLabel.Size = new System.Drawing.Size(16, 19);
            this.lnToleranceMinLabel.TabIndex = 10;
            this.lnToleranceMinLabel.Text = "0";
            this.lnToleranceMinLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // lnToleranceTrackBar
            // 
            this.lnToleranceTrackBar.BackColor = System.Drawing.Color.Transparent;
            this.lnToleranceTrackBar.LargeChange = 1;
            this.lnToleranceTrackBar.Location = new System.Drawing.Point(136, 102);
            this.lnToleranceTrackBar.MouseWheelBarPartitions = 5;
            this.lnToleranceTrackBar.Name = "lnToleranceTrackBar";
            this.lnToleranceTrackBar.Size = new System.Drawing.Size(515, 23);
            this.lnToleranceTrackBar.TabIndex = 9;
            this.lnToleranceTrackBar.Text = "metroTrackBar2";
            this.lnToleranceTrackBar.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.lnToleranceTrackBar.Value = 5;
            // 
            // lnToleranceLabel
            // 
            this.lnToleranceLabel.AutoSize = true;
            this.lnToleranceLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.lnToleranceLabel.Location = new System.Drawing.Point(3, 97);
            this.lnToleranceLabel.Name = "lnToleranceLabel";
            this.lnToleranceLabel.Size = new System.Drawing.Size(123, 25);
            this.lnToleranceLabel.TabIndex = 8;
            this.lnToleranceLabel.Text = "Line Tolerance:";
            this.lnToleranceLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // pxToleranceTextBox
            // 
            // 
            // 
            // 
            this.pxToleranceTextBox.CustomButton.Image = null;
            this.pxToleranceTextBox.CustomButton.Location = new System.Drawing.Point(37, 1);
            this.pxToleranceTextBox.CustomButton.Name = "";
            this.pxToleranceTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.pxToleranceTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.pxToleranceTextBox.CustomButton.TabIndex = 1;
            this.pxToleranceTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.pxToleranceTextBox.CustomButton.UseSelectable = true;
            this.pxToleranceTextBox.CustomButton.Visible = false;
            this.pxToleranceTextBox.Lines = new string[0];
            this.pxToleranceTextBox.Location = new System.Drawing.Point(669, 28);
            this.pxToleranceTextBox.MaxLength = 32767;
            this.pxToleranceTextBox.Name = "pxToleranceTextBox";
            this.pxToleranceTextBox.PasswordChar = '\0';
            this.pxToleranceTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.pxToleranceTextBox.SelectedText = "";
            this.pxToleranceTextBox.SelectionLength = 0;
            this.pxToleranceTextBox.SelectionStart = 0;
            this.pxToleranceTextBox.ShortcutsEnabled = true;
            this.pxToleranceTextBox.Size = new System.Drawing.Size(59, 23);
            this.pxToleranceTextBox.TabIndex = 7;
            this.pxToleranceTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.pxToleranceTextBox.UseSelectable = true;
            this.pxToleranceTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.pxToleranceTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // pxToleranceMaxLabel
            // 
            this.pxToleranceMaxLabel.AutoSize = true;
            this.pxToleranceMaxLabel.Location = new System.Drawing.Point(632, 49);
            this.pxToleranceMaxLabel.Name = "pxToleranceMaxLabel";
            this.pxToleranceMaxLabel.Size = new System.Drawing.Size(30, 19);
            this.pxToleranceMaxLabel.TabIndex = 6;
            this.pxToleranceMaxLabel.Text = "255";
            this.pxToleranceMaxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // pxToleranceMinLabel
            // 
            this.pxToleranceMinLabel.AutoSize = true;
            this.pxToleranceMinLabel.Location = new System.Drawing.Point(131, 49);
            this.pxToleranceMinLabel.Name = "pxToleranceMinLabel";
            this.pxToleranceMinLabel.Size = new System.Drawing.Size(16, 19);
            this.pxToleranceMinLabel.TabIndex = 5;
            this.pxToleranceMinLabel.Text = "0";
            this.pxToleranceMinLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // pxToleranceTrackBar
            // 
            this.pxToleranceTrackBar.BackColor = System.Drawing.Color.Transparent;
            this.pxToleranceTrackBar.LargeChange = 1;
            this.pxToleranceTrackBar.Location = new System.Drawing.Point(136, 29);
            this.pxToleranceTrackBar.Maximum = 255;
            this.pxToleranceTrackBar.MouseWheelBarPartitions = 5;
            this.pxToleranceTrackBar.Name = "pxToleranceTrackBar";
            this.pxToleranceTrackBar.Size = new System.Drawing.Size(515, 23);
            this.pxToleranceTrackBar.TabIndex = 4;
            this.pxToleranceTrackBar.Text = "metroTrackBar1";
            this.pxToleranceTrackBar.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.pxToleranceTrackBar.Value = 5;
            // 
            // pxToleranceLabel
            // 
            this.pxToleranceLabel.AutoSize = true;
            this.pxToleranceLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.pxToleranceLabel.Location = new System.Drawing.Point(3, 24);
            this.pxToleranceLabel.Name = "pxToleranceLabel";
            this.pxToleranceLabel.Size = new System.Drawing.Size(127, 25);
            this.pxToleranceLabel.TabIndex = 3;
            this.pxToleranceLabel.Text = "Pixel Tolerance:";
            this.pxToleranceLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // appearanceTabPage
            // 
            this.appearanceTabPage.Controls.Add(this.tearColorHexLabel);
            this.appearanceTabPage.Controls.Add(this.tearColorPanel);
            this.appearanceTabPage.Controls.Add(this.tearColorHexBox);
            this.appearanceTabPage.Controls.Add(this.tearColorLabel);
            this.appearanceTabPage.Controls.Add(this.videoColorHexLabel);
            this.appearanceTabPage.Controls.Add(this.videoColorPanel);
            this.appearanceTabPage.Controls.Add(this.videoColorHexBox);
            this.appearanceTabPage.Controls.Add(this.videoColorLabel);
            this.appearanceTabPage.HorizontalScrollbarBarColor = true;
            this.appearanceTabPage.HorizontalScrollbarHighlightOnWheel = false;
            this.appearanceTabPage.HorizontalScrollbarSize = 10;
            this.appearanceTabPage.Location = new System.Drawing.Point(4, 54);
            this.appearanceTabPage.Name = "appearanceTabPage";
            this.appearanceTabPage.Size = new System.Drawing.Size(783, 369);
            this.appearanceTabPage.TabIndex = 2;
            this.appearanceTabPage.Text = "Appearance";
            this.appearanceTabPage.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.appearanceTabPage.VerticalScrollbarBarColor = true;
            this.appearanceTabPage.VerticalScrollbarHighlightOnWheel = false;
            this.appearanceTabPage.VerticalScrollbarSize = 10;
            // 
            // tearColorHexLabel
            // 
            this.tearColorHexLabel.AutoSize = true;
            this.tearColorHexLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.tearColorHexLabel.Location = new System.Drawing.Point(210, 97);
            this.tearColorHexLabel.Name = "tearColorHexLabel";
            this.tearColorHexLabel.Size = new System.Drawing.Size(45, 25);
            this.tearColorHexLabel.TabIndex = 18;
            this.tearColorHexLabel.Text = "Hex:";
            this.tearColorHexLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // tearColorPanel
            // 
            this.tearColorPanel.BackColor = System.Drawing.Color.Crimson;
            this.tearColorPanel.Location = new System.Drawing.Point(131, 92);
            this.tearColorPanel.Name = "tearColorPanel";
            this.tearColorPanel.Size = new System.Drawing.Size(64, 39);
            this.tearColorPanel.TabIndex = 17;
            this.tearColorPanel.SetHexBox(tearColorHexBox);
            // 
            // tearColorHexBox
            // 
            // 
            // 
            // 
            this.tearColorHexBox.CustomButton.Image = null;
            this.tearColorHexBox.CustomButton.Location = new System.Drawing.Point(62, 1);
            this.tearColorHexBox.CustomButton.Name = "";
            this.tearColorHexBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.tearColorHexBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.tearColorHexBox.CustomButton.TabIndex = 1;
            this.tearColorHexBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.tearColorHexBox.CustomButton.UseSelectable = true;
            this.tearColorHexBox.CustomButton.Visible = false;
            this.tearColorHexBox.Lines = new string[0];
            this.tearColorHexBox.Location = new System.Drawing.Point(261, 99);
            this.tearColorHexBox.MaxLength = 32767;
            this.tearColorHexBox.Name = "tearColorHexBox";
            this.tearColorHexBox.PasswordChar = '\0';
            this.tearColorHexBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.tearColorHexBox.SelectedText = "";
            this.tearColorHexBox.SelectionLength = 0;
            this.tearColorHexBox.SelectionStart = 0;
            this.tearColorHexBox.ShortcutsEnabled = true;
            this.tearColorHexBox.Size = new System.Drawing.Size(84, 23);
            this.tearColorHexBox.TabIndex = 16;
            this.tearColorHexBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.tearColorHexBox.UseSelectable = true;
            this.tearColorHexBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.tearColorHexBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // tearColorLabel
            // 
            this.tearColorLabel.AutoSize = true;
            this.tearColorLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.tearColorLabel.Location = new System.Drawing.Point(3, 97);
            this.tearColorLabel.Name = "tearColorLabel";
            this.tearColorLabel.Size = new System.Drawing.Size(93, 25);
            this.tearColorLabel.TabIndex = 15;
            this.tearColorLabel.Text = "Tear Color:";
            this.tearColorLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // videoColorHexLabel
            // 
            this.videoColorHexLabel.AutoSize = true;
            this.videoColorHexLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.videoColorHexLabel.Location = new System.Drawing.Point(210, 24);
            this.videoColorHexLabel.Name = "videoColorHexLabel";
            this.videoColorHexLabel.Size = new System.Drawing.Size(45, 25);
            this.videoColorHexLabel.TabIndex = 14;
            this.videoColorHexLabel.Text = "Hex:";
            this.videoColorHexLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // videoColorPanel
            // 
            this.videoColorPanel.BackColor = System.Drawing.Color.Chartreuse;
            this.videoColorPanel.Location = new System.Drawing.Point(131, 19);
            this.videoColorPanel.Name = "videoColorPanel";
            this.videoColorPanel.Size = new System.Drawing.Size(64, 39);
            this.videoColorPanel.TabIndex = 13;
            this.videoColorPanel.SetHexBox(videoColorHexBox);
            // 
            // videoColorHexBox
            // 
            // 
            // 
            // 
            this.videoColorHexBox.CustomButton.Image = null;
            this.videoColorHexBox.CustomButton.Location = new System.Drawing.Point(62, 1);
            this.videoColorHexBox.CustomButton.Name = "";
            this.videoColorHexBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.videoColorHexBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.videoColorHexBox.CustomButton.TabIndex = 1;
            this.videoColorHexBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.videoColorHexBox.CustomButton.UseSelectable = true;
            this.videoColorHexBox.CustomButton.Visible = false;
            this.videoColorHexBox.Lines = new string[0];
            this.videoColorHexBox.Location = new System.Drawing.Point(261, 26);
            this.videoColorHexBox.MaxLength = 32767;
            this.videoColorHexBox.Name = "videoColorHexBox";
            this.videoColorHexBox.PasswordChar = '\0';
            this.videoColorHexBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.videoColorHexBox.SelectedText = "";
            this.videoColorHexBox.SelectionLength = 0;
            this.videoColorHexBox.SelectionStart = 0;
            this.videoColorHexBox.ShortcutsEnabled = true;
            this.videoColorHexBox.Size = new System.Drawing.Size(84, 23);
            this.videoColorHexBox.TabIndex = 12;
            this.videoColorHexBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.videoColorHexBox.UseSelectable = true;
            this.videoColorHexBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.videoColorHexBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // videoColorLabel
            // 
            this.videoColorLabel.AutoSize = true;
            this.videoColorLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.videoColorLabel.Location = new System.Drawing.Point(3, 24);
            this.videoColorLabel.Name = "videoColorLabel";
            this.videoColorLabel.Size = new System.Drawing.Size(107, 25);
            this.videoColorLabel.TabIndex = 8;
            this.videoColorLabel.Text = "Video Color:";
            this.videoColorLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // fpsTabPage
            // 
            this.fpsTabPage.Controls.Add(this.refreshRateTextBox);
            this.fpsTabPage.Controls.Add(this.refreshRateMaxLabel);
            this.fpsTabPage.Controls.Add(this.refreshRateMinLabel);
            this.fpsTabPage.Controls.Add(this.refreshRateTrackBar);
            this.fpsTabPage.Controls.Add(this.fpsPrecisionDropDown);
            this.fpsTabPage.Controls.Add(this.refreshRateLabel);
            this.fpsTabPage.Controls.Add(this.fpsPrecisionLabel);
            this.fpsTabPage.Controls.Add(this.fpsTextPositionYPxLabel);
            this.fpsTabPage.Controls.Add(this.fpsTextPositionXPxLabel);
            this.fpsTabPage.Controls.Add(this.textYPositionTextBox);
            this.fpsTabPage.Controls.Add(this.textXPositionTextBox);
            this.fpsTabPage.Controls.Add(this.fpsTextPositionYLabel);
            this.fpsTabPage.Controls.Add(this.fpsTextPositionXLabel);
            this.fpsTabPage.Controls.Add(this.fpsTextPositionLabel);
            this.fpsTabPage.Controls.Add(this.fpsTextBox);
            this.fpsTabPage.Controls.Add(this.fpsTextLabel);
            this.fpsTabPage.Controls.Add(this.shadowCheckBox);
            this.fpsTabPage.Controls.Add(this.shadowColorHexLabel);
            this.fpsTabPage.Controls.Add(this.shadowColorPanel);
            this.fpsTabPage.Controls.Add(this.shadowColorHexBox);
            this.fpsTabPage.Controls.Add(this.shadowColorLabel);
            this.fpsTabPage.HorizontalScrollbarBarColor = true;
            this.fpsTabPage.HorizontalScrollbarHighlightOnWheel = false;
            this.fpsTabPage.HorizontalScrollbarSize = 10;
            this.fpsTabPage.Location = new System.Drawing.Point(4, 54);
            this.fpsTabPage.Name = "fpsTabPage";
            this.fpsTabPage.Size = new System.Drawing.Size(783, 369);
            this.fpsTabPage.TabIndex = 3;
            this.fpsTabPage.Text = "FPS Text";
            this.fpsTabPage.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.fpsTabPage.VerticalScrollbarBarColor = true;
            this.fpsTabPage.VerticalScrollbarHighlightOnWheel = false;
            this.fpsTabPage.VerticalScrollbarSize = 10;
            // 
            // refreshRateTextBox
            // 
            // 
            // 
            // 
            this.refreshRateTextBox.CustomButton.Image = null;
            this.refreshRateTextBox.CustomButton.Location = new System.Drawing.Point(37, 1);
            this.refreshRateTextBox.CustomButton.Name = "";
            this.refreshRateTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.refreshRateTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.refreshRateTextBox.CustomButton.TabIndex = 1;
            this.refreshRateTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.refreshRateTextBox.CustomButton.UseSelectable = true;
            this.refreshRateTextBox.CustomButton.Visible = false;
            this.refreshRateTextBox.Lines = new string[0];
            this.refreshRateTextBox.Location = new System.Drawing.Point(658, 299);
            this.refreshRateTextBox.MaxLength = 32767;
            this.refreshRateTextBox.Name = "refreshRateTextBox";
            this.refreshRateTextBox.PasswordChar = '\0';
            this.refreshRateTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.refreshRateTextBox.SelectedText = "";
            this.refreshRateTextBox.SelectionLength = 0;
            this.refreshRateTextBox.SelectionStart = 0;
            this.refreshRateTextBox.ShortcutsEnabled = true;
            this.refreshRateTextBox.Size = new System.Drawing.Size(59, 23);
            this.refreshRateTextBox.TabIndex = 44;
            this.refreshRateTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.refreshRateTextBox.UseSelectable = true;
            this.refreshRateTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.refreshRateTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // refreshRateMaxLabel
            // 
            this.refreshRateMaxLabel.AutoSize = true;
            this.refreshRateMaxLabel.Location = new System.Drawing.Point(620, 320);
            this.refreshRateMaxLabel.Name = "refreshRateMaxLabel";
            this.refreshRateMaxLabel.Size = new System.Drawing.Size(35, 19);
            this.refreshRateMaxLabel.TabIndex = 43;
            this.refreshRateMaxLabel.Text = "1000";
            this.refreshRateMaxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // refreshRateMinLabel
            // 
            this.refreshRateMinLabel.AutoSize = true;
            this.refreshRateMinLabel.Location = new System.Drawing.Point(120, 320);
            this.refreshRateMinLabel.Name = "refreshRateMinLabel";
            this.refreshRateMinLabel.Size = new System.Drawing.Size(16, 19);
            this.refreshRateMinLabel.TabIndex = 42;
            this.refreshRateMinLabel.Text = "0";
            this.refreshRateMinLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // refreshRateTrackBar
            // 
            this.refreshRateTrackBar.BackColor = System.Drawing.Color.Transparent;
            this.refreshRateTrackBar.LargeChange = 1;
            this.refreshRateTrackBar.Location = new System.Drawing.Point(125, 300);
            this.refreshRateTrackBar.MouseWheelBarPartitions = 5;
            this.refreshRateTrackBar.Name = "refreshRateTrackBar";
            this.refreshRateTrackBar.Size = new System.Drawing.Size(515, 23);
            this.refreshRateTrackBar.TabIndex = 41;
            this.refreshRateTrackBar.Text = "metroTrackBar3";
            this.refreshRateTrackBar.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.refreshRateTrackBar.Value = 5;
            // 
            // fpsPrecisionDropDown
            // 
            this.fpsPrecisionDropDown.FormattingEnabled = true;
            this.fpsPrecisionDropDown.ItemHeight = 23;
            this.fpsPrecisionDropDown.Items.AddRange(new object[] {
            "1",
            "2",
            "3",
            "4"});
            this.fpsPrecisionDropDown.Location = new System.Drawing.Point(641, 23);
            this.fpsPrecisionDropDown.Name = "fpsPrecisionDropDown";
            this.fpsPrecisionDropDown.Size = new System.Drawing.Size(70, 29);
            this.fpsPrecisionDropDown.TabIndex = 40;
            this.fpsPrecisionDropDown.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.fpsPrecisionDropDown.UseSelectable = true;
            // 
            // refreshRateLabel
            // 
            this.refreshRateLabel.AutoSize = true;
            this.refreshRateLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.refreshRateLabel.Location = new System.Drawing.Point(3, 298);
            this.refreshRateLabel.Name = "refreshRateLabel";
            this.refreshRateLabel.Size = new System.Drawing.Size(110, 25);
            this.refreshRateLabel.TabIndex = 39;
            this.refreshRateLabel.Text = "Refresh Rate:";
            this.refreshRateLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // fpsPrecisionLabel
            // 
            this.fpsPrecisionLabel.AutoSize = true;
            this.fpsPrecisionLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.fpsPrecisionLabel.Location = new System.Drawing.Point(513, 24);
            this.fpsPrecisionLabel.Name = "fpsPrecisionLabel";
            this.fpsPrecisionLabel.Size = new System.Drawing.Size(116, 25);
            this.fpsPrecisionLabel.TabIndex = 38;
            this.fpsPrecisionLabel.Text = "FPS Precision:";
            this.fpsPrecisionLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // fpsTextPositionYPxLabel
            // 
            this.fpsTextPositionYPxLabel.AutoSize = true;
            this.fpsTextPositionYPxLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.fpsTextPositionYPxLabel.Location = new System.Drawing.Point(226, 235);
            this.fpsTextPositionYPxLabel.Name = "fpsTextPositionYPxLabel";
            this.fpsTextPositionYPxLabel.Size = new System.Drawing.Size(30, 25);
            this.fpsTextPositionYPxLabel.TabIndex = 37;
            this.fpsTextPositionYPxLabel.Text = "px";
            this.fpsTextPositionYPxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // fpsTextPositionXPxLabel
            // 
            this.fpsTextPositionXPxLabel.AutoSize = true;
            this.fpsTextPositionXPxLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.fpsTextPositionXPxLabel.Location = new System.Drawing.Point(226, 171);
            this.fpsTextPositionXPxLabel.Name = "fpsTextPositionXPxLabel";
            this.fpsTextPositionXPxLabel.Size = new System.Drawing.Size(30, 25);
            this.fpsTextPositionXPxLabel.TabIndex = 36;
            this.fpsTextPositionXPxLabel.Text = "px";
            this.fpsTextPositionXPxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // textYPositionTextBox
            // 
            // 
            // 
            // 
            this.textYPositionTextBox.CustomButton.Image = null;
            this.textYPositionTextBox.CustomButton.Location = new System.Drawing.Point(42, 1);
            this.textYPositionTextBox.CustomButton.Name = "";
            this.textYPositionTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.textYPositionTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.textYPositionTextBox.CustomButton.TabIndex = 1;
            this.textYPositionTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.textYPositionTextBox.CustomButton.UseSelectable = true;
            this.textYPositionTextBox.CustomButton.Visible = false;
            this.textYPositionTextBox.Lines = new string[0];
            this.textYPositionTextBox.Location = new System.Drawing.Point(161, 237);
            this.textYPositionTextBox.MaxLength = 32767;
            this.textYPositionTextBox.Name = "textYPositionTextBox";
            this.textYPositionTextBox.PasswordChar = '\0';
            this.textYPositionTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.textYPositionTextBox.SelectedText = "";
            this.textYPositionTextBox.SelectionLength = 0;
            this.textYPositionTextBox.SelectionStart = 0;
            this.textYPositionTextBox.ShortcutsEnabled = true;
            this.textYPositionTextBox.Size = new System.Drawing.Size(64, 23);
            this.textYPositionTextBox.TabIndex = 35;
            this.textYPositionTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.textYPositionTextBox.UseSelectable = true;
            this.textYPositionTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.textYPositionTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // textXPositionTextBox
            // 
            // 
            // 
            // 
            this.textXPositionTextBox.CustomButton.Image = null;
            this.textXPositionTextBox.CustomButton.Location = new System.Drawing.Point(42, 1);
            this.textXPositionTextBox.CustomButton.Name = "";
            this.textXPositionTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.textXPositionTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.textXPositionTextBox.CustomButton.TabIndex = 1;
            this.textXPositionTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.textXPositionTextBox.CustomButton.UseSelectable = true;
            this.textXPositionTextBox.CustomButton.Visible = false;
            this.textXPositionTextBox.Lines = new string[0];
            this.textXPositionTextBox.Location = new System.Drawing.Point(161, 173);
            this.textXPositionTextBox.MaxLength = 32767;
            this.textXPositionTextBox.Name = "textXPositionTextBox";
            this.textXPositionTextBox.PasswordChar = '\0';
            this.textXPositionTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.textXPositionTextBox.SelectedText = "";
            this.textXPositionTextBox.SelectionLength = 0;
            this.textXPositionTextBox.SelectionStart = 0;
            this.textXPositionTextBox.ShortcutsEnabled = true;
            this.textXPositionTextBox.Size = new System.Drawing.Size(64, 23);
            this.textXPositionTextBox.TabIndex = 34;
            this.textXPositionTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.textXPositionTextBox.UseSelectable = true;
            this.textXPositionTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.textXPositionTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // fpsTextPositionYLabel
            // 
            this.fpsTextPositionYLabel.AutoSize = true;
            this.fpsTextPositionYLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.fpsTextPositionYLabel.Location = new System.Drawing.Point(131, 235);
            this.fpsTextPositionYLabel.Name = "fpsTextPositionYLabel";
            this.fpsTextPositionYLabel.Size = new System.Drawing.Size(24, 25);
            this.fpsTextPositionYLabel.TabIndex = 33;
            this.fpsTextPositionYLabel.Text = "y:";
            this.fpsTextPositionYLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // fpsTextPositionXLabel
            // 
            this.fpsTextPositionXLabel.AutoSize = true;
            this.fpsTextPositionXLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.fpsTextPositionXLabel.Location = new System.Drawing.Point(131, 171);
            this.fpsTextPositionXLabel.Name = "fpsTextPositionXLabel";
            this.fpsTextPositionXLabel.Size = new System.Drawing.Size(24, 25);
            this.fpsTextPositionXLabel.TabIndex = 32;
            this.fpsTextPositionXLabel.Text = "x:";
            this.fpsTextPositionXLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // fpsTextPositionLabel
            // 
            this.fpsTextPositionLabel.AutoSize = true;
            this.fpsTextPositionLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.fpsTextPositionLabel.Location = new System.Drawing.Point(3, 171);
            this.fpsTextPositionLabel.Name = "fpsTextPositionLabel";
            this.fpsTextPositionLabel.Size = new System.Drawing.Size(108, 25);
            this.fpsTextPositionLabel.TabIndex = 31;
            this.fpsTextPositionLabel.Text = "Text Position:";
            this.fpsTextPositionLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // fpsTextBox
            // 
            // 
            // 
            // 
            this.fpsTextBox.CustomButton.Image = null;
            this.fpsTextBox.CustomButton.Location = new System.Drawing.Point(315, 1);
            this.fpsTextBox.CustomButton.Name = "";
            this.fpsTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.fpsTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.fpsTextBox.CustomButton.TabIndex = 1;
            this.fpsTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.fpsTextBox.CustomButton.UseSelectable = true;
            this.fpsTextBox.CustomButton.Visible = false;
            this.fpsTextBox.Lines = new string[0];
            this.fpsTextBox.Location = new System.Drawing.Point(133, 26);
            this.fpsTextBox.MaxLength = 32767;
            this.fpsTextBox.Name = "fpsTextBox";
            this.fpsTextBox.PasswordChar = '\0';
            this.fpsTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.fpsTextBox.SelectedText = "";
            this.fpsTextBox.SelectionLength = 0;
            this.fpsTextBox.SelectionStart = 0;
            this.fpsTextBox.ShortcutsEnabled = true;
            this.fpsTextBox.Size = new System.Drawing.Size(337, 23);
            this.fpsTextBox.TabIndex = 30;
            this.fpsTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.fpsTextBox.UseSelectable = true;
            this.fpsTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.fpsTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // fpsTextLabel
            // 
            this.fpsTextLabel.AutoSize = true;
            this.fpsTextLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.fpsTextLabel.Location = new System.Drawing.Point(3, 24);
            this.fpsTextLabel.Name = "fpsTextLabel";
            this.fpsTextLabel.Size = new System.Drawing.Size(76, 25);
            this.fpsTextLabel.TabIndex = 29;
            this.fpsTextLabel.Text = "FPS Text:";
            this.fpsTextLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // shadowCheckBox
            // 
            this.shadowCheckBox.AutoSize = true;
            this.shadowCheckBox.Location = new System.Drawing.Point(403, 103);
            this.shadowCheckBox.Name = "shadowCheckBox";
            this.shadowCheckBox.Size = new System.Drawing.Size(97, 15);
            this.shadowCheckBox.TabIndex = 28;
            this.shadowCheckBox.Text = "Show Shadow";
            this.shadowCheckBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.shadowCheckBox.UseSelectable = true;
            // 
            // shadowColorHexLabel
            // 
            this.shadowColorHexLabel.AutoSize = true;
            this.shadowColorHexLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.shadowColorHexLabel.Location = new System.Drawing.Point(240, 97);
            this.shadowColorHexLabel.Name = "shadowColorHexLabel";
            this.shadowColorHexLabel.Size = new System.Drawing.Size(45, 25);
            this.shadowColorHexLabel.TabIndex = 27;
            this.shadowColorHexLabel.Text = "Hex:";
            this.shadowColorHexLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // shadowColorPanel
            // 
            this.shadowColorPanel.BackColor = System.Drawing.Color.Chartreuse;
            this.shadowColorPanel.Location = new System.Drawing.Point(161, 92);
            this.shadowColorPanel.Name = "shadowColorPanel";
            this.shadowColorPanel.Size = new System.Drawing.Size(64, 39);
            this.shadowColorPanel.TabIndex = 26;
            this.shadowColorPanel.SetHexBox(shadowColorHexBox);
            // 
            // shadowColorHexBox
            // 
            // 
            // 
            // 
            this.shadowColorHexBox.CustomButton.Image = null;
            this.shadowColorHexBox.CustomButton.Location = new System.Drawing.Point(62, 1);
            this.shadowColorHexBox.CustomButton.Name = "";
            this.shadowColorHexBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.shadowColorHexBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.shadowColorHexBox.CustomButton.TabIndex = 1;
            this.shadowColorHexBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.shadowColorHexBox.CustomButton.UseSelectable = true;
            this.shadowColorHexBox.CustomButton.Visible = false;
            this.shadowColorHexBox.Lines = new string[0];
            this.shadowColorHexBox.Location = new System.Drawing.Point(291, 99);
            this.shadowColorHexBox.MaxLength = 32767;
            this.shadowColorHexBox.Name = "shadowColorHexBox";
            this.shadowColorHexBox.PasswordChar = '\0';
            this.shadowColorHexBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.shadowColorHexBox.SelectedText = "";
            this.shadowColorHexBox.SelectionLength = 0;
            this.shadowColorHexBox.SelectionStart = 0;
            this.shadowColorHexBox.ShortcutsEnabled = true;
            this.shadowColorHexBox.Size = new System.Drawing.Size(84, 23);
            this.shadowColorHexBox.TabIndex = 25;
            this.shadowColorHexBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.shadowColorHexBox.UseSelectable = true;
            this.shadowColorHexBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.shadowColorHexBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // shadowColorLabel
            // 
            this.shadowColorLabel.AutoSize = true;
            this.shadowColorLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.shadowColorLabel.Location = new System.Drawing.Point(3, 97);
            this.shadowColorLabel.Name = "shadowColorLabel";
            this.shadowColorLabel.Size = new System.Drawing.Size(123, 25);
            this.shadowColorLabel.TabIndex = 24;
            this.shadowColorLabel.Text = "Shadow Color:";
            this.shadowColorLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // outputTabPage
            // 
            this.outputTabPage.Controls.Add(this.writerHeightLabel);
            this.outputTabPage.Controls.Add(this.writerWidthLabel);
            this.outputTabPage.Controls.Add(this.writerLabel);
            this.outputTabPage.Controls.Add(this.writerHeightPxLabel);
            this.outputTabPage.Controls.Add(this.writerWidthPxLabel);
            this.outputTabPage.Controls.Add(this.writerHeightTextBox);
            this.outputTabPage.Controls.Add(this.writerWidthTextBox);
            this.outputTabPage.Controls.Add(this.viewerLabel);
            this.outputTabPage.Controls.Add(this.viewerHeightPxLabel);
            this.outputTabPage.Controls.Add(this.viewerWidthPxLabel);
            this.outputTabPage.Controls.Add(this.viewerHeightTextBox);
            this.outputTabPage.Controls.Add(this.viewerWidthTextBox);
            this.outputTabPage.Controls.Add(this.viewerHeightLabel);
            this.outputTabPage.Controls.Add(this.viewerWidthLabel);
            this.outputTabPage.Controls.Add(this.outputSizesLabel);
            this.outputTabPage.Controls.Add(this.logfileExtensionLabel);
            this.outputTabPage.Controls.Add(this.logfileTextBox);
            this.outputTabPage.Controls.Add(this.logfileLabel);
            this.outputTabPage.Controls.Add(this.codecTextBox);
            this.outputTabPage.Controls.Add(this.codecLabel);
            this.outputTabPage.Controls.Add(this.bmpsCheckBox);
            this.outputTabPage.Controls.Add(this.outputExtensionDropDown);
            this.outputTabPage.Controls.Add(this.outputFileTextBox);
            this.outputTabPage.Controls.Add(this.outputFileLabel);
            this.outputTabPage.HorizontalScrollbarBarColor = true;
            this.outputTabPage.HorizontalScrollbarHighlightOnWheel = false;
            this.outputTabPage.HorizontalScrollbarSize = 10;
            this.outputTabPage.Location = new System.Drawing.Point(4, 54);
            this.outputTabPage.Name = "outputTabPage";
            this.outputTabPage.Size = new System.Drawing.Size(783, 369);
            this.outputTabPage.TabIndex = 4;
            this.outputTabPage.Text = "Output";
            this.outputTabPage.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.outputTabPage.VerticalScrollbarBarColor = true;
            this.outputTabPage.VerticalScrollbarHighlightOnWheel = false;
            this.outputTabPage.VerticalScrollbarSize = 10;
            // 
            // writerHeightLabel
            // 
            this.writerHeightLabel.AutoSize = true;
            this.writerHeightLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.writerHeightLabel.Location = new System.Drawing.Point(318, 336);
            this.writerHeightLabel.Name = "writerHeightLabel";
            this.writerHeightLabel.Size = new System.Drawing.Size(66, 25);
            this.writerHeightLabel.TabIndex = 70;
            this.writerHeightLabel.Text = "Height:";
            this.writerHeightLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // writerWidthLabel
            // 
            this.writerWidthLabel.AutoSize = true;
            this.writerWidthLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.writerWidthLabel.Location = new System.Drawing.Point(323, 287);
            this.writerWidthLabel.Name = "writerWidthLabel";
            this.writerWidthLabel.Size = new System.Drawing.Size(61, 25);
            this.writerWidthLabel.TabIndex = 69;
            this.writerWidthLabel.Text = "Width:";
            this.writerWidthLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // writerLabel
            // 
            this.writerLabel.AutoSize = true;
            this.writerLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.writerLabel.Location = new System.Drawing.Point(389, 245);
            this.writerLabel.Name = "writerLabel";
            this.writerLabel.Size = new System.Drawing.Size(58, 25);
            this.writerLabel.TabIndex = 68;
            this.writerLabel.Text = "Writer";
            this.writerLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // writerHeightPxLabel
            // 
            this.writerHeightPxLabel.AutoSize = true;
            this.writerHeightPxLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.writerHeightPxLabel.Location = new System.Drawing.Point(453, 336);
            this.writerHeightPxLabel.Name = "writerHeightPxLabel";
            this.writerHeightPxLabel.Size = new System.Drawing.Size(30, 25);
            this.writerHeightPxLabel.TabIndex = 67;
            this.writerHeightPxLabel.Text = "px";
            this.writerHeightPxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // writerWidthPxLabel
            // 
            this.writerWidthPxLabel.AutoSize = true;
            this.writerWidthPxLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.writerWidthPxLabel.Location = new System.Drawing.Point(453, 287);
            this.writerWidthPxLabel.Name = "writerWidthPxLabel";
            this.writerWidthPxLabel.Size = new System.Drawing.Size(30, 25);
            this.writerWidthPxLabel.TabIndex = 66;
            this.writerWidthPxLabel.Text = "px";
            this.writerWidthPxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // writerHeightTextBox
            // 
            // 
            // 
            // 
            this.writerHeightTextBox.CustomButton.Image = null;
            this.writerHeightTextBox.CustomButton.Location = new System.Drawing.Point(42, 1);
            this.writerHeightTextBox.CustomButton.Name = "";
            this.writerHeightTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.writerHeightTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.writerHeightTextBox.CustomButton.TabIndex = 1;
            this.writerHeightTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.writerHeightTextBox.CustomButton.UseSelectable = true;
            this.writerHeightTextBox.CustomButton.Visible = false;
            this.writerHeightTextBox.Lines = new string[0];
            this.writerHeightTextBox.Location = new System.Drawing.Point(388, 338);
            this.writerHeightTextBox.MaxLength = 32767;
            this.writerHeightTextBox.Name = "writerHeightTextBox";
            this.writerHeightTextBox.PasswordChar = '\0';
            this.writerHeightTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.writerHeightTextBox.SelectedText = "";
            this.writerHeightTextBox.SelectionLength = 0;
            this.writerHeightTextBox.SelectionStart = 0;
            this.writerHeightTextBox.ShortcutsEnabled = true;
            this.writerHeightTextBox.Size = new System.Drawing.Size(64, 23);
            this.writerHeightTextBox.TabIndex = 65;
            this.writerHeightTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.writerHeightTextBox.UseSelectable = true;
            this.writerHeightTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.writerHeightTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // writerWidthTextBox
            // 
            // 
            // 
            // 
            this.writerWidthTextBox.CustomButton.Image = null;
            this.writerWidthTextBox.CustomButton.Location = new System.Drawing.Point(42, 1);
            this.writerWidthTextBox.CustomButton.Name = "";
            this.writerWidthTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.writerWidthTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.writerWidthTextBox.CustomButton.TabIndex = 1;
            this.writerWidthTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.writerWidthTextBox.CustomButton.UseSelectable = true;
            this.writerWidthTextBox.CustomButton.Visible = false;
            this.writerWidthTextBox.Lines = new string[0];
            this.writerWidthTextBox.Location = new System.Drawing.Point(388, 289);
            this.writerWidthTextBox.MaxLength = 32767;
            this.writerWidthTextBox.Name = "writerWidthTextBox";
            this.writerWidthTextBox.PasswordChar = '\0';
            this.writerWidthTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.writerWidthTextBox.SelectedText = "";
            this.writerWidthTextBox.SelectionLength = 0;
            this.writerWidthTextBox.SelectionStart = 0;
            this.writerWidthTextBox.ShortcutsEnabled = true;
            this.writerWidthTextBox.Size = new System.Drawing.Size(64, 23);
            this.writerWidthTextBox.TabIndex = 64;
            this.writerWidthTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.writerWidthTextBox.UseSelectable = true;
            this.writerWidthTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.writerWidthTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // viewerLabel
            // 
            this.viewerLabel.AutoSize = true;
            this.viewerLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.viewerLabel.Location = new System.Drawing.Point(176, 245);
            this.viewerLabel.Name = "viewerLabel";
            this.viewerLabel.Size = new System.Drawing.Size(63, 25);
            this.viewerLabel.TabIndex = 61;
            this.viewerLabel.Text = "Viewer";
            this.viewerLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // viewerHeightPxLabel
            // 
            this.viewerHeightPxLabel.AutoSize = true;
            this.viewerHeightPxLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.viewerHeightPxLabel.Location = new System.Drawing.Point(240, 336);
            this.viewerHeightPxLabel.Name = "viewerHeightPxLabel";
            this.viewerHeightPxLabel.Size = new System.Drawing.Size(30, 25);
            this.viewerHeightPxLabel.TabIndex = 54;
            this.viewerHeightPxLabel.Text = "px";
            this.viewerHeightPxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // viewerWidthPxLabel
            // 
            this.viewerWidthPxLabel.AutoSize = true;
            this.viewerWidthPxLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.viewerWidthPxLabel.Location = new System.Drawing.Point(240, 287);
            this.viewerWidthPxLabel.Name = "viewerWidthPxLabel";
            this.viewerWidthPxLabel.Size = new System.Drawing.Size(30, 25);
            this.viewerWidthPxLabel.TabIndex = 53;
            this.viewerWidthPxLabel.Text = "px";
            this.viewerWidthPxLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // viewerHeightTextBox
            // 
            // 
            // 
            // 
            this.viewerHeightTextBox.CustomButton.Image = null;
            this.viewerHeightTextBox.CustomButton.Location = new System.Drawing.Point(42, 1);
            this.viewerHeightTextBox.CustomButton.Name = "";
            this.viewerHeightTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.viewerHeightTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.viewerHeightTextBox.CustomButton.TabIndex = 1;
            this.viewerHeightTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.viewerHeightTextBox.CustomButton.UseSelectable = true;
            this.viewerHeightTextBox.CustomButton.Visible = false;
            this.viewerHeightTextBox.Lines = new string[0];
            this.viewerHeightTextBox.Location = new System.Drawing.Point(175, 338);
            this.viewerHeightTextBox.MaxLength = 32767;
            this.viewerHeightTextBox.Name = "viewerHeightTextBox";
            this.viewerHeightTextBox.PasswordChar = '\0';
            this.viewerHeightTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.viewerHeightTextBox.SelectedText = "";
            this.viewerHeightTextBox.SelectionLength = 0;
            this.viewerHeightTextBox.SelectionStart = 0;
            this.viewerHeightTextBox.ShortcutsEnabled = true;
            this.viewerHeightTextBox.Size = new System.Drawing.Size(64, 23);
            this.viewerHeightTextBox.TabIndex = 52;
            this.viewerHeightTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.viewerHeightTextBox.UseSelectable = true;
            this.viewerHeightTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.viewerHeightTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // viewerWidthTextBox
            // 
            // 
            // 
            // 
            this.viewerWidthTextBox.CustomButton.Image = null;
            this.viewerWidthTextBox.CustomButton.Location = new System.Drawing.Point(42, 1);
            this.viewerWidthTextBox.CustomButton.Name = "";
            this.viewerWidthTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.viewerWidthTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.viewerWidthTextBox.CustomButton.TabIndex = 1;
            this.viewerWidthTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.viewerWidthTextBox.CustomButton.UseSelectable = true;
            this.viewerWidthTextBox.CustomButton.Visible = false;
            this.viewerWidthTextBox.Lines = new string[0];
            this.viewerWidthTextBox.Location = new System.Drawing.Point(175, 289);
            this.viewerWidthTextBox.MaxLength = 32767;
            this.viewerWidthTextBox.Name = "viewerWidthTextBox";
            this.viewerWidthTextBox.PasswordChar = '\0';
            this.viewerWidthTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.viewerWidthTextBox.SelectedText = "";
            this.viewerWidthTextBox.SelectionLength = 0;
            this.viewerWidthTextBox.SelectionStart = 0;
            this.viewerWidthTextBox.ShortcutsEnabled = true;
            this.viewerWidthTextBox.Size = new System.Drawing.Size(64, 23);
            this.viewerWidthTextBox.TabIndex = 51;
            this.viewerWidthTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.viewerWidthTextBox.UseSelectable = true;
            this.viewerWidthTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.viewerWidthTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // viewerHeightLabel
            // 
            this.viewerHeightLabel.AutoSize = true;
            this.viewerHeightLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.viewerHeightLabel.Location = new System.Drawing.Point(103, 336);
            this.viewerHeightLabel.Name = "viewerHeightLabel";
            this.viewerHeightLabel.Size = new System.Drawing.Size(66, 25);
            this.viewerHeightLabel.TabIndex = 50;
            this.viewerHeightLabel.Text = "Height:";
            this.viewerHeightLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // viewerWidthLabel
            // 
            this.viewerWidthLabel.AutoSize = true;
            this.viewerWidthLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.viewerWidthLabel.Location = new System.Drawing.Point(108, 287);
            this.viewerWidthLabel.Name = "viewerWidthLabel";
            this.viewerWidthLabel.Size = new System.Drawing.Size(61, 25);
            this.viewerWidthLabel.TabIndex = 49;
            this.viewerWidthLabel.Text = "Width:";
            this.viewerWidthLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // outputSizesLabel
            // 
            this.outputSizesLabel.AutoSize = true;
            this.outputSizesLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.outputSizesLabel.Location = new System.Drawing.Point(3, 245);
            this.outputSizesLabel.Name = "outputSizesLabel";
            this.outputSizesLabel.Size = new System.Drawing.Size(112, 25);
            this.outputSizesLabel.TabIndex = 48;
            this.outputSizesLabel.Text = "Output Sizes:";
            this.outputSizesLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // logfileExtensionLabel
            // 
            this.logfileExtensionLabel.AutoSize = true;
            this.logfileExtensionLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.logfileExtensionLabel.Location = new System.Drawing.Point(455, 97);
            this.logfileExtensionLabel.Name = "logfileExtensionLabel";
            this.logfileExtensionLabel.Size = new System.Drawing.Size(39, 25);
            this.logfileExtensionLabel.TabIndex = 47;
            this.logfileExtensionLabel.Text = ".csv";
            this.logfileExtensionLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // logfileTextBox
            // 
            // 
            // 
            // 
            this.logfileTextBox.CustomButton.Image = null;
            this.logfileTextBox.CustomButton.Location = new System.Drawing.Point(322, 1);
            this.logfileTextBox.CustomButton.Name = "";
            this.logfileTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.logfileTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.logfileTextBox.CustomButton.TabIndex = 1;
            this.logfileTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.logfileTextBox.CustomButton.UseSelectable = true;
            this.logfileTextBox.CustomButton.Visible = false;
            this.logfileTextBox.Lines = new string[0];
            this.logfileTextBox.Location = new System.Drawing.Point(108, 99);
            this.logfileTextBox.MaxLength = 32767;
            this.logfileTextBox.Name = "logfileTextBox";
            this.logfileTextBox.PasswordChar = '\0';
            this.logfileTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.logfileTextBox.SelectedText = "";
            this.logfileTextBox.SelectionLength = 0;
            this.logfileTextBox.SelectionStart = 0;
            this.logfileTextBox.ShortcutsEnabled = true;
            this.logfileTextBox.Size = new System.Drawing.Size(344, 23);
            this.logfileTextBox.TabIndex = 46;
            this.logfileTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.logfileTextBox.UseSelectable = true;
            this.logfileTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.logfileTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // logfileLabel
            // 
            this.logfileLabel.AutoSize = true;
            this.logfileLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.logfileLabel.Location = new System.Drawing.Point(3, 97);
            this.logfileLabel.Name = "logfileLabel";
            this.logfileLabel.Size = new System.Drawing.Size(74, 25);
            this.logfileLabel.TabIndex = 45;
            this.logfileLabel.Text = "Log File:";
            this.logfileLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // codecTextBox
            // 
            // 
            // 
            // 
            this.codecTextBox.CustomButton.Image = null;
            this.codecTextBox.CustomButton.Location = new System.Drawing.Point(50, 1);
            this.codecTextBox.CustomButton.Name = "";
            this.codecTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.codecTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.codecTextBox.CustomButton.TabIndex = 1;
            this.codecTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.codecTextBox.CustomButton.UseSelectable = true;
            this.codecTextBox.CustomButton.Visible = false;
            this.codecTextBox.Lines = new string[0];
            this.codecTextBox.Location = new System.Drawing.Point(108, 173);
            this.codecTextBox.MaxLength = 32767;
            this.codecTextBox.Name = "codecTextBox";
            this.codecTextBox.PasswordChar = '\0';
            this.codecTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.codecTextBox.SelectedText = "";
            this.codecTextBox.SelectionLength = 0;
            this.codecTextBox.SelectionStart = 0;
            this.codecTextBox.ShortcutsEnabled = true;
            this.codecTextBox.Size = new System.Drawing.Size(72, 23);
            this.codecTextBox.TabIndex = 44;
            this.codecTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.codecTextBox.UseSelectable = true;
            this.codecTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.codecTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // codecLabel
            // 
            this.codecLabel.AutoSize = true;
            this.codecLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.codecLabel.Location = new System.Drawing.Point(3, 171);
            this.codecLabel.Name = "codecLabel";
            this.codecLabel.Size = new System.Drawing.Size(64, 25);
            this.codecLabel.TabIndex = 43;
            this.codecLabel.Text = "Codec:";
            this.codecLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
            // 
            // bmpsCheckBox
            // 
            this.bmpsCheckBox.AutoSize = true;
            this.bmpsCheckBox.Location = new System.Drawing.Point(567, 30);
            this.bmpsCheckBox.Name = "bmpsCheckBox";
            this.bmpsCheckBox.Size = new System.Drawing.Size(145, 15);
            this.bmpsCheckBox.TabIndex = 42;
            this.bmpsCheckBox.Text = "Output Bitmaps as well";
            this.bmpsCheckBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.bmpsCheckBox.UseSelectable = true;
            // 
            // outputExtensionDropDown
            // 
            this.outputExtensionDropDown.FormattingEnabled = true;
            this.outputExtensionDropDown.ItemHeight = 23;
            this.outputExtensionDropDown.Items.AddRange(new object[] {
            ".avi",
            ".mp4"});
            this.outputExtensionDropDown.Location = new System.Drawing.Point(458, 22);
            this.outputExtensionDropDown.Name = "outputExtensionDropDown";
            this.outputExtensionDropDown.Size = new System.Drawing.Size(70, 29);
            this.outputExtensionDropDown.TabIndex = 41;
            this.outputExtensionDropDown.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.outputExtensionDropDown.UseSelectable = true;
            // 
            // outputFileTextBox
            // 
            // 
            // 
            // 
            this.outputFileTextBox.CustomButton.Image = null;
            this.outputFileTextBox.CustomButton.Location = new System.Drawing.Point(322, 1);
            this.outputFileTextBox.CustomButton.Name = "";
            this.outputFileTextBox.CustomButton.Size = new System.Drawing.Size(21, 21);
            this.outputFileTextBox.CustomButton.Style = MetroFramework.MetroColorStyle.Blue;
            this.outputFileTextBox.CustomButton.TabIndex = 1;
            this.outputFileTextBox.CustomButton.Theme = MetroFramework.MetroThemeStyle.Light;
            this.outputFileTextBox.CustomButton.UseSelectable = true;
            this.outputFileTextBox.CustomButton.Visible = false;
            this.outputFileTextBox.Lines = new string[0];
            this.outputFileTextBox.Location = new System.Drawing.Point(108, 26);
            this.outputFileTextBox.MaxLength = 32767;
            this.outputFileTextBox.Name = "outputFileTextBox";
            this.outputFileTextBox.PasswordChar = '\0';
            this.outputFileTextBox.ScrollBars = System.Windows.Forms.ScrollBars.None;
            this.outputFileTextBox.SelectedText = "";
            this.outputFileTextBox.SelectionLength = 0;
            this.outputFileTextBox.SelectionStart = 0;
            this.outputFileTextBox.ShortcutsEnabled = true;
            this.outputFileTextBox.Size = new System.Drawing.Size(344, 23);
            this.outputFileTextBox.TabIndex = 6;
            this.outputFileTextBox.Theme = MetroFramework.MetroThemeStyle.Dark;
            this.outputFileTextBox.UseSelectable = true;
            this.outputFileTextBox.WaterMarkColor = System.Drawing.Color.FromArgb(((int)(((byte)(109)))), ((int)(((byte)(109)))), ((int)(((byte)(109)))));
            this.outputFileTextBox.WaterMarkFont = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Pixel);
            // 
            // outputFileLabel
            // 
            this.outputFileLabel.AutoSize = true;
            this.outputFileLabel.FontSize = MetroFramework.MetroLabelSize.Tall;
            this.outputFileLabel.Location = new System.Drawing.Point(3, 24);
            this.outputFileLabel.Name = "outputFileLabel";
            this.outputFileLabel.Size = new System.Drawing.Size(100, 25);
            this.outputFileLabel.TabIndex = 5;
            this.outputFileLabel.Text = "Output File:";
            this.outputFileLabel.Theme = MetroFramework.MetroThemeStyle.Dark;

            // 
            // lnTolerancePercentageLabel
            // 
            this.lnTolerancePercentageLabel.AutoSize = true;
            this.lnTolerancePercentageLabel.Location = new System.Drawing.Point(734, 102);
            this.lnTolerancePercentageLabel.Name = "lnTolerancePercentageLabel";
            this.lnTolerancePercentageLabel.Size = new System.Drawing.Size(20, 19);
            this.lnTolerancePercentageLabel.TabIndex = 13;
            this.lnTolerancePercentageLabel.Text = "%";
            this.lnTolerancePercentageLabel.Theme = MetroFramework.MetroThemeStyle.Dark;
  

            this.videoSubTabControl.ResumeLayout(false);
            this.inputTabPage.ResumeLayout(false);
            this.inputTabPage.PerformLayout();
            this.processingTabPage.ResumeLayout(false);
            this.processingTabPage.PerformLayout();
            this.appearanceTabPage.ResumeLayout(false);
            this.appearanceTabPage.PerformLayout();
            this.fpsTabPage.ResumeLayout(false);
            this.fpsTabPage.PerformLayout();
            this.outputTabPage.ResumeLayout(false);
            this.outputTabPage.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
