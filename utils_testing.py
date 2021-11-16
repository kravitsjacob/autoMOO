"""Testing library for utils.py"""

import unittest
import pandas as pd
import numpy as np

import utils


class AnalysisLib(unittest.TestCase):

    def test_create_dashboard_default(self):
        """
        Default test to see if app is created with basic inputs
        """
        # Setup
        df = pd.DataFrame({'A': [0, 1], 'B': [2, 1]})
        cor_matrix = df.corr().to_numpy()
        group_labels_with_columns = dict(
            zip(df.columns.values, df.columns.values)
        )
        group_values = df.to_numpy()

        # Create AutoMOO app (assertion assumed no error raised)
        utils.create_dashboard(
            group_labels_with_columns,
            group_values,
            cor_matrix
        )

    def test_column_grouping_all_grouping(self):
        # Setup
        df_test = pd.DataFrame(
            {
                'A': [0, 1, 2],
                'B': [0, 1, 2],
                'C': [0, 1, 2]
            }
        )
        cor_matrix, cor_matrix_visual = utils.correlation_matrix(df_test, None)
        data = df_test.to_numpy()
        column_labels = dict(
            zip(df_test.columns.values, df_test.columns.values)
        )
        cor_threshold = 0.5

        # Run
        group_labels_with_columns, group_values = utils.group_columns(
            column_labels,
            data,
            cor_threshold,
            cor_matrix
        )

        # Test
        group_labels_with_columns_expect = {'Group 1': ['A', 'B', 'C']}
        group_values_expect = [np.array([0, 1, 2])]

        self.assertEqual(
            group_labels_with_columns,
            group_labels_with_columns_expect
        )

    def test_column_grouping_no_grouping(self):
        # Setup
        df_test = pd.DataFrame(
            {
                'A': [0, 1, 2],
                'B': [2, 1, 0],
                'C': [1, 1, 2]
            }
        )
        cor_matrix, cor_matrix_visual = utils.correlation_matrix(df_test, None)
        data = df_test.to_numpy()
        column_labels = dict(
            zip(df_test.columns.values, df_test.columns.values)
        )
        cor_threshold = 0.9

        # Run
        group_labels_with_columns, group_values = utils.group_columns(
            column_labels,
            data,
            cor_threshold,
            cor_matrix
        )

        # Test
        group_labels_with_columns_expect = {
            'Group 1': ['A'],
            'Group 2': ['B'],
            'Group 3': ['C']
        }
        group_values_expect = data

    def test_column_grouping_basic_grouping(self):
        # Setup
        df_test = pd.DataFrame(
            {
                'A': [0, 1, 2],
                'B': [0, 1, 1.5],
                'C': [2, 1, 0],
                'D': [1.5, 1, 0],
            }
        )
        cor_matrix, cor_matrix_visual = utils.correlation_matrix(df_test, None)
        data = df_test.to_numpy()
        column_labels = dict(
            zip(df_test.columns.values, df_test.columns.values)
        )
        cor_threshold = 0.9

        # Run
        group_labels_with_columns, group_values = utils.group_columns(
            column_labels,
            data,
            cor_threshold,
            cor_matrix
        )

        # Test
        group_labels_with_columns_expect = {
            'Group 1': ['A', 'B'],
            'Group 2': ['C', 'D']
        }
        group_values_expect = np.array(
            [
                [0, 2],
                [1, 1],
                [2, 0]
            ]
        )


if __name__ == '__main__':
    unittest.main()
