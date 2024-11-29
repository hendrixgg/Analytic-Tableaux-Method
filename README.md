# CISC/CMPE 204 Modelling Project

https://github.com/hendrixgg/Analytic-Tableaux-Method

Welcome to the major project for CISC/CMPE 204!

To note:
* The propositional logic formula parsing does not take into account operator precedence. So if you see a formula, without enough parentheses it may not represent exactly what you expect.

## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.
* `tableaux_prover`: Contains a python module with the necessary components to employ the [Method of Analytic Tableaux](https://en.wikipedia.org/wiki/Method_of_analytic_tableaux).
    * `formula_symbols.py`: Contains relevant datastructures, constants, and functions for working with symbols that make up propositional logic formulas.
    * `inference_rules.py`: Contains the InferenceRule class and the necessary information to model the inference rules used in the [Method of Analytic Tableaux](https://en.wikipedia.org/wiki/Method_of_analytic_tableaux).
    * `propositional_logic_formula.py`: Contains the PropositionalLogicFormula class, string conversion functions and one function to return all of the atomic propositions contained within a PropositionalLogicFormula object.
    * `tableaux_aggregator.py`: Contains a functoin to generate the branches for the tableau of a formula and some associated helper functions.
    * `tableaux_classifier.py`: Contains a function to classify a PropositionalLogicFormula as either tautology, contradiciton, or contingency using the [Method of Analytic Tableaux](https://en.wikipedia.org/wiki/Method_of_analytic_tableaux).



## Running With Docker

By far the most reliable way to get things running is with [Docker](https://www.docker.com). This section runs through the steps and extra tips to running with Docker. You can remove this section for your final submission, and replace it with a section on how to run your project.

1. First, download Docker https://www.docker.com/get-started, and get it running.

2. Navigate to your project folder on the command line.

3. We first have to build the course image. To do so use the command:
`docker build -t analytic-tableaux-method .`

4. Now that we have the image we can run the image as a container by using the command: `docker run -it -v $(pwd):/PROJECT analytic-tableaux-method /bin/bash`

    `$(pwd)` will be the current path to the folder and will link to the container

    `/PROJECT` is the folder in the container that will be tied to your local directory

5. From there the two folders should be connected, everything you do in one automatically updates in the other. For the project you will write the code in your local directory and then run it through the docker command line. A quick test to see if they're working is to create a file in the folder on your computer then use the terminal to see if it also shows up in the docker container.

6. End the terminal session using the `exit`.

### Mac Users w/ M1 Chips

If you happen to be building and running things on a Mac with an M1 chip, then you will likely need to add the following parameter to both the build and run scripts:

```
--platform linux/x86_64
```

For example, the build command would become:

```
docker build --platform linux/x86_64 -t analytic-tableaux-method .
```

### Mount on Different OS'

In the run script above, the `-v $(pwd):/PROJECT` is used to mount the current directory to the container. If you are using a different OS, you may need to change this to the following:

- Windows PowerShell: `-v ${PWD}:/PROJECT`
- Windows CMD: `-v %cd%:/PROJECT`
- Mac: `-v $(pwd):/PROJECT`

Finally, if you are in a folder with a bunch of spaces in the absolute path, then it will break things unless you "quote" the current directory like this (e.g., on Windows CMD):

```
docker run -it -v "%cd%":/PROJECT analytic-tableaux-method
```
