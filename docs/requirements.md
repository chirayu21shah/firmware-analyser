# Part 2 - Implementation

## 1. Firmware Analyzer

Suppose that one of the automotive vendors sent to you a firmware archive and asked you to find different security issues. We know that some of the vendors are using a special authentication tokens in the following format:

Starting with `"<Tkn"` then later 3 digits, 5 English capital letters followed by a `"Tkn>"`.

For example: `<Tkn435JFIRKTkn>`.

You should implement a function that receives a directory path on the disk and a path to a CSV file output. The function should find the above pattern in all the files under the directory tree of the given path and report the results into the output CSV in the following format:

- Path - The relative path of the found file to the given root path
- Token - The identified token string
- Occurrences - The number of occurrences of the Token inside the file Path

The results should be sorted by (Path, Occurrences, Token)

The function also needs to print to a json of the total finding of each token in all of the files. for example, if token `<Tkn435JFIRKTkn>` was found only in f1- 5 times and in f2 - 3 times it should print:

```json
{"<Tkn435JFIRKTkn>": 8}
```

```python
def analyze_firmware(directory_path, csv_output_path):
 """
 Reports to the csv output path all the found files and token
information
 """
```

Notes:

- The function should work as fast as possible - so multi-threading /multi-processing should be used.
- You can assume that each file can be read into the memory

## 2. Flask HTTP Server

Implement a Flask HTTP Server that receives a firmware file (as in questions 1), runs the analysis and returns to the user a json response with the statistics.

## 3. Asynchronous Analysis

Add ability to do the analysis in asynchronous way - meaning that the flask server will have a thread pool / process pool that each one of the requests will be analyzed as a job and the user will be required to pull the results (You can assume that the results will be managed in the memory)