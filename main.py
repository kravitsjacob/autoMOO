
import pandas as pd
import utils


def main():

    # TODO create true input function
    df = pd.read_csv('example_datasets/water_energy_sensitivity.csv')
    group_labels_with_columns = dict(zip(df.columns.values, df.columns.values))  # Assumes each column is group
    group_values = df.to_numpy()

    # Create dashboard
    utils.create_dashboard(group_labels_with_columns, group_values)

    return 0


if __name__ == '__main__':
    main()
