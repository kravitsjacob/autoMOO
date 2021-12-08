"""Testing library for utils.py"""

import os
import unittest

import utils


class AnalysisLib(unittest.TestCase):

    def test_file_reader_import(self):
        """
        Basic test for the file reader
        """
        # Setup
        test_file = open('test.txt', 'w')
        test_file.write("A,B,C\n1,0.1,'1'\n 2,0.2,'2'\n3,0.3,'3'")
        test_file.close()

        # Run
        result = utils.file_reader('test.txt')
        os.remove('test.txt')

        # Test
        expect = [
            {'A': 1, 'B': 0.1, 'C': '1'},
            {'A': 2, 'B': 0.2, 'C': '2'},
            {'A': 3, 'B': 0.3, 'C': '3'}
        ]
        self.assertEqual(expect, result)

    def test_create_dashboard_default(self):
        """
        Default test to see if app is created with basic inputs
        """
        # Setup
        data = [
            {'A': 0, 'B': 0},
            {'A': 1, 'B': 1},
        ]

        # Create AutoMOO app (assertion assumed no error raised)
        utils.create_dashboard(
            data=data,
            cor_colormap='RdBu'
        )

    def test_column_grouping_all_grouping(self):
        """
        Test where all columns are grouped
        """
        # Setup
        data = [
            {'A': 0, 'B': 0, 'C': 0},
            {'A': 1, 'B': 1, 'C': 1},
            {'A': 2, 'B': 2, 'C': 2}
        ]
        cors, _ = utils.correlation_matrix(data, None)
        cor_threshold = 0.5

        # Run
        data_grouped, group_labels_with_columns = utils.group_columns(
            data=data,
            cors=cors,
            cor_threshold=cor_threshold,
        )

        # Test
        group_labels_with_columns_expect = {'Group 1': ['A', 'B', 'C']}
        data_grouped_expect = [
            {'Group 1': 0},
            {'Group 1': 1},
            {'Group 1': 2}
        ]
        self.assertEqual(
            group_labels_with_columns,
            group_labels_with_columns_expect
        )
        self.assertEqual(
            data_grouped,
            data_grouped_expect
        )

    def test_column_grouping_no_grouping(self):
        """
        Test where no columns are grouped
        """
        # Setup
        data = [
            {'A': 0, 'B': 2, 'C': 1},
            {'A': 1, 'B': 1, 'C': 1},
            {'A': 2, 'B': 0, 'C': 2}
        ]
        cors, _ = utils.correlation_matrix(data, None)
        cor_threshold = 0.9

        # Run
        data_grouped, group_labels_with_columns = utils.group_columns(
            data=data,
            cors=cors,
            cor_threshold=cor_threshold,
        )

        # Test
        group_labels_with_columns_expect = {
            'Group 1': ['A'],
            'Group 2': ['B'],
            'Group 3': ['C']
        }
        data_grouped_expect = [
            {'Group 1': 0, 'Group 2': 2, 'Group 3': 1},
            {'Group 1': 1, 'Group 2': 1, 'Group 3': 1},
            {'Group 1': 2, 'Group 2': 0, 'Group 3': 2}
        ]
        self.assertEqual(
            group_labels_with_columns,
            group_labels_with_columns_expect
        )
        self.assertEqual(
            data_grouped,
            data_grouped_expect
        )

    def test_column_grouping_basic_grouping(self):
        """
        Test where some columns are grouped
        """
        # Setup
        data = [
            {'A': 0, 'B': 0.0, 'C': 2, 'D': 1.5},
            {'A': 1, 'B': 1.0, 'C': 1, 'D': 1.0},
            {'A': 2, 'B': 1.5, 'C': 0, 'D': 0.0}
        ]
        cors, _ = utils.correlation_matrix(data, None)
        cor_threshold = 0.9

        # Run
        data_grouped, group_labels_with_columns = utils.group_columns(
            data=data,
            cors=cors,
            cor_threshold=cor_threshold,
        )

        # Test
        group_labels_with_columns_expect = {
            'Group 1': ['A', 'B'],
            'Group 2': ['C', 'D']
        }
        data_grouped_expect = [
            {'Group 1': 0, 'Group 2': 2},
            {'Group 1': 1, 'Group 2': 1},
            {'Group 1': 2, 'Group 2': 0}
        ]
        self.assertEqual(
            group_labels_with_columns,
            group_labels_with_columns_expect
        )
        self.assertEqual(
            data_grouped,
            data_grouped_expect
        )


if __name__ == '__main__':
    unittest.main()
