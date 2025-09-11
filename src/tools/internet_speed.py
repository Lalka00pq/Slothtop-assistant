# 3rd party
import speedtest
from langchain.tools import tool


@tool
def test_internet_speed():
    """Test the internet speed using speedtest.net.

    Returns:
        dict: A dictionary containing download speed, upload speed, and ping.
    """
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
    except Exception as e:
        return {"error": f"Failed to connect to speedtest.net: {e}, please check your internet connection."}
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000      # Convert to Mbps
    ping = st.results.ping
    return {
        "download_speed (Mbps)": download_speed,
        "upload_speed (Mbps)": upload_speed,
        "ping (ms)": ping
    }
