"""Melite Unity batch node: ComfyUI graphs drive headless Unity.

The estate owns no Unity subprocess — graphs call THIS node, and
this node shells `unity -batchmode` (proxy.run_unity_batch). Unity
is a host requirement (env MELITE_UNITY_BIN / UNITY_BIN, else
PATH); unresolvable = loud refusal before any run starts.

Only stdlib imports at module scope. folder_paths (ComfyUI core)
is imported lazily inside the methods that need it, so the module
stays importable off-server.
"""

from __future__ import annotations

import json

from .proxy import run_unity_batch


class MeliteUnityBatch:
    """Run a Unity Editor static method headless. The command-line
    card: the project path + ClassName.MethodName ride the graph,
    Unity -batchmode executes it, the log rides the output."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Absolute path to the Unity project "
                                   "directory (contains Assets/).",
                    },
                ),
                "execute_method": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Static method to run "
                                   "(ClassName.MethodName in the project).",
                    },
                ),
            },
            "optional": {
                "scene": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Scene to open first (-openScene; "
                                   "empty = the project's default).",
                    },
                ),
                "extra_args": (
                    "STRING",
                    {
                        "default": "[]",
                        "multiline": True,
                        "tooltip": "JSON list of extra CLI args appended "
                                   "after the method (e.g. -nographics).",
                    },
                ),
                "timeout": (
                    "INT",
                    {
                        "default": 600, "min": 60, "max": 3600, "step": 60,
                        "tooltip": "Seconds before the headless run is killed.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("log",)
    FUNCTION = "run"
    CATEGORY = "Melite/Unity"

    def run(self, project_path, execute_method,
            scene="", extra_args="[]", timeout=600):
        try:
            args = json.loads(extra_args) if extra_args.strip() else []
        except json.JSONDecodeError as exc:
            raise ValueError(
                "MeliteUnityBatch: extra_args is not a JSON list: %s"
                % (exc,)) from exc
        if not isinstance(args, list):
            raise ValueError(
                "MeliteUnityBatch: extra_args must be a JSON list, "
                "got %s" % (type(args).__name__,))
        log = run_unity_batch(
            project_path, execute_method,
            scene=scene if isinstance(scene, str) else "",
            args=tuple(str(a) for a in args),
            timeout=int(timeout),
        )
        return (log,)


NODE_CLASS_MAPPINGS = {
    "MeliteUnityBatch": MeliteUnityBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MeliteUnityBatch": "Unity Batch (command line)",
}
