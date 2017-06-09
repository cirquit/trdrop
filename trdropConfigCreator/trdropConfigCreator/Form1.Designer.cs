namespace trdropConfigCreator
{
    partial class Form1
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
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.inputTab = new System.Windows.Forms.TabPage();
            this.outputTab = new System.Windows.Forms.TabPage();
            this.styleTab = new System.Windows.Forms.TabPage();
            this.processingTab = new System.Windows.Forms.TabPage();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.fileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.openToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exitToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.editToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.resetToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addFileButton = new System.Windows.Forms.Button();
            this.checkedListBox1 = new System.Windows.Forms.CheckedListBox();
            this.videoColorPanel = new System.Windows.Forms.Panel();
            this.panel1 = new System.Windows.Forms.Panel();
            this.videoColorsLabel = new System.Windows.Forms.Label();
            this.videoColorsLabel1 = new System.Windows.Forms.Label();
            this.videoColorsLabel2 = new System.Windows.Forms.Label();
            this.videoColorsLabel3 = new System.Windows.Forms.Label();
            this.videoColorsButton1 = new System.Windows.Forms.Button();
            this.videoColorsButton2 = new System.Windows.Forms.Button();
            this.videoColorsButton3 = new System.Windows.Forms.Button();
            this.videoColorsTextBox1 = new System.Windows.Forms.TextBox();
            this.videoColorsTextBox2 = new System.Windows.Forms.TextBox();
            this.videoColorsTextBox3 = new System.Windows.Forms.TextBox();
            this.videoColorsHexLabel = new System.Windows.Forms.Label();
            this.colorDialog1 = new System.Windows.Forms.ColorDialog();
            this.panel2 = new System.Windows.Forms.Panel();
            this.tearColorsHexLabel = new System.Windows.Forms.Label();
            this.tearColorsTextBox3 = new System.Windows.Forms.TextBox();
            this.tearColorsTextBox2 = new System.Windows.Forms.TextBox();
            this.tearColorsTextBox1 = new System.Windows.Forms.TextBox();
            this.tearColorsButton3 = new System.Windows.Forms.Button();
            this.tearColorsButton2 = new System.Windows.Forms.Button();
            this.tearColorsButton1 = new System.Windows.Forms.Button();
            this.tearColorsLabel3 = new System.Windows.Forms.Label();
            this.tearColorsLabel2 = new System.Windows.Forms.Label();
            this.tearColorsLabel1 = new System.Windows.Forms.Label();
            this.tearColorsLabel = new System.Windows.Forms.Label();
            this.panel3 = new System.Windows.Forms.Panel();
            this.label1 = new System.Windows.Forms.Label();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.textBox2 = new System.Windows.Forms.TextBox();
            this.textBox3 = new System.Windows.Forms.TextBox();
            this.button1 = new System.Windows.Forms.Button();
            this.button2 = new System.Windows.Forms.Button();
            this.button3 = new System.Windows.Forms.Button();
            this.plotColorsLinesLabel = new System.Windows.Forms.Label();
            this.xyAxesLabel = new System.Windows.Forms.Label();
            this.plotColorsBGLabel = new System.Windows.Forms.Label();
            this.plotColorsLabel = new System.Windows.Forms.Label();
            this.plotColorsOpacityLabel = new System.Windows.Forms.Label();
            this.trackBar1 = new System.Windows.Forms.TrackBar();
            this.textBox4 = new System.Windows.Forms.TextBox();
            this.tabControl1.SuspendLayout();
            this.inputTab.SuspendLayout();
            this.styleTab.SuspendLayout();
            this.processingTab.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            this.panel1.SuspendLayout();
            this.panel2.SuspendLayout();
            this.panel3.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBar1)).BeginInit();
            this.SuspendLayout();
            // 
            // tabControl1
            // 
            this.tabControl1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.tabControl1.Controls.Add(this.inputTab);
            this.tabControl1.Controls.Add(this.processingTab);
            this.tabControl1.Controls.Add(this.styleTab);
            this.tabControl1.Controls.Add(this.outputTab);
            this.tabControl1.Location = new System.Drawing.Point(13, 27);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(881, 548);
            this.tabControl1.TabIndex = 0;
            // 
            // inputTab
            // 
            this.inputTab.Controls.Add(this.checkedListBox1);
            this.inputTab.Controls.Add(this.addFileButton);
            this.inputTab.Font = new System.Drawing.Font("Montserrat", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.inputTab.Location = new System.Drawing.Point(4, 22);
            this.inputTab.Name = "inputTab";
            this.inputTab.Padding = new System.Windows.Forms.Padding(3);
            this.inputTab.Size = new System.Drawing.Size(944, 568);
            this.inputTab.TabIndex = 0;
            this.inputTab.Text = "Input";
            this.inputTab.UseVisualStyleBackColor = true;
            // 
            // outputTab
            // 
            this.outputTab.Location = new System.Drawing.Point(4, 22);
            this.outputTab.Name = "outputTab";
            this.outputTab.Padding = new System.Windows.Forms.Padding(3);
            this.outputTab.Size = new System.Drawing.Size(696, 565);
            this.outputTab.TabIndex = 1;
            this.outputTab.Text = "Output";
            this.outputTab.UseVisualStyleBackColor = true;
            // 
            // styleTab
            // 
            this.styleTab.Controls.Add(this.panel3);
            this.styleTab.Controls.Add(this.panel2);
            this.styleTab.Controls.Add(this.panel1);
            this.styleTab.Location = new System.Drawing.Point(4, 22);
            this.styleTab.Name = "styleTab";
            this.styleTab.Size = new System.Drawing.Size(873, 522);
            this.styleTab.TabIndex = 2;
            this.styleTab.Text = "Style";
            this.styleTab.UseVisualStyleBackColor = true;
            // 
            // processingTab
            // 
            this.processingTab.Controls.Add(this.videoColorPanel);
            this.processingTab.Location = new System.Drawing.Point(4, 22);
            this.processingTab.Name = "processingTab";
            this.processingTab.Size = new System.Drawing.Size(944, 568);
            this.processingTab.TabIndex = 3;
            this.processingTab.Text = "Processing";
            this.processingTab.UseVisualStyleBackColor = true;
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.fileToolStripMenuItem,
            this.editToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(908, 24);
            this.menuStrip1.TabIndex = 1;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // fileToolStripMenuItem
            // 
            this.fileToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.openToolStripMenuItem,
            this.exitToolStripMenuItem});
            this.fileToolStripMenuItem.Name = "fileToolStripMenuItem";
            this.fileToolStripMenuItem.Size = new System.Drawing.Size(37, 20);
            this.fileToolStripMenuItem.Text = "File";
            // 
            // openToolStripMenuItem
            // 
            this.openToolStripMenuItem.Name = "openToolStripMenuItem";
            this.openToolStripMenuItem.Size = new System.Drawing.Size(152, 22);
            this.openToolStripMenuItem.Text = "Open...";
            // 
            // exitToolStripMenuItem
            // 
            this.exitToolStripMenuItem.Name = "exitToolStripMenuItem";
            this.exitToolStripMenuItem.Size = new System.Drawing.Size(152, 22);
            this.exitToolStripMenuItem.Text = "Exit";
            // 
            // editToolStripMenuItem
            // 
            this.editToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.resetToolStripMenuItem});
            this.editToolStripMenuItem.Name = "editToolStripMenuItem";
            this.editToolStripMenuItem.Size = new System.Drawing.Size(39, 20);
            this.editToolStripMenuItem.Text = "Edit";
            // 
            // resetToolStripMenuItem
            // 
            this.resetToolStripMenuItem.Name = "resetToolStripMenuItem";
            this.resetToolStripMenuItem.Size = new System.Drawing.Size(152, 22);
            this.resetToolStripMenuItem.Text = "Reset";
            // 
            // addFileButton
            // 
            this.addFileButton.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.addFileButton.Location = new System.Drawing.Point(21, 109);
            this.addFileButton.Name = "addFileButton";
            this.addFileButton.Size = new System.Drawing.Size(101, 23);
            this.addFileButton.TabIndex = 1;
            this.addFileButton.Text = "Add Video File";
            this.addFileButton.UseVisualStyleBackColor = true;
            // 
            // checkedListBox1
            // 
            this.checkedListBox1.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.checkedListBox1.CheckOnClick = true;
            this.checkedListBox1.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.checkedListBox1.FormattingEnabled = true;
            this.checkedListBox1.Items.AddRange(new object[] {
            "Video 1",
            "Video 2",
            "Video 3"});
            this.checkedListBox1.Location = new System.Drawing.Point(20, 20);
            this.checkedListBox1.Name = "checkedListBox1";
            this.checkedListBox1.Size = new System.Drawing.Size(902, 64);
            this.checkedListBox1.TabIndex = 2;
            this.checkedListBox1.SelectedIndexChanged += new System.EventHandler(this.checkedListBox1_SelectedIndexChanged);
            // 
            // videoColorPanel
            // 
            this.videoColorPanel.Location = new System.Drawing.Point(4, 4);
            this.videoColorPanel.Name = "videoColorPanel";
            this.videoColorPanel.Size = new System.Drawing.Size(200, 100);
            this.videoColorPanel.TabIndex = 0;
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.videoColorsHexLabel);
            this.panel1.Controls.Add(this.videoColorsTextBox3);
            this.panel1.Controls.Add(this.videoColorsTextBox2);
            this.panel1.Controls.Add(this.videoColorsTextBox1);
            this.panel1.Controls.Add(this.videoColorsButton3);
            this.panel1.Controls.Add(this.videoColorsButton2);
            this.panel1.Controls.Add(this.videoColorsButton1);
            this.panel1.Controls.Add(this.videoColorsLabel3);
            this.panel1.Controls.Add(this.videoColorsLabel2);
            this.panel1.Controls.Add(this.videoColorsLabel1);
            this.panel1.Controls.Add(this.videoColorsLabel);
            this.panel1.Location = new System.Drawing.Point(17, 16);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(303, 159);
            this.panel1.TabIndex = 0;
            // 
            // videoColorsLabel
            // 
            this.videoColorsLabel.AutoSize = true;
            this.videoColorsLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.videoColorsLabel.Location = new System.Drawing.Point(4, 4);
            this.videoColorsLabel.Name = "videoColorsLabel";
            this.videoColorsLabel.Size = new System.Drawing.Size(78, 13);
            this.videoColorsLabel.TabIndex = 0;
            this.videoColorsLabel.Text = "Video Colors";
            this.videoColorsLabel.Click += new System.EventHandler(this.label1_Click);
            // 
            // videoColorsLabel1
            // 
            this.videoColorsLabel1.AutoSize = true;
            this.videoColorsLabel1.Location = new System.Drawing.Point(23, 38);
            this.videoColorsLabel1.Name = "videoColorsLabel1";
            this.videoColorsLabel1.Size = new System.Drawing.Size(46, 13);
            this.videoColorsLabel1.TabIndex = 1;
            this.videoColorsLabel1.Text = "Video 1:";
            // 
            // videoColorsLabel2
            // 
            this.videoColorsLabel2.AutoSize = true;
            this.videoColorsLabel2.Location = new System.Drawing.Point(23, 78);
            this.videoColorsLabel2.Name = "videoColorsLabel2";
            this.videoColorsLabel2.Size = new System.Drawing.Size(46, 13);
            this.videoColorsLabel2.TabIndex = 2;
            this.videoColorsLabel2.Text = "Video 2:";
            this.videoColorsLabel2.Click += new System.EventHandler(this.label3_Click);
            // 
            // videoColorsLabel3
            // 
            this.videoColorsLabel3.AutoSize = true;
            this.videoColorsLabel3.Location = new System.Drawing.Point(23, 118);
            this.videoColorsLabel3.Name = "videoColorsLabel3";
            this.videoColorsLabel3.Size = new System.Drawing.Size(46, 13);
            this.videoColorsLabel3.TabIndex = 3;
            this.videoColorsLabel3.Text = "Video 3:";
            // 
            // videoColorsButton1
            // 
            this.videoColorsButton1.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.videoColorsButton1.Location = new System.Drawing.Point(95, 33);
            this.videoColorsButton1.Name = "videoColorsButton1";
            this.videoColorsButton1.Size = new System.Drawing.Size(75, 23);
            this.videoColorsButton1.TabIndex = 4;
            this.videoColorsButton1.Text = "Pick";
            this.videoColorsButton1.UseVisualStyleBackColor = true;
            // 
            // videoColorsButton2
            // 
            this.videoColorsButton2.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.videoColorsButton2.Location = new System.Drawing.Point(95, 73);
            this.videoColorsButton2.Name = "videoColorsButton2";
            this.videoColorsButton2.Size = new System.Drawing.Size(75, 23);
            this.videoColorsButton2.TabIndex = 5;
            this.videoColorsButton2.Text = "Pick";
            this.videoColorsButton2.UseVisualStyleBackColor = true;
            // 
            // videoColorsButton3
            // 
            this.videoColorsButton3.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.videoColorsButton3.Location = new System.Drawing.Point(95, 113);
            this.videoColorsButton3.Name = "videoColorsButton3";
            this.videoColorsButton3.Size = new System.Drawing.Size(75, 23);
            this.videoColorsButton3.TabIndex = 6;
            this.videoColorsButton3.Text = "Pick";
            this.videoColorsButton3.UseVisualStyleBackColor = true;
            // 
            // videoColorsTextBox1
            // 
            this.videoColorsTextBox1.Location = new System.Drawing.Point(186, 34);
            this.videoColorsTextBox1.Name = "videoColorsTextBox1";
            this.videoColorsTextBox1.Size = new System.Drawing.Size(100, 20);
            this.videoColorsTextBox1.TabIndex = 7;
            // 
            // videoColorsTextBox2
            // 
            this.videoColorsTextBox2.Location = new System.Drawing.Point(186, 74);
            this.videoColorsTextBox2.Name = "videoColorsTextBox2";
            this.videoColorsTextBox2.Size = new System.Drawing.Size(100, 20);
            this.videoColorsTextBox2.TabIndex = 8;
            // 
            // videoColorsTextBox3
            // 
            this.videoColorsTextBox3.Location = new System.Drawing.Point(186, 114);
            this.videoColorsTextBox3.Name = "videoColorsTextBox3";
            this.videoColorsTextBox3.Size = new System.Drawing.Size(100, 20);
            this.videoColorsTextBox3.TabIndex = 9;
            // 
            // videoColorsHexLabel
            // 
            this.videoColorsHexLabel.AutoSize = true;
            this.videoColorsHexLabel.Location = new System.Drawing.Point(223, 15);
            this.videoColorsHexLabel.Name = "videoColorsHexLabel";
            this.videoColorsHexLabel.Size = new System.Drawing.Size(29, 13);
            this.videoColorsHexLabel.TabIndex = 10;
            this.videoColorsHexLabel.Text = "Hex:";
            // 
            // panel2
            // 
            this.panel2.Controls.Add(this.tearColorsHexLabel);
            this.panel2.Controls.Add(this.tearColorsTextBox3);
            this.panel2.Controls.Add(this.tearColorsTextBox2);
            this.panel2.Controls.Add(this.tearColorsTextBox1);
            this.panel2.Controls.Add(this.tearColorsButton3);
            this.panel2.Controls.Add(this.tearColorsButton2);
            this.panel2.Controls.Add(this.tearColorsButton1);
            this.panel2.Controls.Add(this.tearColorsLabel3);
            this.panel2.Controls.Add(this.tearColorsLabel2);
            this.panel2.Controls.Add(this.tearColorsLabel1);
            this.panel2.Controls.Add(this.tearColorsLabel);
            this.panel2.Location = new System.Drawing.Point(326, 16);
            this.panel2.Name = "panel2";
            this.panel2.Size = new System.Drawing.Size(303, 159);
            this.panel2.TabIndex = 11;
            // 
            // tearColorsHexLabel
            // 
            this.tearColorsHexLabel.AutoSize = true;
            this.tearColorsHexLabel.Location = new System.Drawing.Point(223, 15);
            this.tearColorsHexLabel.Name = "tearColorsHexLabel";
            this.tearColorsHexLabel.Size = new System.Drawing.Size(29, 13);
            this.tearColorsHexLabel.TabIndex = 10;
            this.tearColorsHexLabel.Text = "Hex:";
            // 
            // tearColorsTextBox3
            // 
            this.tearColorsTextBox3.Location = new System.Drawing.Point(186, 114);
            this.tearColorsTextBox3.Name = "tearColorsTextBox3";
            this.tearColorsTextBox3.Size = new System.Drawing.Size(100, 20);
            this.tearColorsTextBox3.TabIndex = 9;
            // 
            // tearColorsTextBox2
            // 
            this.tearColorsTextBox2.Location = new System.Drawing.Point(186, 74);
            this.tearColorsTextBox2.Name = "tearColorsTextBox2";
            this.tearColorsTextBox2.Size = new System.Drawing.Size(100, 20);
            this.tearColorsTextBox2.TabIndex = 8;
            // 
            // tearColorsTextBox1
            // 
            this.tearColorsTextBox1.Location = new System.Drawing.Point(186, 34);
            this.tearColorsTextBox1.Name = "tearColorsTextBox1";
            this.tearColorsTextBox1.Size = new System.Drawing.Size(100, 20);
            this.tearColorsTextBox1.TabIndex = 7;
            // 
            // tearColorsButton3
            // 
            this.tearColorsButton3.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.tearColorsButton3.Location = new System.Drawing.Point(95, 113);
            this.tearColorsButton3.Name = "tearColorsButton3";
            this.tearColorsButton3.Size = new System.Drawing.Size(75, 23);
            this.tearColorsButton3.TabIndex = 6;
            this.tearColorsButton3.Text = "Pick";
            this.tearColorsButton3.UseVisualStyleBackColor = true;
            // 
            // tearColorsButton2
            // 
            this.tearColorsButton2.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.tearColorsButton2.Location = new System.Drawing.Point(95, 73);
            this.tearColorsButton2.Name = "tearColorsButton2";
            this.tearColorsButton2.Size = new System.Drawing.Size(75, 23);
            this.tearColorsButton2.TabIndex = 5;
            this.tearColorsButton2.Text = "Pick";
            this.tearColorsButton2.UseVisualStyleBackColor = true;
            // 
            // tearColorsButton1
            // 
            this.tearColorsButton1.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.tearColorsButton1.Location = new System.Drawing.Point(95, 33);
            this.tearColorsButton1.Name = "tearColorsButton1";
            this.tearColorsButton1.Size = new System.Drawing.Size(75, 23);
            this.tearColorsButton1.TabIndex = 4;
            this.tearColorsButton1.Text = "Pick";
            this.tearColorsButton1.UseVisualStyleBackColor = true;
            // 
            // tearColorsLabel3
            // 
            this.tearColorsLabel3.AutoSize = true;
            this.tearColorsLabel3.Location = new System.Drawing.Point(23, 118);
            this.tearColorsLabel3.Name = "tearColorsLabel3";
            this.tearColorsLabel3.Size = new System.Drawing.Size(46, 13);
            this.tearColorsLabel3.TabIndex = 3;
            this.tearColorsLabel3.Text = "Video 3:";
            // 
            // tearColorsLabel2
            // 
            this.tearColorsLabel2.AutoSize = true;
            this.tearColorsLabel2.Location = new System.Drawing.Point(23, 78);
            this.tearColorsLabel2.Name = "tearColorsLabel2";
            this.tearColorsLabel2.Size = new System.Drawing.Size(46, 13);
            this.tearColorsLabel2.TabIndex = 2;
            this.tearColorsLabel2.Text = "Video 2:";
            // 
            // tearColorsLabel1
            // 
            this.tearColorsLabel1.AutoSize = true;
            this.tearColorsLabel1.Location = new System.Drawing.Point(23, 38);
            this.tearColorsLabel1.Name = "tearColorsLabel1";
            this.tearColorsLabel1.Size = new System.Drawing.Size(46, 13);
            this.tearColorsLabel1.TabIndex = 1;
            this.tearColorsLabel1.Text = "Video 1:";
            // 
            // tearColorsLabel
            // 
            this.tearColorsLabel.AutoSize = true;
            this.tearColorsLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.tearColorsLabel.Location = new System.Drawing.Point(4, 4);
            this.tearColorsLabel.Name = "tearColorsLabel";
            this.tearColorsLabel.Size = new System.Drawing.Size(72, 13);
            this.tearColorsLabel.TabIndex = 0;
            this.tearColorsLabel.Text = "Tear Colors";
            this.tearColorsLabel.Click += new System.EventHandler(this.label5_Click);
            // 
            // panel3
            // 
            this.panel3.Controls.Add(this.textBox4);
            this.panel3.Controls.Add(this.trackBar1);
            this.panel3.Controls.Add(this.label1);
            this.panel3.Controls.Add(this.plotColorsOpacityLabel);
            this.panel3.Controls.Add(this.textBox1);
            this.panel3.Controls.Add(this.textBox2);
            this.panel3.Controls.Add(this.textBox3);
            this.panel3.Controls.Add(this.button1);
            this.panel3.Controls.Add(this.button2);
            this.panel3.Controls.Add(this.button3);
            this.panel3.Controls.Add(this.plotColorsLinesLabel);
            this.panel3.Controls.Add(this.xyAxesLabel);
            this.panel3.Controls.Add(this.plotColorsBGLabel);
            this.panel3.Controls.Add(this.plotColorsLabel);
            this.panel3.Location = new System.Drawing.Point(17, 181);
            this.panel3.Name = "panel3";
            this.panel3.Size = new System.Drawing.Size(303, 212);
            this.panel3.TabIndex = 12;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(223, 15);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(29, 13);
            this.label1.TabIndex = 10;
            this.label1.Text = "Hex:";
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(186, 114);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(100, 20);
            this.textBox1.TabIndex = 9;
            // 
            // textBox2
            // 
            this.textBox2.Location = new System.Drawing.Point(186, 74);
            this.textBox2.Name = "textBox2";
            this.textBox2.Size = new System.Drawing.Size(100, 20);
            this.textBox2.TabIndex = 8;
            // 
            // textBox3
            // 
            this.textBox3.Location = new System.Drawing.Point(186, 34);
            this.textBox3.Name = "textBox3";
            this.textBox3.Size = new System.Drawing.Size(100, 20);
            this.textBox3.TabIndex = 7;
            // 
            // button1
            // 
            this.button1.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.button1.Location = new System.Drawing.Point(95, 113);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(75, 23);
            this.button1.TabIndex = 6;
            this.button1.Text = "Pick";
            this.button1.UseVisualStyleBackColor = true;
            // 
            // button2
            // 
            this.button2.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.button2.Location = new System.Drawing.Point(95, 73);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(75, 23);
            this.button2.TabIndex = 5;
            this.button2.Text = "Pick";
            this.button2.UseVisualStyleBackColor = true;
            // 
            // button3
            // 
            this.button3.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.button3.Location = new System.Drawing.Point(95, 33);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(75, 23);
            this.button3.TabIndex = 4;
            this.button3.Text = "Pick";
            this.button3.UseVisualStyleBackColor = true;
            // 
            // plotColorsLinesLabel
            // 
            this.plotColorsLinesLabel.AutoSize = true;
            this.plotColorsLinesLabel.Location = new System.Drawing.Point(23, 118);
            this.plotColorsLinesLabel.Name = "plotColorsLinesLabel";
            this.plotColorsLinesLabel.Size = new System.Drawing.Size(35, 13);
            this.plotColorsLinesLabel.TabIndex = 3;
            this.plotColorsLinesLabel.Text = "Lines:";
            // 
            // xyAxesLabel
            // 
            this.xyAxesLabel.AutoSize = true;
            this.xyAxesLabel.Location = new System.Drawing.Point(23, 78);
            this.xyAxesLabel.Name = "xyAxesLabel";
            this.xyAxesLabel.Size = new System.Drawing.Size(50, 13);
            this.xyAxesLabel.TabIndex = 2;
            this.xyAxesLabel.Text = "XY Axes:";
            // 
            // plotColorsBGLabel
            // 
            this.plotColorsBGLabel.AutoSize = true;
            this.plotColorsBGLabel.Location = new System.Drawing.Point(23, 38);
            this.plotColorsBGLabel.Name = "plotColorsBGLabel";
            this.plotColorsBGLabel.Size = new System.Drawing.Size(68, 13);
            this.plotColorsBGLabel.TabIndex = 1;
            this.plotColorsBGLabel.Text = "Background:";
            // 
            // plotColorsLabel
            // 
            this.plotColorsLabel.AutoSize = true;
            this.plotColorsLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.plotColorsLabel.Location = new System.Drawing.Point(4, 4);
            this.plotColorsLabel.Name = "plotColorsLabel";
            this.plotColorsLabel.Size = new System.Drawing.Size(68, 13);
            this.plotColorsLabel.TabIndex = 0;
            this.plotColorsLabel.Text = "Plot Colors";
            // 
            // plotColorsOpacityLabel
            // 
            this.plotColorsOpacityLabel.AutoSize = true;
            this.plotColorsOpacityLabel.Location = new System.Drawing.Point(23, 157);
            this.plotColorsOpacityLabel.Name = "plotColorsOpacityLabel";
            this.plotColorsOpacityLabel.Size = new System.Drawing.Size(46, 13);
            this.plotColorsOpacityLabel.TabIndex = 11;
            this.plotColorsOpacityLabel.Text = "Opacity:";
            // 
            // trackBar1
            // 
            this.trackBar1.BackColor = System.Drawing.SystemColors.Window;
            this.trackBar1.Location = new System.Drawing.Point(87, 154);
            this.trackBar1.Maximum = 100;
            this.trackBar1.Name = "trackBar1";
            this.trackBar1.Size = new System.Drawing.Size(165, 45);
            this.trackBar1.TabIndex = 12;
            this.trackBar1.TickFrequency = 10;
            // 
            // textBox4
            // 
            this.textBox4.Location = new System.Drawing.Point(255, 154);
            this.textBox4.Name = "textBox4";
            this.textBox4.Size = new System.Drawing.Size(31, 20);
            this.textBox4.TabIndex = 13;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(908, 587);
            this.Controls.Add(this.tabControl1);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "Form1";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.tabControl1.ResumeLayout(false);
            this.inputTab.ResumeLayout(false);
            this.styleTab.ResumeLayout(false);
            this.processingTab.ResumeLayout(false);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.panel2.ResumeLayout(false);
            this.panel2.PerformLayout();
            this.panel3.ResumeLayout(false);
            this.panel3.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBar1)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage inputTab;
        private System.Windows.Forms.TabPage processingTab;
        private System.Windows.Forms.TabPage styleTab;
        private System.Windows.Forms.TabPage outputTab;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem fileToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem openToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exitToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem editToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem resetToolStripMenuItem;
        private System.Windows.Forms.CheckedListBox checkedListBox1;
        private System.Windows.Forms.Button addFileButton;
        private System.Windows.Forms.Panel videoColorPanel;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Label videoColorsLabel;
        private System.Windows.Forms.Label videoColorsLabel2;
        private System.Windows.Forms.Label videoColorsLabel1;
        private System.Windows.Forms.Label videoColorsLabel3;
        private System.Windows.Forms.Label videoColorsHexLabel;
        private System.Windows.Forms.TextBox videoColorsTextBox3;
        private System.Windows.Forms.TextBox videoColorsTextBox2;
        private System.Windows.Forms.TextBox videoColorsTextBox1;
        private System.Windows.Forms.Button videoColorsButton3;
        private System.Windows.Forms.Button videoColorsButton2;
        private System.Windows.Forms.Button videoColorsButton1;
        private System.Windows.Forms.ColorDialog colorDialog1;
        private System.Windows.Forms.Panel panel2;
        private System.Windows.Forms.Label tearColorsHexLabel;
        private System.Windows.Forms.TextBox tearColorsTextBox3;
        private System.Windows.Forms.TextBox tearColorsTextBox2;
        private System.Windows.Forms.TextBox tearColorsTextBox1;
        private System.Windows.Forms.Button tearColorsButton3;
        private System.Windows.Forms.Button tearColorsButton2;
        private System.Windows.Forms.Button tearColorsButton1;
        private System.Windows.Forms.Label tearColorsLabel3;
        private System.Windows.Forms.Label tearColorsLabel2;
        private System.Windows.Forms.Label tearColorsLabel1;
        private System.Windows.Forms.Label tearColorsLabel;
        private System.Windows.Forms.Panel panel3;
        private System.Windows.Forms.TrackBar trackBar1;
        private System.Windows.Forms.Label plotColorsOpacityLabel;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.TextBox textBox2;
        private System.Windows.Forms.TextBox textBox3;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.Label plotColorsLinesLabel;
        private System.Windows.Forms.Label xyAxesLabel;
        private System.Windows.Forms.Label plotColorsBGLabel;
        private System.Windows.Forms.Label plotColorsLabel;
        private System.Windows.Forms.TextBox textBox4;
    }
}

