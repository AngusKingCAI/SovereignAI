from __future__ import annotations

import subprocess
import sys


def install_ollama() -> bool:
    print("Installing Ollama...")
    try:
        subprocess.run(
            [
                "winget", "install", "Ollama.Ollama",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            check=True,
        )
        print("Ollama installed successfully via winget")
        return True
    except Exception as exc:
        print(f"winget install failed: {exc}")
        print("Please download Ollama from https://ollama.com")
        return False


def start_ollama() -> bool:
    print("Starting Ollama service...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Ollama service started in background")
        return True
    except Exception as exc:
        print(f"Failed to start Ollama: {exc}")
        return False


def pull_model(model_name: str = "tinyllama") -> bool:
    print(f"Pulling model {model_name}...")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"Model {model_name} pulled successfully")
        return True
    except Exception as exc:
        print(f"Failed to pull model: {exc}")
        return False


def install_llama_cpp() -> bool:
    print("Installing llama-cpp-python...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "llama-cpp-python"],
            check=True,
        )
        print("llama-cpp-python installed successfully")
        return True
    except Exception as exc:
        print(f"Failed to install llama-cpp-python: {exc}")
        return False


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Install dependencies for diagnostic harness")
    parser.add_argument("--ollama", action="store_true", help="Install Ollama")
    parser.add_argument("--llama-cpp", action="store_true", help="Install llama-cpp-python")
    parser.add_argument("--start-ollama", action="store_true", help="Start Ollama service")
    parser.add_argument("--pull-model", type=str, default="tinyllama", help="Pull Ollama model")
    args = parser.parse_args()

    if args.ollama:
        install_ollama()

    if args.llama_cpp:
        install_llama_cpp()

    if args.start_ollama:
        start_ollama()

    if args.pull_model:
        pull_model(args.pull_model)


if __name__ == "__main__":
    main()
