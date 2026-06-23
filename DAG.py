from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import stocks # Import your class

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 6, 20),
}

# The wrapper function to be called by Airflow
def run_etl_pipeline(**kwargs):
    # Instantiate the class, passing any required parameters
    #etl = MyETLProcess(config_param="prod_env")
    etl = stocks()
    # Call class methods
    etl.ticks_sql()
    etl.sql_insert()

with DAG(
    dag_id='class_caller_dag',
    default_args=default_args,
    schedule='@daily',
    catchup=False
) as dag:

    # Call the wrapper function from the DAG using PythonOperator
    run_task = PythonOperator(
        task_id='run_etl_task',
        python_callable=run_etl_pipeline,
      #  provide_context=True,
    )
    
    run_task