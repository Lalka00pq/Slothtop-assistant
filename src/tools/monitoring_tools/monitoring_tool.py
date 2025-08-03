# python
import os
import signal
import threading
import time
from collections import deque
import multiprocessing
# 3rd party
import flet as ft
import psutil
from langchain.tools import tool


class CPUMonitor:
    """
    Class for monitoring CPU and memory usage.

    Attributes:
        cpu_history: deque of CPU usage history
        memory_history: deque of memory usage history
        is_monitoring: flag for monitoring status
    """

    def __init__(self):
        """
        Initializes the CPUMonitor class.
        """
        self.cpu_history = deque([0.0]*30, maxlen=30)
        self.memory_history = deque([0.0]*30, maxlen=30)
        self.is_monitoring = False
        self.monitoring_thread = None
        self.page = None
        self.cpu_chart = None
        self.memory_chart = None

    def start_monitoring(self):
        """Starts monitoring process"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stops monitoring process"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

        if self.page:
            self.page = None
            self.cpu_chart = None
            self.memory_chart = None

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            self.cpu_history.append(psutil.cpu_percent())
            self.memory_history.append(psutil.virtual_memory().percent)

            if self.page and self.cpu_chart and self.memory_chart:
                try:
                    self.cpu_chart.data_series[0].data_points = [
                        ft.LineChartDataPoint(x, y)
                        for x, y in enumerate(self.cpu_history)
                    ]
                    self.memory_chart.data_series[0].data_points = [
                        ft.LineChartDataPoint(x, y)
                        for x, y in enumerate(self.memory_history)
                    ]
                    self.page.update()
                except Exception:
                    pass

            time.sleep(1)

    def create_dashboard(self, page: ft.Page):
        """Creates dashboard with charts"""
        self.page = page
        page.title = "System Monitor"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20

        self.cpu_chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(x, y)
                        for x, y in enumerate(self.cpu_history)
                    ],
                    stroke_width=2,
                    color=ft.Colors.BLUE,
                    curved=True,
                ),
            ],
            border=ft.Border(
                top=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                bottom=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                left=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                right=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=10,
                color=ft.Colors.GREY_400,
                width=1,
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=5,
                color=ft.Colors.GREY_400,
                width=1,
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=x,
                        label=ft.Text(f"{x}%"),
                    )
                    for x in range(0, 101, 20)
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=x,
                        label=ft.Text(f"{x}s"),
                    )
                    for x in range(0, 31, 5)
                ],
                labels_size=40,
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            min_y=0,
            max_y=100,
            min_x=0,
            max_x=30,
            expand=True,
        )

        # Memory график
        self.memory_chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(x, y)
                        for x, y in enumerate(self.memory_history)
                    ],
                    stroke_width=2,
                    color=ft.Colors.GREEN,
                    curved=True,
                ),
            ],
            border=ft.Border(
                top=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                bottom=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                left=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                right=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=10,
                color=ft.Colors.GREY_400,
                width=1,
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=5,
                color=ft.Colors.GREY_400,
                width=1,
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=x,
                        label=ft.Text(f"{x}%"),
                    )
                    for x in range(0, 101, 20)
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=x,
                        label=ft.Text(f"{x}s"),
                    )
                    for x in range(0, 31, 5)
                ],
                labels_size=40,
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            min_y=0,
            max_y=100,
            min_x=0,
            max_x=30,
            expand=True,
        )

        page.add(
            ft.Text("CPU Usage", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.cpu_chart,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=10,
                padding=10,
                margin=ft.margin.only(bottom=20),
                height=300,
            ),
            ft.Text("Memory Usage", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.memory_chart,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=10,
                padding=10,
                height=300,
            ),
        )


cpu_monitor = CPUMonitor()


def run_flet_dashboard(page: ft.Page):
    """Function to run Flet dashboard."""
    def on_window_close(e):
        cpu_monitor.stop_monitoring()
        page.window_destroy()

    page.on_close = on_window_close
    cpu_monitor.create_dashboard(page)
    cpu_monitor.start_monitoring()


def run_flet_app_process():
    """Function to run Flet application in a separate process."""
    try:
        ft.app(target=run_flet_dashboard, view=ft.AppView.FLET_APP)
    finally:
        cpu_monitor.stop_monitoring()


monitoring_process = None


@tool
def start_monitoring_tool() -> str:
    """Tool to start system resource monitoring.

    Returns:
        str: Message indicating the status of the operation
    """
    global monitoring_process

    if monitoring_process and monitoring_process.is_alive():
        return "Monitoring is already running."

    monitoring_process = multiprocessing.Process(target=run_flet_app_process)
    monitoring_process.daemon = True
    monitoring_process.start()

    return "System monitoring started. Charts are updated in real time in a separate window."


@tool
def stop_monitoring_tool() -> str:
    """Tool to stop system resource monitoring.

    Returns:
        str: Message indicating the status of the operation
    """
    global monitoring_process
    try:
        cpu_monitor.stop_monitoring()

        def kill_process(process):
            """Helper function to kill a process"""
            if process and process.is_alive():
                process.terminate()
                process.join(timeout=1)

        if monitoring_process:
            kill_process(monitoring_process)
            monitoring_process = None

        for process in multiprocessing.active_children():
            kill_process(process)

        cpu_monitor.page = None
        cpu_monitor.cpu_chart = None
        cpu_monitor.memory_chart = None

        return "System monitoring stopped and window closed."
    except Exception as e:
        try:
            if monitoring_process and monitoring_process.pid:
                os.kill(monitoring_process.pid, signal.SIGTERM)
        except Exception:
            pass
        return f"Error while stopping monitoring: {str(e)}"
