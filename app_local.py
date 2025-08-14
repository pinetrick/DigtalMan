#!/user/bin/env python
# coding=utf-8
"""
@project : face2face_train
@author  : huyi
@file   : app.py
@ide    : PyCharm
@time   : 2023-12-06 19:04:21
"""
import os

os.chdir('/code')
import time
import traceback
from enum import Enum

from service.self_logger import logger
from flask import Flask, request
from service.config import *
from service.trans_dh_service import TransDhTask, Status,a, init_p, get_run_flag, task_dic

import json
import threading
import gc
import cv2

app = Flask(__name__)


class EasyResponse:
    def __init__(
            self,
            code,
            success,
            msg, data: dict):
        self.code = code
        self.success = success
        self.msg = msg
        self.data = data


class ResponseCode(Enum):
    system_error = [9999, '系统异常']
    success = [10000, '成功']
    busy = [10001, '忙碌中']
    error1 = [10002, '参数异常']
    error2 = [10003, '获取锁异常']
    error3 = [10004, '任务不存在']

@app.route('/easy/submit', methods=['POST'])
def easy_submit():
    request_data = json.loads(request.data)
    _code = request_data['code']
    if not get_run_flag():
        logger.warning('%s -> busy ', _code)
        return json.dumps(
            EasyResponse(ResponseCode.busy.value[0], True, ResponseCode.busy.value[1], {}),
            default=lambda obj: obj.__dict__,
            sort_keys=True, ensure_ascii=False,
            indent=4)

    try:
        if 'audio_url' not in request_data or request_data['audio_url'] == '':
            return json.dumps(
                EasyResponse(ResponseCode.error1.value[0], False, 'audio_url参数缺失', {}),
                default=lambda obj: obj.__dict__,
                sort_keys=True, ensure_ascii=False,
                indent=4)
        if 'video_url' not in request_data or request_data['video_url'] == '':
            return json.dumps(
                EasyResponse(ResponseCode.error1.value[0], False, 'video_url参数缺失', {}),
                default=lambda obj: obj.__dict__,
                sort_keys=True, ensure_ascii=False,
                indent=4)
        if 'code' not in request_data or request_data['code'] == '':
            return json.dumps(
                EasyResponse(ResponseCode.error1.value[0], False, 'code参数缺失', {}),
                default=lambda obj: obj.__dict__,
                sort_keys=True, ensure_ascii=False,
                indent=4)
        _audio_url = request_data['audio_url']
        _video_url = request_data['video_url']
        _code = request_data['code']

        if 'watermark_switch' not in request_data or request_data['watermark_switch'] == '':
            _watermark_switch = 0
        else:
            if str(request_data['watermark_switch']) == '1':
                _watermark_switch = 1
            else:
                _watermark_switch = 0
        if 'digital_auth' not in request_data or request_data['digital_auth'] == '':
            _digital_auth = 0
        else:
            if str(request_data['digital_auth']) == '1':
                _digital_auth = 1
            else:
                _digital_auth = 0
        if 'chaofen' not in request_data or request_data['chaofen'] == '':
            _chaofen = 0
        else:
            if str(request_data['chaofen']) == '1':
                _chaofen = 1
            else:
                _chaofen = 0

        if 'pn' not in request_data or request_data['pn'] == '':
            _pn = 1
        else:
            if str(request_data['pn']) == '1':
                _pn = 1
            else:
                _pn = 0
        task = TransDhTask(_code, _audio_url, _video_url, _watermark_switch, _digital_auth, _chaofen, _pn,)
        threading.Thread(target=task.work).start()
        return json.dumps(
            EasyResponse(ResponseCode.success.value[0], True, ResponseCode.success.value[0], {}),
            default=lambda obj: obj.__dict__,
            sort_keys=True, ensure_ascii=False,
            indent=4)
    except Exception as e:
        traceback.print_exc()
        return json.dumps(
            EasyResponse(ResponseCode.system_error.value[0], False, ResponseCode.system_error.value[1], {}),
            default=lambda obj: obj.__dict__,
            sort_keys=True, ensure_ascii=False,
            indent=4)
    finally:
        gc.collect()


@app.route('/easy/query', methods=['GET'])
def easy_query():
    del_flag = False
    get_data = request.args.to_dict()
    try:
        _code = get_data.get('code', '-1')
        if _code == '-1':
            return json.dumps(
                EasyResponse(ResponseCode.error1.value[0], False, 'code参数缺失', {}),
                default=lambda obj: obj.__dict__,
                sort_keys=True, ensure_ascii=False,
                indent=4)
        task_progress = task_dic.get(_code, '-1')
        if task_progress != '-1':
            d = task_progress
            _status = d[0]
            _progress = d[1]
            _result = d[2]
            _msg = d[3]
            if _status == Status.run:
                return json.dumps(
                    EasyResponse(ResponseCode.success.value[0], True, '', {
                        'code': _code,
                        'status': _status.value,
                        'progress': _progress,
                        'result': _result,
                        'msg': _msg
                    }),
                    default=lambda obj: obj.__dict__,
                    sort_keys=True, ensure_ascii=False,
                    indent=4)
            elif _status == Status.success:
                del_flag = True
                return json.dumps(
                    EasyResponse(ResponseCode.success.value[0], True, '', {
                        'code': _code,
                        'status': _status.value,
                        'progress': _progress,
                        'result': _result,
                        'msg': _msg,
                        'cost': d[4],
                        "video_duration": d[5],
                        "width": d[6],
                        "height": d[7]
                    }),
                    default=lambda obj: obj.__dict__,
                    sort_keys=True, ensure_ascii=False,
                    indent=4)
            elif _status == Status.error:
                del_flag = True
                return json.dumps(
                    EasyResponse(ResponseCode.success.value[0], True, '', {
                        'code': _code,
                        'status': _status.value,
                        'progress': _progress,
                        'result': _result,
                        'msg': _msg
                    }),
                    default=lambda obj: obj.__dict__,
                    sort_keys=True, ensure_ascii=False, indent=4)
        else:
            return json.dumps(
                EasyResponse(ResponseCode.error3.value[0], True, ResponseCode.error3.value[1], {}),
                default=lambda obj: obj.__dict__,
                sort_keys=True, ensure_ascii=False,
                indent=4)
    except Exception as e:
        traceback.print_exc()
        return json.dumps(
            EasyResponse(ResponseCode.system_error.value[0], False, ResponseCode.system_error.value[1], {}),
            default=lambda obj: obj.__dict__,
            sort_keys=True, ensure_ascii=False,
            indent=4)
    finally:
        if del_flag:
            try:
                del task_dic[_code]
            except Exception as e:
                traceback.print_exc()
                return json.dumps(
                    EasyResponse(ResponseCode.error3.value[0], True, ResponseCode.error3.value[1], {}),
                    default=lambda obj: obj.__dict__,
                    sort_keys=True, ensure_ascii=False,
                    indent=4)


if __name__ == '__main__':
    a()
    init_p()
    time.sleep(15)
    logger.info("******************* TransDhServer服务启动 *******************")
    if not os.path.exists(temp_dir):
        logger.info("创建临时目录")
        os.makedirs(temp_dir)
    if not os.path.exists(result_dir):
        logger.info("创建结果目录")
        os.makedirs(result_dir)

    app.run(
        host=str(server_ip),
        port=int(server_port),
        debug=False,
        threaded=False)
