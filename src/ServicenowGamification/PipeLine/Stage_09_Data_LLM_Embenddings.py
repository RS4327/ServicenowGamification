import os
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sns_LLM_Embendings import CreateEmbedings,PromptBuilder
 
from ServicenowGamification import logger

Stage_Name='Data LLM Embenddings'

class DataLLMCreateEmbenddingsPipeLine:
    def __init__(self):
        pass

    def main(self):
        try:
           ##### Inputs ##################
           
            incident_data = {
                    "number": "INC001001",
                    "short_description":
                        "VPN connection failure",
                    "description":
                        "User unable to connect to corporate VPN.",
                    "category": "Network",
                    "subcategory": "VPN",
                    "priority": 1,
                    "assignment_group":
                        "Network Support",
                    "assigned_to": "John",
                    "resolution_hours": 6.5,
                    "mttr": 5.2,
                    "customer_rating": 4.5
                }
            gamification_data = {
                "assigned_to": "John",
                "total_points": 850,
                "points_per_ticket": 42.5,
                "badges": 5,
                "rewards": 2,
                "achievements": 8,
                "level": 7,
                "leaderboard_rank": 3,
                "monthly_rank": 2,
                "recognition_score": 91
            }

            sla_data = {
                "sla_prediction": "Breached",
                "sla_confidence": 0.91,
                "sla_percentage": 72,
                "predicted_resolution_hours": 9.2
                }
                
            workload_data = {
                "workload_prediction": 18,
                "workload_level": "High",
                "confidence": 0.89,
                "total_incidents": 25,
                "active_incidents": 12,
                "pending_incidents": 6,
                "resolved_incidents": 7
            }

            performance_data = {
                "assigned_to": "John",
                "performance_prediction": 3,
                "performance_category": "Excellent",
                "confidence": 0.98,
                "quality_score": 91,
                "skill_score": 88,
                "fcr": 92,
                "mttr": 5.2,
                "sla_percentage": 95
            }
            retrieved_incidents = [
                {
                    "rank": 1,
                    "distance": 0.82,
                    "document":
                        "ServiceNow Incident INC000981 - VPN failure"
                },

                {
                    "rank": 2,
                    "distance": 1.04,
                    "document":
                        "ServiceNow Incident INC000875 - VPN timeout"
                },

                {
                    "rank": 3,
                    "distance": 1.21,
                    "document":
                        "ServiceNow Incident INC000754 - Network VPN issue"
                }

            ]     





            config = ConfigurationManager().get_create_embendings_config()

            embendings = CreateEmbedings(config)

            embendings.connect()
            prompt_builder = PromptBuilder()
                        
            prompt = prompt_builder.build_prompt(
                task="recommendation",
                incident_data=incident_data,
                sla_data=sla_data,
                workload_data=workload_data,
                performance_data=performance_data,
                gamification_data=gamification_data 
            )
            
            print(prompt)
            
            print("=" * 70)
            print("GENERATED PROMPT")
            print("=" * 70)
            
            print(prompt)
            
            embendings.connect()
            
            embendings.test_connection()
            response = embendings.generate_response(prompt)
            
            print("=" * 70)
            print("LLM RESPONSE")
            print("=" * 70)
            
            print(response)
            


        except Exception as e:
            raise e
        
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataLLMCreateEmbenddingsPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e


