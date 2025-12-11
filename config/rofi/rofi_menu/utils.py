import subprocess
from typing import Union, List


def run_cmd(cmd: Union[str, List[str]], timeout=None, background=False):
    """Run a command, return (stdout, stderr)."""
    if isinstance(cmd, str):
        cmd = cmd.split(" ")

    if background:
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.pid, ""

    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout or 10)
    return p.stdout.strip(), p.stderr.strip()


def get_process_elapsed_time(pid: int) -> int:
    uptime = run_cmd(["cat", "/proc/uptime"])[0].split(" ")[0]
    process_start = run_cmd(["cat", f"/proc/{pid}/stat"])[0].split(" ")[21]
    clock, _ = run_cmd(['getconf', 'CLK_TCK'])
    elapsed_ms = (float(uptime) - float(process_start) / float(clock)) * 1000

    return f"{elapsed_ms}"
