"""Testing library for utils.py"""

import unittest
import pandas as pd

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


if __name__ == '__main__':
    unittest.main()
