"""Shared headless-Unity plumbing: resolve the binary, run batchmode.

LAW: this pack NEVER installs Unity — no downloads, no Hub
automation, no bundled binary. (The binary is a HOST REQUIREMENT
resolved as:

  1. MELITE_UNITY_BIN / UNITY_BIN env (explicit path wins)
  2. PATH lookup (shutil.which("unity"))

Unresolvable = loud RuntimeError naming the env vars and the binary.
The contract mirrors melite-blender-proxy-nodes' proxy.py so the
estate compose gate and the node name the same need, one queue slot
apart.
"""

from __future__ import annotations

import os
import shutil
import subprocess

ENV_VARS = ("MELITE_UNITY_BIN", "UNITY_BIN")
BINARY = "unity"


def resolve_unity_binary() -> str:
    """Return the Unity executable path, or raise loudly."""
    for var in ENV_VARS:
        candidate = os.environ.get(var)
        if candidate:
            if os.path.isfile(candidate):
                return candidate
            raise RuntimeError(
                "MeliteUnityProxy: %s points at %r, which is not a "
                "file — fix the env var or unset it" % (var, candidate))
    discovered = shutil.which(BINARY)
    if discovered:
        return discovered
    raise RuntimeError(
        "MeliteUnityProxy: Unity binary not found. Install Unity "
        "and put it on PATH, or set %s to the executable."
        % " or ".join(ENV_VARS))


def run_unity_batch(project_path: str, execute_method: str, scene: str = "",
                    args: tuple[str, ...] = (),
                    timeout: int = 600) -> str:
    """Run a Unity static method headless; return combined stdout.

    Raises FileNotFoundError for a missing project dir (caller bug —
    fix the caller) and RuntimeError for a failed run (Unity's
    stderr tail rides the message so the queue ledger names the
    cause).
    """
    if not os.path.isdir(project_path):
        raise FileNotFoundError(
            "MeliteUnityProxy: project not found: %s" % project_path)
    if not execute_method or not execute_method.strip():
        raise ValueError(
            "MeliteUnityProxy: execute_method is required "
            "(ClassName.MethodName in the project).")
    binary = resolve_unity_binary()
    cmd = [binary, "-batchmode", "-quit",
           "-projectPath", project_path,
           "-executeMethod", execute_method.strip()]
    if scene and scene.strip():
        cmd += ["-openScene", scene.strip()]
    cmd += [str(a) for a in args]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "MeliteUnityProxy: unity -batchmode timed out after %ds "
            "(method %s)" % (timeout, execute_method)) from exc
    if proc.returncode != 0:
        raise RuntimeError(
            "MeliteUnityProxy: unity -batchmode failed (rc=%d, method "
            "%s):\n%s"
            % (proc.returncode, execute_method,
               (proc.stderr or proc.stdout or "")[-2000:]))
    return proc.stdout or ""
