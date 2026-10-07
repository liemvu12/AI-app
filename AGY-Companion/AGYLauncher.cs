using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace AGYLauncher
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            try
            {
                string baseDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\', '/');
                string targetDir = baseDir;

                if (Directory.Exists(Path.Combine(baseDir, "agy_terminal_bridge")))
                {
                    targetDir = Path.Combine(baseDir, "agy_terminal_bridge");
                }

                // Kiểm tra cờ --tui
                bool isTuiMode = args != null && args.Length > 0 && Array.Exists(args, a => a.Equals("--tui", StringComparison.OrdinalIgnoreCase));

                // Tìm đường dẫn Python môi trường ảo
                string pythonExe = ResolvePython(targetDir);

                // Nếu chưa có .venv, tự động chạy setup_env.bat để khởi tạo
                if (string.IsNullOrEmpty(pythonExe))
                {
                    string setupBat = Path.Combine(targetDir, "setup_env.bat");
                    if (File.Exists(setupBat))
                    {
                        var psiSetup = new ProcessStartInfo
                        {
                            FileName = "cmd.exe",
                            Arguments = string.Format("/c \"{0}\"", setupBat),
                            WorkingDirectory = targetDir,
                            UseShellExecute = false
                        };
                        var p = Process.Start(psiSetup);
                        if (p != null)
                        {
                            p.WaitForExit();
                        }
                        pythonExe = ResolvePython(targetDir);
                    }
                }

                string companionPy = Path.Combine(targetDir, "companion.py");
                string companionCoreExe = Path.Combine(targetDir, "companion_core.exe");
                string distCoreExe = Path.Combine(targetDir, "dist", "companion_core", "companion_core.exe");

                string companionCmd;
                if (File.Exists(companionCoreExe))
                {
                    companionCmd = string.Format("\"{0}\" --tui", companionCoreExe);
                }
                else if (File.Exists(distCoreExe))
                {
                    companionCmd = string.Format("\"{0}\" --tui", distCoreExe);
                }
                else if (!string.IsNullOrEmpty(pythonExe) && File.Exists(companionPy))
                {
                    companionCmd = string.Format("\"{0}\" \"{1}\" --tui", pythonExe, companionPy);
                }
                else if (File.Exists(companionPy))
                {
                    companionCmd = string.Format("python \"{0}\" --tui", companionPy);
                }
                else
                {
                    MessageBox.Show(
                        "Không tìm thấy module chạy của AGY Companion!\n\nVui lòng đảm bảo file 'companion.py' nằm trong thư mục cài đặt.",
                        "AGY Companion",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error
                    );
                    return;
                }

                if (isTuiMode)
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = "powershell",
                        Arguments = string.Format("-NoExit -Command \"{0}\"", companionCmd),
                        WorkingDirectory = targetDir,
                        UseShellExecute = true
                    };
                    Process.Start(psi);
                    return;
                }

                // Mặc định: Mở Windows Terminal chia đôi màn hình Split-Pane
                try
                {
                    var psiWt = new ProcessStartInfo
                    {
                        FileName = "wt.exe",
                        Arguments = string.Format(
                            "-d \"{0}\" powershell -NoExit -Command \"agy\" ; split-pane -V -s 0.33 -d \"{1}\" powershell -NoExit -Command \"{2}\"",
                            targetDir, targetDir, companionCmd
                        ),
                        WorkingDirectory = targetDir,
                        UseShellExecute = true
                    };
                    Process.Start(psiWt);
                }
                catch
                {
                    // Fallback sang launch_split.bat hoặc 2 cửa sổ độc lập
                    string launchBat = Path.Combine(targetDir, "launch_split.bat");
                    if (File.Exists(launchBat))
                    {
                        var psiBat = new ProcessStartInfo
                        {
                            FileName = "cmd.exe",
                            Arguments = string.Format("/c \"{0}\"", launchBat),
                            WorkingDirectory = targetDir,
                            UseShellExecute = true
                        };
                        Process.Start(psiBat);
                    }
                    else
                    {
                        Process.Start(new ProcessStartInfo("powershell", "-NoExit -Command \"agy\"") { WorkingDirectory = targetDir, UseShellExecute = true });
                        Process.Start(new ProcessStartInfo("powershell", string.Format("-NoExit -Command \"{0}\"", companionCmd)) { WorkingDirectory = targetDir, UseShellExecute = true });
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Không thể khởi động ứng dụng:\n" + ex.Message,
                    "Lỗi khởi chạy",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        static string ResolvePython(string targetDir)
        {
            string[] candidates = new string[]
            {
                Path.Combine(targetDir, ".venv", "Scripts", "python.exe"),
                Path.Combine(targetDir, "..", ".venv", "Scripts", "python.exe"),
                Path.Combine(targetDir, "..", "..", ".venv", "Scripts", "python.exe")
            };

            foreach (var cand in candidates)
            {
                if (File.Exists(cand))
                {
                    return Path.GetFullPath(cand);
                }
            }

            return null;
        }
    }
}
