from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class ThemeManager:
    @staticmethod
    def get_theme(theme_name="dark"):
        """Get theme palette"""
        if theme_name == "dark":
            return ThemeManager._get_dark_theme()
        else:
            return ThemeManager._get_light_theme()
            
    @staticmethod
    def _get_dark_theme():
        """Get dark theme palette"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(40, 40, 40))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor("#2ecc71"))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        return palette
        
    @staticmethod
    def _get_light_theme():
        """Get light theme palette"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(233, 233, 233))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor("#2ecc71"))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        return palette
