from __future__ import unicode_literals

import os

from mopidy import exceptions, settings
from mopidy.utils import settings as setting_utils

from tests import unittest


class ValidateSettingsTest(unittest.TestCase):
    def setUp(self):
        self.defaults = {
            'MPD_SERVER_HOSTNAME': '::',
            'MPD_SERVER_PORT': 6600,
            'SPOTIFY_BITRATE': 160,
        }

    def test_no_errors_yields_empty_dict(self):
        result = setting_utils.validate_settings(self.defaults, {})
        self.assertEqual(result, {})

    def test_unknown_setting_returns_error(self):
        result = setting_utils.validate_settings(
            self.defaults, {'MPD_SERVER_HOSTNMAE': '127.0.0.1'})
        self.assertEqual(
            result['MPD_SERVER_HOSTNMAE'],
            'Unknown setting. Did you mean MPD_SERVER_HOSTNAME?')

    def test_custom_settings_does_not_return_errors(self):
        result = setting_utils.validate_settings(
            self.defaults, {'CUSTOM_MYAPP_SETTING': 'foobar'})
        self.assertNotIn('CUSTOM_MYAPP_SETTING', result)

    def test_not_renamed_setting_returns_error(self):
        result = setting_utils.validate_settings(
            self.defaults, {'SERVER_HOSTNAME': '127.0.0.1'})
        self.assertEqual(
            result['SERVER_HOSTNAME'],
            'Deprecated setting. Use MPD_SERVER_HOSTNAME.')

    def test_unneeded_settings_returns_error(self):
        result = setting_utils.validate_settings(
            self.defaults, {'SPOTIFY_LIB_APPKEY': '/tmp/foo'})
        self.assertEqual(
            result['SPOTIFY_LIB_APPKEY'],
            'Deprecated setting. It may be removed.')

    def test_unavailable_bitrate_setting_returns_error(self):
        result = setting_utils.validate_settings(
            self.defaults, {'SPOTIFY_BITRATE': 50})
        self.assertEqual(
            result['SPOTIFY_BITRATE'],
            'Unavailable Spotify bitrate. '
            'Available bitrates are 96, 160, and 320.')

    def test_two_errors_are_both_reported(self):
        result = setting_utils.validate_settings(
            self.defaults, {'FOO': '', 'BAR': ''})
        self.assertEqual(len(result), 2)


class SettingsProxyTest(unittest.TestCase):
    def setUp(self):
        self.settings = setting_utils.SettingsProxy(settings)
        self.settings.local.clear()

    def test_set_and_get_attr(self):
        self.settings.TEST = 'test'
        self.assertEqual(self.settings.TEST, 'test')

    def test_getattr_raises_error_on_missing_setting(self):
        try:
            self.settings.TEST
            self.fail('Should raise exception')
        except exceptions.SettingsError as e:
            self.assertEqual('Setting "TEST" is not set.', e.message)

    def test_getattr_raises_error_on_empty_setting(self):
        self.settings.TEST = ''
        try:
            self.settings.TEST
            self.fail('Should raise exception')
        except exceptions.SettingsError as e:
            self.assertEqual('Setting "TEST" is empty.', e.message)

    def test_getattr_does_not_raise_error_if_setting_is_false(self):
        self.settings.TEST = False
        self.assertEqual(False, self.settings.TEST)

    def test_getattr_does_not_raise_error_if_setting_is_none(self):
        self.settings.TEST = None
        self.assertEqual(None, self.settings.TEST)

    def test_getattr_does_not_raise_error_if_setting_is_zero(self):
        self.settings.TEST = 0
        self.assertEqual(0, self.settings.TEST)

    def test_setattr_updates_runtime_settings(self):
        self.settings.TEST = 'test'
        self.assertIn('TEST', self.settings.runtime)

    def test_setattr_updates_runtime_with_value(self):
        self.settings.TEST = 'test'
        self.assertEqual(self.settings.runtime['TEST'], 'test')

    def test_runtime_value_included_in_current(self):
        self.settings.TEST = 'test'
        self.assertEqual(self.settings.current['TEST'], 'test')

    def test_value_ending_in_path_is_expanded(self):
        self.settings.TEST_PATH = '~/test'
        actual = self.settings.TEST_PATH
        expected = os.path.expanduser('~/test')
        self.assertEqual(actual, expected)

    def test_value_ending_in_path_is_absolute(self):
        self.settings.TEST_PATH = './test'
        actual = self.settings.TEST_PATH
        expected = os.path.abspath('./test')
        self.assertEqual(actual, expected)

    def test_value_ending_in_file_is_expanded(self):
        self.settings.TEST_FILE = '~/test'
        actual = self.settings.TEST_FILE
        expected = os.path.expanduser('~/test')
        self.assertEqual(actual, expected)

    def test_value_ending_in_file_is_absolute(self):
        self.settings.TEST_FILE = './test'
        actual = self.settings.TEST_FILE
        expected = os.path.abspath('./test')
        self.assertEqual(actual, expected)

    def test_value_not_ending_in_path_or_file_is_not_expanded(self):
        self.settings.TEST = '~/test'
        actual = self.settings.TEST
        self.assertEqual(actual, '~/test')

    def test_value_not_ending_in_path_or_file_is_not_absolute(self):
        self.settings.TEST = './test'
        actual = self.settings.TEST
        self.assertEqual(actual, './test')

    def test_value_ending_in_file_can_be_none(self):
        self.settings.TEST_FILE = None
        self.assertEqual(self.settings.TEST_FILE, None)

    def test_value_ending_in_path_can_be_none(self):
        self.settings.TEST_PATH = None
        self.assertEqual(self.settings.TEST_PATH, None)
