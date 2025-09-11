# python
import time
from collections import deque
import threading
from abc import ABC, abstractmethod
from typing import List
# 3rd party
import flet as ft  # type: ignore


class Monitor(ABC):
    """
    Base abstract class for all monitors.

    Attributes:
        is_monitoring: flag for monitoring status
        monitoring_thread: monitoring thread
        page: Flet page
        charts: list of charts
        histories: list of histories of values for each graph
    """

    def __init__(self, chart_names: List[str], colors: List[str]):
        """
        Initializes the Monitor class.

        Args:
            chart_names: list of chart names
            colors: list of colors for each graph
        """
        if len(chart_names) != len(colors):
            raise ValueError(
                "The number of chart names must match the number of colors")

        self.is_monitoring = False
        self.monitoring_thread = None
        self.page = None
        self.charts = []
        self.histories = [deque([0.0]*30, maxlen=30) for _ in chart_names]
        self.chart_names = chart_names
        self.colors = colors

    def start_monitoring(self):
        """Starts the monitoring process"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stops the monitoring process"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

        if self.page:
            self.page = None
            self.charts = []

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            values = self._get_monitor_values()
            for history, value in zip(self.histories, values):
                history.append(value)

            if self.page and self.charts:
                try:
                    for chart, history in zip(self.charts, self.histories):
                        chart.data_series[0].data_points = [
                            ft.LineChartDataPoint(x, y)
                            for x, y in enumerate(history)
                        ]
                    self.page.update()
                except Exception:
                    pass

            time.sleep(1)

    def create_dashboard(self, page: ft.Page):
        """Creates a dashboard with graphs"""
        self.page = page
        page.title = "System Monitor"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20

        for name, color, history in zip(self.chart_names, self.colors, self.histories):
            chart = self._create_chart(history, color)
            self.charts.append(chart)

            page.add(
                ft.Text(name, size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=chart,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=10,
                    padding=10,
                    margin=ft.margin.only(bottom=20),
                    height=300,
                )
            )

    def _create_chart(self, history: deque, color: str) -> ft.LineChart:
        """Creates a graph with given parameters"""
        return ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(x, y)
                        for x, y in enumerate(history)
                    ],
                    stroke_width=2,
                    color=color,
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

    @abstractmethod
    def _get_monitor_values(self) -> List[float]:
        """
        Abstract method for getting values for monitoring.
        Must return a list of values for each graph.
        """
        pass
