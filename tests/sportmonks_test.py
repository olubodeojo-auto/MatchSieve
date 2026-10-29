"""Manual SportMonks head-to-head smoke test.

The legacy script referenced an undefined global named api. Configure a
SportMonks client explicitly before using this manual check.
"""
def main():
    raise SystemExit(
        "This legacy smoke test needs an explicitly configured SportMonks client. "
        "Initialize the client and credentials before running the head-to-head check."
    )
if __name__ == "__main__":
    main()
