"""Example Run Script for AutoMOO"""

import pandas as pd
import utils


def main():
    # TODO create true input function
    df = pd.read_csv('example_datasets/machine_learning_dam_hazard.csv')
    cor_matrix = df.corr().to_numpy()
    group_labels_with_columns = dict(
        zip(df.columns.values, df.columns.values)
    )  # Assumes each column is group
    group_values = df.to_numpy()

    # Create dashboard
    app = utils.create_dashboard(
        group_labels_with_columns,
        group_values,
        cor_matrix
    )

    # Run dashboard
    app.run_server(debug=True)

    return 0


if __name__ == '__main__':
    main()
