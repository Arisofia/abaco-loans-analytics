"""Entrypoint wrapper for python -m abaco_pipeline.main."""

from python.abaco_pipeline.main import main


if __name__ == "__main__":
    raise SystemExit(main())
