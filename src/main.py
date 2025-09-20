import os
import sys
from PyQt5.QtWidgets import QApplication
from gui.app_window import AppWindow

def main():
    # Ensure working dir is repo root so relative 'scripts' path works
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)

    app = QApplication(sys.argv)
    window = AppWindow(scripts_dir=os.path.join(repo_root, "scripts"))
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
