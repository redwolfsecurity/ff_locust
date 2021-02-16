# Manage locust event hooks
from locust import events
# Create JSON from python objects
import json
# Create MS timestamps
import time
# Handle traceback to string
import traceback
# To request table server API
import requests
# For environment variables
import os
# To manage file paths
from pathlib import Path
# To get a random line from file
import random
# Pandas - a greate data management tool
# Used to read tsv
import pandas as pd
# math to compute ceil of floating point ms measurements
import math


class FF_Locust():    
    def __init__(self):
        print('FF_INITIALIZED')
        events.request_success.add_listener(self.hook_request_success)
        events.request_failure.add_listener(self.hook_request_fail)
        events.spawning_complete.add_listener(self.hook_spawning_complete)
        events.test_stop.add_listener(self.hook_test_stop)
        events.test_start.add_listener(self.hook_test_start)
        events.user_error.add_listener(self.hook_user_error)
        events.init.add_listener(self.hook_init)
        events.quitting.add_listener(self.hook_quitting)
        events.worker_report.add_listener(self.hook_worker_report)
        events.report_to_master.add_listener(self.hook_report_to_master)
        self.url = os.getenv('FF_TABLE_SERVER_URL')
        self.tables = {} # store table state
        # self.table = os.getenv('TABLE')
        if self.url is None:
            self.is_local = True
        else:
            self.is_local = False

        if self.is_local is False:
            try:
                request = requests.get( url )
                if request.status_code == 200:
                    self.is_remote_reachable = True
                else:
                    self.is_remote_reachable = False
            except:
                self.is_remote_reachable = False
        if self.is_local:
            self.ff_log({"description": "FF_TABLE_SERVER_URL environment variable not found. FF Locust Running in local mode and will look for local tsv files"})
        else:
            self.ff_log({"description": "FF_TABLE_SERVER_URL environment variable found. FF Locust Running in remote mode and will look for data at {}".format(self.url)})

    ##############################################################################
    # Fired when a request is completed successfully. This event is typically used to report requests when writing custom clients for locust.
    # 
    # request_type - Request type method used
    # name - Path to the URL that was called (or override name if it was used in the call to the client)
    #        EXAMPLE: "03. SaveForm - /form"
    # response_time:Response time in milliseconds
    # response_length:Content-length of the response
    # **kw is future proofing against addition of new parameters
    def hook_request_success(self, request_type, name, response_time, response_length, **kw):
        self.ff_log(self.ff_metric("request_success", 
            {"response_time_ms": math.ceil(response_time), "content_length": response_length},
            {"name": name, "request_type": request_type}))

    ##############################################################################
    # Fired when a request fails. This event is typically used to report failed requests when writing custom clients for locust.
    # 
    # request_type:Request type method used
    # name:Path to the URL that was called (or override name if it was used in the call to the client)
    # response_time:Time in milliseconds until exception was thrown
    # response_length:Content-length of the response
    # exception:Exception instance that was thrown
    # **kw is future proofing against addition of new parameters
    def hook_request_fail(self, request_type, name, response_time, response_length, exception, **kw):
        self.ff_log(self.ff_metric("request_failure",
            {"response_time_ms": math.ceil(response_time), "content_length": response_length, "exception": str(exception)},
            {"name": name, "request_type": request_type, "is_error": True}))

    ##############################################################################
    # Fired when all simulated users has been spawned.
    # 
    # user_count:Number of users that were spawned
    # **kw is future proofing against addition of new parameters
    # @events.spawning_complete.add_listener
    def hook_spawning_complete(self, user_count, **kw):
        self.ff_log(self.ff_metric("spawning_complete",
            {"user_count": user_count}))

    ##############################################################################
    # Fired when a load test is stopped. When running locust distributed the event is only fired on the master node and not on each worker node.
    # 
    # **kw is future proofing against addition of new parameters
    def hook_test_stop(self, **kw):
        self.ff_log(self.ff_metric("test_stop", {"count": 1}))

    ##############################################################################
    # Fired when a new load test is started. It's not fired again if the number of users change during a test.
    # When running locust distributed the event is only fired on the master node and not on each worker node.
    # 
    # **kw is future proofing against addition of new parameters
    def hook_test_start(self, **kw):
        self.ff_log(self.ff_metric("test_start", {"count": 1}))

    ##############################################################################
    # Fired when an exception occurs inside the execution of a User class.
    # We cannot create fields from exception or tb or user_instance parameters because they are not serializable.
    #
    # user_instance:User class instance where the exception occurred
    # exception:Exception that was thrown
    # tb:Traceback object (from e.__traceback__)
    # **kw is future proofing against addition of new parameters
    def hook_user_error(self, user_instance, exception, tb, **kw):
        # print('FF EXCEPTION', exception)
        self.ff_log(self.ff_metric("user_error",
            {"exception": str(exception), "traceback": ''.join(traceback.format_tb(tb))},
            {"is_error": True}))


    ##############################################################################
    # Fired when the locust process is exiting
    #
    # environment:Locust environment instance 
    # **kw is future proofing against addition of new parameters
    def hook_quitting(self, environment, **kw):
        self.ff_log(self.ff_metric("quitting",
            {"count": 1}, {"url": environment.host}))

    ##############################################################################
    # Used when Locust is running in master mode and is fired when the master server receives a report from a Locust worker server.
    # This event can be used to aggregate data from the locust worker servers.
    #
    # client_id:Client id of the reporting worker
    # data:Data dict with the data from the worker node
    # **kw is future proofing against addition of new parameters
    def hook_worker_report(self, client_id, data, **kw):
        self.ff_log(self.ff_metric("worker_report",
            data, {"client_id": client_id}))

    ##############################################################################
    # Used when Locust is running in worker mode. It can be used to attach data to the dicts that are regularly sent to the master.
    # It's fired regularly when a report is to be sent to the master server.
    # Note that the keys 'stats' and 'errors' are used by Locust and shouldn't be overridden.
    #
    # client_id:The client id of the running locust process.
    # data:Data dict that can be modified in order to attach data that should be sent to the master.
    # **kw is future proofing against addition of new parameters
    def hook_report_to_master(self, client_id, data, **kw):
        self.ff_log(self.ff_metric("report_to_master",
            data, {"client_id": client_id}))


    ##############################################################################
    # Fired when Locust is started, once the Environment instance and locust runner instance have been created.
    # This hook can be used by end-users' code to run code that requires access to the Environment.
    # For example to register listeners to request_success, request_failure or other events.
    #
    # environment:Environment instance
    # **kw is future proofing against addition of new parameters
    def hook_init(self, environment, **kw):
        self.ff_log(self.ff_metric("init", {"count": 1}, {"url": environment.host}))

    # Create self.ff_metric
    # Outputs JSON in self.ff_metric format
    def ff_metric(self, measurement, fields = None, tags = None):
        # Create python object
        metric_object = {
            "mime_type": "timeseries/metric",
            "measurement": measurement,
            "timestamp_epoch_ms": round(time.time() * 1000),
        }
        # Check parameters of function
        if (fields is None):
            print('FF_ERROR {"description": "No fields for measurement, InfluxDB requires fields."}')
            return
        else:
            metric_object["fields"] = fields
        if (tags is not None):
            metric_object["tags"] = tags

        # Convert python object into JSON
        metric_json = json.dumps(metric_object)
        return metric_json
    
    def get_table_metadata(self, table):
        if table is None:
            self.error({"description": "No table provided to get metadata for.", "is_error": True})
            return {}
        if table[-4:] == '.tsv':
            table = table[:-4]
        if table not in self.tables:
            self.error({"description": "No metadata found for table: {}".format(table), "is_error": True})
            return {}
        return self.tables[table]

    def set_table_metadata(self, table, tsv):
        if table is None:
            self.error({"description": "No table provided to set metadata for.", "is_error": True})
            return
        if tsv is None:
            self.error({"description": "No tsv provided to set metadata for.", "is_error": True})
            return
        if table[-4:] == '.tsv':
            table = table[:-4]
        if table not in self.tables:
            self.tables[table] = {
                "__index": 0
            }
        self.tables[table].update({
            '__list': table,
            '__timestamp_epoch_ms': round(time.time() * 1000),
            '__remaining_count': len(tsv) - self.tables[table]['__index'],
            '__list_count': len(tsv)
        })

    def set_next_index(self, table):
        if table is None:
            self.error({"description": "No table provided to increase index for.", "is_error": True})
            return
        if table[-4:] == '.tsv':
            table = table[:-4]
        if table not in self.tables:
            self.error({"description": "Table metadata not found, can't increase index.", "is_error": True})
            return
        if '__index' not in self.tables[table]:
            self.error({"description": "Table metadata not set, index must be set before increasing it.", "is_error": True})
            return
        self.tables[table]['__index'] += 1

    def get_data_next(self, table = None, looping = True):
        if table == None:
            self.error({"description": "No table provided to metadata for.", "is_error": True})
            return False
        if self.is_local:
            if (table[-4:].lower() != '.tsv'):
                self.error({"decription": "Input table file does not end in .tsv", "is_error": True})
                return False
            # self.error({"description": "Local version of get_next_data is not yet complete.", "is_error": True})
            # return False
            # Look for file
            file_path = Path(__file__).parents[0] / table
            # lines = open(file_path).read().splitlines()
            # Use pandas to read tsv
            try:
                df = pd.read_csv(file_path, sep='\t', header=0)
                tsv = list(df.T.to_dict().values())
            except Exception as error:
                self.error({"description": "Failed to read tsv file {}. Check it's existence and ensure it is a well formatted tsv file with column headers.".format(file_path), "is_error": True})
                return False
            # We set table metadata (if metadata is already set its updated and index remains the same)
            self.set_table_metadata(table, tsv)
            # We must return an object like:
            # {
            #    '__list': 'users',
            #    '__timestamp_epoch_ms': 1613070277418,
            #    '__index': 0,
            #    '__remaining_count': 1,
            #    '__list_count': 1,
            #    'first_name': 'John',
            #    'last_name': 'Doe'
            # }
            metadata = self.get_table_metadata(table) # get table metadata (__ attributes above)
            index = metadata["__index"]
            if (looping and index == metadata['__list_count']):
                # reset index
                index = 0
                self.tables[table[:-4]]['__index'] = 0
            if (not looping and index == metadata['__list_count']):
                return None
            result = tsv[index] # get tsv row at index
            result.update(metadata) # add metadata
            self.set_next_index(table) # Update table index
            return result
        else:
            # Check if table has .extension and strip
            if (table[-4:].lower() == '.tsv'):
                table = table.split('.')[0]
            if (table not in self.tables):
                self.tables[table] = {"is_done": False}
            try:
                request = requests.get(self.url + 'list/get/' + table + '/next')
                if request.status_code == 200:
                    data = request.json()
                    if ('is_error' in data):
                        self.error({"description": "Table service reported an error.", "message": data['short_description']})
                        return False
                    if (not looping):
                        if (data['__remaining_count'] == 1 and not self.tables[table]['is_done']):
                            self.tables[table] = {"is_done": True}
                            self.ff_log(data)
                            return data
                        else:
                            if ('is_done' in self.tables[table]):
                                if (self.tables[table]["is_done"]):
                                    return None
                        self.ff_log(data)
                        return data
                    else:
                        self.ff_log(data)
                        return data
                else:
                    self.error({"description": "Failed to access ff table service.", "status_code": request.status_code})    
            except Exception as error:
                self.error({"description": "Failed to access ff table service.", "message": error})

    def get_data_random(self, table = None):
        if table == None:
            self.error({"description": "No table provided to get data from.", "is_error": true})
            return False
        if self.is_local:
            if (table[-4:].lower() != '.tsv'):
                self.error({"decription": "Input table file does not end in .tsv", "is_error": true})
                return False
            # Look for file
            file_path = Path(__file__).parents[0] / table
            # lines = open(file_path).read().splitlines()
            # Use pandas to read tsv
            try:
                df = pd.read_csv(file_path, sep='\t', header=0)
                tsv = list(df.T.to_dict().values())
                self.set_table_metadata(table, tsv)
                 # We must return an object like:
                # {
                #    '__list': 'users',
                #    '__timestamp_epoch_ms': 1613070277418,
                #    '__index': 0,
                #    '__remaining_count': 1,
                #    '__list_count': 1,
                #    'first_name': 'John',
                #    'last_name': 'Doe'
                # }
                index = random.choice(range(len(tsv)))
                result = tsv[index]
                metadata = self.get_table_metadata(table)
                metadata['__index'] = index
                result.update(metadata)
                return result
            except Exception as error:
                self.error({"description": "Failed to read tsv file {}. Check it's existence and ensure it is a well formatted tsv file with column headers.".format(file_path), "is_error": True})
                return False
        else:
            # Check if table has .extension and strip
            if (table[-4:].lower() == '.tsv'):
                table = table.split('.')[0]
            try:
                request = requests.get(self.url + 'list/get/' + table + '/random')
                if request.status_code == 200:
                    data = request.json()
                    if ('is_error' in data):
                        self.error({"description": "Table service reported an error.", "message": data['short_description']})
                        return False
                    return data
                else:
                    self.error({"description": "Failed to access ff table service.", "status_code": request.status_code})    
            except Exception as error:
                self.error({"description": "Failed to access ff table service.", "message": error})
        

    def error(self, error_json):
        self.ff_log(error_json)
    
    def event(self, event_json):
        self.ff_log(event_json)

    # helper to create FF_LOG formatted metrics JSON logs
    # input metric JSON
    # output FF_LOG {JSON}
    def ff_log(self, ff_json):
        # Print JSON
        print("FF_LOG {}".format(ff_json))
