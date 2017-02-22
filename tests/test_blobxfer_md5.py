# coding=utf-8
"""Tests for md5"""

# stdlib imports
import time
# non-stdlib imports
# local imports
import blobxfer.models as models
import blobxfer.util as util
# module under test
import blobxfer.md5 as md5


def test_done_cv():
    a = None
    try:
        a = md5.LocalFileMd5Offload()
        assert a.done_cv == a._done_cv
    finally:
        if a:
            a.finalize_md5_processes()


def test_finalize_md5_processes():
    a = None
    try:
        a = md5.LocalFileMd5Offload(num_workers=0)
    finally:
        if a:
            a.finalize_md5_processes()

    for proc in a._md5_procs:
        assert not proc.is_alive()


def test_from_add_to_done_non_pagealigned(tmpdir):
    file = tmpdir.join('a')
    file.write('abc')

    remote_md5 = util.compute_md5_for_file_asbase64(str(file))

    a = None
    try:
        a = md5.LocalFileMd5Offload(num_workers=1)
        result = a.get_localfile_md5_done()
        assert result is None

        a.add_localfile_for_md5_check(
            str(file), remote_md5, models.AzureStorageModes.Block)
        i = 33
        checked = False
        while i > 0:
            result = a.get_localfile_md5_done()
            if result is None:
                time.sleep(0.3)
                i -= 1
                continue
            assert len(result) == 2
            assert result[0] == str(file)
            assert result[1]
            checked = True
            break
        assert checked
    finally:
        if a:
            a.finalize_md5_processes()


def test_from_add_to_done_pagealigned(tmpdir):
    file = tmpdir.join('a')
    file.write('abc')

    remote_md5 = util.compute_md5_for_file_asbase64(str(file), True)

    a = None
    try:
        a = md5.LocalFileMd5Offload(num_workers=1)
        result = a.get_localfile_md5_done()
        assert result is None

        a.add_localfile_for_md5_check(
            str(file), remote_md5, models.AzureStorageModes.Page)
        i = 33
        checked = False
        while i > 0:
            result = a.get_localfile_md5_done()
            if result is None:
                time.sleep(0.3)
                i -= 1
                continue
            assert len(result) == 2
            assert result[0] == str(file)
            assert result[1]
            checked = True
            break
        assert checked
    finally:
        if a:
            a.finalize_md5_processes()
