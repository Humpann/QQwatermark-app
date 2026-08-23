import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

def run_git_push():
    repo_url = entry_url.get().strip()
    if not repo_url:
        messagebox.showwarning("提示", "请输入您的 GitHub 仓库地址！")
        return

    btn_submit.config(state="disabled", text="正在上传中...")
    status_label.config(text="正在连接 GitHub 并推送代码，请稍候...", fg="#3b82f6")
    root.update()

    work_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        # Check git init
        if not os.path.exists(os.path.join(work_dir, ".git")):
            subprocess.run(["git", "init"], cwd=work_dir, check=True)
            subprocess.run(["git", "config", "user.name", "OmniMedia"], cwd=work_dir, check=True)
            subprocess.run(["git", "config", "user.email", "omnimedia@example.com"], cwd=work_dir, check=True)

        subprocess.run(["git", "add", "."], cwd=work_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Deploy to Vercel/Cloud"], cwd=work_dir, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=work_dir, check=True)
        subprocess.run(["git", "remote", "remove", "origin"], cwd=work_dir, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=work_dir, check=True)

        # Push
        result = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=work_dir, capture_output=True, text=True)

        if result.returncode == 0:
            status_label.config(text="🎉 上传成功！代码已同步至 GitHub！", fg="#10b981")
            messagebox.showinfo("成功", "🎉 代码已成功推送到您的 GitHub 仓库！\n\n现在打开 https://vercel.com 即可一键导入部署上线！")
        else:
            status_label.config(text="上传失败，请检查网络或 GitHub 登录凭证", fg="#ef4444")
            messagebox.showerror("推送失败", f"Git 返回错误：\n{result.stderr}")
    except Exception as e:
        status_label.config(text="运行出错", fg="#ef4444")
        messagebox.showerror("错误", f"发生异常：{str(e)}")
    finally:
        btn_submit.config(state="normal", text="一键推送到 GitHub")

root = tk.Tk()
root.title("OmniMedia Pro · GitHub 一键上传助手")
root.geometry("540x260")
root.resizable(False, False)
root.configure(bg="#0f172a")

# Center Window
root.eval('tk::PlaceWindow . center')

title_label = tk.Label(root, text="🚀 OmniMedia Pro · GitHub 一键上传工具", font=("Microsoft YaHei UI", 13, "bold"), fg="#ffffff", bg="#0f172a")
title_label.pack(pady=(20, 10))

frame_input = tk.Frame(root, bg="#0f172a")
frame_input.pack(fill="x", padx=30, pady=5)

lbl_hint = tk.Label(frame_input, text="请输入您的 GitHub 仓库地址 (HTTPS URL):", font=("Microsoft YaHei UI", 9), fg="#94a3b8", bg="#0f172a")
lbl_hint.pack(anchor="w", pady=(0, 5))

entry_url = tk.Entry(frame_input, font=("Consolas", 10), bg="#1e293b", fg="#f8fafc", insertbackground="white", relief="flat", highlightthickness=1, highlightcolor="#6366f1", highlightbackground="#334155")
entry_url.pack(fill="x", ipady=6)

status_label = tk.Label(root, text="", font=("Microsoft YaHei UI", 9), fg="#94a3b8", bg="#0f172a")
status_label.pack(pady=(5, 5))

btn_submit = tk.Button(root, text="一键推送到 GitHub", font=("Microsoft YaHei UI", 10, "bold"), bg="#6366f1", fg="#ffffff", activebackground="#4f46e5", activeforeground="#ffffff", relief="flat", cursor="hand2", command=run_git_push)
btn_submit.pack(fill="x", padx=30, ipady=8, pady=(0, 15))

if __name__ == "__main__":
    root.mainloop()
