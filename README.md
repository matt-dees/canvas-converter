# README.md

## Convert raw txt files to Canvas approved CSVs!

## Usage

This script is used to convert raw grades txt files to files that can be uploaded to Canvas. It also has the
ability to merge partner grades if the partners are provided in a CSV file.

The script accepts input via JSON.

`raw_to_canvas.py --config <PATH_TO_JSON_CONFIG>`

A config file MUST have the following keys:

```
{
  "points": "<POINTS POSSIBLE ON THE ASSIGNMENT>",
  "assignment": "<NAME OF THE ASSIGNMENT>",
  "output_file": "<PATH TO OUTPUT FILE (e.g. output.canvas)>",
  "grades": "<PATH TO GRADES.TXT (e.g. grades.txt)>",
}
```

It can also contain a path to partners.csv file, which can be obtained by downloading the CSV of the Google Form.
```
{
    "partners": "<PATH TO PARTNERS.CSV>"
}
```

## Example

The `examples` directory contains exemplar files. 

`grades.txt` - Examples grades.txt file which would be output by the grading script.

`config.json` - Example JSON configuration file that would be passed to this script.

`partners.csv` - Example CSV file which would be downloaded from the Google Form.

The script would then be run with:

`raw_to_canvas.py --config examples/config.json`.

It would produce the file that can be uploaded to Canvas in `examples/output.canvas`

## Uploading to Canvas

The `*.canvas` file output by the script can be "uploaded" to Canvas via the **Convert file for import** button.
The output file from this script obeys the format specified here: https://uci.service-now.com/sp/?id=kb_article&sysparm_article=KB0011908&sys_kb_id=92fed62c1bbbdc1436a321fcbc4bcbd7&spa=1.

Once the file is converted using that button, you will be able to download aan `export.csv` file. This file can then be imported with
**Actions > Import**. 