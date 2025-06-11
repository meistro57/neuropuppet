from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from flask import Flask, redirect, render_template_string, request, url_for

from core.utils import load_config

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"

app = Flask(__name__)


HTML_TEMPLATE = """
<!doctype html>
<title>Neuropuppet Config</title>
<h1>Marionette Configuration</h1>
<form method="post">
  <fieldset>
    <legend>Serial</legend>
    Port: <input type="text" name="serial_port" value="{{serial.port}}"><br>
    Baudrate: <input type="number" name="serial_baudrate" value="{{serial.baudrate}}"><br>
    Timeout: <input type="number" step="0.1" name="serial_timeout" value="{{serial.timeout}}"><br>
  </fieldset>
  <fieldset>
    <legend>RL</legend>
    Timesteps: <input type="number" name="rl_total_timesteps" value="{{rl.total_timesteps}}"><br>
    Learning rate: <input type="text" name="rl_learning_rate" value="{{rl.learning_rate}}"><br>
    Device: <input type="text" name="rl_device" value="{{rl.device}}"><br>
  </fieldset>
  <fieldset>
    <legend>Vision</legend>
    Camera index: <input type="number" name="vision_camera_index" value="{{vision.camera_index}}"><br>
    Use MediaPipe: <input type="checkbox" name="vision_use_mediapipe" {% if vision.use_mediapipe %}checked{% endif %}><br>
  </fieldset>
  <input type="submit" value="Save">
</form>
"""


def load_current_config() -> Dict[str, Any]:
    return load_config(CONFIG_PATH)


def update_config(data: Dict[str, Any]) -> None:
    cfg = load_current_config()
    cfg.setdefault("serial", {})
    cfg.setdefault("rl", {})
    cfg.setdefault("vision", {})

    cfg["serial"]["port"] = data.get("serial_port", cfg["serial"].get("port"))
    cfg["serial"]["baudrate"] = int(data.get("serial_baudrate", cfg["serial"].get("baudrate", 115200)))
    cfg["serial"]["timeout"] = float(data.get("serial_timeout", cfg["serial"].get("timeout", 1.0)))

    cfg["rl"]["total_timesteps"] = int(data.get("rl_total_timesteps", cfg["rl"].get("total_timesteps", 10000)))
    cfg["rl"]["learning_rate"] = float(data.get("rl_learning_rate", cfg["rl"].get("learning_rate", 0.0003)))
    cfg["rl"]["device"] = data.get("rl_device", cfg["rl"].get("device", "cpu"))

    cfg["vision"]["camera_index"] = int(data.get("vision_camera_index", cfg["vision"].get("camera_index", 0)))
    cfg["vision"]["use_mediapipe"] = "vision_use_mediapipe" in data

    CONFIG_PATH.write_text(yaml_dump(cfg))


def yaml_dump(cfg: Dict[str, Any]) -> str:
    import yaml  # local import to avoid dependency if not using web app
    return yaml.dump(cfg, sort_keys=False)


@app.route("/", methods=["GET", "POST"])
def config_page():
    if request.method == "POST":
        update_config(request.form.to_dict())
        return redirect(url_for("config_page"))
    cfg = load_current_config()
    return render_template_string(HTML_TEMPLATE, **cfg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
