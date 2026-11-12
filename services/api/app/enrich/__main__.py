"""Makes the folder runnable:  python -m app.enrich

Python runs this file when you "run" the package. The real code is in run.py,
so tests can import it without starting a run.
"""

from app.enrich.run import main

main()
