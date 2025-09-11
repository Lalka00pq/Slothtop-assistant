# python
import os
import signal
import multiprocessing
from typing import List
# 3rd party
import flet as ft  # type: ignore
import psutil
from langchain.tools import tool  # type: ignore
from src.tools.computer_state_tools.monitoring_tools.monitoring_class import Monitor
import GPUtil  # type: ignore


class CPUMonitor(Monitor):
    """
    Class for monitoring CPU and memory usage.
    """

    def __init__(self):
        """
        Initializes the CPUMonitor class.
        """
        super().__init__(
            chart_names=["CPU Usage", "Memory Usage"],
            colors=[ft.Colors.BLUE, ft.Colors.GREEN]
        )

    def _get_monitor_values(self) -> List[float]:
        """
        Gets the current values of CPU and memory.

        Returns:
            List[float]: List of values [cpu_percent, memory_percent]
        """
        return [
            psutil.cpu_percent(),
            psutil.virtual_memory().percent
        ]


class GPUMonitor(Monitor):
    def __init__(self):
        super().__init__(
            chart_names=["GPU Usage", "GPU Temperature"],
            colors=[ft.Colors.GREEN, ft.Colors.RED]
        )

    def _get_monitor_values(self) -> List[float]:
        """
        Gets the current values of GPU.

        Returns:
            List[float]: List of values [gpu_percent, gpu_temperature]
        """
        try:
            gpu_usage = GPUtil.getGPUs()
            return [
                gpu_usage[0].load * 100,
                gpu_usage[0].temperature,
            ]
        except Exception as e:
            raise Exception(
                f"Error getting GPU usage: {e}, do you have a GPU?")


cpu_monitor = CPUMonitor()
gpu_monitor = GPUMonitor()

# TODO Change methods for monitoring cpu and gpu (combine into one)


def run_flet_dashboard_cpu(page: ft.Page):
    """Function to run Flet dashboard."""
    def on_window_close(e):
        cpu_monitor.stop_monitoring()

    page.on_close = on_window_close
    cpu_monitor.create_dashboard(page)
    cpu_monitor.start_monitoring()


def run_flet_dashboard_gpu(page: ft.Page):

    def on_window_close(e):
        gpu_monitor.stop_monitoring()

    page.on_close = on_window_close
    gpu_monitor.create_dashboard(page)
    gpu_monitor.start_monitoring()


def run_flet_app_process_cpu():
    """Function to run Flet application in a separate process."""
    try:
        ft.app(target=run_flet_dashboard_cpu, view=ft.AppView.FLET_APP)
    finally:
        cpu_monitor.stop_monitoring()


def run_flet_app_process_gpu():

    try:
        ft.app(target=run_flet_dashboard_gpu, view=ft.AppView.FLET_APP)
    finally:
        gpu_monitor.stop_monitoring()


monitoring_process_cpu = None
monitoring_process_gpu = None


@tool
def start_monitoring_cpu_tool() -> str:
    """Tool to start system resource monitoring.

    Returns:
        str: Message indicating the status of the operation
    """
    global monitoring_process_cpu

    if monitoring_process_cpu and monitoring_process_cpu.is_alive():
        return "Monitoring is already running."

    monitoring_process_cpu = multiprocessing.Process(
        target=run_flet_app_process_cpu)
    monitoring_process_cpu.daemon = True
    monitoring_process_cpu.start()

    return "System monitoring started. Charts are updated in real time in a separate window."


@tool
def stop_monitoring_cpu_tool() -> str:
    """Tool to stop system resource monitoring.

    Returns:
        str: Message indicating the status of the operation
    """
    global monitoring_process_cpu
    try:
        cpu_monitor.stop_monitoring()

        def kill_process(process):
            """Helper function to kill a process"""
            if process and process.is_alive():
                process.terminate()
                process.join(timeout=1)

        if monitoring_process_cpu:
            kill_process(monitoring_process_cpu)
            monitoring_process_cpu = None

        for process in multiprocessing.active_children():
            kill_process(process)

        return "System monitoring stopped and window closed."
    except Exception as e:
        try:
            if monitoring_process_cpu and monitoring_process_cpu.pid:
                os.kill(monitoring_process_cpu.pid, signal.SIGTERM)
        except Exception:
            pass
        return f"Error while stopping monitoring: {str(e)}"


@tool
def start_monitoring_gpu_tool() -> str:
    """Tool to start GPU monitoring.

    Returns:
        str: Message indicating the status of the operation
    """
    global monitoring_process_gpu

    if monitoring_process_gpu and monitoring_process_gpu.is_alive():
        return "Monitoring is already running."

    monitoring_process_gpu = multiprocessing.Process(
        target=run_flet_app_process_gpu)
    monitoring_process_gpu.daemon = True
    monitoring_process_gpu.start()

    return "GPU monitoring started. Charts are updated in real time in a separate window."


@tool
def stop_monitoring_gpu_tool() -> str:
    """Tool to stop GPU monitoring.

    Returns:
        str: Message indicating the status of the operation
    """
    global monitoring_process_gpu
    try:
        gpu_monitor.stop_monitoring()

        def kill_process(process):
            """Helper function to kill a process"""
            if process and process.is_alive():
                process.terminate()
                process.join(timeout=1)

        if monitoring_process_gpu:
            kill_process(monitoring_process_gpu)
            monitoring_process_gpu = None

        for process in multiprocessing.active_children():
            kill_process(process)

        return "System monitoring stopped and window closed."
    except Exception as e:
        try:
            if monitoring_process_gpu and monitoring_process_gpu.pid:
                os.kill(monitoring_process_gpu.pid, signal.SIGTERM)
        except Exception:
            pass
        return f"Error while stopping monitoring: {str(e)}"
