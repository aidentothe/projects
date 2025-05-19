# My Projects Portfolio

Hi there! I’m Aiden, and this repository houses the source code for my personal projects website. Over the years, I’ve built a variety of interactive demos, games, and visualizations—primarily using JavaScript, HTML, and CSS—that explore physics, algorithms, and creative coding techniques. I’m excited to share my experiments and learnings with you!

## Table of Contents

- [Overview](#overview)
- [Features & Projects](#features--projects)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Scripts](#development-scripts)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

This site is a static portfolio showcasing:

- **Physics Simulations**: From gravity and Verlet integration to wave propagation and circuit modeling.
- **Algorithm Visualizations**: Pathfinding, raycasting, Perlin noise, and more.
- **Interactive Games**: Minesweeper 3D, gravity-based golf, bomb-defusal puzzles, and other playful experiments.

Each folder in the repo represents a standalone demo or game you can open in your browser to explore how it works. I’ve documented my approach, challenges, and optimizations directly in the code and accompanying HTML pages.

## Features & Projects

Here are some highlights:

- **Physics**  
  - `gravity`, `gravity2`, `gravity-golf`: Custom gravity engines with gameplay twists.  
  - `verlet`: Demonstrates Verlet integration for soft-body dynamics.  
  - `wave`: Interactive wave simulations, perfect for learning about oscillations.

- **Algorithms**  
  - `raycasting`: A basic 3D renderer inspired by early first-person shooters.  
  - `perlin`: Visualizing Perlin noise for terrain and texture generation.  
  - `graph-algorithms`: Pathfinding and graph traversal demos.

- **Games & Puzzles**  
  - `bomb-party`: A cooperative defusal game in the browser.  
  - `minesweeper3d`: A 3D twist on the classic Minesweeper.  
  - `golf`: Physics-driven mini-golf courses.  
  - `game-pigeon`, `car`, `circle`, `oly`: Smaller interactive demos and challenge puzzles.

Check out [projects.html](projects.html) for live links and screenshots.

## Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/aidentothe/projects.git
   cd projects
   ```

2. **Serve locally (recommended)**
   I like using Python’s simple HTTP server:
   ```bash
   python3 -m http.server 8000
   ```
   Then open `http://localhost:8000/index.html` in your browser.

3. **Explore**
   - `index.html` welcomes you with an overview.  
   - `home.html` and `projects.html` navigate to individual examples.  
   - Dive into any folder to view the source, demos, and notes.

## Project Structure

```plaintext
├── index.html         # Landing page
├── home.html          # About / overview section
├── projects.html      # Interactive project directory
├── assets/            # Shared CSS, SVGs, and images
├── scripts/           # Utility and build scripts (e.g., add_projects_commits.py)
└── [project folders]  # E.g., gravity, raycasting, bomb-party, etc.
```

Inside each project folder, you’ll usually find:
- An `index.html` demo page  
- A `main.js` (or similar) with the interactive code  
- Comments or notes in the source explaining the approach

## Development Scripts

I’ve included a small Python script, `add_projects_commits.py`, that automates adding GitHub commit counts to my project listing. Feel free to adapt it for your own static sites.

## Contributing

I’m always open to feedback and improvements! If you’d like to suggest a feature, fix a bug, or share optimizations:

1. Fork the repo.  
2. Create a new branch (`git checkout -b feature/YourFeature`).  
3. Make your changes and commit with clear messages.  
4. Submit a pull request—happy to review and merge!

## License

This repository is currently unlicensed. Feel free to reach out if you’d like to discuss terms for reuse or collaboration.

## Contact

I’m Aiden—let’s connect!

- GitHub: [@aidentothe](https://github.com/aidentothe)  
- Email: aiden.to.the@example.com  

Thanks for stopping by, and I hope you enjoy tinkering with these demos as much as I did building them!
