import sys
import os
import importlib.util
import asyncio
from qasync import QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Software | Valentine x KadenDev Collaboration")
        self.resize(800, 600)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.load_plugins()

    def load_plugins(self):
        plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_path = os.path.join(plugins_dir, filename)
                plugin_name = os.path.splitext(filename)[0]
                widget, name = self.load_plugin(plugin_path, plugin_name)
                if widget and name:
                    self.tabs.addTab(widget, name)

    def load_plugin(self, path, module_name):
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error loading {module_name}: {e}")
            return None, None

        if hasattr(module, "get_widget") and hasattr(module, "get_name"):
            try:
                widget = module.get_widget()
                name = module.get_name()
                if isinstance(widget, QWidget) and isinstance(name, str):
                    return widget, name
            except Exception as e:
                print(f"Error initializing {module_name}: {e}")
        return None, None


async def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    await QEventLoop(app).run_forever()


if __name__ == "__main__":
    asyncio.run(main())
