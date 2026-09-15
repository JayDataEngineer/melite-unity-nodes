"""melite-unity-nodes — headless Unity inside ComfyUI graphs.

Wraps `unity -batchmode` as a subprocess node: the MeliteUnityBatch
node runs a project static method (ClassName.MethodName) and returns
its log. Subprocess isolation (resilience law): the Unity editor
runs in a child process, never dlopened — a bad batch can only fail
the node.

LAW: this pack NEVER installs Unity. The binary is a HOST
REQUIREMENT (MELITE_UNITY_BIN / UNITY_BIN, else PATH); unresolvable
= loud refusal before any run starts.
"""
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
