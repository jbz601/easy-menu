# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import sys
import time
from mog_commons.unittest import TestCase, base_unittest
from easy_menu.setting.setting import Loader
from easy_menu.exceptions import EncodingError

if sys.version_info < (3, 3):
    import mock
else:
    from unittest import mock


class TestLoader(TestCase):
    def _testfile(self, filename):
        return os.path.join(os.path.abspath(os.path.curdir), 'tests', 'resources', filename)

    def test_is_url(self):
        self.assertEqual(Loader('.', '.').is_url('http://example.com/foo.yml'), True)
        self.assertEqual(Loader('.', '.').is_url('https://example.com/foo.yml'), True)
        self.assertEqual(Loader('.', '.').is_url('ftp://example.com/foo.yml'), False)
        self.assertEqual(Loader('.', '.').is_url('/etc/foo/bar.yml'), False)

    def test_load(self):
        self.maxDiff = None

        with self.withAssertOutput('Reading file: %s\n' % self._testfile('minimum.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', stdout=out).load(False, self._testfile('minimum.yml')),
                {'': []}
            )

        with self.withAssertOutput('Reading file: %s\n' % self._testfile('nested.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', stdout=out).load(False, self._testfile('nested.yml')),
                {'Main Menu': [
                    {'Sub Menu 1': [
                        {'Menu 1': 'echo 1'},
                        {'Menu 2': 'echo 2'}
                    ]},
                    {'Sub Menu 2': [
                        {'Sub Menu 3': [
                            {'Menu 3': 'echo 3'},
                            {'Menu 4': 'echo 4'}
                        ]}, {'Menu 5': 'echo 5'}
                    ]},
                    {'Menu 6': 'echo 6'}]}
            )
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('with_meta.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', stdout=out).load(False, self._testfile('with_meta.yml')),
                {'meta': {'work_dir': '/tmp', 'lock': True},
                 'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}, {'Menu 4': 'echo 4'},
                               {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}]}
            )
        with self.withAssertOutput('', '') as (out, err):
            loader = Loader('.', '.', stdout=out)
            loader.cache = {(False, 'https://example.com/foo.yml'): {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            }

            self.assertEqual(
                loader.load(False, 'https://example.com/foo.yml'),
                {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            )
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('minimum.yml'), '') as (out, err):
            self.assertEqual(
                Loader(os.path.join(os.path.abspath(os.path.curdir), 'tests', 'resources'), '.', stdout=out).load(
                    False, 'minimum.yml'
                ),
                {'': []}
            )
        # multiple commands
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('multi_commands.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', stdout=out).load(False, self._testfile('multi_commands.yml')),
                {
                    'Main Menu': [
                        {'Sub Menu 1': [
                            {'Menu 1': ['echo 1', 'echo 2']},
                        ]},
                        {'Sub Menu 2': [
                            {'Sub Menu 3': [
                                {'Menu 3': 'echo 3'},
                                {'Menu 4': 'echo 4'}
                            ]}, {'Menu 5': 'echo 5'}
                        ]},
                        {'Menu 6': ['echo 1', 'echo 2', 'false', 'echo 3']}]
                }
            )
        # template
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('with_template.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', stdout=out).load(False, self._testfile('with_template.yml')),
                {
                    'Main Menu': [
                        {'Menu 1': 'echo 1'},
                        {'Menu 2': 'echo 2'},
                        {'Menu 3': 'echo 3'},
                    ]
                })
        path = self._testfile('with_template_utf8_ja.yml')
        with self.withAssertOutput('Reading file: %s\n' % path, '') as (out, err):
            self.assertEqual(
                Loader('.', '.', stdout=out).load(False, path),
                {
                    "メインメニュー": [
                        {"サービス稼動状態確認": "echo 'サービス稼動状態確認'"},
                        {"サーバリソース状況確認": "echo 'サーバリソース状況確認'"},
                        {"業務状態制御メニュー": [
                            {"業務状態確認": "echo '業務状態確認'"},
                            {"業務開始": "echo '業務開始'"},
                            {"業務終了": "echo '業務終了'"}
                        ]},
                        {"Webサービス制御メニュー": [
                            {"Webサービス状態確認": "echo 'Webサービス状態確認'"},
                            {"Webサービス起動": "echo 'Webサービス起動'"},
                            {"Webサービス停止": "echo 'Webサービス停止'"}
                        ]},
                        {"サーバ再起動": "echo 'サーバ再起動'"}
                    ]
                }
            )

    def test_load_unicode(self):
        expect_data = {
            "メインメニュー": [
                {"サービス稼動状態確認": "echo 'サービス稼動状態確認'"},
                {"サーバリソース状況確認": "echo 'サーバリソース状況確認'"},
                {"業務状態制御メニュー": [
                    {"業務状態確認": "echo '業務状態確認'"},
                    {"業務開始": "echo '業務開始'"},
                    {"業務終了": "echo '業務終了'"}
                ]},
                {"Webサービス制御メニュー": [
                    {"Webサービス状態確認": "echo 'Webサービス状態確認'"},
                    {"Webサービス起動": "echo 'Webサービス起動'"},
                    {"Webサービス停止": "echo 'Webサービス停止'"}
                ]},
                {"サーバ再起動": "echo 'サーバ再起動'"}
            ]
        }
        # utf-8
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('utf8_ja.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', encoding='utf-8', stdout=out).load(False, self._testfile('utf8_ja.yml')),
                expect_data
            )
        # utf-8 with fallback
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('utf8_ja.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', encoding='sjis', stdout=out).load(False, self._testfile('utf8_ja.yml')),
                expect_data
            )
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('utf8_ja.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', encoding='ascii', stdout=out).load(False, self._testfile('utf8_ja.yml')),
                expect_data
            )
        # SJIS
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('sjis_ja.yml'), '') as (out, err):
            self.assertEqual(
                Loader('.', '.', encoding='sjis', stdout=out).load(False, self._testfile('sjis_ja.yml')),
                expect_data
            )

    @base_unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
    def test_load_dynamic(self):
        with self.withAssertOutput(
                """Executing: echo '{"Main Menu":[{"Menu 1":"echo 1"},{"Menu 2":"echo 2"}]}'\n""", '') as (out, err):
            self.assertEqual(Loader('.', '.', encoding='utf-8', stdout=out).load(
                True,
                """echo '{"Main Menu":[{"Menu 1":"echo 1"},{"Menu 2":"echo 2"}]}'"""),
                {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            )

    @mock.patch('easy_menu.setting.loader.urlopen')
    def test_load_http(self, urlopen_mock):
        # create a mock
        urlopen_mock.return_value.read.return_value = b'{"title":[{"a":"x"},{"b":"y"}]}'

        with self.withAssertOutput('Reading from URL: http://localhost/xxx.yml\n', '') as (out, err):
            self.assertEqual(
                Loader('.', '.', encoding='utf-8', stdout=out).load(False, 'http://localhost/xxx.yml'),
                {'title': [{'a': 'x'}, {'b': 'y'}]}
            )

    @mock.patch('easy_menu.setting.loader.urlopen')
    def test_load_encoding_error_http(self, urlopen_mock):
        # create a mock
        urlopen_mock.return_value.read.return_value = '{"あ":[{"い":"う"},{"え":"お"}]}'.encode('sjis')

        path = 'http://localhost/xxx.yml'
        with self.withAssertOutput('Reading from URL: %s\n' % path, '') as (out, err):
            self.assertRaisesMessage(
                EncodingError,
                'Failed to decode with utf-8: %s' % path,
                Loader('.', '.', encoding='utf-8', stdout=out).load, False, path
            )

    def test_load_encoding_error_cmd(self):
        cmd = 'cat tests/resources/sjis_ja.yml'  # output should be SJIS

        with self.withAssertOutput('Executing: %s\n' % cmd, '') as (out, err):
            self.assertRaisesMessage(
                EncodingError,
                'Failed to decode with utf-8: %s' % cmd,
                Loader('.', '.', encoding='utf-8', stdout=out).load, True, cmd
            )

    @base_unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
    def test_eval_command_with_cache(self):
        self.maxDiff = None

        cache_dir = os.path.join(os.path.curdir, 'tests', 'work')
        cache_path = os.path.join(cache_dir, '0a', '94fa9075f9a2fb97d46556e1628aaf')
        cmd = """echo "Menu:\\n  - $(date +%H%M%S): echo ." """
        expected = '\n'.join([
            'Executing: echo "Menu:\\n  - $(date +%H%M%S): echo ." ',
            'Writing eval cache: %s' % cache_path,
            'Reading eval cache: %s' % cache_path,
            'Executing: echo "Menu:\\n  - $(date +%H%M%S): echo ." ',
            'Writing eval cache: %s' % cache_path,
            'Executing: echo "Menu:\\n  - $(date +%H%M%S): echo ." ',
            'Writing eval cache: %s' % cache_path,
            ''
        ])

        def clear_files():
            if os.path.exists(cache_path):
                os.remove(cache_path)
            if os.path.exists(os.path.dirname(cache_path)):
                os.removedirs(os.path.dirname(cache_path))
            if os.path.exists(cache_dir):
                os.removedirs(cache_dir)

        try:
            with self.withAssertOutput(expected, '') as (out, err):
                # create cache
                d1 = Loader('.', cache_dir, encoding='utf-8', stdout=out)._eval_command_with_cache(cmd, 2)

                # read from cache
                d2 = Loader('.', cache_dir, encoding='utf-8', stdout=out)._eval_command_with_cache(cmd, 2)
                self.assertEqual(d1, d2)

                # create cache
                time.sleep(2)
                d3 = Loader('.', cache_dir, encoding='utf-8', stdout=out)._eval_command_with_cache(cmd, 2)
                self.assertNotEqual(d1, d3)

                # not use cache
                time.sleep(1)
                d4 = Loader('.', cache_dir, encoding='utf-8', stdout=out, clear_cache=True
                            )._eval_command_with_cache(cmd, 10)
                self.assertNotEqual(d3, d4)
        finally:
            clear_files()
