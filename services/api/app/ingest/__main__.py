"""Makes the folder runnable:  python -m app.ingest

Python runs this file when you "run" the package. The real code is in run.py,
so tests can import it without starting a run.
"""

from app.ingest.run import main

main()
