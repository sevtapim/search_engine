# Small Search Engine

## Description

A search engine implementation using Pyhton programming language for the Introduction to Python course.

## Documentation

For detailed description how parts fit together and how the small search engine works, see [docs](./docs).

## Usage

1- Firstly, you need to generate the `index.txt` file. To create an index from the corpus file type:

```sh
cd src
python3 indexGenerator.py
```

2- Secondly, to get a list of file names that contain the search terms, type:

```sh
python3 indexSearcher.py
```

3- Now search session has started. During a session you can ask to the system things like:

```plain
Query >> AND(teacher NOT(OR(student students)))
Query >> AND(multimedia NOT(megabytes))
Query >> AND(students)
Query >> OR(teachers)
```

## License

MIT License