#!/usr/bin/env python3
"""auto_committer.py — generate a plausible-looking commit history

This utility walks each top-level project directory inside a Git monorepo,
randomly splits that project’s files into several chunks, and records a week of
commits for every project, starting with a user-supplied start date.  Each
project corresponds to a different calendar week so the resulting history reads
sequentially in *git log*.

The script is deliberately deterministic-ish (the commits for a given *project /
seed* pair are always identical) and tries to stay side-effect-free unless the
`--push` flag is supplied.

Typical usage
-------------
$ python auto_committer.py --start-date 2024-05-01 --push

Requirements
------------
- GitPython  (    pip install gitpython   )
- A local checkout that already has a remote named ``origin``

"""
from __future__ import annotations

import argparse
import logging
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List

from git import Actor, InvalidGitRepositoryError, Repo

# ---------------------------------------------------------------------------
# Default configuration (may be overridden by CLI flags)
# ---------------------------------------------------------------------------
PROJECTS_TO_IGNORE: set[str] = {
    ".git",
    ".idea",
    ".vscode",
    "images",
    "sounds",
}
MIN_COMMITS_PER_PROJECT = 6
MAX_COMMITS_PER_PROJECT = 13
DEFAULT_START_DATE = "2024-05-01"
DEFAULT_BRANCH = "main"
AUTHOR = Actor("Auto Commit Bot", "autocommit@example.com")

COMMIT_MESSAGES: list[str] = [
    "Add initial project files",
    "Implement core functionality",
    "Refactor code structure",
    "Update documentation",
    "Fix minor bugs",
    "Improve performance",
    "Add tests",
    "Update styles",
    "Add new feature",
    "Cleanup code",
    "Update dependencies",
    "Polish UI",
    "Final tweaks before release",
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def find_project_dirs(repo_root: Path) -> list[Path]:
    """Return immediate sub-directories that should be treated as projects."""
    dirs = [
        d
        for d in repo_root.iterdir()
        if d.is_dir() and d.name not in PROJECTS_TO_IGNORE and not d.name.startswith(".")
    ]
    logging.debug("Identified project directories: %s", [d.name for d in dirs])
    return dirs


def list_files_recursively(project_path: Path, repo_root: Path) -> list[str]:
    """Return every file path **relative to *repo_root*** inside *project_path*."""
    all_files = [
        str(p.relative_to(repo_root))
        for p in project_path.rglob("*")
        if p.is_file()
    ]
    logging.debug("Files found in %s: %s", project_path.name, all_files)
    return all_files


def split_list(lst: list[str], min_parts: int = MIN_COMMITS_PER_PROJECT, max_parts: int = MAX_COMMITS_PER_PROJECT) -> list[list[str]]:
    """Shuffle *lst* and split it into *n* reasonably equal chunks."""
    if not lst:
        return []
    n_parts = random.randint(min_parts, max_parts)
    random.shuffle(lst)
    groups = [lst[i :: n_parts] for i in range(n_parts)]
    logging.debug("Split list into %d groups", len(groups))
    return groups


def random_time_within_week(week_start: datetime) -> datetime:
    """Return a random *datetime* inside the seven-day window starting at *week_start*."""
    delta = timedelta(days=random.randint(0, 6), seconds=random.randint(0, 86_399))
    ts = week_start + delta
    logging.debug("Generated random timestamp: %s", ts.isoformat())
    return ts


def commit_group(
    repo: Repo,
    file_group: list[str],
    msg: str,
    timestamp: datetime,
) -> None:
    """Stage *file_group* and create a commit stamped with *timestamp*."""
    if not file_group:
        logging.debug("Empty file group, skipping commit.")
        return

    lock_file = repo.working_tree_dir and Path(repo.working_tree_dir) / ".git" / "index.lock"
    if lock_file and lock_file.exists():
        logging.warning("Found stale lock file at %s, waiting briefly then removing it.", lock_file)
        time.sleep(0.5)  # small delay to avoid race condition
        try:
            lock_file.unlink()
            logging.info("Removed stale lock file.")
        except Exception as e:
            logging.error("Failed to remove lock file: %s", e)
            return

    logging.info("Staging files: %s", file_group)
    repo.index.add(file_group)
    iso_ts = timestamp.isoformat()
    repo.index.commit(
        msg,
        author=AUTHOR,
        committer=AUTHOR,
        author_date=iso_ts,
        commit_date=iso_ts,
    )
    logging.info("Committed with message: '%s' at %s", msg, iso_ts)


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def generate_history(repo_root: Path, start_date: datetime) -> None:
    """Walk *repo_root* and create commits week-by-week starting *start_date*."""
    try:
        repo = Repo(repo_root)
    except InvalidGitRepositoryError as exc:
        raise SystemExit(f"{repo_root} is not a Git repository: {exc}") from exc

    logging.info("Using Git repository at %s", repo_root)
    projects = find_project_dirs(repo_root)
    logging.info("Found %d projects: %s", len(projects), ", ".join(p.name for p in projects))

    for week_idx, project in enumerate(projects):
        files = list_files_recursively(project, repo_root)
        if not files:
            logging.warning("Skipping %s — no files found", project.name)
            continue

        week_start = start_date + timedelta(weeks=week_idx)
        groups = split_list(files)
        logging.info(
            "Committing %d groups (%d files) for %s, week beginning %s",
            len(groups),
            len(files),
            project.name,
            week_start.date(),
        )

        for g in groups:
            commit_group(
                repo,
                g,
                msg=random.choice(COMMIT_MESSAGES),
                timestamp=random_time_within_week(week_start),
            )


# ---------------------------------------------------------------------------
# CLI glue
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:  # noqa: ANN001
    parser = argparse.ArgumentParser(description="Generate a realistic commit history across sub-projects.")
    parser.add_argument(
        "repo",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Path to the Git repository (defaults to current directory)",
    )
    parser.add_argument(
        "--start-date",
        default=DEFAULT_START_DATE,
        help="ISO date (YYYY-MM-DD) to start committing from [default: %(default)s]",
    )
    parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        help="Branch to push commits to [default: %(default)s]",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the generated commits to origin/<branch> after creation",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed the PRNG for deterministic output",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase output verbosity (can be supplied multiple times)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # ------------------------------------------------------------------
    # Logging config
    # ------------------------------------------------------------------
    log_level = logging.WARNING - min(args.verbose, 3) * 10  # Allow up to -vvv
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    if args.seed is not None:
        random.seed(args.seed)
        logging.info("Seeded PRNG with %d", args.seed)

    try:
        start_date = datetime.fromisoformat(args.start_date)
    except ValueError as exc:
        raise SystemExit(f"Invalid --start-date '{args.start_date}'; must be YYYY-MM-DD") from exc

    logging.info("Generating commit history starting from %s", start_date.date())
    generate_history(args.repo.resolve(), start_date)

    if args.push:
        repo = Repo(args.repo)
        logging.info("Pushing commits to origin/%s…", args.branch)
        repo.remotes.origin.push(args.branch)
        logging.info("Push complete.")


if __name__ == "__main__":
    main()
