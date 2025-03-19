#!/usr/bin/python3

from argparse import ArgumentParser, FileType
from threading import Thread, Lock
from requests import get, exceptions
from time import time

subdomains = []
lock = Lock()

def prepare_args():
    """Prepare Arguments"""
    parser = ArgumentParser(
        description="Python-based fast subdomain finder",
        usage="%(prog)s google.com",
        epilog="Example - %(prog)s -w /usr/share/wordlists/wordlist.txt -t 500 -V google.com"
    )
    parser.add_argument(metavar="Domain", dest="domain", help="Domain Name")
    parser.add_argument(
        "-w", "--wordlist", dest="wordlist", metavar="", type=FileType("r"),
        help="Wordlist of subdomains", default=None
    )
    parser.add_argument(
        "-t", "--threads", dest="threads", metavar="", type=int,
        help="Number of threads to use", default=500
    )
    parser.add_argument(
        "-V", "--verbose", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "-v", "--version", action="version", help="Print version", version="%(prog)s 1.0"
    )
    return parser.parse_args()

def prepare_words():
    """Generator function for words"""
    try:
        if arguments.wordlist:
            words = arguments.wordlist.read().split()
        else:
            with open("wordlist.txt", "r") as f:
                words = f.read().split()
        for word in words:
            yield word
    except Exception as e:
        print(f"Error reading wordlist: {e}")
        exit(1)

def check_subdomain():
    """Check subdomain for a valid HTTP response"""
    while True:
        try:
            with lock:  # Ensure thread safety
                word = next(words)
            
            url = f"https://{word}.{arguments.domain}"
            response = get(url, timeout=10)

            if response.status_code in {200, 301, 302}:  # Accept redirects too
                with lock:
                    subdomains.append(url)
                if arguments.verbose:
                    print(url)
        except (exceptions.ConnectionError, exceptions.ReadTimeout):
            continue
        except StopIteration:
            break
        except Exception as e:
            pass  # Prevent unexpected crashes

def prepare_threads():
    """Create, start, and join threads"""
    thread_list = []
    for _ in range(arguments.threads):
        thread = Thread(target=check_subdomain) 
        thread_list.append(thread)
        thread.start()
    for thread in thread_list:
        thread.join()

if __name__ == "__main__":
    arguments = prepare_args()
    words = prepare_words()
    
    start_time = time()
    prepare_threads()
    end_time = time()

    print("Subdomains Found:\n", "\n".join(subdomains))
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")
