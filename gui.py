import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import requests
from requests.auth import HTTPBasicAuth
import io

BASE_URL = "http://localhost:8000"

class FastAPIClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FastAPI Client")
        self.geometry("400x300")
        
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self, text="Username:").pack()
        tk.Entry(self, textvariable=self.username).pack()
        
        tk.Label(self, text="Password:").pack()
        tk.Entry(self, textvariable=self.password, show="*").pack()
        
        tk.Button(self, text="Sign Up", command=self.signup).pack(pady=5)
        tk.Button(self, text="Sign In", command=self.signin).pack(pady=5)
        tk.Button(self, text="Upload File", command=self.upload_file).pack(pady=5)
        tk.Button(self, text="View & Download Files", command=self.view_files).pack(pady=5)

    def signup(self):
        response = requests.post(f"{BASE_URL}/signup/", json={"username": self.username.get(), "password": self.password.get()})
        if response.status_code == 200:
            messagebox.showinfo("Success", "User created successfully.")
        else:
            messagebox.showerror("Error", response.json().get("detail"))

    def signin(self):
        response = requests.get(f"{BASE_URL}/files/", auth=HTTPBasicAuth(self.username.get(), self.password.get()))
        if response.status_code == 200:
            messagebox.showinfo("Success", "Sign in successful.")
        else:
            messagebox.showerror("Error", "Failed to sign in. Please check your username and password.")

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            files = {'file': open(file_path, 'rb')}
            response = requests.post(f"{BASE_URL}/uploadfile/", files=files, auth=HTTPBasicAuth(self.username.get(), self.password.get()))
            if response.status_code == 200:
                messagebox.showinfo("Success", "File uploaded successfully.")
            else:
                messagebox.showerror("Error", "Failed to upload file.")
    
    def view_files(self):
        response = requests.get(f"{BASE_URL}/files/", auth=HTTPBasicAuth(self.username.get(), self.password.get()))
        if response.status_code == 200:
            files = response.json()
            if files:
                file_to_download = simpledialog.askstring("Download File", "Enter filename to download:\n" + "\n".join(files))
                if file_to_download and file_to_download in files:
                    self.download_file(file_to_download)
                else:
                    messagebox.showinfo("Info", "File not selected or not found.")
            else:
                messagebox.showinfo("Info", "No files uploaded.")
        else:
            messagebox.showerror("Error", "Failed to retrieve files.")

    def download_file(self, filename):
        response = requests.get(f"{BASE_URL}/files/download/{filename}", auth=HTTPBasicAuth(self.username.get(), self.password.get()), stream=True)
        if response.status_code == 200:
            file_path = filedialog.asksaveasfilename(defaultextension=".*", initialfile=filename)
            if file_path:
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192): 
                        f.write(chunk)
                messagebox.showinfo("Success", "File downloaded successfully.")
        else:
            messagebox.showerror("Error", "Failed to download file.")

if __name__ == "__main__":
    app = FastAPIClient()
    app.mainloop()
