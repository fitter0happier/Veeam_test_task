import argparse
import hashlib
import logging
import os
import shutil
import time

def configure_logging(logfile):
    """Configure logging to file and console."""

    logging.basicConfig(
        filename=logfile,  
        filemode='a',      
        level=logging.INFO,  
        format='%(asctime)s - %(levelname)s - %(message)s' 
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)  
    console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))  
    logging.getLogger('').addHandler(console) 


def handle_cmd_errors(args):
    """Validate command-line arguments."""

    if not os.path.exists(args.source_path):
        raise FileNotFoundError(f"Source path does not exist: {args.source_path}")
    
    if not os.path.exists(args.replica_path):
        os.makedirs(args.replica_path, exist_ok=True)  

    if not os.path.isdir(args.source_path) or not os.path.isdir(args.replica_path):
        raise NotADirectoryError("Both source and replica paths must be directories.")
    
    if args.interval <= 0:
        raise ValueError("Synchronization interval must be greater than zero.")
    

def calculate_md5(file_path):
    """Calculate MD5 hash of a file."""

    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    

def sync_folders(source, replica):
    """Synchronize source folder with replica folder."""

    # Add new directories to the source 
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            source_dir = os.path.join(root, directory)
            replica_dir = os.path.join(replica, os.path.relpath(source_dir, source))
            if not os.path.exists(replica_dir):
                logging.info(f"Creating directory: {replica_dir}")
                os.makedirs(replica_dir, exist_ok=True)


    # Add or modified files to the replica
    source_contents = set()
    for root, _, files in os.walk(source):
        for file in files:
            source_path = os.path.relpath(os.path.join(root, file), source)
            source_contents.add(source_path)

            source_file = os.path.join(source, source_path)
            replica_file = os.path.join(replica, source_path)

            if (not os.path.exists(replica_file) 
                or calculate_md5(source_file) != calculate_md5(replica_file)):
                try:
                    os.makedirs(os.path.dirname(replica_file), exist_ok=True)
                    shutil.copy2(source_file, replica_file)
                    logging.info(f"Copied/Updated: {source_file} -> {replica_file}")
                except PermissionError as e:
                    logging.error(f"Permission denied: {e}")
                except FileNotFoundError as e:
                    logging.error(f"File not found: {e}")

    # Remove directories files that are no longer in the source
    for root, dirs, files in os.walk(replica, topdown=False):  
        for file in files:
            replica_path = os.path.relpath(os.path.join(root, file), replica)
            if replica_path not in source_contents:
                replica_file = os.path.join(replica, replica_path)
                try:
                    os.remove(replica_file)
                    logging.info(f"Deleted file: {replica_file}")
                except PermissionError as e:
                    logging.error(f"Permission denied while deleting file: {replica_file}")
                except FileNotFoundError as e:
                    logging.error(f"File already deleted: {replica_file}")

        for directory in dirs:
            replica_dir = os.path.join(root, directory)
            source_dir = os.path.join(source, os.path.relpath(replica_dir, replica))
            if not os.path.exists(source_dir):
                try:
                    shutil.rmtree(replica_dir)
                    logging.info(f"Removed directory: {replica_dir}")
                except PermissionError as e:
                    logging.error(f"Permission denied while deleting directory: {replica_dir}")


def main():
    args_parser = argparse.ArgumentParser(
        description=(
            "Synchronizes content from a source folder to a replica folder, "
            "ensuring an identical copy is maintained periodically."
        )
    )
    args_parser.add_argument('source_path', type=str, help="Path to the source folder.")
    args_parser.add_argument('replica_path', type=str, help="Path to the replica folder.")
    args_parser.add_argument('interval', type=int, help="Synchronization interval in seconds.")
    args_parser.add_argument('logfile', type=str, help="Path to the log file.")
    
    args = args_parser.parse_args()
    configure_logging(args.logfile)
    
    try:
        handle_cmd_errors(args)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        logging.error(e)
        return

    logging.info("The synchronization process has started.")
    logging.info(f"It will run every {args.interval} seconds.")

    try:
        while True:
            logging.info("Starting synchronization cycle.")
            sync_folders(args.source_path, args.replica_path)
            logging.info("Synchronization cycle complete.")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info("Synchronization interrupted by user.")


if __name__ == "__main__":
    main()
