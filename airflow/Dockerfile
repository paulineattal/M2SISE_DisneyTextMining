FROM apache/airflow:2.0.0

USER root

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt


RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p $AIRFLOW_HOME && \
    chown -R airflow: $AIRFLOW_HOME

COPY --chown=airflow:root dags/ /opt/airflow/dags
COPY --chown=airflow:root logs/ /opt/airflow/logs

#COPY script.sh /script.sh
#RUN chmod +x /script.sh
#CMD ["/script.sh"]

USER airflow

#RUN airflow db reset
RUN airflow db init
#RUN airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@admin.org 
#a commenter si ca marche pas 
#RUN airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin


#CMD ["bash", "-c", " airflow db reset && airflow db init && airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@admin.org && airflow webserver & airflow scheduler"]
CMD ["bash", "-c", "airflow webserver & airflow scheduler"]

#

# Expose the port for the web server
EXPOSE 8080
