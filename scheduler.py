```python
import os
import time
import subprocess
import schedule
from datetime import datetime


# ============================================================
# SERVICE NOW GAMIFICATION
# PYTHON SCHEDULER
# ============================================================


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_DIR = r"C:\Users\RSR\PYTHON\ServicenowGamification"


# ============================================================
# PYTHON FROM LL MTRACKER CONDA ENVIRONMENT
# ============================================================

PYTHON_EXE = (
    r"C:\Users\rajum\anaconda3\envs\llmtracker\python.exe"
)


# ============================================================
# MAIN SCRIPT
# ============================================================

MAIN_SCRIPT = os.path.join(
    PROJECT_DIR,
    "main_metrics.py"
)


# ============================================================
# LOG DIRECTORY
# ============================================================

LOG_DIR = os.path.join(
    PROJECT_DIR,
    "Logs"
)


# ============================================================
# CREATE LOG DIRECTORY
# ============================================================

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# ============================================================
# VALIDATE PATHS
# ============================================================

if not os.path.exists(PYTHON_EXE):

    raise FileNotFoundError(
        f"Python executable not found:\n{PYTHON_EXE}"
    )


if not os.path.exists(MAIN_SCRIPT):

    raise FileNotFoundError(
        f"main_metrics.py not found:\n{MAIN_SCRIPT}"
    )


# ============================================================
# RUN MAIN METRICS
# ============================================================

def run_main_metrics():

    start_time = datetime.now()

    # --------------------------------------------------------
    # DAILY LOG FILE
    # --------------------------------------------------------

    log_file_name = (
        "main_metrics_"
        + start_time.strftime("%Y-%m-%d")
        + ".log"
    )

    log_file = os.path.join(
        LOG_DIR,
        log_file_name
    )

    print()
    print("=" * 70)
    print("MAIN METRICS JOB STARTED")
    print("=" * 70)

    print(
        "Start Time :",
        start_time.strftime("%Y-%m-%d %H:%M:%S")
    )

    print(
        "Python     :",
        PYTHON_EXE
    )

    print(
        "Script     :",
        MAIN_SCRIPT
    )

    print("=" * 70)


    # ========================================================
    # OPEN LOG FILE
    # ========================================================

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as log:

        # ----------------------------------------------------
        # JOB HEADER
        # ----------------------------------------------------

        log.write("\n")
        log.write("=" * 70 + "\n")

        log.write(
            "JOB STARTED : "
            + start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            + "\n"
        )

        log.write(
            "PROJECT     : "
            + PROJECT_DIR
            + "\n"
        )

        log.write(
            "PYTHON      : "
            + PYTHON_EXE
            + "\n"
        )

        log.write(
            "SCRIPT      : "
            + MAIN_SCRIPT
            + "\n"
        )

        log.write("=" * 70 + "\n")


        try:

            # =================================================
            # RUN main_metrics.py
            # =================================================

            result = subprocess.run(

                [
                    PYTHON_EXE,
                    MAIN_SCRIPT
                ],

                cwd=PROJECT_DIR,

                stdout=log,

                stderr=subprocess.STDOUT,

                text=True
            )


            # =================================================
            # END TIME
            # =================================================

            end_time = datetime.now()


            # =================================================
            # CALCULATE DURATION
            # =================================================

            duration = (
                end_time - start_time
            )


            # =================================================
            # CHECK RESULT
            # =================================================

            if result.returncode == 0:

                status = "SUCCESS"

            else:

                status = "FAILED"


            # =================================================
            # WRITE RESULT TO LOG
            # =================================================

            log.write("\n")

            log.write(
                "STATUS      : "
                + status
                + "\n"
            )

            log.write(
                "ERROR CODE  : "
                + str(result.returncode)
                + "\n"
            )

            log.write(
                "END TIME    : "
                + end_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                + "\n"
            )

            log.write(
                "DURATION    : "
                + str(duration)
                + "\n"
            )

            log.write("=" * 70 + "\n")


            # =================================================
            # PRINT RESULT
            # =================================================

            print(
                "STATUS      :",
                status
            )

            print(
                "End Time    :",
                end_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            print(
                "Duration    :",
                duration
            )

            print(
                "Log File    :",
                log_file
            )

            print("=" * 70)


        except Exception as e:

            # =================================================
            # EXCEPTION HANDLING
            # =================================================

            end_time = datetime.now()

            duration = (
                end_time - start_time
            )

            log.write("\n")

            log.write(
                "STATUS      : FAILED\n"
            )

            log.write(
                "EXCEPTION   : "
                + str(e)
                + "\n"
            )

            log.write(
                "END TIME    : "
                + end_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                + "\n"
            )

            log.write(
                "DURATION    : "
                + str(duration)
                + "\n"
            )

            log.write("=" * 70 + "\n")


            print(
                "STATUS      : FAILED"
            )

            print(
                "ERROR       :",
                str(e)
            )

            print(
                "Log File    :",
                log_file
            )

            print("=" * 70)


# ============================================================
# SCHEDULE
# ============================================================

schedule.every(10).minutes.do(
    run_main_metrics
)


# ============================================================
# SCHEDULER START
# ============================================================

print()
print("=" * 70)
print("SERVICE NOW GAMIFICATION SCHEDULER")
print("=" * 70)

print(
    "Project Directory :",
    PROJECT_DIR
)

print(
    "Python Executable  :",
    PYTHON_EXE
)

print(
    "Main Script        :",
    MAIN_SCRIPT
)

print(
    "Schedule           :",
    "Every 10 minutes"
)

print(
    "Scheduler Started  :",
    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)

print("=" * 70)


# ============================================================
# RUN MAIN METRICS IMMEDIATELY
# ============================================================

print()
print("Running initial job...")

run_main_metrics()


# ============================================================
# CONTINUOUS SCHEDULER
# ============================================================

print()
print("=" * 70)
print("SCHEDULER IS RUNNING")
print("Next execution will happen every 10 minutes")
print("Press CTRL + C to stop")
print("=" * 70)


while True:

    try:

        schedule.run_pending()

        time.sleep(1)

    except KeyboardInterrupt:

        print()
        print("=" * 70)
        print("SCHEDULER STOPPED")
        print("=" * 70)

        break

    except Exception as e:

        print()
        print("=" * 70)
        print("SCHEDULER ERROR")
        print("=" * 70)

        print(
            "Error:",
            str(e)
        )

        print("=" * 70)

        time.sleep(5)

