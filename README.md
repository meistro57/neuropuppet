# 🤖 Neuropuppet: AI-Controlled Marionette Puppet

> "Where strings meet sentience."

---

## 🎯 Overview

**Neuropuppet** is a working prototype that merges robotics, machine vision, and AI to control a humanoid marionette puppet. Using stepper motors to pull strings, the puppet learns through feedback to wave, walk, and perform gestures using reinforcement or imitation learning.

This project is a living intersection of mechanical puppetry, stepper control, and self-learning AI.

---

## 🛠️ Hardware Overview

| Component | Description | Est. Cost (USD) |
|----------|-------------|----------------:|
| **6x NEMA 17 Steppers** | Pull puppet strings via spools | ~$10–$15 each |
| **6x Pololu A4988 Drivers** | Microstepping motor drivers | ~$7–$10 each |
| **Arduino Mega** | Controls motors with step/direction signals | ~$30 |
| **Raspberry Pi 4** | Runs vision & AI logic | ~$45–$55 |
| **USB/Pi Camera** | Tracks puppet’s pose | ~$20–$30 |
| **Puppet (30–50 cm)** | Custom or store-bought with jointed limbs | ~$20–$50 |
| **Motor Frame + Rigging** | Supports motors and guides strings | ~$30 |
| **Power Supply (12V, 10A)** | Runs steppers | ~$25 |

**Total Est.:** ~$250–$350

---

## 🧵 Mechanical Rigging

- **Top bar with mounted motors**
- Strings route vertically from each motor through pulleys
- Strings attach to: head, hands, and feet
- Nylon fishing line preferred
- All motors use same spool size for uniformity

**Degrees of Freedom:**
- Head (1), Arms (2), Legs (2), Torso (optional)

---

## ⚡ Electronics Summary

- Step/Dir signals per motor via Arduino
- A4988 drivers with 1/16 microstepping
- 12V 6–10A PSU with proper decoupling caps
- Serial communication with Pi (via `pyserial`)
- Optional: Limit switches or encoder marks for homing

---

## 🧠 Software Architecture

Written in Python (venv + pip). Main components:

```
├── arduino/motor_control.ino        # Stepper control firmware
├── core/
│   ├── vision.py                    # OpenCV or MediaPipe tracking
│   ├── control.py                   # Sends motor commands to Arduino
│   ├── rl_agent.py                  # AI learning agent
│   └── utils.py                     # Config, logging, tools
├── main.py                          # Training/control loop entry
```

**Dependencies:**
```bash
opencv-python
mediapipe
pyserial
torch or tensorflow
stable-baselines3 (for RL)
```

---

## 🧠 AI Motion Learning

Neuropuppet supports:

### 🟡 Reinforcement Learning
- **State:** 2D positions of hands, feet, head from vision
- **Action:** Relative movement of each motor (e.g. δ1 to δ6)
- **Reward:** Pose accuracy, smoothness, or musical timing
- **Frameworks:** PyTorch + Stable Baselines3 (PPO or DDPG)

### 🟣 Imitation Learning
- Human performs motion → AI learns via captured vision
- Train a model to mimic action sequences from video

---

## 📹 Vision Feedback

- **MediaPipe Pose** or color markers
- Extract keypoint coordinates (e.g. hands, feet)
- Normalize frame size, smooth over time
- Use as RL state or imitation reference

---

## 🧪 Testing & Calibration

- Manual homing or switch-based homing
- Start with scripted sequences
- Log motion outcomes vs vision
- Refine motor steps per string movement empirically

---

## 🧯 Safety Notes

- Clamp motion range
- Watch for string tangles
- Always have a physical kill switch for 12V line
- Use acceleration profiles (via AccelStepper)

---

## 🌌 Future Plans

- Audio-driven dancing (beat → motion)
- 3D pose tracking with stereo camera
- Web dashboard for choreography
- Emotion-driven movement (pose + face sync)

---

## 🔗 Inspiration & References

- [Groovin’ Grover – Servo Marionette (Instructables)](http://www.instructables.com/id/Groovin-Grover-A-Microcontroller-based-Marionett/)
- [PuppetMaster – ETH Zürich](https://spectrum.ieee.org/eth-surich-puppetmaster-robot)
- [ROMS – NTU Singapore Robotic Marionette](https://mrl.cs.nyu.edu/~perlin/courses/spring2006/class-0424/04-c-hmm-puppet-d[1].pdf)
- [Stepper Motor Control – Pololu A4988 Guide](https://www.pololu.com/product/1182)
- [Vision Tracking – MediaPipe](https://developers.google.com/mediapipe)

---

© 2025 Neuropuppet. MIT Licensed. Contributions welcome!

> Pull the strings — or let the puppet pull you.
