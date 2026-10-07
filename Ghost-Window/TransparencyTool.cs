using System;
using System.Collections.Generic;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;

namespace GhostWindow
{
    public class Program
    {
        [STAThread]
        public static void Main()
        {
            try
            {
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(new MainWindow());
            }
            catch (Exception ex)
            {
                MessageBox.Show("Lỗi khởi động: " + ex.Message, "Ghost Window Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    public class MainWindow : Form
    {
        // Win32 API Imports
        [DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        public static extern int GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll")]
        public static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

        [DllImport("user32.dll")]
        public static extern bool SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags);

        [DllImport("user32.dll")]
        public static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

        [DllImport("user32.dll")]
        public static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

        [DllImport("user32.dll")]
        public static extern bool IsWindowVisible(IntPtr hWnd);

        public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

        public const int GWL_EXSTYLE = -20;
        public const int WS_EX_LAYERED = 0x80000;
        public const int LWA_ALPHA = 0x2;

        public const uint MOD_ALT = 0x0001;
        public const uint MOD_CONTROL = 0x0002;

        public const int WM_HOTKEY = 0x0312;
        public const int SW_MINIMIZE = 6;

        // UI Controls
        private Label lblHeader;
        private Label lblSubHeader;
        private Label lblSelectWindow;
        private ComboBox cmbWindows;
        private Button btnRefresh;
        private Label lblOpacity;
        private TrackBar trackOpacity;
        private Label lblOpacityValue;
        private Button btnPreset5;
        private Button btnPreset15;
        private Button btnPreset35;
        private Button btnPreset60;
        private Button btnPreset100;
        private Button btnBossKey;
        private GroupBox grpShortcuts;
        private Label lblShortcuts;
        private NotifyIcon notifyIcon;
        private CheckBox chkMinimizeToTray;

        private class WindowItem
        {
            public IntPtr Handle { get; set; }
            public string Title { get; set; }
            public override string ToString() { return Title; }
        }

        public MainWindow()
        {
            InitializeComponent();
            RegisterGlobalHotkeys();
            RefreshWindowList();
        }

        private void InitializeComponent()
        {
            this.Text = "Ghost Chrome - Chế Độ Tàng Hình & Trong Suốt";
            this.Size = new Size(500, 560);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.BackColor = Color.FromArgb(24, 30, 42);
            this.ForeColor = Color.White;
            this.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);

            // Header Icon & Title
            lblHeader = new Label
            {
                Text = "👻 Ghost Window - Trong Suốt Chrome",
                Font = new Font("Segoe UI", 14f, FontStyle.Bold),
                ForeColor = Color.FromArgb(129, 140, 248),
                Location = new Point(20, 16),
                AutoSize = true
            };

            lblSubHeader = new Label
            {
                Text = "Làm mờ/trong suốt cửa sổ Chrome hoặc ứng dụng bất kỳ để người ngoài không chú ý",
                ForeColor = Color.FromArgb(156, 163, 175),
                Location = new Point(22, 48),
                Size = new Size(440, 20),
                Font = new Font("Segoe UI", 8.5f)
            };

            // Select Window
            lblSelectWindow = new Label
            {
                Text = "Chọn cửa sổ cần làm trong suốt:",
                Location = new Point(20, 78),
                AutoSize = true,
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold)
            };

            cmbWindows = new ComboBox
            {
                Location = new Point(20, 104),
                Size = new Size(340, 28),
                DropDownStyle = ComboBoxStyle.DropDownList,
                BackColor = Color.FromArgb(37, 45, 61),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat
            };
            cmbWindows.SelectedIndexChanged += (s, e) => ApplySelectedOpacity();

            btnRefresh = new Button
            {
                Text = "🔄 Làm mới",
                Location = new Point(368, 103),
                Size = new Size(95, 30),
                BackColor = Color.FromArgb(51, 65, 85),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Cursor = Cursors.Hand
            };
            btnRefresh.FlatAppearance.BorderSize = 0;
            btnRefresh.Click += (s, e) => RefreshWindowList();

            // Opacity Slider
            lblOpacity = new Label
            {
                Text = "Độ rõ nét / Độ trong suốt:",
                Location = new Point(20, 148),
                AutoSize = true,
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold)
            };

            lblOpacityValue = new Label
            {
                Text = "35% (Văn phòng lý tưởng)",
                Location = new Point(220, 148),
                AutoSize = true,
                ForeColor = Color.FromArgb(96, 165, 250),
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold)
            };

            trackOpacity = new TrackBar
            {
                Location = new Point(20, 174),
                Size = new Size(445, 45),
                Minimum = 5,
                Maximum = 100,
                Value = 35,
                TickFrequency = 5,
                BackColor = Color.FromArgb(24, 30, 42)
            };
            trackOpacity.Scroll += (s, e) =>
            {
                UpdateOpacityLabel();
                ApplySelectedOpacity();
            };

            // Preset Buttons (5 buttons spanning 445px)
            btnPreset5 = CreatePresetButton("🫥 5%", 20, 226, 83, 5);
            btnPreset15 = CreatePresetButton("👻 15%", 110, 226, 83, 15);
            btnPreset35 = CreatePresetButton("💼 35%", 200, 226, 83, 35);
            btnPreset60 = CreatePresetButton("🕶️ 60%", 290, 226, 83, 60);
            btnPreset100 = CreatePresetButton("💡 100%", 380, 226, 83, 100);

            // Boss Key Button
            btnBossKey = new Button
            {
                Text = "🚨 Boss Key: Ẩn ngay cửa sổ Chrome (Ctrl + Alt + Z)",
                Location = new Point(20, 272),
                Size = new Size(445, 38),
                BackColor = Color.FromArgb(220, 38, 38),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 10f, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            btnBossKey.FlatAppearance.BorderSize = 0;
            btnBossKey.Click += (s, e) => TriggerBossKey();

            // Shortcuts GroupBox
            grpShortcuts = new GroupBox
            {
                Text = "⌨️ Phím tắt toàn cục (Dùng bất cứ khi nào đang lướt Chrome):",
                Location = new Point(20, 322),
                Size = new Size(445, 140),
                ForeColor = Color.FromArgb(156, 163, 175),
                Font = new Font("Segoe UI", 8.5f, FontStyle.Bold)
            };

            lblShortcuts = new Label
            {
                Text = "• Ctrl + Alt + 1 : Làm trong suốt 10% (Siêu tàng hình)\n" +
                       "• Ctrl + Alt + 2 : Làm trong suốt 20%\n" +
                       "• Ctrl + Alt + 3 : Làm trong suốt 30% (Khuyên dùng khi có người qua lại)\n" +
                       "• Ctrl + Alt + 4..9 : Làm trong suốt 40% đến 90%\n" +
                       "• Ctrl + Alt + 0 : Khôi phục 100% (Bình thường)\n" +
                       "• Ctrl + Alt + Z : Boss Key (Ẩn thu nhỏ cửa sổ lập tức)",
                Location = new Point(12, 22),
                Size = new Size(420, 110),
                ForeColor = Color.FromArgb(229, 231, 235),
                Font = new Font("Segoe UI", 9f, FontStyle.Regular)
            };
            grpShortcuts.Controls.Add(lblShortcuts);

            // Minimize to tray checkbox
            chkMinimizeToTray = new CheckBox
            {
                Text = "Thu nhỏ xuống góc đồng hồ khi đóng cửa sổ",
                Location = new Point(20, 474),
                AutoSize = true,
                Checked = true,
                ForeColor = Color.FromArgb(156, 163, 175),
                Font = new Font("Segoe UI", 8.5f)
            };

            // Notify Icon
            notifyIcon = new NotifyIcon
            {
                Text = "Ghost Window\nCtrl+Alt+1..9 để chỉnh mờ\nCtrl+Alt+0 để khôi phục",
                Icon = SystemIcons.Application,
                Visible = false
            };
            notifyIcon.DoubleClick += (s, e) =>
            {
                this.Show();
                this.WindowState = FormWindowState.Normal;
                notifyIcon.Visible = false;
            };

            var contextMenu = new ContextMenuStrip();
            contextMenu.Items.Add("Mở giao diện điều khiển", null, (s, e) =>
            {
                this.Show();
                this.WindowState = FormWindowState.Normal;
                notifyIcon.Visible = false;
            });
            contextMenu.Items.Add("Khôi phục 100% cho cửa sổ đang xem", null, (s, e) => SetActiveWindowOpacity(255));
            contextMenu.Items.Add(new ToolStripSeparator());
            contextMenu.Items.Add("Thoát", null, (s, e) =>
            {
                notifyIcon.Visible = false;
                Application.Exit();
            });
            notifyIcon.ContextMenuStrip = contextMenu;

            // Add Controls to Form
            this.Controls.Add(lblHeader);
            this.Controls.Add(lblSubHeader);
            this.Controls.Add(lblSelectWindow);
            this.Controls.Add(cmbWindows);
            this.Controls.Add(btnRefresh);
            this.Controls.Add(lblOpacity);
            this.Controls.Add(lblOpacityValue);
            this.Controls.Add(trackOpacity);
            this.Controls.Add(btnPreset5);
            this.Controls.Add(btnPreset15);
            this.Controls.Add(btnPreset35);
            this.Controls.Add(btnPreset60);
            this.Controls.Add(btnPreset100);
            this.Controls.Add(btnBossKey);
            this.Controls.Add(grpShortcuts);
            this.Controls.Add(chkMinimizeToTray);

            this.FormClosing += MainWindow_FormClosing;
        }

        private Button CreatePresetButton(string text, int x, int y, int width, int opacityVal)
        {
            var btn = new Button
            {
                Text = text,
                Location = new Point(x, y),
                Size = new Size(width, 34),
                BackColor = Color.FromArgb(37, 45, 61),
                ForeColor = Color.FromArgb(224, 231, 255),
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 8.5f, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            btn.FlatAppearance.BorderSize = 1;
            btn.FlatAppearance.BorderColor = Color.FromArgb(55, 65, 81);
            btn.Click += (s, e) =>
            {
                trackOpacity.Value = opacityVal;
                UpdateOpacityLabel();
                ApplySelectedOpacity();
            };
            return btn;
        }

        private void UpdateOpacityLabel()
        {
            int val = trackOpacity.Value;
            string note = "";
            if (val <= 10) note = " (Cực mờ - Tàng hình tuyệt đối)";
            else if (val <= 20) note = " (Siêu mờ - Tàng hình)";
            else if (val <= 40) note = " (Văn phòng lý tưởng)";
            else if (val <= 70) note = " (Vừa phải)";
            else if (val < 100) note = " (Nhẹ)";
            else note = " (Rõ nét 100%)";

            lblOpacityValue.Text = val + "%" + note;
        }

        private void RefreshWindowList()
        {
            cmbWindows.Items.Clear();
            IntPtr chromeHwnd = IntPtr.Zero;

            EnumWindows((hWnd, lParam) =>
            {
                if (IsWindowVisible(hWnd))
                {
                    StringBuilder sb = new StringBuilder(256);
                    GetWindowText(hWnd, sb, 256);
                    string title = sb.ToString().Trim();

                    if (!string.IsNullOrEmpty(title) && title != this.Text && title != "Program Manager")
                    {
                        var item = new WindowItem { Handle = hWnd, Title = title };
                        int idx = cmbWindows.Items.Add(item);

                        // Auto-select Chrome or Edge if found
                        if (title.IndexOf("Chrome", StringComparison.OrdinalIgnoreCase) >= 0 && chromeHwnd == IntPtr.Zero)
                        {
                            chromeHwnd = hWnd;
                            cmbWindows.SelectedIndex = idx;
                        }
                    }
                }
                return true;
            }, IntPtr.Zero);

            if (cmbWindows.SelectedIndex == -1 && cmbWindows.Items.Count > 0)
            {
                cmbWindows.SelectedIndex = 0;
            }
        }

        private void ApplySelectedOpacity()
        {
            WindowItem item = cmbWindows.SelectedItem as WindowItem;
            if (item != null)
            {
                byte alpha = (byte)((trackOpacity.Value / 100.0) * 255);
                SetWindowOpacity(item.Handle, alpha);
            }
        }

        private void TriggerBossKey()
        {
            WindowItem item = cmbWindows.SelectedItem as WindowItem;
            if (item != null)
            {
                ShowWindow(item.Handle, SW_MINIMIZE);
            }
            else
            {
                IntPtr fg = GetForegroundWindow();
                if (fg != IntPtr.Zero && fg != this.Handle)
                {
                    ShowWindow(fg, SW_MINIMIZE);
                }
            }
        }

        private void SetWindowOpacity(IntPtr hWnd, byte alpha)
        {
            if (hWnd == IntPtr.Zero || hWnd == this.Handle) return;

            try
            {
                int exStyle = GetWindowLong(hWnd, GWL_EXSTYLE);
                if (alpha >= 255)
                {
                    SetLayeredWindowAttributes(hWnd, 0, 255, LWA_ALPHA);
                    SetWindowLong(hWnd, GWL_EXSTYLE, exStyle & ~WS_EX_LAYERED);
                }
                else
                {
                    SetWindowLong(hWnd, GWL_EXSTYLE, exStyle | WS_EX_LAYERED);
                    SetLayeredWindowAttributes(hWnd, 0, alpha, LWA_ALPHA);
                }
            }
            catch {}
        }

        private void SetActiveWindowOpacity(byte alpha)
        {
            IntPtr hWnd = GetForegroundWindow();
            if (hWnd != IntPtr.Zero && hWnd != this.Handle)
            {
                SetWindowOpacity(hWnd, alpha);
            }
            else
            {
                WindowItem item = cmbWindows.SelectedItem as WindowItem;
                if (item != null)
                {
                    SetWindowOpacity(item.Handle, alpha);
                }
            }
        }

        private void RegisterGlobalHotkeys()
        {
            // Ctrl + Alt + 0..9
            for (int i = 0; i <= 9; i++)
            {
                RegisterHotKey(this.Handle, 100 + i, MOD_CONTROL | MOD_ALT, (uint)(0x30 + i));
            }
            // Ctrl + Alt + Z (Boss Key)
            RegisterHotKey(this.Handle, 200, MOD_CONTROL | MOD_ALT, 0x5A);
        }

        private void UnregisterGlobalHotkeys()
        {
            for (int i = 0; i <= 9; i++)
            {
                UnregisterHotKey(this.Handle, 100 + i);
            }
            UnregisterHotKey(this.Handle, 200);
        }

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == WM_HOTKEY)
            {
                int id = m.WParam.ToInt32();
                if (id >= 100 && id <= 109)
                {
                    int digit = id - 100;
                    byte alpha = (digit == 0) ? (byte)255 : (byte)(digit * 25.5);
                    SetActiveWindowOpacity(alpha);
                }
                else if (id == 200)
                {
                    IntPtr fg = GetForegroundWindow();
                    if (fg != IntPtr.Zero && fg != this.Handle)
                    {
                        ShowWindow(fg, SW_MINIMIZE);
                    }
                }
            }
            base.WndProc(ref m);
        }

        private void MainWindow_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (e.CloseReason == CloseReason.UserClosing && chkMinimizeToTray.Checked)
            {
                e.Cancel = true;
                this.Hide();
                notifyIcon.Visible = true;
                notifyIcon.ShowBalloonTip(2000, "Ghost Window đang chạy ngầm", "Dùng Ctrl+Alt+1..9 để làm mờ cửa sổ. Bấm đúp vào icon này để mở lại.", ToolTipIcon.Info);
            }
            else
            {
                UnregisterGlobalHotkeys();
                notifyIcon.Visible = false;
                notifyIcon.Dispose();
            }
        }
    }
}
