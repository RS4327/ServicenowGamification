import os
import sys
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(r"C:\Users\RSR\PYTHON\ServicenowGamification")

# Change working directory
os.chdir(PROJECT_ROOT)

# Add src folder to Python Path
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Imports
from ServicenowGamification.PipeLine.Stage_01_Data_Ingestion import DataIngestionPipeLine
from ServicenowGamification.PipeLine.Stage_02_Data_PreProcessing import DataPreProcessingPipeLine
from ServicenowGamification.PipeLine.Stage_03_Data_Metricalculation import DataMetricsCalculationPipeLine
from ServicenowGamification.PipeLine.Stage_04_Data_Gamification import DataGamificationPipeLine
from ServicenowGamification.Components.Agent_DashBoard import AgentDashBoard
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager

def main():

    try:

        print("=" * 70)
        print("STARTING MAIN AGENT")
        print("=" * 70)

        # ---------------------------------------------------------
        # Load configuration
        # ---------------------------------------------------------

        config_manager = ConfigurationManager()

        config = config_manager.get_datagamificationconfig()

        obj = AgentDashBoard( )

        agent_header_df = obj.run()

        print(
            "Agent Dashboard completed successfully."
        )

        print(
            agent_header_df
        )

        return  

    except Exception as e:

        print("=" * 70)
        print("MAIN AGENT FAILED")
        print("=" * 70)

        print(
            "Error:",
            str(e)
        )

        raise


if __name__ == "__main__":

    main()