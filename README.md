# Simplex algorithm

This is my repo for the [simplex algorithm](https://en.wikipedia.org/wiki/Simplex_algorithm), which I need to implement for an Optimisation and Approximation class as part of my master. Please note that this is only academical work.

## Dependencies

This program is written in python3 and uses [numpy](http://www.numpy.org/) and [tabulate](https://pypi.python.org/pypi/tabulate)

## Use

`python3 simplex.py input_file`. By default, the program will use Bland's rule but one can specify which pivot rule to use: `-r` for random, `-m` for the maximum coefficient in the objective vector.

### Example
`python3 simplex.py input_file -r` runs the program with the pivot rule Random.

`-v` allows the user to run the verbose mode
