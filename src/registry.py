from .panels import MainPanel, TestPanel


class PanelRegistry:
    def __init__(self) -> None:
        MainPanel().registry()
        TestPanel().registry()
