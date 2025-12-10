# -*- coding: utf-8 -*-
import unittest
from context import monday_com


class TestMondayComIntegration(unittest.TestCase):
    """Test suite for Monday.com integration"""

    def test_integration_loaded(self):
        """Test that the integration loads successfully"""
        self.assertIsNotNone(monday_com)
        self.assertEqual(monday_com.name, "Monday.com")


if __name__ == '__main__':
    unittest.main()
