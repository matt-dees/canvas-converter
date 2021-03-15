import pandas as pd
import os
import json
import argparse


class BColors:
    """
    Holds escape codes for printing pretty colors to the terminal in error cases.
    """
    HEADER: str = '\033[95m'
    OKBLUE: str = '\033[94m'
    OKCYAN: str = '\033[96m'
    OKGREEN: str = '\033[92m'
    WARNING: str = '\033[93m'
    FAIL: str = '\033[91m'
    ENDC: str = '\033[0m'
    BOLD: str = '\033[1m'
    UNDERLINE: str = '\033[4m'


class Partners:
    """
    Intermediate representation for holding partner pairings. This is useful for projects where partners are an option.
    Typically the partners fill out a Google Form CSV. The CSV should be downloaded and a Parters object should be
    created by passing that file to the constructor.
    """
    def __init__(self, csv):
        """
        Creates a Partners instantiation from a CSV file. Important: if any partner is not reciprocated, for instance
        if student A wrote down student B as their partner, but student B did not write down student A, an error is
        thrown. This should be resolved manually and fixed before sent to the script.

        self._partners should store the partner dictionary internally.

        :param csv: CSV file downloaded from Google Form
        """
        # Hopefully these stay the same. Google Form columns for fetching the UCInetID of the partners
        P1_UCINETID_COLUMN: str = "What is your UCI Net ID (**NOT** your ID number)?  For most students, " \
                                  "it is the prefix to your @uci.edu email address)."
        P2_UCINETID_COLUMN: str = "What is your partner's UCI Net ID?"

        # Convert CSV to Pandas DataFrame for easy processing
        df = pd.read_csv(csv)

        # Function used to preprocess entries. E.g. remove whitespace
        preprocess = lambda x: x.lower().strip()

        # Extract UCInetIDs for each partner from the DataFrame.
        p1_ucinet_ids = map(preprocess,
                            df[P1_UCINETID_COLUMN])
        p2_ucinet_ids = map(preprocess, df[P2_UCINETID_COLUMN])

        # Merge the two columns representing each UCInetID. Easier to work with this way.
        d = dict(zip(p1_ucinet_ids, p2_ucinet_ids))

        # This is a tuple of students and their corresponding partner that WERE NOT reciprocated.
        # If this dictionary is not empty we have a problem. Print out the troublemakers and exit with error code.
        no_partners = dict(filter(lambda elem: elem[1] not in d or d[elem[1]] != elem[0], d.items()))

        # TODO: Still undecided what to do in this case. For now just dump the troublemakers so grader is aware.
        if len(no_partners) != 0:
            print(f"{BColors.WARNING} Warning! Asymmetric partners:")
            for (k, v) in no_partners.items():
                print(k, v)
            print(f"{BColors.ENDC}")

        # Set our instance variable to the dictionary of partners
        self._partners = d

    def as_dict(self):
        """
        Converts the internal partner representation to a dictionary so other classes can use it effectively.
        :return: Dictionary of partners. E.g.
        {
          "student1": "student2",
          "student2": "student1"
        }

        Each student that has a partner will have a key in this dictionary.
        """
        return dict(self._partners)


class Config:
    """
    This class is an intermediate representation for the configuration passed to the script. As of now the configuration
    should hold the following keys:

    """
    POINTS_POSSIBLE: str = "points"
    ASSIGNMENT_NAME: str = "assignment"
    GRADES: str = "grades"
    PARTNERS: str = "partners"  # optional
    OUTPUT_FILE: str = "output_file"

    def __init__(self, json_file):
        """
        Initialize the Config intermediate representation from a JSON file.

        Expected form:

        {
            "points": "5",
            "assignment": "Project 4",
            "output_file": "<path>/test.canvas",
            "grades": "<path>/proj4rawgrades.txt",
            "partners": "<path>/proj4partners.csv"
        }
        :param json_file: Path to JSON file that will be used to create the Config object. See above for expected keys.
        """
        def _verify_config(config):
            """
            Make sure expected keys are present in the config dict. Print errors and exit if mandatory keys are not
            there.
            :param config: Dictionary containing configuration parameters we retrieved from the JSON file.
            :return: None
            """

            if Config.POINTS_POSSIBLE not in config:
                print(f"{BColors.FAIL} Error! Key \"{Config.POINTS_POSSIBLE}\" not in config file. {BColors.ENDC}")
                exit(1)
            if Config.ASSIGNMENT_NAME not in config:
                print(f"{BColors.FAIL} Error! Key \"{Config.ASSIGNMENT_NAME}\" not in config file. {BColors.ENDC}")
                exit(1)
            if Config.GRADES not in config:
                print(f"{BColors.FAIL} Error! key \"{Config.GRADES}\" not in config file. {BColors.ENDC}")
                exit(1)
            if Config.OUTPUT_FILE not in config:
                print(f"{BColors.FAIL} Error! key \"{Config.OUTPUT_FILE}\" not in config file. {BColors.ENDC}")
                exit(1)

            # Make sure grades.csv file is actually a path to a file. Bail if not.
            if not os.path.isfile(config[Config.GRADES]):
                print(f"{BColors.FAIL} Error! {config[Config.GRADES]} is not a valid path. {BColors.ENDC}")
                exit(1)

            # Make sure partners.csv file is actually a path to a file if it's in the config.
            if Config.PARTNERS in config and not os.path.isfile(config[Config.PARTNERS]):
                print(f"{BColors.FAIL} Error! {config[Config.PARTNERS]} is not a valid path. {BColors.ENDC}")
                exit(1)

        # Make sure JSON file is actually a path to a file.
        if not os.path.isfile(json_file):
            print(f"{BColors.FAIL} Error! \"{json_file}\" is not a file, please enter a valid path. {BColors.ENDC}")
            exit(1)

        # Open the JSON file and use the json file to load its dict representation.
        with open(json_file, 'r') as js:
            try:
                config = json.load(js)
            except json.JSONDecodeError:
                config = None
                print(f"{BColors.FAIL} Error! Could not decode JSON file: \"{json_file}\". {BColors.ENDC}")
                exit(1)

        # Make sure expected keys are present.
        _verify_config(config)

        # Save config in private variable for use later.
        self._config = config

    def as_dict(self):
        """
        Return the Config object as a dictionary.
        :return: Dictionary representing the config. Should have the necessary keys by now. We error checked.
        """
        return dict(self._config)


class Grades:
    """
    Internal representation for the Grades. As of now you can only load from raw txt file. This file should be output
    from the grading script.
    """
    def __init__(self, csv):
        """
        Creates a Grades object from a "csv". "csv" in quotes because it's not really a CSV file. It is separated by
        tabs and doesn't really have column headers. For example,

        student1 8.0
        student2 0.0
        student 3 4.123

        Pandas has support for reading these types of files using read_csv() so that's why the parameter is called
        "csv".
        :param csv: grades.txt RAW file that will be used to fill in this object.
        """

        # Expect the file to be delimited by either tabs or commas.
        self._df = pd.read_csv(csv, sep='\t|,', engine='python', skipinitialspace=True, header=None)

        # Add columns because the raw txt file doesn't have them.
        self._df.columns = ["student", "score"]

        # Set index using our new columns.
        self._df = self._df.set_index("student")

    def merge_partners_grades(self, partners):
        """
        Adds entries for each student's partner. If the student's partner did not submit anything they will not be in
        the DataFrame. Thus we need to create a new entry for the student's partner with the correct score. They both
        get the same score. If both student submitted they get the minimum of the two scores.
        :param partners: Dictionary containing the partner pairings.
        :return: None
        """

        # If there were no partners for this assignment just get out.
        if not partners:
            return

        # Create a new DataFrame which will contain the partner entries. We'll append this at the end.
        partner_df = pd.DataFrame()

        # Loop through all students and:
        #   if they have a partner, create a DataFrame entry for the partner and add it to the new partner DataFrame.
        for student in self._df.index:
            # If the student doesn't have a partner, we don't need to modify the entry at all. Just continue.
            if student not in partners:
                continue

            # Lookup partner of the students
            partner = partners[student]

            # Lookup score we are going to assign to the partner
            student_score = self._df.loc[student]["score"]

            # Partner does not exist in the current DataFrame.
            # We need to create an entry for the partner with the score.
            if partner not in self._df.index:
                partner_df = partner_df.append({"student": partner, "score": student_score}, ignore_index=True)
                continue

            # TODO: Should we notify when this happens?
            # If we get here, both the partner and the student submitted code. Get the minimum and assign to both.
            partner_score = self._df.loc[partner]["score"]
            self._df.loc[student]["score"] = min(student_score, partner_score)
            self._df.loc[partners[student]]["score"] = min(student_score, partner_score)

        if not partner_df.empty:
            # partner_df holds the partner scores we need to merge into the original DataFrame. Let's do that.
            partner_df = partner_df.set_index("student")
            self._df = self._df.append(partner_df)

    def write(self, writer):
        """
        Write the Grades object to the File Object.
        :param writer: File Object we'll be writing to.
        :return: None
        """
        self._df.to_csv(writer, header=False)


class CanvasWriter:
    """
    Class used to encapsulate functionality for writing Canvas files. These files look like the following:

    ,Assignment Name
    Points Possible, 4
    student1, 3
    student2, 4
    student3, 0

    See: https://uci.service-now.com/sp/?id=kb_article&sysparm_article=KB0011908&sys_kb_id=92fed62c1bbbdc1436a321fcbc4bcbd7&spa=1
    """
    @staticmethod
    def write(output_file, grades, assignment_name, points_possible):
        """
        Write the grades in the correct format to <output_file>.
        :param output_file: File we're going to write to
        :param grades: Grades object containing student grades for the assignment.
        :param assignment_name: Assignment name, will be the first row of the file
        :param points_possible: Points possible for the assignment, will be in the second row
        :return: None
        """
        with open(output_file, 'w') as writer:
            writer.write(f",{assignment_name}\n")
            writer.write(f"Points Possible,{points_possible}\n")
            grades.write(writer)


def main():

    def _get_program_arguments():
        DESCRIPTION_STR: str = "Convert raw grade files to Canvas approved CSVs!"

        parser = argparse.ArgumentParser(description=DESCRIPTION_STR)
        parser.add_argument('--config', dest='config', type=str, required=True,
                            help="Path to JSON configuration file (e.g. config.json). "
                                 "See README.md for expected JSON keys.")
        args = parser.parse_args()
        return args

    args = _get_program_arguments()
    config = Config(json_file=args.config).as_dict()
    partners = Partners(csv=config[Config.PARTNERS]).as_dict() if Config.PARTNERS in config else None
    grades = Grades(csv=config[Config.GRADES])
    grades.merge_partners_grades(partners)
    CanvasWriter.write(output_file=config[Config.OUTPUT_FILE], grades=grades,
                       assignment_name=config[Config.ASSIGNMENT_NAME], points_possible=config[Config.POINTS_POSSIBLE])


if __name__ == "__main__":
    main()
