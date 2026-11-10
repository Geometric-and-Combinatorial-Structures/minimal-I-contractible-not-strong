"""Run a subprocess with a deadline and preserve output on timeout."""
import os
import signal
import subprocess


def _stop(proc):
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except ProcessLookupError:
        pass


def _drain(proc):
    try:
        return proc.communicate(timeout=2)
    except subprocess.TimeoutExpired as error:
        # A detached descendant may still hold a pipe after the direct child
        # and its process group have stopped. Do not wait for that descendant.
        for stream in (proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()
        proc.wait(timeout=2)
        return error.stdout, error.stderr


def run_process(command, *, timeout=None, capture_output=False, input=None, check=False, **kwargs):
    if capture_output:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    if input is not None:
        kwargs["stdin"] = subprocess.PIPE
    with subprocess.Popen(command, start_new_session=(os.name == "posix"), **kwargs) as proc:
        try:
            stdout, stderr = proc.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            _stop(proc)
            stdout, stderr = _drain(proc)
            if proc.text_mode:
                stdout = stdout.decode(proc.encoding or "utf-8", proc.errors or "strict") if isinstance(stdout, bytes) else stdout
                stderr = stderr.decode(proc.encoding or "utf-8", proc.errors or "strict") if isinstance(stderr, bytes) else stderr
            raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr) from error
        except BaseException:
            _stop(proc)
            _drain(proc)
            raise
    result = subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)
    if check:
        result.check_returncode()
    return result
