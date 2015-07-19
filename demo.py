#!/usr/bin/env python
import flask
import multiprocessing
import os
import sys
from flask import request

# CAUTION! This line is only used for a development environment, when pywps is not installed
from werkzeug.wrappers import Response

sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.path.pardir))

from server import Server
from processes.sleep import Sleep
from processes.ultimate_question import UltimateQuestion
from processes.centroids import Centroids
from processes.sayhello import SayHello
from processes.feature_count import FeatureCount
from processes.buffer import Buffer
from processes.area import Area
from processes.bboxinout import Box


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--waitress', action='store_true')
    parser.add_argument('-d', '--daemon', action='store_true')
    args = parser.parse_args()

    if args.daemon:
        pid = None
        try:
            pid = os.fork()
        except OSError as e:
             raise Exception, "%s [%d]" % (e.strerror, e.errno)

        if (pid == 0):
            os.setsid()
            start(args)
        else:
            os._exit(0)

    else:
        start(args)

def start(args, kill = None):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pywps.cfg")

    processes = [
        FeatureCount(),
        SayHello(),
        Centroids(),
        UltimateQuestion(),
        Sleep(),
        Buffer(),
        Area(),
        Box()
    ]

    # List of servers to start up
    server_list = [
        Server(processes=processes, host='0.0.0.0', port=5001, config_file=config_file),
        Server(processes=processes, host='0.0.0.0', port=5002)
    ]

    # List of server instances running
    server_instances = {}
    counter = 0
    for s in server_list:
        p = multiprocessing.Process(target=s.run)
        p.start()
        server_instances[counter] = {'Process': p, 'ServerObject': s}
        counter += 1

    if args.waitress:
        # TODO: make waitress use multiprocessing
        pass
        import waitress
        from pywps import configuration

        configuration.load_configuration(config_file)
        host = configuration.get_config_value('wps', 'serveraddress').split('://')[1]
        port = int(configuration.get_config_value('wps', 'serverport'))

        #waitress.serve(s.app, host=host, port=port)
    else:
        rest_app = flask.Flask(__name__)

        @rest_app.route('/rest/server', methods=['GET', 'POST'])
        def rest_servers():
            js = {}
            for s in server_instances:
                process = server_instances[s]['Process']
                server = server_instances[s]['ServerObject']
                json_server = {}
                json_server['pid'] = process.pid
                json_server['host'] = server.host
                json_server['port'] = server.port
                json_server['alive'] = process.is_alive()
                js[s] = json_server
            response = flask.jsonify(js)
            response.status_code = 200
            return response

        @rest_app.route('/rest/server/<int:serverid>', methods=['GET', 'PUT', 'DELETE'])
        def rest_server(serverid):
            if request.method == 'GET':
                try:
                    process = server_instances[serverid]['Process']
                    server = server_instances[serverid]['ServerObject']
                    json_server = {}
                    json_server['pid'] = process.pid
                    json_server['host'] = server.host
                    json_server['port'] = server.port
                    json_server['alive'] = process.is_alive()
                    response = flask.jsonify(json_server)
                    response.status_code = 200
                    return response
                except:
                    return Response(status=500)

            if request.method == 'PUT':
                try:
                    # only parse json and if Header Content-Type is application/json
                    data = request.get_json()

                    if 'host' not in data:
                        return Response(response='No host specified!', status=400)

                    if 'port' not in data:
                        return Response(response='No port specified!', status=400)

                    # remove running instance so we can create an updated version
                    if serverid in server_instances:
                        _terminate_process(serverid)

                    # create and add process
                    server_put = Server(processes=processes, host=data['host'], port=data['port'])
                    process_put = multiprocessing.Process(target=server_put.run)
                    process_put.start()
                    server_instances[serverid] = {'Process': process_put, 'ServerObject': server_put}
                    return Response(status=201)
                except:
                    return Response(status=500)

            if request.method == 'DELETE':
                try:
                    if serverid in server_instances:
                        _terminate_process()
                    return Response(status=200)
                except Exception as e:
                    return Response(status=500)

            return Response(status=405)

        # Terminates a process and removes it from the list
        def _terminate_process(serverid):
            process_delete = server_instances[serverid]['Process']
            process_delete.terminate()
            process_delete.join()
            if process_delete.is_alive():
                return Response(response='Error terminating process: %s with pid: %s' % (serverid, process_delete.pid), status=500)
            del server_instances[serverid]

        rest_app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
