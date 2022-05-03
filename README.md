The purpose of this project is to define a well-specified SSV format for tabular data, and
provider libraries and tools for working with this format.

# What is SSV?

SSV stands for "Separator Separated Values". It is a file format similar to CSV or TSV, but
instead of using commas (or tabs) and newlines to separate fields and records, it uses the ASCII
Unit Separator and Record Separator characters.

# Why SSV?

The problem with CSV and TSV is that the delimiters can, and often do, occur in field content, which
necessitates some form of escaping or quoting. While many applications support such escaping or
quoting, there is not a well-established standard, and applications can treat the same file
inconsistently. In addition, properly generating or parsing escapes and quotes can be difficult with
standard Unix commands, or in languages that don't have a CSV library with just support.

It turns out ASCII already has dedicated characters for separators, and those characters
are very rare in most text. So, by using those characters, we can avoid the problem of text
conflicting with the delimiters.

Unfortunately, these characters are non-printing, so displaying the file on a terminal or in a
text editor isn't as human friendly as CSV or TSV. This is somewhat alleviated by making the
delimiter include a whitespace character as well, so the actual delimiters are `\x1f\t` for the
field delimiter and `\x1e\n` for the record delimiter. Which means when printed to terminal for
example, it will look similar to a TSV file.


# Separator Separated Values

Text is encoded as UTF-8.

Records (rows) are separated by '\\x1e\\n' (Record Separator [RS] and newline [LF])

Fields are separated by '\\x1f\\t' (Unit Separator [US] and tab [HT])


# "Compact" Separator Separated Values

Similar to above except the separators don't include newlines or tabs.

## Future extensions

The following are currently out of scope for this project, but may possibly be explored as extensions
at a later time:

- Escaping the delimiters. (probably only necessary for binary data that would probably be better
  to base64 encode anyway).
- Multiple documents in a single file delimited by the File Separator and/or Group Separator
- Inline indication if first row is header. For now, the application or user is responsible for determining this.
- Non-text data types. For now, parsing fields as anything besides text is up to the application.
