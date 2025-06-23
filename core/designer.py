from __future__ import annotations

"""Simple 3D environment for designing puppet poses."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pyglet
from pyglet.gl import (
    glBegin,
    glClearColor,
    glColor3f,
    glEnd,
    glEnable,
    glLoadIdentity,
    glRotatef,
    glTranslatef,
    glVertex3f,
    GL_DEPTH_TEST,
    GL_LINES,
)

import yaml


@dataclass
class Joint:
    x: float
    y: float
    z: float


class PuppetDesigner(pyglet.window.Window):
    """Interactive 3D designer for puppet poses."""

    def __init__(self, width: int = 800, height: int = 600) -> None:
        super().__init__(width, height, "Neuropuppet 3D Designer")
        self.joints: Dict[str, Joint] = {
            "head": Joint(0.0, 1.0, 0.0),
            "torso": Joint(0.0, 0.0, 0.0),
            "left_hand": Joint(-0.5, 0.5, 0.0),
            "right_hand": Joint(0.5, 0.5, 0.0),
            "left_foot": Joint(-0.3, -1.0, 0.0),
            "right_foot": Joint(0.3, -1.0, 0.0),
        }
        self.selected = "head"
        self.rx = 0.0
        self.ry = 0.0
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        self.step = 0.1
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule_interval(self.update, 1 / 60)

    def on_draw(self) -> None:  # pragma: no cover - requires display
        self.clear()
        glLoadIdentity()
        glTranslatef(0, 0, -5)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        self._draw_skeleton()

    def _draw_skeleton(self) -> None:
        lines = [
            ("head", "torso"),
            ("torso", "left_hand"),
            ("torso", "right_hand"),
            ("torso", "left_foot"),
            ("torso", "right_foot"),
        ]
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        for a, b in lines:
            ja = self.joints[a]
            jb = self.joints[b]
            glVertex3f(ja.x, ja.y, ja.z)
            glVertex3f(jb.x, jb.y, jb.z)
        glEnd()
        # highlight selected joint
        glColor3f(1, 0, 0)
        sel = self.joints[self.selected]
        glBegin(GL_LINES)
        glVertex3f(sel.x - 0.05, sel.y, sel.z)
        glVertex3f(sel.x + 0.05, sel.y, sel.z)
        glVertex3f(sel.x, sel.y - 0.05, sel.z)
        glVertex3f(sel.x, sel.y + 0.05, sel.z)
        glVertex3f(sel.x, sel.y, sel.z - 0.05)
        glVertex3f(sel.x, sel.y, sel.z + 0.05)
        glEnd()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        key = pyglet.window.key
        if symbol == key._1:
            self.selected = "head"
        elif symbol == key._2:
            self.selected = "left_hand"
        elif symbol == key._3:
            self.selected = "right_hand"
        elif symbol == key._4:
            self.selected = "left_foot"
        elif symbol == key._5:
            self.selected = "right_foot"
        elif symbol == key.S and modifiers & key.MOD_CTRL:
            self.save_pose(Path("pose.yaml"))

    def update(self, dt: float) -> None:
        key = pyglet.window.key
        j = self.joints[self.selected]
        if self.keys[key.LEFT]:
            j.x -= self.step
        if self.keys[key.RIGHT]:
            j.x += self.step
        if self.keys[key.UP]:
            j.y += self.step
        if self.keys[key.DOWN]:
            j.y -= self.step
        if self.keys[key.PAGEUP]:
            j.z += self.step
        if self.keys[key.PAGEDOWN]:
            j.z -= self.step
        if self.keys[key.A]:
            self.ry -= 1
        if self.keys[key.D]:
            self.ry += 1
        if self.keys[key.W]:
            self.rx -= 1
        if self.keys[key.S]:
            self.rx += 1

    def save_pose(self, path: Path) -> None:
        data = {name: (j.x, j.y, j.z) for name, j in self.joints.items()}
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f)
        print(f"Pose saved to {path}")


def main() -> None:
    window = PuppetDesigner()
    pyglet.app.run()


if __name__ == "__main__":  # pragma: no cover - manual usage
    main()
