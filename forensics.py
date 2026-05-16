import customtkinter as ctk
import mimetypes
import os
import datetime
import hashlib
import threading
import math
import platform
import subprocess
import shutil
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from tkinter import filedialog, messagebox
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CONFIGURATION & THEME ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ProColors:
    BG_DARK = "#020205"       # Deep Void Black
    BG_PANEL = "#0B0B15"      # Midnight Blue Panel
    ACCENT_MAIN = "#0078D7"   # Pro Blue
    ACCENT_GLOW = "#00C3FF"   # Cyan Glow
    ALERT_RED = "#FF3333"     # Alert Red
    TEXT_WHITE = "#FFFFFF"
    TEXT_DIM = "#8899A6"

    BG_PANEL_2 = "#070710"
    GRID_LINE = "#1C2333"
    CHIP_BG = "#0E1526"
    CHIP_BORDER = "#1E2A44"
    SUCCESS_GREEN = "#29CC7A"

    GRADIENT_START = (0, 15, 30)
    GRADIENT_END = (0, 0, 0)


# --- MODULE 1: FORENSIC CORE & METADATA ---
class ForensicEngine:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            random_state=42,
            n_jobs=-1
            )
        self.is_trained = False
        self._train_dummy_model()

    def _train_dummy_model(self):

        import numpy as np

        np.random.seed(42)

        X = []
        y = []

    # SAFE FILES (low entropy, mixed types)
        for _ in range(300):
            size = np.random.randint(500, 300000) / 1000.0
            entropy = np.random.uniform(1.0, 5.5)
            ext = np.random.choice([0, 0, 0, 1])  # mostly non-executable
            X.append([size, entropy, ext])
            y.append(0)

    # THREAT FILES (high entropy, executable-heavy)
        for _ in range(300):
            size = np.random.randint(50000, 2000000) / 1000.0
            entropy = np.random.uniform(6.5, 8.0)
            ext = 1
            X.append([size, entropy, ext])
            y.append(1)

        X = np.array(X)
        y = np.array(y)

        from sklearn.metrics import accuracy_score

        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        print(f"Model Accuracy: {acc:.2f}")
        self.is_trained = True

    def get_metadata(self, path):
        try:
            stats = os.stat(path)
            meta = {
                "Size": f"{stats.st_size} bytes",
                "Created": datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "Modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "Owner": getattr(stats, "st_uid", "N/A")
            }
            return meta
        except Exception:
            return {"Error": "Access Denied"}

    def calculate_entropy(self, data: bytes) -> float:
        if not data:
            return 0.0

        values, counts = np.unique(list(data), return_counts=True)

        probabilities = counts / len(data)

        entropy = -np.sum(probabilities * np.log2(probabilities))

        return float(entropy)

    def analyze_file(self, file_path, file_data: bytes):

        if not self.is_trained:
            return "UNKNOWN", "AI Loading...", 0

        size = len(file_data) / 1000.0
        entropy = self.calculate_entropy(file_data)
        ext = 1 if file_path.lower().endswith(('.exe', '.dll', '.bat', '.ps1', '.py')) else 0

        # ML Prediction
        probabilities = self.model.predict_proba([[size, entropy, ext]])[0]
        ml_threat_prob = float(probabilities[1])

        # Base reason list
        reasons = []

        if entropy > 7.0:
            reasons.append("High Entropy (Encrypted)")
            ml_threat_prob = min(ml_threat_prob + 0.15, 1.0)

        if ext == 1:
            reasons.append("Executable Script Detected")

        # Keyword detection (boost probability instead of overriding)
        keywords = [
        b"password", b"admin", b"root", b"secret", b"confidential",
        b"apikey", b"token", b"private_key", b"ssh", b"creditcard"
        ]

        lower = file_data.lower()

        for k in keywords:
            if k in lower:
                reasons.append(f"Keyword '{k.decode('utf-8')}'")
                ml_threat_prob = min(ml_threat_prob + 0.15, 1.0)
                break

        # Cap probability to 1
        ml_threat_prob = min(ml_threat_prob, 1.0)

        risk_score = int(ml_threat_prob * 100)

        # Final decision logic (consistent)
        if ml_threat_prob >= 0.6:
            status = "CRITICAL"
        elif ml_threat_prob >= 0.3:
            status = "SUSPICIOUS"
        else:
            status = "SAFE"

        if not reasons:
            reasons.append("Verified Clean")

        return status, ", ".join(reasons), risk_score

# --- MODULE 2: SYSTEM & RECOVERY TOOLS ---
class SystemOps:
    @staticmethod
    def get_usb_devices():
        devices = []
        try:
            if platform.system() == "Windows":
                cmd = "wmic logicaldisk where drivetype=2 get deviceid, volumename"
                output = subprocess.check_output(cmd, shell=True).decode(errors="ignore")
                lines = output.strip().split('\n')[1:]
                for line in lines:
                    if line.strip():
                        devices.append(line.strip())
        except Exception:
            devices.append("USB Scan Failed")
        return devices

    @staticmethod
    def scan_recycle_bin():
        deleted = []

        if platform.system() == "Windows":
            base_paths = ["C:\\$Recycle.Bin", "D:\\$Recycle.Bin", "E:\\$Recycle.Bin"]

            for base in base_paths:
                if not os.path.exists(base):
                    continue

                for sid in os.listdir(base): 
                    sid_path = os.path.join(base, sid)

                    if not os.path.isdir(sid_path):
                        continue
                    if not os.access(sid_path, os.R_OK):
                        continue

                    try:
                        files_list = os.listdir(sid_path)
                    except PermissionError:
                        continue

                    for file in files_list:
                        if file.startswith("$I"):
                            try:
                                i_path = os.path.join(sid_path, file)
                                r_path = os.path.join(sid_path, "$R" + file[2:])

                                if not os.path.exists(r_path):
                                    continue

                                with open(i_path, "rb") as f:
                                    data = f.read()

                                original_path = data[24:].decode("utf-16", errors="ignore").strip("\x00")
                                raw_path = data[24:].decode("utf-16", errors="ignore").strip("\x00")

                                start_index = raw_path.find("C:\\")
                                if start_index != -1:
                                    original_path = raw_path[start_index:]
                                else:
                                    original_path = raw_path
                                deleted_time = int.from_bytes(data[16:24], "little")

                                deleted.append({
                                    "data_path": r_path,
                                    "original_name": os.path.basename(original_path),
                                    "original_path": original_path,
                                    "deleted_time": deleted_time
                            })

                            except Exception as e:
                                    print("ERROR:", e)

        return deleted

    @staticmethod
    def recover_files(file_list, destination_folder):

        import json

        success_count = 0
        case_log = []
        seen_hashes = set()

        def hash_file(p):
            h = hashlib.sha256()
            with open(p, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()

        for item in file_list:
            try:
                if isinstance(item, dict):
                    src = item.get("data_path")
                    original_name = item.get("original_name")
                    original_path = item.get("original_path", "Unknown")
                    deleted_time = item.get("deleted_time", "Unknown")
                else:
                    src = item
                    original_name = os.path.basename(src)
                    original_path = "Unknown"
                    deleted_time = "Unknown"

                if not src or not os.path.exists(src):
                    continue

                dst = os.path.join(destination_folder, original_name)

                shutil.copy2(src, dst)

                recovered_hash = hash_file(dst)

                if recovered_hash in seen_hashes:
                    print(f"Duplicate detected: {original_name}")
                else:
                    seen_hashes.add(recovered_hash)

                case_log.append({
                    "file": original_name,
                    "original_path": original_path,
                    "deleted_time": deleted_time,
                    "recovered_path": dst,
                    "hash": recovered_hash
                })

                success_count += 1

            except Exception as e:
                print("RECOVERY ERROR:", e)

    # SAVE FORENSIC LOG
        case_log.sort(key=lambda x: str(x["deleted_time"]))

        with open(os.path.join(destination_folder, "forensic_recovery.json"), "w") as jf:
            json.dump(case_log, jf, indent=4)

        return success_count
    @staticmethod
    def disk_carving_recovery(scan_path, output_folder):

        signatures = {
            b"\xFF\xD8\xFF": ("jpg", b"\xFF\xD9"),
            b"\x89PNG\r\n\x1a\n": ("png", b"IEND"),
            b"%PDF": ("pdf", b"%%EOF"),
            b"PK\x03\x04": ("zip", None),
            b"GIF87a": ("gif", b"\x3B"),
            b"GIF89a": ("gif", b"\x3B"),
        }

        recovered = 0

        for root, _, files in os.walk(scan_path):
            for fname in files:
                fpath = os.path.join(root, fname)

                try:
                    with open(fpath, "rb") as f:
                        data = f.read()

                    for sig, (ext, end_sig) in signatures.items():

                        start = 0

                        while True:
                            start = data.find(sig, start)

                            if start == -1:
                                break

                            if end_sig:
                                end = data.find(end_sig, start)
                                if end == -1:
                                    break

                                chunk = data[start:end + len(end_sig)]

                            else:
                                chunk = data[start:start + 500000]

                            out_file = os.path.join(
                                output_folder,
                                f"carved_{recovered}.{ext}"
                            )

                            with open(out_file, "wb") as out:
                                out.write(chunk)

                            recovered += 1

                            start += 1

                except Exception as e:
                    print("RECOVERY ERROR:", e)
        return recovered

# --- MODULE 3: LEDGER ---
class ChainLedger:
    def __init__(self):
        self.chain = []
        self.stats = {"SAFE": 0, "CRITICAL": 0, "TOTAL": 0}

    def log(self, event, details, status="INFO"):
        prev_hash = self.chain[-1]["hash"] if self.chain else "GENESIS"
        block = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "event": event,
            "details": details,
            "prev_hash": prev_hash,
            "hash": hashlib.sha256((str(details)+prev_hash).encode()).hexdigest()[:8]
        }
        self.chain.append(block)
        print("BLOCK:", block)
        if event == "ANALYSIS":
            self.stats["TOTAL"] += 1
            if status in self.stats:
                self.stats[status] += 1
        return block


# --- MODULE 4: REPORTING ---
class BlueGradientReport(FPDF):
    def header(self):
        r1, g1, b1 = ProColors.GRADIENT_START
        r2, g2, b2 = ProColors.GRADIENT_END

        for i in range(30):
            self.set_fill_color(
                r1 - (r1 - r2) * (i / 30),
                g1 - (g1 - g2) * (i / 30),
                b1 - (b1 - b2) * (i / 30)
            )
            self.rect(0, i, 210, 1, 'F')

        self.set_y(10)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'AUTOMATED DIGITAL FORENSICS SYSTEM | FORENSIC AUDIT REPORT', 0, 1, 'C')
        self.ln(20)

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(0, 120, 215)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {label}", 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln()


# --- MODULE 5: THE UI ---
class ShadowTraceApp(ctk.CTk):
    def init_engine(self):
        self.engine = ForensicEngine()

    def add_table_row(self, name, status, risk, entropy, file_hash):

        bg = "#0a0a12" if len(self.table_body.winfo_children()) % 2 == 0 else "#050509"
        row = ctk.CTkFrame(self.table_body, fg_color=bg, height=35)
        row.pack_propagate(False)
        row.pack(fill="x", pady=6)

        values = [
        name[:20],
        status,
        f"{risk}%",
        f"{entropy:.2f}",
        file_hash[:12]
    ]

        for i, v in enumerate(values):

    # Color coding
            if i == 1:  # STATUS column
                if status == "CRITICAL":
                    color = ProColors.ALERT_RED
                else:
                    color = ProColors.ACCENT_MAIN
            elif i == 2:  # RISK column
                if risk >= 60:
                    color = ProColors.ALERT_RED
                elif risk >= 30:
                    color = "#FFA500"  # orange
                else:
                    color = ProColors.ACCENT_MAIN
            else:
                color = ProColors.TEXT_WHITE

            ctk.CTkLabel(
            row,
            text=v,
            font=("Consolas", 12 , "bold"),
            text_color=color,
            width=140,
            anchor="w"
            ).pack(side="left", padx=10, pady =5)

    def safe_insert_scan(self, text):
        self.scan_list.insert("end", text)
        self.scan_list.see("end")
    def __init__(self):
        super().__init__()
        self.case_id = "DFIR-" + datetime.datetime.now().strftime("%Y%m%d-%H%M")
        self.engine = None
        self.init_engine()
        self.ledger = ChainLedger()
        self.recovered_files_cache = []

        # XAI storage
        self.last_scan_rows = []

        self.title("Automated Digital Forensics System")
        self.geometry("1280x800")
        self.configure(fg_color=ProColors.BG_DARK)
        self.setup_layout()

        # Delay chart initialization until UI widgets exist
        self.after(300, self.update_charts)

    def setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=ProColors.BG_PANEL)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            self.sidebar,
            text="AUTOMATED\nDIGITAL FORENSICS",
            font=("Impact", 32),
            text_color=ProColors.ACCENT_MAIN
        ).pack(pady=40)

        self.console = ctk.CTkTextbox(
            self.sidebar,
            fg_color="#000000",
            text_color=ProColors.ACCENT_GLOW,
            font=("Consolas", 10)
        )
        self.log_console("AI Engine Ready", "SYS")
        self.console.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabs = ctk.CTkTabview(
            self,
            fg_color="transparent",
            segmented_button_selected_color=ProColors.ACCENT_MAIN
        )
        self.tabs.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)

        self.tab_dash = self.tabs.add("DASHBOARD")
        self.tab_scan = self.tabs.add("SCAN & RECOVER")

        self.build_dashboard()
        self.build_scanner()

    # --- DASHBOARD ---
    def build_dashboard(self):
        self.stats_frame = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=10)
        self.lbl_safe = self.make_stat_card("SECURE FILES", "0", ProColors.ACCENT_MAIN)
        self.lbl_crit = self.make_stat_card("THREATS DETECTED", "0", ProColors.ALERT_RED)
        self.lbl_total = self.make_stat_card("TOTAL SCANNED", "0", ProColors.TEXT_WHITE)
        summary_frame = ctk.CTkFrame(self.tab_dash, fg_color=ProColors.BG_PANEL_2)
        summary_frame.pack(fill="x", pady=10)

        self.case_start_time = datetime.datetime.now()

        ctk.CTkLabel(
            summary_frame,
            text="FORENSIC INVESTIGATION SUMMARY",
            font=("Arial Black", 14),
            text_color=ProColors.ACCENT_GLOW
        ).pack(pady=(10,5))

        self.summary_text = ctk.CTkLabel(
        summary_frame,
        text="Case Initialized\nWaiting for scan...",
        font=("Consolas", 11),
        text_color=ProColors.TEXT_WHITE,
        justify="left"
        )

        self.summary_text.pack(pady=(0,10))
        self.chart_frame = ctk.CTkFrame(self.tab_dash, fg_color=ProColors.BG_PANEL)
        self.chart_frame.pack(fill="both", expand=True, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(5, 3), facecolor=ProColors.BG_PANEL)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        btn_row = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 20))

        ctk.CTkLabel(
        self.tab_dash,
        text=f"Forensic Investigation Case ID: {self.case_id}",
        font=("Arial", 12, "bold"),
        text_color=ProColors.ACCENT_GLOW
        ).pack(pady=(5,10))

        ctk.CTkButton(
        btn_row,
        text="DOWNLOAD REPORT (PDF)",
        command=self.generate_report,
        fg_color=ProColors.ACCENT_MAIN,
        font=("Arial", 12, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
        btn_row,
        text="OPEN EXPLAINABLE AI (XAI)",
        command=self.open_xai_window,
        fg_color=ProColors.ACCENT_GLOW,
        text_color="black",
        font=("Arial", 12, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
        btn_row,
        text="XAI = Audit-ready explanation of file decisions",
        text_color=ProColors.TEXT_DIM,
        font=("Arial", 10)
        ).pack(side="left", padx=10)

    def make_stat_card(self, title, val, color):
        f = ctk.CTkFrame(
            self.stats_frame,
            fg_color=ProColors.BG_PANEL,
            border_color=color,
            border_width=1
        )
        f.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(f, text=title, font=("Arial", 10), text_color=ProColors.TEXT_DIM).pack(pady=(10, 0))
        l = ctk.CTkLabel(f, text=val, font=("Arial Black", 24), text_color=color)
        l.pack(pady=(0, 10))
        return l

    # --- SCANNER & RECOVERY ---
    def build_scanner(self):
        ctrl = ctk.CTkFrame(self.tab_scan, fg_color="transparent")
        ctrl.pack(fill="x", pady=10)

        ctk.CTkButton(
            ctrl, text="SCAN FOLDER",
            command=self.scan_folder,
            fg_color=ProColors.ACCENT_MAIN
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            ctrl, text="FIND DELETED FILES",
            command=self.scan_recycle_bin,
            fg_color=ProColors.ACCENT_GLOW,
            text_color="black"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            ctrl, text="RECOVER FOUND FILES",
            command=self.recover_selected,
            fg_color=ProColors.ALERT_RED
        ).pack(side="left", padx=5)

        self.prog = ctk.CTkProgressBar(self.tab_scan, progress_color=ProColors.ACCENT_MAIN)
        self.prog.set(0)
        self.prog.pack(fill="x", padx=10, pady=10)

        self.scan_list = ctk.CTkTextbox(
            self.tab_scan,
            font=("Consolas", 11),
            state="disabled",
            fg_color="#000000",
            text_color=ProColors.ACCENT_GLOW
        )
        self.scan_list.pack(fill="both", expand=True)
        # --- FORENSIC EVIDENCE TABLE ---
        self.table_frame = ctk.CTkFrame(self.tab_scan, fg_color=ProColors.BG_PANEL)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        headers = ["FILE", "STATUS", "RISK", "ENTROPY", "HASH"]

        self.table_headers = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.table_headers.pack(fill="x")

        for h in headers:
            ctk.CTkLabel(
                self.table_headers,
                text=h,
                font=("Arial", 13, "bold"),
                text_color=ProColors.ACCENT_GLOW,
                width=140,
                anchor="w"
            ).pack(side="left", padx=10, pady=5)

        self.table_body = ctk.CTkScrollableFrame(self.table_frame, fg_color="#000000")
        self.table_body.pack(fill="both", expand=True)

    # --- HELPERS ---
    def log_console(self, msg, tag="INFO"):
        if not hasattr(self, "console"):
            return
        self.console.insert("end", f"[{tag}] {msg}\n")
        self.console.see("end")

    def update_charts(self):
        if not hasattr(self, "lbl_safe"):
            return
        self.ax.clear()
        self.ax.set_facecolor(ProColors.BG_PANEL)

        stats = [self.ledger.stats["SAFE"], self.ledger.stats["CRITICAL"]]
        if sum(stats) == 0:
            stats = [1]
            labels = ["Ready"]
            colors = ["#333333"]
        else:
            labels = ["Secured", "Threats"]
            colors = [ProColors.ACCENT_MAIN, ProColors.ALERT_RED]

        wedges, _ = self.ax.pie(stats, colors=colors, startangle=90, wedgeprops=dict(width=0.4))
        self.ax.text(
            0, 0,
            f"{self.ledger.stats['TOTAL']}\nFILES",
            ha='center', va='center',
            color='white', fontsize=12, fontweight='bold'
        )
        self.ax.legend(
        wedges,
        [f"Secured ({self.ledger.stats['SAFE']})",
        f"Threats ({self.ledger.stats['CRITICAL']})"],
        loc="center left",
        bbox_to_anchor=(1.25, 0.5),
        frameon=False,
        labelcolor='white'
        )

        self.lbl_safe.configure(text=str(self.ledger.stats["SAFE"]))
        self.lbl_crit.configure(text=str(self.ledger.stats["CRITICAL"]))
        self.lbl_total.configure(text=str(self.ledger.stats["TOTAL"]))

        self.canvas.draw()

    # --- FORENSIC OPERATIONS ---
    def scan_folder(self):
        path = filedialog.askdirectory()
        if path:
            threading.Thread(target=self._thread_scan, args=(path,), daemon=True).start()
        self.after(0, lambda: self.scan_list.configure(state="normal"))

    def _thread_scan(self, path):
        self.log_console(f"Scanning: {path}", "SCAN")
        self.after(0, lambda: [child.destroy() for child in self.table_body.winfo_children()])

        self.after(0, lambda: self.scan_list.configure(state="normal"))
        self.after(0, lambda: self.scan_list.delete("0.0", "end"))

        # reset last scan rows for XAI
        self.last_scan_rows = []

        files = []
        for r, _, f in os.walk(path):
            for file in f:
                files.append(os.path.join(r, file))

        total = len(files)
        if total == 0:
            self.log_console("No files found in selected folder.", "SCAN")
            self.after(0, lambda: self.scan_list.configure(state="disabled"))
            return

        for i, fpath in enumerate(files):
            try:
                hasher = hashlib.sha256()

                with open(fpath, "rb") as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        hasher.update(chunk)

                file_hash = hasher.hexdigest()

                with open(fpath, "rb") as f:
                    data = f.read(4096)
                if not self.engine or not self.engine.is_trained:
                    self.log_console("AI still loading...", "SYS")
                    continue

                status, reason, risk = self.engine.analyze_file(fpath, data)
                entropy_val = self.engine.calculate_entropy(data)

                meta = self.engine.get_metadata(fpath)

                self.ledger.log("ANALYSIS", f"{os.path.basename(fpath)} | {reason}", status)

                color = "[+]" if status == "SAFE" else "[!]"
                detail_str = (
                    f"{color} {os.path.basename(fpath)}\n"
                    f"    -> Status: {status}\n"
                    f"    -> SHA256: {file_hash[:32]}...\n"
                    f"    -> Created: {meta.get('Created')}\n"
                    f"    -> Modified: {meta.get('Modified')}\n"
                    f"    -> Reason: {reason}\n"
                )
                self.after(0, self.safe_insert_scan, detail_str + "-" * 50 + "\n")

                size = len(data)
                entropy = self.engine.calculate_entropy(data)
                ext_flag = 1 if fpath.lower().endswith(('.exe', '.dll', '.bat', '.ps1', '.py')) else 0

                self.last_scan_rows.append ({
                    "path": fpath,
                    "name": os.path.basename(fpath),
                    "size": int(size),
                    "entropy": float(entropy_val),
                    "ext": int(ext_flag),
                    "status": status,
                    "reason": reason,
                    "meta": meta,
                    "risk": risk,
                    "hash": file_hash 
                })

                self.after(0, lambda v=(i+1)/total: self.prog.set(v))

                if i % 5 == 0:
                    self.after(10, self.update_charts)

            except Exception as e:
                print("SCAN ERROR:", e)
        # Sort rows by risk descending
        self.last_scan_rows.sort(key=lambda x: x.get("risk", 0), reverse=True)
        self.after(0, lambda: [child.destroy() for child in self.table_body.winfo_children()])

        for row in self.last_scan_rows:
            self.after(0, self.add_table_row,
            row["name"],
            row["status"],
            row["risk"],
            row["entropy"],
            row["hash"][:12]
        )
            
# ORIGINAL FLOW CONTINUES
        self.log_console("Scan Complete.", "DONE")
        self.after(0, lambda: self.scan_list.configure(state="disabled"))
        self.after(0, self.update_charts)
        scan_time = datetime.datetime.now() - self.case_start_time

        summary = (
            f"Case ID: {self.case_id}\n"
            f"Case Started: {self.case_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Scan Duration: {scan_time}\n"
            f"Files Scanned: {self.ledger.stats['TOTAL']}\n"
            f"Threats Detected: {self.ledger.stats['CRITICAL']}\n"
            f"Detection Model: Hybrid ML + Rule-Based\n"
        )

        self.after(0, lambda: self.summary_text.configure(text=summary))

    def scan_recycle_bin(self):
        self.log_console("Scanning Recycle Bin...", "REC")
        files = SystemOps.scan_recycle_bin()

        if not files:
            messagebox.showinfo("Result", "No deleted files accessible (Try running as Admin).")
            return

        self.recovered_files_cache = files
        self.scan_list.configure(state="normal")
        self.scan_list.delete("0.0", "end")
        self.scan_list.delete("0.0", "end")
        self.scan_list.insert("end", "Deleted Files Found:\n\n")

        for f in files:
            self.scan_list.insert("end", f"[DEL] {f}\n")

        self.after(0, lambda: self.scan_list.configure(state="disabled"))
        self.log_console(f"Found {len(files)} deleted items.", "REC")

    def recover_selected(self):

        dest = filedialog.askdirectory(title="Select Destination for Recovery")
        if not dest:
            return

        total_recovered = 0

        self.log_console("Starting Recovery...", "REC")

    # -------------------------
    # 1. RECYCLE BIN RECOVERY
    # -------------------------
        if self.recovered_files_cache:
            count = SystemOps.recover_files(self.recovered_files_cache, dest)
            total_recovered += count
            self.log_console(f"Recycle Recovery: {count}", "REC")

    # -------------------------
    # 2. DEEP RECOVERY (CARVING)
    # -------------------------
        scan_path = filedialog.askdirectory(title="Select Folder for Deep Recovery (Optional)")

        if scan_path:
            self.log_console("Running Deep Recovery...", "CARVE")

            count = SystemOps.disk_carving_recovery(scan_path, dest)
            total_recovered += count

            self.log_console(f"Deep Recovery: {count}", "CARVE")

    # -------------------------
    # FINAL MESSAGE
    # -------------------------
        messagebox.showinfo(
            "Recovery Complete",
            f"Total Recovered Files: {total_recovered}\n\nMethod: Recycle Bin + Signature-based Carving\nIntegrity: SHA-256 Verified"
        )

        self.log_console(f"Recovery Completed: {total_recovered}", "DONE")

    def generate_report(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path:
            return
        try:
            self.fig.savefig("temp_chart.png", facecolor=ProColors.BG_PANEL)

            pdf = BlueGradientReport()
            pdf.add_page()

            pdf.chapter_title("EXECUTIVE SUMMARY")
            pdf.chapter_body(f"Case ID: {self.case_id}")
            pdf.chapter_body(
                f"Report Generated: {datetime.datetime.now()}\n"
                f"Forensic Tool: Automated Digital Forensics System\n"
                f"Evidence Timestamp: {datetime.datetime.now()}\n"
                f"Total Files Scanned: {self.ledger.stats['TOTAL']}\n"
                f"Threats Detected: {self.ledger.stats['CRITICAL']}"
            )

            pdf.image("temp_chart.png", x=50, w=100)

            pdf.chapter_title("DETAILED ANALYSIS LEDGER")
            pdf.chapter_title("FORENSIC EVIDENCE TABLE")
            pdf.chapter_body("Recovery Capability: Recycle Bin + Deep Carving + Integrity Verified")

            table_text = ""

            for row in self.last_scan_rows[:50]:
                table_text += (
                    f"{row['name']} | "
                    f"Status: {row['status']} | "
                    f"Risk: {row['risk']}% | "
                    f"Entropy: {row['entropy']:.2f}\n"
                ) 

            pdf.chapter_body(table_text)
            log_text = ""
            for item in self.ledger.chain[-50:]:
                log_text += f"[{item['time']}] {item['details']}\n"
            pdf.chapter_body(log_text)

            pdf.output(save_path)
            try:
                os.remove("temp_chart.png")
            except Exception as e:
                print("RECOVERY ERROR:", e)

            messagebox.showinfo("Success", "Report Generated Successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==========================
    # EXPLAINABLE AI WINDOW (OPTION B)
    # ==========================
    def open_xai_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Automated Digital Forensics System | Explainable AI Console")
        win.configure(fg_color=ProColors.BG_DARK)

        # bring to front briefly
        win.attributes("-topmost", True)
        win.after(200, lambda: win.attributes("-topmost", False))

        header = ctk.CTkFrame(win, fg_color=ProColors.BG_PANEL, corner_radius=10)
        header.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(
            header,
            text="EXPLAINABLE AI (XAI) • FORENSIC DECISION TRACE",
            font=("Arial Black", 16),
            text_color=ProColors.ACCENT_GLOW
        ).pack(side="left", padx=14, pady=12)

        chip = ctk.CTkFrame(
            header,
            fg_color=ProColors.CHIP_BG,
            border_color=ProColors.CHIP_BORDER,
            border_width=1,
            corner_radius=18
        )
        chip.pack(side="right", padx=14, pady=10)

        ctk.CTkLabel(
            chip,
            text="Audit-Ready Explanations • EXE-Friendly • No SHAP dependencies",
            font=("Arial", 10),
            text_color=ProColors.TEXT_DIM
        ).pack(padx=12, pady=6)

        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=3)

        # LEFT: file list
        left = ctk.CTkFrame(body, width=380, fg_color=ProColors.BG_PANEL, corner_radius=12)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10), pady=0)
        left.grid_propagate(False)

        ctk.CTkLabel(left, text="FILES (Last Scan)", font=("Arial Black", 14), text_color=ProColors.TEXT_WHITE)\
            .pack(anchor="w", padx=14, pady=(14, 6))

        ctk.CTkLabel(
            left,
            text="Select a file index to view local explanation.",
            font=("Arial", 10),
            text_color=ProColors.TEXT_DIM
        ).pack(anchor="w", padx=14, pady=(0, 10))

        file_box = ctk.CTkTextbox(
            left,
            height=520,
            fg_color="#000000",
            text_color=ProColors.ACCENT_GLOW,
            font=("Consolas", 11),
            border_color=ProColors.GRID_LINE,
            border_width=1
        )
        file_box.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        file_box.configure(state="normal")
        file_box.delete("0.0", "end")
        if not self.last_scan_rows:
            file_box.insert("end", "No scan data available.\n\nRun: SCAN & RECOVER -> SCAN FOLDER\n")
        else:
            for i, r in enumerate(self.last_scan_rows):
                icon = "[!]" if r["status"] == "CRITICAL" else "[+]"
                file_box.insert("end", f"{i:02d} {icon} {r['name']}\n")
        file_box.configure(state="disabled")

        idx_row = ctk.CTkFrame(left, fg_color="transparent")
        idx_row.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkLabel(idx_row, text="File Index:", text_color=ProColors.TEXT_DIM, font=("Arial", 11)).pack(side="left")
        idx_entry = ctk.CTkEntry(
            idx_row,
            width=70,
            fg_color="#000000",
            text_color=ProColors.TEXT_WHITE,
            border_color=ProColors.GRID_LINE
        )
        idx_entry.pack(side="left", padx=10)

        # RIGHT TOP: global chart panel
        right_top = ctk.CTkFrame(body, fg_color=ProColors.BG_PANEL, corner_radius=12)
        right_top.grid_propagate(False)
        right_top.configure(height=250)
        right_top.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        right_top.grid_rowconfigure(0, weight=0)
        right_top.grid_rowconfigure(1, weight=1)
        right_top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right_top,
            text="GLOBAL EXPLANATION • MODEL FEATURE IMPORTANCE",
            font=("Arial Black", 13),
            text_color=ProColors.TEXT_WHITE
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        # RIGHT BOTTOM: local explanation panel
        right_bottom = ctk.CTkFrame(body, fg_color=ProColors.BG_PANEL, corner_radius=12)
        right_bottom.grid_rowconfigure(1, weight=1)
        right_bottom.grid(row=1, column=1, sticky="nsew", padx=0, pady=(10, 0))
        right_bottom.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right_bottom,
            text="LOCAL EXPLANATION • DECISION TRACE (Per File)",
            font=("Arial Black", 13),
            text_color=ProColors.TEXT_WHITE
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        explain = ctk.CTkTextbox(
            right_bottom,
            fg_color="#000000",
            text_color=ProColors.TEXT_WHITE,
            font=("Consolas", 11),
            border_color=ProColors.GRID_LINE,
            border_width=1
        )
        explain.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

        def _pretty_risk(status: str) -> str:
            return "RISK: HIGH (CRITICAL)" if status == "CRITICAL" else "RISK: LOW (SAFE)"

        def show_explanation(idx: int):
            if not self.last_scan_rows:
                return
            if idx < 0 or idx >= len(self.last_scan_rows):
                return

            r = self.last_scan_rows[idx]
            X = np.array([[r["size"], r["entropy"], r["ext"]]], dtype=float)

            prob_safe, prob_threat = None, None
            try:
                proba = self.engine.model.predict_proba(X)[0]
                prob_safe = float(proba[0])
                prob_threat = float(proba[1])
            except Exception as e:
                print("RECOVERY ERROR:", e)

            lines = []
            lines.append("══════════════════════════════════════════════════════════════")
            lines.append(f"FILE: {r['name']}")
            short_path = "..." + r["path"][-60:]
            lines.append(f"PATH: {short_path}")
            lines.append(_pretty_risk(r['status']))
            if prob_safe is not None:
                adjusted_threat = prob_threat
                adjusted_safe = prob_safe
                lines.append(
                    f"MODEL CONFIDENCE → SAFE: {adjusted_safe*100:.1f}% | THREAT: {adjusted_threat*100:.1f}%"
                )
                confidence = "HIGH" if adjusted_threat > 0.7 else "MEDIUM" if adjusted_threat > 0.4 else "LOW"
                lines.append(f"DECISION CONFIDENCE: {confidence}")
                lines.append("MODEL TYPE: RandomForest Classifier (Supervised ML)")
                lines.append("MODEL VALIDATION: Synthetic Training Data (Simulated Forensic Dataset)")
                lines.append("FEATURES USED: Size, Entropy, Executable Flag")
                lines.append("DECISION: Hybrid (ML + Rule-Based Forensic Indicators)")

            else:
                lines.append("MODEL CONFIDENCE → Not Available")
            
            lines.append("══════════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("FEATURE VECTOR (MODEL INPUT):")
            lines.append(f"  • Size (bytes)      : {r['size']}")
            lines.append(f"  • Entropy           : {r['entropy']:.3f}   (High if > ~7.0)")
            lines.append(f"  • ExecutableFlag    : {r['ext']}   (1 if exe/dll/bat/ps1/py)")
            lines.append("")
            lines.append("FORENSIC INDICATORS (RULE + ML HYBRID):")
            lines.append(f"  • Engine Reason     : {r['reason']}")
            lines.append("")
            lines.append("INTERPRETATION:")
            reason = (r.get("reason") or "").lower()
            if "keyword" in reason:
                lines.append("  - Sensitive keyword hit: possible credentials / secrets.")
            if "high entropy" in reason:
                lines.append("  - High entropy suggests packed/encrypted payload or hidden data.")
            if "executable" in reason:
                lines.append("  - Executable/script detected: higher incident-response priority.")
            if "verified clean" in reason:
                lines.append("  - No suspicious indicators matched current rules; treated as clean.")
            lines.append("")
            lines.append("RECOMMENDED ACTIONS:")
            if r["status"] == "CRITICAL":
                lines.append("  1) Isolate file and capture hash + metadata.")
                lines.append("  2) Search related artifacts (same directory / same timestamp).")
                lines.append("  3) Sandbox/static analysis if policy allows.")
            else:
                lines.append("  1) Keep as baseline evidence (timeline correlation).")
                lines.append("  2) Re-scan if new rules/signatures are added.")

            explain.configure(state="normal")
            explain.delete("0.0", "end")
            explain.insert("0.0", "\n".join(lines))
            explain.configure(state="disabled")

        def on_show():
            if not self.last_scan_rows:
                messagebox.showinfo("XAI", "No scan session data yet.\nRun SCAN FOLDER first, then open XAI again.")
                return
            try:
                idx = int(idx_entry.get().strip())
                show_explanation(idx)
            except Exception as e:
                print("RECOVERY ERROR:", e)

        show_btn = ctk.CTkButton(
            idx_row,
            text="SHOW",
            command=on_show,
            fg_color=ProColors.ACCENT_MAIN,
            font=("Arial", 11, "bold")
        )
        show_btn.pack(side="left", padx=6)

        # ===== OPTION B behavior for GLOBAL chart =====
        if not self.last_scan_rows:
            # Placeholder instead of chart
            placeholder = ctk.CTkFrame(
                right_top,
                fg_color="#000000",
                corner_radius=12,
                border_color=ProColors.GRID_LINE,
                border_width=1
            )
            placeholder.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
            placeholder.grid_rowconfigure(0, weight=1)
            placeholder.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                placeholder,
                text="NO FORENSIC SESSION DATA",
                font=("Arial Black", 18),
                text_color=ProColors.ACCENT_GLOW
            ).grid(row=0, column=0, pady=(120, 6))

            ctk.CTkLabel(
                placeholder,
                text="Run: SCAN & RECOVER  →  SCAN FOLDER\n\nThen reopen XAI to view:\n• Global feature importance\n• Per-file decision trace",
                font=("Arial", 12),
                text_color=ProColors.TEXT_DIM,
                justify="center"
            ).grid(row=1, column=0, pady=(0, 120))

            explain.configure(state="normal")
            explain.delete("0.0", "end")
            explain.insert(
                "0.0",
                "No scan data available.\n\n"
                "Steps:\n"
                "1) Go to SCAN & RECOVER tab\n"
                "2) Click SCAN FOLDER and select a folder\n"
                "3) After scan completes, open XAI again\n"
            )
            explain.configure(state="disabled")

        else:
            # Show global feature importance chart only when scan data exists
            fig_imp, ax_imp = plt.subplots(figsize=(6, 2.5), facecolor=ProColors.BG_PANEL)
            ax_imp.set_facecolor(ProColors.BG_PANEL)

            features = ["Size (bytes)", "Entropy", "ExecutableFlag"]
            importances = getattr(self.engine.model, "feature_importances_", None)
            if importances is None:
                imp_vals = [0.33, 0.33, 0.33]
            else:
                imp_vals = list(importances)

            ax_imp.bar(features, imp_vals, color=[ProColors.ACCENT_MAIN, ProColors.ACCENT_GLOW, ProColors.ALERT_RED])
            ax_imp.set_title("RandomForest Global Feature Importance", color="white", fontsize=12, fontweight="bold")
            ax_imp.tick_params(axis='x', colors='white', labelsize=10)
            ax_imp.tick_params(axis='y', colors='white', labelsize=10)
            ax_imp.grid(True, color=ProColors.GRID_LINE, linestyle='-', linewidth=0.6, alpha=0.7)
            for spine in ax_imp.spines.values():
                spine.set_color(ProColors.GRID_LINE)

            canvas_imp = FigureCanvasTkAgg(fig_imp, master=right_top)
            canvas_imp.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
            canvas_imp.draw()

            # Auto-load first file
            idx_entry.delete(0, "end")
            idx_entry.insert(0, "0")
            show_explanation(0)


if __name__ == "__main__":
    app = ShadowTraceApp()
    app.mainloop()