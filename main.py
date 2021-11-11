"""Example Run Script for autoMOO"""

import pandas as pd
import utils



def main():
    '''
    This is the main function which run all other functions
    '''
    # pulling in arguments through input parser
    args = utils.input_parser()
    #pulling information from config file
    data_file, prefs,corr_colormap = utils.config_parser(args)
    #reading data csv
    df = pd.read_csv(data_file)
    # creating correlation matrices
    cor_matrix, cor_matrix_visual = utils.correlation_matrix(df,corr_colormap)
  
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
