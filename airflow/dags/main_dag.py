# main.py
from execute_scrapping_dag import dag, scrapping_task, scrapping
from clean_dag import dag_clean, recodage_type_float_task, ajout_levels_task, recodage_type_int_task, clean_date_ajout_task, add_date_task, save_clean_file_task, last_task
from dag_dw import alimente_dw_task

try:
    scrapping_task.set_downstream(recodage_type_float_task)
    recodage_type_float_task.set_downstream(ajout_levels_task)
    ajout_levels_task.set_downstream(recodage_type_int_task)
    recodage_type_int_task.set_downstream(clean_date_ajout_task)
    clean_date_ajout_task.set_downstream(add_date_task)
    add_date_task.set_downstream(save_clean_file_task)
    save_clean_file_task.set_downstream(last_task)
    last_task.set_downstream(alimente_dw_task)

except:

    recodage_type_float_task.set_downstream(ajout_levels_task)
    ajout_levels_task.set_downstream(recodage_type_int_task)
    recodage_type_int_task.set_downstream(clean_date_ajout_task)
    clean_date_ajout_task.set_downstream(add_date_task)
    add_date_task.set_downstream(save_clean_file_task)
    save_clean_file_task.set_downstream(last_task)
    last_task.set_downstream(alimente_dw_task)

