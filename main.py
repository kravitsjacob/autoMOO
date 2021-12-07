"""Example Run Script for autoMOO"""

import utils


def main():
    """
    This is the main function which run all other functions
    """
    # Pulling in arguments through input parser
    data_file, cor_colormap = utils.input_parser()

    # Importing data
    data = utils.file_reader(data_file)

    # Create Dashboard
    app = utils.create_dashboard(
        data=data,
        cor_colormap=cor_colormap
    )

    # Run dashboard
    app.run_server(debug=True)

    return 0


if __name__ == '__main__':
    main()
