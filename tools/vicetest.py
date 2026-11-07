#!/usr/bin/env python3
# Original code by Konstantinos Patronas, used under the MIT licence below.
# Adapted for general use in c64home: project-specific parts (login, shell
# prompt, kernel variables) removed; prompt, REU size and hang-dump labels
# made parameters.
#
# MIT License
#
# Copyright (c) 2026 Konstantinos Patronas <kpatronas@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Drive VICE (x64sc) through its remote monitor for automated tests.

    with Vice("build/hello_basic.prg") as v:
        v.wait_for("ready.")
        print(v.run("print 2+2"))       # -> " 4"
        print(v.screen())

Environment: X64SC (path to x64sc), VICEFLAGS (extra flags, e.g. -ntsc),
VT_WINDOW=1 (show VICE's window), VT_KEEP=1 (keep scratch files),
VT_HANGDUMP=file (on a timeout, append CPU state and the screen to file).
"""
import atexit
import os
import re
import socket
import subprocess
import tempfile
import time

X64 = os.environ.get("X64SC", "x64sc")


def scratch_file(path):
    """Delete this run's scratch file (e.g. a disk image copy) when the test
    process exits. VT_KEEP=1 keeps them, to look at after a failure."""
    if not os.environ.get("VT_KEEP"):
        atexit.register(lambda: os.path.exists(path) and os.remove(path))
    return path


def screen_to_text(codes):
    out = []
    for c in codes:
        c &= 0x7f
        if c == 0:
            out.append("@")
        elif 1 <= c <= 26:
            out.append(chr(ord("a") + c - 1))
        elif c == 27:
            out.append("[")
        elif c == 28:
            out.append("\\")
        elif c == 29:
            out.append("]")
        elif c == 30:
            out.append("^")
        elif c == 31:
            out.append("<")
        elif 32 <= c <= 63:
            out.append(chr(c))
        elif 65 <= c <= 90:
            out.append(chr(c))
        elif c == 0x5d:
            out.append("|")
        elif c == 0x64:
            out.append("_")
        else:
            out.append("?")
    return "".join(out)


def free_port():
    """A TCP port nothing listens on now. (A port made from the pid could
    collide when several VICEs run side by side.)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Vice:
    """prompt: regex for a screen row that is the program's prompt, used by
    run(). The default fits BASIC's "ready."; a shell might use r"^\\S+ \\$$".
    labels: an ld65 label file (-Ln) to name addresses in a hang dump."""

    def __init__(self, image, reu=None, port=None, warp=True, extra=(),
                 prompt=r"^ready\.$", labels=None):
        self.image = image
        self.prompt = re.compile(prompt)
        self.labels = labels
        self.port = port or free_port()
        args = [X64, "-default", "+sound", "-minimized",
                "-remotemonitor", "-remotemonitoraddress", f"ip4://127.0.0.1:{self.port}"]
        if not os.environ.get("VT_WINDOW"):   # VT_WINDOW=1: show VICE's window
            args.append("-console")
        if warp:
            args.append("-warp")
        if reu:
            args += ["-reu", "-reusize", str(reu)]   # KB: 128, 256, 512, 1024, ...
        args += list(extra)
        args += os.environ.get("VICEFLAGS", "").split()   # e.g. -ntsc
        args += ["-autostart", image]
        self.log = tempfile.NamedTemporaryFile(prefix="vice", suffix=".log", delete=False)
        self.proc = subprocess.Popen(args, stdout=self.log, stderr=subprocess.STDOUT)
        # a setUpClass that fails skips tearDownClass: don't leave VICE running
        atexit.register(self._reap)
        self.sock = None
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                self.sock = socket.create_connection(("127.0.0.1", self.port), timeout=2)
                break
            except OSError:
                time.sleep(0.3)
        if not self.sock:
            self._reap()
            raise RuntimeError("could not connect to VICE monitor")
        self._cmd("x")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def close(self):
        try:
            self.sock.sendall(b"quit\n")
            time.sleep(0.3)
            self.sock.close()
        except OSError:
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()

    def _reap(self):
        if self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()

    def _cmd(self, c, wait=0.15):
        """Send a monitor command and return its output. Every command stops
        emulation until "x" is sent."""
        self.sock.sendall((c + "\n").encode())
        time.sleep(wait)
        self.sock.settimeout(0.4)
        out = b""
        try:
            while True:
                d = self.sock.recv(65536)
                if not d:
                    break
                out += d
        except socket.timeout:
            pass
        return out.decode(errors="replace")

    def mem(self, start, end):
        """Read memory through the monitor's save command (retries while
        VICE is still starting up)."""
        for attempt in range(5):
            fd, path = tempfile.mkstemp(suffix=".bin")
            os.close(fd)
            os.unlink(path)
            self._cmd(f'save "{path}" 0 {start:04x} {end:04x}', wait=0.2)
            self._cmd("x")
            for _ in range(50):
                if os.path.exists(path) and os.path.getsize(path) >= end - start + 3:
                    break
                time.sleep(0.05)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = f.read()[2:]
                os.unlink(path)
                return list(data[:end - start + 1])
            time.sleep(1)
        raise RuntimeError("VICE monitor did not save memory")

    def screen_lines(self):
        codes = self.mem(0x0400, 0x07e7)
        text = screen_to_text(codes)
        return [text[i:i + 40].rstrip() for i in range(0, len(text), 40)]

    def screen(self):
        return "\n".join(self.screen_lines())

    def type(self, text):
        """Type text through the KERNAL keyboard buffer; '\\n' is RETURN.
        Fed in small pieces so the 10-key buffer never overflows. A program
        that scans the keyboard matrix itself won't see these keys."""
        for chunk in re.findall(r"[^\n]{1,8}|\n", text):
            if chunk == "\n":
                esc = "\\x0d"
            else:
                esc = chunk.replace("\\", "\\\\").replace(" ", "\\x20")
            self._cmd("keybuf " + esc)
            self._cmd("x", wait=0.25)

    def wait_for(self, text, timeout=60, after=None):
        """Wait until `text` is on screen (below the last `after`, if given);
        return the screen."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            s = self.screen()
            if text in s if after is None else text in s.split(after)[-1]:
                return s
            time.sleep(0.5)
        self._on_timeout()
        raise TimeoutError(f"{text!r} not on screen:\n{self.screen()}")

    def run(self, command, timeout=90):
        """Type a command line and return its output: the rows between the
        last row ending in the command and the next prompt row. Prompt and
        command must fit on one 40-column row, or the wrapped command is
        never found and this times out although the command ran."""
        self.type(command + "\n")
        want = command.strip()
        result = []

        def done(lines):
            idx = None
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].endswith(want):
                    idx = i
                    break
            if idx is None:
                return False
            for j in range(idx + 1, len(lines)):
                if self.prompt.match(lines[j]):
                    result[:] = lines[idx + 1:j]
                    return True
            return False
        self._wait(done, timeout, what=command)
        return "\n".join(result)

    def _wait(self, pred, timeout, what="condition"):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if pred(self.screen_lines()):
                return
            time.sleep(0.4)
        self._on_timeout()
        raise TimeoutError(f"timeout waiting for {what}:\n{self.screen()}")

    def _on_timeout(self):
        """With VT_HANGDUMP=file set, append the C64's registers and recent
        instructions (named from the label file, if given), drive 8's
        registers, history and command buffer, and the screen."""
        path = os.environ.get("VT_HANGDUMP")
        if not path:
            return
        by_addr = []
        if self.labels:
            with open(self.labels) as f:
                for line in f:          # ld65 -Ln: "al 00c010 .name"
                    parts = line.split()
                    if len(parts) >= 3:
                        by_addr.append((int(parts[1], 16), parts[2].lstrip(".")))
            by_addr.sort()

        def where(addr):
            best = None
            for a, n in by_addr:
                if a > addr:
                    break
                best = "%s+%d" % (n, addr - a)
            return best or ""

        out = ["== HANGDUMP (monitor port %d)" % self.port, self._cmd("r", wait=0.5)]
        for line in self._cmd("chis 60", wait=1.0).splitlines()[-60:]:
            m = re.match(r"\.?C:([0-9a-f]{4})", line.strip(), re.I)
            out.append(line + ("   " + where(int(m.group(1), 16)) if m else ""))
        out.append("== drive 8")
        self._cmd("device 8:", wait=0.5)
        out += [self._cmd("r", wait=0.5), self._cmd("chis 40", wait=1.0),
                self._cmd("m 0200 0230", wait=0.5)]
        self._cmd("device c:", wait=0.5)
        self._cmd("x")
        out.append("== screen\n" + self.screen())
        with open(path, "a") as f:
            f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        sys.exit("usage: vicetest.py IMAGE [SECONDS]  (prints the screen after SECONDS)")
    with Vice(sys.argv[1]) as v:
        time.sleep(float(sys.argv[2]) if len(sys.argv) > 2 else 5)
        print(v.screen())
