# melite-unity-nodes

Headless Unity inside ComfyUI graphs: the `MeliteUnityBatch` node
runs `unity -batchmode -quit -projectPath <project> -executeMethod
<Class.Method>` and returns the run log on its `log` output.

## Host requirement

This pack NEVER installs Unity. Resolve the binary as:

1. `MELITE_UNITY_BIN` / `UNITY_BIN` env (explicit path wins)
2. `PATH` lookup (`unity`)

Unresolvable = loud `RuntimeError` before any run starts.

## Node

`MeliteUnityBatch (command line)` (`Melite/Unity`):

- `project_path` — absolute Unity project directory (must exist)
- `execute_method` — `ClassName.MethodName` static method in the project
- `scene` (optional) — scene opened first via `-openScene`
- `extra_args` (optional) — JSON list of extra CLI args
- `timeout` (optional) — seconds before the run is killed (60–3600)

Every failure is loud: missing project, bad `extra_args` JSON,
timeout, and non-zero exit (Unity's stderr tail rides the message).
