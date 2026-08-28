from __future__ import annotations

import sys
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFileDialog, QGridLayout, QGroupBox, QLabel, QMainWindow, QMessageBox, QPushButton, QComboBox, QProgressBar, QTextEdit, QVBoxLayout, QWidget
from .application.analysis import AnalysisCancelled, AnalysisEngine
from .storage.repository import LocalRepository

class Worker(QObject):
    progress=Signal(float); finished=Signal(dict); failed=Signal(str)
    def __init__(self, path, profile, provider): super().__init__(); self.path=path; self.profile=profile; self.provider=provider; self.stop=False
    def run(self):
        try: self.finished.emit(AnalysisEngine().analyze(self.path, profile=self.profile, provider=self.provider, progress=lambda f,*_: self.progress.emit(f), cancelled=lambda: self.stop))
        except Exception as e: self.failed.emit(str(e))
    def cancel(self): self.stop=True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.repo=LocalRepository(); self.input_path=None; self.job_id=None; self.setAcceptDrops(True); self.setWindowTitle("Heiba AI Analysis"); self.resize(1180,760); self.dark(); self.build_ui()
    def dark(self): self.setStyleSheet("QMainWindow,QWidget{background:#101820;color:#e8edf2;font-family:Segoe UI} QGroupBox{border:1px solid #2e4251;border-radius:8px;margin-top:10px;padding:12px;font-weight:600} QPushButton{background:#1e8b74;color:white;border:0;border-radius:5px;padding:9px 16px} QPushButton:hover{background:#27a889} QComboBox,QTextEdit{background:#172630;border:1px solid #344d5b;border-radius:4px;padding:6px;color:#e8edf2} QProgressBar{border:1px solid #344d5b;border-radius:4px;text-align:center} QProgressBar::chunk{background:#1e8b74}")
    def build_ui(self):
        root=QWidget(); self.setCentralWidget(root); layout=QVBoxLayout(root)
        top=QGridLayout(); title=QLabel("HEIBA AI ANALYSIS"); title.setStyleSheet("font-size:24px;font-weight:bold;color:#6ee7c8"); top.addWidget(title,0,0,1,2); top.addWidget(QLabel("Research & Development Only"),1,0); self.lang=QPushButton("العربية / EN"); self.lang.clicked.connect(self.toggle_language); top.addWidget(self.lang,0,2); layout.addLayout(top)
        grid=QGridLayout(); left=QVBoxLayout(); right=QVBoxLayout()
        imp=QGroupBox("Import / استيراد"); il=QVBoxLayout(imp); self.file_label=QLabel("Drag & drop MP4, MOV, MKV, AVI, WebM here"); self.file_label.setMinimumHeight(80); self.file_label.setAlignment(Qt.AlignCenter); il.addWidget(self.file_label); choose=QPushButton("Choose video"); choose.clicked.connect(self.choose); il.addWidget(choose); left.addWidget(imp)
        prof=QGroupBox("Profiles"); pl=QGridLayout(prof); pl.addWidget(QLabel("Profile"),0,0); self.profile=QComboBox(); self.profile.addItems(["balanced","fast","high_accuracy","moving_camera","low_light"]); pl.addWidget(self.profile,0,1); pl.addWidget(QLabel("Provider"),1,0); self.provider=QComboBox(); self.provider.addItems(["auto","cpu","cuda","tensorrt","openvino","windowsml"]); pl.addWidget(self.provider,1,1); left.addWidget(prof)
        self.start=QPushButton("Start analysis"); self.start.clicked.connect(self.start_analysis); self.cancel=QPushButton("Cancel"); self.cancel.clicked.connect(self.cancel_analysis); self.cancel.setEnabled(False); left.addWidget(self.start); left.addWidget(self.cancel)
        diag=QGroupBox("Diagnostics"); dl=QVBoxLayout(diag); self.diag=QLabel("Provider: auto\nModel: unverified test backend\nCPU fallback: available"); dl.addWidget(self.diag); left.addWidget(diag); left.addStretch()
        out=QGroupBox("Live Analysis / Decision"); ol=QVBoxLayout(out); self.status=QLabel("No analysis loaded. Real detections and tracks appear here."); self.status.setMinimumHeight(250); ol.addWidget(self.status); self.progress=QProgressBar(); ol.addWidget(self.progress); self.log=QTextEdit(); self.log.setReadOnly(True); ol.addWidget(self.log); buttons=QGridLayout(); c=QPushButton("Correct"); c.clicked.connect(lambda: self.feedback("Correct")); ic=QPushButton("Incorrect"); ic.clicked.connect(lambda: self.feedback("Incorrect")); ex=QPushButton("Open export folder"); ex.clicked.connect(self.open_export); buttons.addWidget(c,0,0); buttons.addWidget(ic,0,1); buttons.addWidget(ex,0,2); ol.addLayout(buttons); right.addWidget(out)
        grid.addLayout(left,0,0); grid.addLayout(right,0,1); layout.addLayout(grid)
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dropEvent(self,e): self.set_input(Path(e.mimeData().urls()[0].toLocalFile()))
    def choose(self):
        p,_=QFileDialog.getOpenFileName(self,"Select video","","Video (*.mp4 *.mov *.mkv *.avi *.webm)");
        if p: self.set_input(Path(p))
    def set_input(self,p): self.input_path=p; self.file_label.setText(str(p));
    def start_analysis(self):
        if not self.input_path: QMessageBox.warning(self,"Input","Select a video first / اختر فيديو أولًا"); return
        self.thread=QThread(); self.worker=Worker(self.input_path,self.profile.currentText(),self.provider.currentText()); self.worker.moveToThread(self.thread); self.thread.started.connect(self.worker.run); self.worker.progress.connect(self.progress.setValue); self.worker.finished.connect(self.done); self.worker.failed.connect(self.failed); self.thread.start(); self.start.setEnabled(False); self.cancel.setEnabled(True)
    def cancel_analysis(self): self.worker.cancel(); self.status.setText("Cancellation requested / تم طلب الإلغاء")
    def done(self,r): self.job_id=r["job_id"]; self.status.setText("NO_DECISION — Needs human review\n"+r["decision"]["reason"]); self.log.setPlainText(str(r["paths"])); self.diag.setText(f"Provider: {r['provider']['name']}\nModel: {r['model']['name']}\nTracker: {r['tracker']}\nFrames: {r['metadata']['frame_count']}"); self.cleanup()
    def failed(self,e): QMessageBox.critical(self,"Analysis error",e); self.cleanup()
    def cleanup(self): self.start.setEnabled(True); self.cancel.setEnabled(False); self.thread.quit(); self.thread.wait()
    def feedback(self,label):
        if not self.job_id: return
        self.repo.save_feedback(self.job_id,label,"",self.input_path); self.log.append(f"Feedback saved locally: {label}")
    def open_export(self):
        if self.job_id: QFileDialog.getExistingDirectory(self,"Export folder",str(self.repo.exports/self.job_id))
    def toggle_language(self):
        rtl=self.layoutDirection()!=Qt.RightToLeft; self.setLayoutDirection(Qt.RightToLeft if rtl else Qt.LeftToRight); self.lang.setText("EN / العربية" if rtl else "العربية / EN"); self.repo.set_setting("language","ar" if rtl else "en")

def main():
    app=QApplication(sys.argv); w=MainWindow(); w.show(); return app.exec()

if __name__ == "__main__": raise SystemExit(main())
