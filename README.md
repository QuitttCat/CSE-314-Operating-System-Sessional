# CSE 314 – Operating System Sessional

[![Stars](https://img.shields.io/github/stars/QuitttCat/CSE-314-Operating-System-Sessional?style=flat-square&logo=github)](https://github.com/QuitttCat/CSE-314-Operating-System-Sessional/stargazers)
[![Forks](https://img.shields.io/github/forks/QuitttCat/CSE-314-Operating-System-Sessional?style=flat-square&logo=github)](https://github.com/QuitttCat/CSE-314-Operating-System-Sessional/network/members)
[![Issues](https://img.shields.io/github/issues/QuitttCat/CSE-314-Operating-System-Sessional?style=flat-square)](https://github.com/QuitttCat/CSE-314-Operating-System-Sessional/issues)
[![License](https://img.shields.io/github/license/QuitttCat/CSE-314-Operating-System-Sessional?style=flat-square)](https://github.com/QuitttCat/CSE-314-Operating-System-Sessional/blob/main/LICENSE)
![Last Commit](https://img.shields.io/github/last-commit/QuitttCat/CSE-314-Operating-System-Sessional?style=flat-square&logo=git)

This repository contains solutions and resources for the offline assignments in  
**CSE 314: Operating Systems Sessional (BUET)**.

Assignments cover **shell scripting**, **xv6 kernel hacking** (system calls & scheduling),  
and **inter-process communication (IPC)** with C++ threads and a Pygame visualizer.

---

## 🧰 Tech Stack

### Languages & Scripting

![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)
![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)
![C++](https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

### OS, Tools & Frameworks

![xv6](https://img.shields.io/badge/xv6-RISC--V-000000?style=for-the-badge&logo=linux&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GCC](https://img.shields.io/badge/GCC-00457C?style=for-the-badge&logo=gnu&logoColor=white)
![QEMU](https://img.shields.io/badge/QEMU-FF6600?style=for-the-badge&logo=qemu&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

---

## 📚 Table of Contents

- [Overview](#overview)
- [Offline 1 – Shell Scripting](#offline-1--shell-scripting)
- [Offline 2 – xv6 + Scheduling](#offline-2--xv6--scheduling)
- [Offline 3 – Inter Process Communication ipc](#offline-3--inter-process-communication-ipc)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Author](#author)
- [License](#license)
- [Star & Support](#star--support)

---

## 🧠 Overview

This repository is organized around three offline assignments:

- **Offline 1 – Shell Scripting**  
  Automates handling of student submissions: organizing files, extracting metrics, compiling/running code, and generating CSV reports.

- **Offline 2 – xv6 + Scheduling**  
  Extends xv6 (RISC-V) with:
  - New system calls (e.g., syscall statistics, `settickets`, `getpinfo`)
  - A multi-level feedback queue (MLFQ) scheduler
  - Support tools/notes for setting up the xv6 environment

- **Offline 3 – Inter Process Communication (IPC)**  
  A Peaky Blinders–themed simulation:
  - C++ threads for operatives
  - Synchronization of shared typewriting stations (no busy waiting)
  - Reader–writer pattern for logbook access (readers priority)
  - Pygame visualizer showing operatives, queues, stations, and logbook

All implementations follow the official assignment specifications.

---

## 📁 Offline 1 – Shell Scripting

**Goal:** Automate evaluation of student submissions using Bash.

**Highlights:**
- Unzips and organizes submissions by language (**C**, **C++**, **Python**, **Java**)
- Counts lines of code, comments, and functions
- Compiles and runs programs against test cases
- Generates a `result.csv` with metrics and verdicts
- Supports command-line flags (e.g., verbose mode, skip execution/metrics)

**Key script:**
- `Offline 1 - Shell Scripting/organize.sh`

---

## 🧾 Offline 2 – xv6 + Scheduling

**Goal:** Modify xv6 to add new system calls and implement an MLFQ scheduler.

**Key features:**
- New system call to maintain syscall statistics and display them via a `history` command
- Lottery / ticket-based process control via `settickets` and `getpinfo`
- Multi-Level Feedback Queue (MLFQ) scheduler implementation
- Patch-based workflow for modifying xv6 (`2105044.patch`)

**Key files:**
- `Offline 2 - xv6 + Scheduling/2105044.patch`  
- `Offline 2 - xv6 + Scheduling/Jan25_CSE314_Assignment2_Spec.pdf`

---

## 🕵️ Offline 3 – Inter Process Communication (IPC)

**Goal:** Simulate a concurrent intelligence operation with multiple operatives and shared resources.

**Concepts:**
- Threads, mutexes, and semaphores
- Producer–consumer–style interactions
- Reader–writer problem (readers priority)
- Avoiding busy waiting

**Components:**
- `2105044.cpp` – C++ thread-based simulation
- `run.sh` – Bash script to compile and run the simulation
- `input.txt` / `output.txt` – Sample I/O
- `simulation.py` – Pygame visualizer of operatives, stations, queues, and logbook

**Theme:**  
Peaky Blinders–inspired intelligence operation with multiple typewriting stations and a shared logbook.

---

## 🗂 File Structure

```text
CSE-314-Operating-System-Sessional/
├── Offline 1 - Shell Scripting/
│   ├── CSE314_Jan_25_Shell_Offline_Specification.pdf
│   └── organize.sh
├── Offline 2 - xv6 + Scheduling/
│   ├── 2105044.patch
│   └── Jan25_CSE314_Assignment2_Spec.pdf
├── Offline 3 - Inter Process Communication (IPC)/
│   ├── 2105044.cpp
│   ├── CSE314_Jan_25_IPC_Offline.pdf
│   ├── input.txt
│   ├── output.txt
│   ├── README
│   ├── run.sh
│   └── simulation.py
├── xv6 Resources.docx
├── README.md
└── LICENSE

```
## ⚙️ Installation

### Prerequisites
- **Bash Shell**: Required for running scripts in Offline 1 and Offline 3.
- **GCC/G++ Compiler**: For compiling C/C++ code in Offline 3 (e.g., `g++` for `2105044.cpp`).
- **Python 3.x**: For the visual simulation in Offline 3. Install Pygame with:
  ```
  pip install pygame
  ```
- **xv6 Environment** (Offline 2 only):
  - RISC-V toolchain (GCC for RISC-V).
  - QEMU emulator.
  - Install as per MIT's guide: [xv6 Tools](https://pdos.csail.mit.edu/6.828/2022/tools.html).
- **Git**: For cloning repositories and applying patches.

### Setup Steps
1. **Clone this Repository**:
   ```
   git clone https://github.com/QuitttCat/CSE-314-Operating-System-Sessional.git
   cd CSE-314-Operating-System-Sessional
   ```

2. **For Offline 2 (xv6)**:
   - Clone the xv6 repository:
     ```
     git clone https://github.com/mit-pdos/xv6-riscv.git
     cd xv6-riscv
     ```
   - Apply the patch:
     ```
     git apply ../Offline\ 2\ -\ xv6\ +\ Scheduling/2105044.patch
     ```
   - Build and run:
     ```
     make clean
     make qemu
     ```

3. **For Offline 3 (Pygame Simulation)**:
   - Ensure Pygame is installed (see prerequisites).
   - No additional setup needed for the C++ simulation beyond G++.

---

## 🚀 Usage

### Offline 1 – Shell Scripting
Navigate to the folder:
```
cd Offline\ 1\ -\ Shell\ Scripting/
```
Run the script with required folders and optional flags:
```
bash organize.sh <submissions_folder> <target_folder> <test_folder> <answer_folder> [-v] [-noexecute] [-nolc] [-nocc] [-nofc]
```
- **Output**: Generates `result.csv` in `<target_folder>` with student IDs, names, languages, match counts, line/comment/function metrics.
- **Flags**:
  - `-v`: Verbose output.
  - `-noexecute`: Skip compilation/execution and matching.
  - `-nolc`: Skip line counting.
  - `-nocc`: Skip comment counting.
  - `-nofc`: Skip function counting.

### Offline 2 – xv6 + Scheduling
After setup (see Installation):
1. In the xv6-riscv directory, enter QEMU with `make qemu`.
2. Test new features:
   - Syscall statistics: Run `history` (all syscalls) or `history <sysno>` (specific syscall).
   - Process info: Run `testprocinfo`.
   - Set tickets: `settickets <n>`.
   - Dummy process: `dummyproc <iterations>` to test scheduling.
3. Exit QEMU with `Ctrl+A` then `X`.

### Offline 3 – Inter Process Communication (IPC)
Navigate to the folder:
```
cd Offline\ 3\ -\ Inter\ Process\ Communication\ (IPC)/
```

1. **Run C++ Simulation**:
   ```
   bash run.sh input.txt output.txt
   ```
   - Compiles `2105044.cpp` to `a.out`.
   - Runs with input from `input.txt` (e.g., "15 5 3 5" for operatives, unit size, recreation interval, logbook interval).
   - Outputs logs to console (similar to `output.txt`).
   - Cleans up `a.out`.

2. **Run Pygame Visualizer**:
   ```
   python simulation.py
   ```
   - Displays a graphical simulation of operatives arriving, queuing at stations, recreating documents, and accessing the logbook.
   - Uses colors for states (e.g., blue for operatives, red/green for stations).
   - Log messages appear at the bottom; simulation runs until all operations complete.

---

## 👤 Author

- **QuitttCat**  
  GitHub: [@QuitttCat](https://github.com/QuitttCat)  
  This repo is based on solutions for BUET CSE 314 assignments.

---

## ⭐ Star & Support

If this repository helped you with your assignments or understanding OS concepts, please give it a ⭐ **star** on GitHub!  

