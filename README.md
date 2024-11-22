# Folder Synchronizer

This project implements a one-way folder synchronization tool that keeps the content of a replica folder identical to a source folder. 
It performs periodic synchronization to ensure the replica matches the source, including adding new files, 
updating modified ones, and removing obsolete files or directories.

## Features

    One-way synchronization: Ensures the replica folder matches the source folder.
    Support for nested directories: Synchronizes files and folders at all levels.
    Periodic synchronization: Runs at a user-specified interval.
    Detailed logging:
        Logs all actions, such as file copying, updates, deletions, and errors.
        Logs are saved to a user-specified file and displayed in the console.
    Command-line interface: Fully configurable via command-line arguments.
    Graceful exit: Handles KeyboardInterrupt (Ctrl+C) to terminate safely.

## Usage
### Prerequisites

    Python 3.6 or higher

### Command-line Arguments
```bash
python folder_synchronizer.py <source_path> <replica_path> <interval> <logfile>
```

    <source_path>: Path to the source folder (must exist).
    <replica_path>: Path to the replica folder (created if it does not exist).
    <interval>: Synchronization interval in seconds (must be greater than 0).
    <logfile>: Path to the log file where actions are recorded.

### Example
```bash
python folder_synchronizer.py ./source ./replica 10 ./sync.log
```

    Synchronizes the contents of ./source to ./replica every 10 seconds.
    Logs all actions to sync.log.

### Stopping the Program

Press Ctrl+C to terminate the synchronization process.
Logging

    File Logging: All synchronization actions (file copying, updates, deletions, and errors) are logged to the file specified by the user.
    Console Logging: All log messages are also displayed in the command-line interface for real-time feedback.

### Error Handling

The program validates all input arguments and handles errors such as:

    Missing or invalid folder paths
    File permission issues
    Unexpected interruptions
