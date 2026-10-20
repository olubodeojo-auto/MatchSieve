# Optional demo dataset

`SYNTHETIC_DEMO_ONLY.csv` is a completely fictional 13-row sample used only to exercise import, report-generation and UI flows. It is **not real fixtures, actual club data, or betting research**. Never publish it, never use it to make a real-world decision, and never mix it into a customer production archive.

It is not auto-imported. To load it into a new local development DB explicitly, run from the project root:

```powershell
python run.py import-csv data/examples/SYNTHETIC_DEMO_ONLY.csv --source-key synthetic_demo
```

Use a clean/disposable development database if you don't want demo records in the same archive as real data.
